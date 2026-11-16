"""Tests for iconic.py. Run from the skill root:

    python3 -m unittest discover -s tools -v

The live path needs a running Obsidian, so these tests drive it through a
fake CLI. The JS that runs inside Obsidian is checked under node against a
fake app; those tests skip when node is absent.
"""
import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import iconic  # noqa: E402

NODE = shutil.which("node")


def run_cli(args, env=None):
    return subprocess.run(
        [sys.executable, str(HERE / "iconic.py"), *args],
        capture_output=True, text=True, env={**os.environ, **(env or {})},
        stdin=subprocess.DEVNULL,
    )


class Merge(unittest.TestCase):
    def test_icon_only_keeps_color_and_unsynced(self):
        cur = {"a.md": {"icon": "x", "color": "red", "unsynced": ["d"]}}
        out, _ = iconic.merge(cur, {"a.md": {"icon": "y"}})
        self.assertEqual(out["a.md"], {"icon": "y", "color": "red", "unsynced": ["d"]})

    def test_color_only_keeps_icon(self):
        out, _ = iconic.merge({"a.md": {"icon": "x"}}, {"a.md": {"color": "blue"}})
        self.assertEqual(out["a.md"], {"icon": "x", "color": "blue"})

    def test_null_field_removes_that_field(self):
        cur = {"a.md": {"icon": "x", "color": "red"}}
        out, _ = iconic.merge(cur, {"a.md": {"color": None}})
        self.assertEqual(out["a.md"], {"icon": "x"})

    def test_null_entry_removes_entry_with_unsynced(self):
        cur = {"a.md": {"icon": "x", "unsynced": ["d"]}, "b.md": {"icon": "z"}}
        out, _ = iconic.merge(cur, {"a.md": None})
        self.assertEqual(out, {"b.md": {"icon": "z"}})

    def test_input_is_not_mutated(self):
        cur = {"a.md": {"icon": "x"}}
        iconic.merge(cur, {"a.md": {"icon": "y"}})
        self.assertEqual(cur, {"a.md": {"icon": "x"}})

    def test_reports_paths_that_would_get_an_icon(self):
        _, needs = iconic.merge({"gone.md": {"icon": "x"}}, {"new.md": {"icon": "y"}, "gone.md": None})
        self.assertEqual(needs, ["new.md"])


class PluginOrder(unittest.TestCase):
    """The plugin sorts Object.entries() with the default comparator"""

    def test_prefix_key_sorts_after_its_extension(self):
        # "a b,[object Object]" < "a,[object Object]" because " " < ","
        self.assertEqual(iconic.plugin_order(["a", "a b"]), ["a b", "a"])

    def test_astral_char_sorts_by_utf16_units(self):
        # U+1F600 is D83D DE00 in UTF-16, below U+FF01
        self.assertEqual(iconic.plugin_order(["！", "\U0001F600"]), ["\U0001F600", "！"])


class Spec(unittest.TestCase):
    def test_rejects_unknown_field(self):
        with self.assertRaises(iconic.UsageError):
            iconic.check_ops({"a.md": {"icon": "x", "colour": "red"}})

    def test_rejects_escaping_path(self):
        for bad in ("../x.md", "a/../../x.md", "/etc/x", ""):
            with self.assertRaises(iconic.UsageError):
                iconic.check_ops({bad: None})

    def test_accepts_vault_root_key(self):
        self.assertEqual(iconic.check_ops({"/": {"icon": "x"}}), {"/": {"icon": "x"}})

    def test_keeps_a_key_exactly_as_written(self):
        # data.json can hold both "a/b" and a stray "a/b/"; each must stay addressable
        ops = {"a/b": {"icon": "x"}, "a/b/": None}
        self.assertEqual(iconic.check_ops(ops), ops)


class Chunks(unittest.TestCase):
    def test_chunks_cover_all_ops_and_fit_the_limit(self):
        ops = {f"dir/note {i}.md": {"icon": "lucide-sigma"} for i in range(500)}
        chunks = iconic.chunk(ops, limit=2000)
        self.assertGreater(len(chunks), 1)
        merged = {}
        for c in chunks:
            self.assertLessEqual(len(json.dumps(c, ensure_ascii=False).encode()), 2000)
            merged.update(c)
        self.assertEqual(merged, ops)

    def test_every_command_fits_one_cli_frame(self):
        base = "/home/user/Хранилище"
        ops = {f"05. Конспекты/Курс/Тема номер {i}.md": {"icon": "👨‍🎨", "color": "yellow"} for i in range(3000)}
        parts = iconic.chunk(ops, iconic.ops_budget(base))
        self.assertGreater(len(parts), 1)
        for part in parts:
            for write in (True, False):
                self.assertLess(len(iconic.apply_js(part, base, write).encode()), iconic.MESSAGE_LIMIT)


