from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import os

# Optional: Set tesseract executable path if not in PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Change if needed

# Filename to use
filename = "image.jpg"

# Check file existence before running OCR
if not os.path.exists(filename):
    print(f"Error: File '{filename}' not found in project directory.")
else:
    # Load and preprocess image
    img = Image.open(filename)
    img = img.convert('L')  # Convert to grayscale for better OCR
    img = img.filter(ImageFilter.MedianFilter())  # Reduce noise
    img = ImageEnhance.Contrast(img).enhance(2)  # Improve text visibility

    # Perform OCR
    text = pytesseract.image_to_string(img)

    print("Extracted Text:")
    print(text)
