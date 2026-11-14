// Compression des photos dans le navigateur avant l'envoi : une photo de
// téléphone (3–10 Mo) est réduite à ~1600 px de côté en JPEG (quelques
// centaines de Ko), ce qui rend l'envoi possible avec un réseau faible.
// En cas d'échec (format non lu par le navigateur…), la photo d'origine est envoyée.
(function () {
  const MAX_SIDE = 1600;
  const QUALITY = 0.8;

  const input = document.querySelector('input[type=file][name=photos]');
  if (!input || !window.DataTransfer || !window.createImageBitmap) return;
  const form = input.form;
  const status = document.createElement("small");
  status.className = "muted photo-status";
  input.after(status);

  const fmt = (n) => n < 1e6 ? Math.round(n / 1e3) + " Ko" : (n / 1e6).toFixed(1).replace(".", ",") + " Mo";

  async function compress(file) {
    if (!file.type.startsWith("image/") || file.type === "image/gif") return file;
    try {
      const bmp = await createImageBitmap(file, { imageOrientation: "from-image" });
      const scale = Math.min(1, MAX_SIDE / Math.max(bmp.width, bmp.height));
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(bmp.width * scale);
      canvas.height = Math.round(bmp.height * scale);
      canvas.getContext("2d").drawImage(bmp, 0, 0, canvas.width, canvas.height);
      bmp.close?.();
      const blob = await new Promise((ok) => canvas.toBlob(ok, "image/jpeg", QUALITY));
      if (!blob || blob.size >= file.size) return file;
      const name = file.name.replace(/\.[^.]*$/, "") + ".jpg";
      return new File([blob], name, { type: "image/jpeg", lastModified: file.lastModified });
    } catch (e) {
      return file;
    }
  }

  let pending = null;
  input.addEventListener("change", () => {
    const originals = Array.from(input.files);
    if (!originals.length || originals.every((f) => f.compressed)) return;
    status.textContent = "Compression des photos…";
    pending = Promise.all(originals.map(compress)).then((files) => {
      const dt = new DataTransfer();
      files.forEach((f) => { f.compressed = true; dt.items.add(f); });
      input.files = dt.files;
      const before = originals.reduce((s, f) => s + f.size, 0);
      const after = files.reduce((s, f) => s + f.size, 0);
      status.textContent = after < before
        ? `Photos compressées : ${fmt(before)} → ${fmt(after)}`
        : "";
      pending = null;
    });
  });

  // Si l'utilisateur valide pendant la compression, on attend qu'elle se termine
  form.addEventListener("submit", (ev) => {
    if (!pending) return;
    ev.preventDefault();
    const btn = form.querySelector("button[type=submit]");
    if (btn) btn.disabled = true;
    pending.then(() => { if (btn) btn.disabled = false; form.requestSubmit(btn); });
  });
})();