class ParseOutput(unittest.TestCase):
    def test_value(self):
        self.assertEqual(iconic.parse_eval('=> {"a": 1}\n'), {"a": 1})

    def test_app_error_with_exit_zero(self):
        with self.assertRaises(iconic.AppError):
            iconic.parse_eval("Error: boom\n")


class FakeVault(unittest.TestCase):
    """A scratch vault with a data.json and a fake CLI"""

    DATA = {
        "biggerIcons": "off",
        "fileIcons": {"a.md": {"icon": "x"}, "b.md": {"icon": "y", "color": "red"}},
        "maxBackups": 5,
    }

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = pathlib.Path(self.tmp.name) / "vault"
        cfg = self.vault / ".obsidian/plugins/iconic"
        cfg.mkdir(parents=True)
        self.data = cfg / "data.json"
        self.data.write_text(json.dumps(self.DATA, indent=2, ensure_ascii=False), encoding="utf-8")
        for f in ("a.md", "b.md", "c.md"):
            (self.vault / f).write_text("", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def fake_cli(self, body):
        path = pathlib.Path(self.tmp.name) / "fake-cli"
        path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IEXEC)
        return {"OBSIDIAN_CLI": str(path)}

    def unreachable(self):
        return self.fake_cli(f"echo '{iconic.UNREACHABLE}'\nexit 1\n")

    def run_iconic(self, *args, env=None):
        return run_cli(["--vault", str(self.vault), *args], env=env)


class Offline(FakeVault):
    def test_without_flag_unreachable_app_is_exit_3_and_file_untouched(self):
        before = self.data.read_bytes()
        r = self.run_iconic("set", "c.md", "--icon", "z", env=self.unreachable())
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("--offline", r.stderr)
        self.assertEqual(self.data.read_bytes(), before)

    def test_offline_refuses_when_app_is_reachable(self):
        before = self.data.read_bytes()
        env = self.fake_cli("echo '=> 1'\n")
        r = self.run_iconic("--offline", "set", "c.md", "--icon", "z", env=env)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("running", r.stderr)
        self.assertEqual(self.data.read_bytes(), before)

    def test_offline_set_writes_plugin_format(self):
        r = self.run_iconic("--offline", "set", "c.md", "b.md", "--icon", "📐", env=self.unreachable())
        self.assertEqual(r.returncode, 0, r.stderr)
        want = json.loads(json.dumps(self.DATA))
        want["fileIcons"]["c.md"] = {"icon": "📐"}
        want["fileIcons"]["b.md"]["icon"] = "📐"
        self.assertEqual(self.data.read_text(encoding="utf-8"), json.dumps(want, indent=2, ensure_ascii=False))

    def test_offline_undo_spec_restores_the_file(self):
        before = self.data.read_bytes()
        r = self.run_iconic("--offline", "set", "a.md", "b.md", "c.md", "--color", "blue", env=self.unreachable())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotEqual(self.data.read_bytes(), before)
        spec = pathlib.Path(self.tmp.name) / "undo.json"
        spec.write_text(json.dumps(json.loads(r.stdout)["undo"]), encoding="utf-8")
        r = self.run_iconic("--offline", "apply", str(spec), env=self.unreachable())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.data.read_bytes(), before)

    def test_offline_unset_without_flags_removes_entry(self):
        r = self.run_iconic("--offline", "unset", "b.md", env=self.unreachable())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("b.md", json.loads(self.data.read_text(encoding="utf-8"))["fileIcons"])

    def test_offline_unset_color_keeps_icon(self):
        r = self.run_iconic("--offline", "unset", "b.md", "--color", env=self.unreachable())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(self.data.read_text(encoding="utf-8"))["fileIcons"]["b.md"], {"icon": "y"})

    def test_offline_refuses_icon_for_missing_path_and_writes_nothing(self):
        before = self.data.read_bytes()
        r = self.run_iconic("--offline", "set", "c.md", "nope.md", "--icon", "z", env=self.unreachable())
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("nope.md", r.stderr)
        self.assertEqual(self.data.read_bytes(), before)

    def test_offline_apply_clears_dangling_key(self):
        self.data.write_text(json.dumps({"fileIcons": {"gone.md": {"icon": "x"}}}, indent=2), encoding="utf-8")
        spec = pathlib.Path(self.tmp.name) / "spec.json"
        spec.write_text('{"gone.md": null}', encoding="utf-8")
        r = self.run_iconic("--offline", "apply", str(spec), env=self.unreachable())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(self.data.read_text(encoding="utf-8"))["fileIcons"], {})


