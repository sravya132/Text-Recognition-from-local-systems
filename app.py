# app.py
from flask import Flask, render_template_string, request, redirect, url_for
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import os

app = Flask(__name__)

IMAGE_PATH = "image.jpg"  # keep image in repo or upload to repo

def ocr_from_image(path):
    if not os.path.exists(path):
        return f"Error: File '{path}' not found."

    img = Image.open(path)
    img = img.convert("L")
    img = img.filter(ImageFilter.MedianFilter())
    img = ImageEnhance.Contrast(img).enhance(2.0)

    # If Tesseract is installed system-wide (apt-get), you don't need to set tesseract_cmd.
    text = pytesseract.image_to_string(img)
    return text

INDEX_HTML = """
<!doctype html>
<title>OCR Result</title>
<h1>OCR Result</h1>
<form method="post" enctype="multipart/form-data">
  <label>Upload an image (optional):</label><br>
  <input type="file" name="file"><br><br>
  <button type="submit">Run OCR</button>
</form>
<hr>
<h2>Extracted text:</h2>
<pre style="white-space: pre-wrap; background:#f8f8f8; padding:10px;">{{ text }}</pre>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    text = ""
    if request.method == "POST":
        # If user uploaded a file, use it temporarily
        uploaded = request.files.get("file")
        if uploaded and uploaded.filename:
            tmp_path = "/tmp/uploaded_image"
            uploaded.save(tmp_path)
            text = ocr_from_image(tmp_path)
        else:
            text = ocr_from_image(IMAGE_PATH)
    else:
        # show extracted text from repo image by default
        text = ocr_from_image(IMAGE_PATH)

    return render_template_string(INDEX_HTML, text=text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
