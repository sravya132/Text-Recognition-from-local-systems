# app.py
import os
import uuid
from flask import Flask, render_template_string, request, redirect, url_for
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Allowable upload extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff"}
UPLOAD_DIR = "/tmp"
IMAGE_PATH = "image.jpg"  # fallback image in repo root

# Safety: limit size (10 MB)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

def allowed_file(filename: str) -> bool:
    if not filename:
        return False
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def ocr_from_image(path: str) -> str:
    if not os.path.exists(path):
        return f"Error: File '{path}' not found."
    try:
        img = Image.open(path)
        img = img.convert("L")
        img = img.filter(ImageFilter.MedianFilter())
        img = ImageEnhance.Contrast(img).enhance(2.0)

        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"OCR error: {e}"

HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>OCR Result</title>
<style>
  :root{
    --card-bg: rgba(255,255,255,0.95);
    --accent: #6a11cb;
    --accent2: #2575fc;
  }
  body{
    margin:0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    min-height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    color:#111;
  }
  .container{
    width: min(980px, 94%);
    margin: 36px auto;
  }
  .card{
    background: var(--card-bg);
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 10px 30px rgba(2,6,23,0.45);
  }
  header {
    display:flex;
    align-items:center;
    gap:16px;
    margin-bottom:12px;
  }
  h1 {
    margin:0;
    font-size:28px;
    color: #111;
  }
  .controls{
    display:flex;
    gap:12px;
    align-items:center;
    margin-bottom:12px;
  }
  input[type=file] {
    padding:6px;
  }
  button {
    background: linear-gradient(90deg,var(--accent),var(--accent2));
    color:white;
    border:none;
    padding:10px 14px;
    font-weight:600;
    border-radius:10px;
    cursor:pointer;
  }
  button:hover{ opacity:0.95; transform:translateY(-1px); }
  .row {
    display:flex;
    gap:18px;
    align-items:flex-start;
  }
  .left {
    width: 380px;
    max-width: 38%;
  }
  .preview {
    border-radius:8px;
    border:1px solid rgba(0,0,0,0.06);
    padding:6px;
    background:#fff;
    display:inline-block;
    width:100%;
    text-align:center;
  }
  img.preview-img {
    max-width:100%;
    height:auto;
    border-radius:6px;
    display:block;
    margin:0 auto;
  }
  .right {
    flex:1;
  }
  h2 { margin-top:0; }
  pre.ocr {
    background:#f5f7fb;
    padding:14px;
    border-radius:8px;
    white-space: pre-wrap;
    max-height:420px;
    overflow:auto;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.5);
  }
  footer {
    margin-top:12px;
    font-size:13px;
    color:#333;
  }
  .muted { color:#666; font-size:13px; }
  .note { margin-top:12px; color:#444; font-size:13px; }
</style>
</head>
<body>
  <div class="container">
    <div class="card">
      <header>
        <h1>OCR Result</h1>
      </header>

      <form method="post" enctype="multipart/form-data" id="ocrForm">
        <div class="controls">
          <input id="fileInput" type="file" name="file" accept="image/*">
          <button type="submit">Run OCR</button>
          <div class="muted">Or click <strong>Run OCR</strong> with no file to process repo <code>image.jpg</code>.</div>
        </div>
      </form>

      <div class="row" style="margin-top:12px;">
        <div class="left">
          <div class="preview">
            <div id="previewArea">
              <img class="preview-img" id="previewImg" src="{{ default_preview }}" alt="preview">
            </div>
            <div class="note muted">Preview of the image that will be OCR'ed</div>
          </div>
        </div>

        <div class="right">
          <h2>Extracted text:</h2>
          <pre class="ocr">{{ text }}</pre>
          <footer>
            <div class="muted">Tip: Use clear, high contrast images for better OCR.</div>
          </footer>
        </div>
      </div>
    </div>
  </div>

<script>
  const fileInput = document.getElementById("fileInput");
  const previewImg = document.getElementById("previewImg");
  const form = document.getElementById("ocrForm");

  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) {
      // show repo image preview fallback
      previewImg.src = "{{ default_preview }}";
      return;
    }
    const url = URL.createObjectURL(file);
    previewImg.src = url;
  });

  // Optional: show a loading state when submitting
  form.addEventListener("submit", () => {
    // Disabled for simplicity - could add spinner
  });
</script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    text = ""
    preview_src = url_for("static", filename="repo_image_preview.jpg") if os.path.exists("image.jpg") else ""
    # Default preview: if image.jpg exists, serve it via a local static path (we'll copy it temporarily)
    # For simplicity, we'll set a data URL fallback if preview static not available.
    default_preview = "/static/repo_image_preview.jpg"

    # If repo image exists, create /static/repo_image_preview.jpg for the browser to fetch
    try:
        static_dir = os.path.join(app.root_path, "static")
        os.makedirs(static_dir, exist_ok=True)
        if os.path.exists(IMAGE_PATH):
            target = os.path.join(static_dir, "repo_image_preview.jpg")
            # copy only if not same file to reduce writes
            if (not os.path.exists(target)) or (os.path.getmtime(target) < os.path.getmtime(IMAGE_PATH)):
                from shutil import copyfile
                copyfile(IMAGE_PATH, target)
    except Exception:
        # ignore static copy errors, preview will be blank
        pass

    if request.method == "POST":
        uploaded = request.files.get("file")
        if uploaded and uploaded.filename and allowed_file(uploaded.filename):
            filename = secure_filename(uploaded.filename)
            # add a short random prefix to avoid collisions
            unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
            save_path = os.path.join(UPLOAD_DIR, unique_name)
            try:
                uploaded.save(save_path)
                text = ocr_from_image(save_path)
            finally:
                try:
                    if os.path.exists(save_path):
                        os.remove(save_path)
                except Exception:
                    pass
        else:
            # No valid uploaded file — use fallback repo image
            text = ocr_from_image(IMAGE_PATH)
    else:
        # GET: show OCR results for repo image by default
        text = ocr_from_image(IMAGE_PATH)

    # If static preview not available, point to repo image path (browser may not load file://)
    if not os.path.exists(os.path.join(app.root_path, "static", "repo_image_preview.jpg")):
        # Use a tiny placeholder data-URL to avoid broken image icon
        default_preview = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='600' height='400'><rect width='100%' height='100%' fill='%23f4f4f6'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%23999' font-size='20'>No preview available</text></svg>"

    return render_template_string(HTML, text=text, default_preview=default_preview)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