FAKE_APP = r'''
import json, os, re, sys
code = next(a for a in sys.argv if a.startswith("code="))[5:]
ops = json.loads(re.search(r"const ops=(.*);\n", code).group(1))
log_path = os.environ["FAKE_LOG"]
calls = open(log_path).read().split() if os.path.exists(log_path) else []
kind = "dry" if "if(false){" in code else "write"
damaged = len(calls) < int(os.environ["FAKE_DAMAGED_CALLS"])
with open(log_path, "a") as log:
    log.write(("damaged-" if damaged else "") + kind + "\n")
if damaged:
    # The app sees U+FFFD in the request, or the reply itself arrives damaged
    print("=> " + ('{"damaged":true}' if len(calls) % 2 == 0 else '{"entries": {"' + chr(0xFFFD) + '": null}}'))
elif kind == "dry":
    print("=> " + json.dumps({"entries": {k: None for k in ops}}))
else:
    print("=> " + os.environ["FAKE_REPLY"])
'''


class Online(FakeVault):
    def fake_app(self, reply, damaged_calls=0):
        script = pathlib.Path(self.tmp.name) / "fake_app.py"
        script.write_text(FAKE_APP, encoding="utf-8")
        self.log = pathlib.Path(self.tmp.name) / "calls.log"
        env = self.fake_cli(f'exec "{sys.executable}" "{script}" "$@"\n')
        return {**env, "FAKE_REPLY": json.dumps({"entries": reply}),
                "FAKE_DAMAGED_CALLS": str(damaged_calls), "FAKE_LOG": str(self.log)}

    def calls(self):
        return self.log.read_text().split() if self.log.exists() else []

    def test_app_error_is_exit_1(self):
        env = self.fake_cli("echo 'Error: Iconic plugin is not loaded'\n")
        r = self.run_iconic("set", "c.md", "--icon", "z", env=env)
        self.assertEqual(r.returncode, 1, r.stderr)

    def test_disk_that_disagrees_with_the_app_is_exit_4(self):
        # The app claims c.md got an icon, but data.json never changed
        r = self.run_iconic("set", "c.md", "--icon", "z", env=self.fake_app({"c.md": {"icon": "z"}}))
        self.assertEqual(r.returncode, 4, r.stderr)

    def test_disk_that_agrees_is_exit_0_after_a_dry_pass(self):
        r = self.run_iconic("set", "b.md", "--icon", "y", env=self.fake_app({"b.md": {"icon": "y", "color": "red"}}))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.calls(), ["dry", "write"])

    def test_damaged_calls_are_sent_again(self):
        env = self.fake_app({"b.md": {"icon": "y", "color": "red"}}, damaged_calls=2)
        r = self.run_iconic("set", "b.md", "--icon", "y", env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.calls(), ["damaged-dry", "damaged-dry", "dry", "write"])

    def test_damage_that_persists_is_exit_1_without_a_write(self):
        env = self.fake_app({"b.md": {"icon": "y"}}, damaged_calls=100)
        r = self.run_iconic("set", "b.md", "--icon", "y", env=env)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertNotIn("write", self.calls())

    def test_spec_with_replacement_char_is_usage_error(self):
        r = self.run_iconic("set", "b" + iconic.DAMAGE + ".md", "--icon", "y", env=self.fake_app({}))
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(self.calls(), [])

    def test_get_only_reads(self):
        r = self.run_iconic("get", "b.md", env=self.fake_app({}))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.calls(), ["dry"])


