// css(name): a page role such as "--surface", or any CSS colour expression, as "#rrggbb" in the
// scheme the page is in now. The vendored report writes its roles as light-dark() and color-mix(),
// so the raw value of a custom property is not a colour that a canvas script can take apart. The
// browser resolves it on a probe element, in whatever form its engine serialises: rgb(),
// color(srgb …), oklab() or oklch(). So the colour is not parsed but painted on a one-pixel canvas
// and read back as sRGB. The role is resolved again on every call, because a page turns dark not
// only by the media query: data-theme on <html> or a host's color-scheme does it too. Only the
// painting is kept, per resolved colour: a heat map asks for the same role once per cell.
const css = (() => {
  const cache = new Map();
  let probe;
  const pixel = document.createElement("canvas").getContext("2d", { willReadFrequently: true });
  pixel.canvas.width = pixel.canvas.height = 1;
  const toHex = (resolved) => {
    pixel.clearRect(0, 0, 1, 1);
    pixel.fillStyle = resolved;
    pixel.fillRect(0, 0, 1, 1);
    const [r, g, b] = pixel.getImageData(0, 0, 1, 1).data;
    return "#" + [r, g, b].map((v) => v.toString(16).padStart(2, "0")).join("");
  };
  return (name) => {
    if (!probe) {
      probe = document.body.appendChild(document.createElement("span"));
      probe.hidden = true;
    }
    probe.style.color = name.startsWith("--") ? `var(${name})` : name;
    const resolved = getComputedStyle(probe).color;
    if (!cache.has(resolved)) cache.set(resolved, toHex(resolved));
    return cache.get(resolved);
  };
})();
