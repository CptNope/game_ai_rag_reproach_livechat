
from PIL import Image
import pytesseract

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"OCR failed: {e}"

if __name__ == "__main__":
    print(extract_text_from_image("game_memory/logs/frame_100.png"))