@unittest.skipUnless(NODE, "node is not installed")
class AppScript(unittest.TestCase):
    """Run the JS sent to Obsidian against a fake app and compare with merge()"""

    def run_js(self, file_icons, ops, existing, saving=False, write=True):
        js = iconic.apply_js(ops, base="/vault", write=write)
        harness = """
const state = %s;
const existing = new Set(%s);
let saves = 0;
const plugin = {
  isSaving: %s,
  settings: {fileIcons: state},
  updateIconSetting(e,t,i,a){i||a?(e[t]||(e[t]={}),i?e[t].icon=i:delete e[t].icon,a?e[t].color=a:delete e[t].color):delete e[t]},
  async saveSettings(){ if(this.isSaving) return; saves++; },
  ruleManager: {triggerRulings(){ return false; }},
  refreshManagers(){},
};
globalThis.sleep = ms => new Promise(r => { setTimeout(() => { plugin.isSaving = false; r(); }, ms); });
globalThis.app = {
  vault: {adapter: {basePath: "/vault"}, getAbstractFileByPath: p => existing.has(p) ? {} : null},
  plugins: {plugins: {iconic: plugin}},
};
(%s).then(out => console.log(JSON.stringify({out: JSON.parse(out), state, saves})));
""" % (json.dumps(file_icons), json.dumps(sorted(existing)), "true" if saving else "false", js)
        r = subprocess.run([NODE, "-e", harness], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    CASES = [
        ({"a.md": {"icon": "x", "color": "red", "unsynced": ["d"]}}, {"a.md": {"icon": "y"}}),
        ({"a.md": {"icon": "x", "color": "red"}}, {"a.md": {"color": None}}),
        ({"a.md": {"icon": "x", "unsynced": ["d"]}}, {"a.md": None}),
        ({}, {"a.md": {"icon": "📐", "color": "yellow"}}),
        ({"a.md": {"icon": "x"}}, {"a.md": {"icon": None}}),
    ]

    def test_js_and_python_agree(self):
        for cur, ops in self.CASES:
            with self.subTest(cur=cur, ops=ops):
                got = self.run_js(json.loads(json.dumps(cur)), ops, {"a.md"})
                want, _ = iconic.merge(cur, ops)
                self.assertEqual(got["state"], want)
                self.assertEqual(got["saves"], 1)
                self.assertEqual(got["out"]["entries"], {k: want.get(k) for k in ops})

    def test_js_refuses_missing_path_and_changes_nothing(self):
        got = self.run_js({"a.md": {"icon": "x"}}, {"a.md": {"icon": "y"}, "nope.md": {"icon": "z"}}, {"a.md"})
        self.assertEqual(got["out"]["missing"], ["nope.md"])
        self.assertEqual(got["state"], {"a.md": {"icon": "x"}})
        self.assertEqual(got["saves"], 0)

    def test_js_dry_pass_reports_and_changes_nothing(self):
        ops = {"a.md": {"icon": "👨‍🎨", "color": None}}
        got = self.run_js({"a.md": {"icon": "x", "color": "red"}}, ops, {"a.md"}, write=False)
        self.assertEqual(got["out"]["entries"], {"a.md": {"icon": "x", "color": "red"}})
        self.assertEqual(got["state"], {"a.md": {"icon": "x", "color": "red"}})
        self.assertEqual(got["saves"], 0)

    def test_js_refuses_a_damaged_request_before_any_change(self):
        got = self.run_js({"a.md": {"icon": "x"}}, {"a.md": {"icon": "y" + iconic.DAMAGE}}, {"a.md"})
        self.assertEqual(got["out"], {"damaged": True})
        self.assertEqual(got["state"], {"a.md": {"icon": "x"}})
        self.assertEqual(got["saves"], 0)

    def test_js_waits_for_a_save_in_flight(self):
        got = self.run_js({}, {"a.md": {"icon": "y"}}, {"a.md"}, saving=True)
        self.assertEqual(got["saves"], 1)

    def test_js_refuses_another_vault(self):
        js = iconic.apply_js({"a.md": None}, base="/other")
        harness = 'globalThis.app={vault:{adapter:{basePath:"/vault"}},plugins:{plugins:{}}};(%s).then(console.log)' % js
        r = subprocess.run([NODE, "-e", harness], capture_output=True, text=True)
        self.assertIn("error", json.loads(r.stdout))


if __name__ == "__main__":
    unittest.main()
