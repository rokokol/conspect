import re
import unittest

from numkit import embed


class Embed(unittest.TestCase):
    # How a module is stripped is sandbox_kit's, tested in its test_page.py
    def test_the_embedded_texts_are_classic_script(self):
        for text in (embed.numkit_js(), embed.kernel_editor_js()):
            self.assertIsNone(re.search(r"^(import|export)\b", text, re.M))
        self.assertIn("function integrate(", embed.numkit_js())
        self.assertIn("function kernelEditor(", embed.kernel_editor_js())


if __name__ == "__main__":
    unittest.main()
