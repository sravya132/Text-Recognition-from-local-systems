from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import io

app = Flask(__name__)

@app.route("/")
def home():
    return "OCR Service Running on Render!"

@app.route("/ocr", methods=["POST"])
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    img_file = request.files["file"]
    img = Image.open(io.BytesIO(img_file.read()))
    text = pytesseract.image_to_string(img)

    return jsonify({"text": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
