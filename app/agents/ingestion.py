import re
from pypdf import PdfReader
from PIL import Image
import pytesseract

class IngestionAgent:
    def __init__(self):
        self.name = "IngestionAgent"

    def process(self, file_path: str) -> str:
        """Extracts and cleans text from PDF or Image."""
        ext = file_path.split(".")[-1].lower()
        
        if ext == "pdf":
            text = self._extract_pdf(file_path)
        elif ext in ["png", "jpg", "jpeg"]:
            text = self._extract_image(file_path)
        else:
            raise ValueError("Unsupported file type")
        
        return self._clean_text(text)

    def _extract_pdf(self, path: str) -> str:
        reader = PdfReader(path)
        return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

    def _extract_image(self, path: str) -> str:
        # Note: Requires Tesseract-OCR installed on your system
        return pytesseract.image_to_string(Image.open(path))

    def _clean_text(self, text: str) -> str:
        # Remove extra whitespace and strange characters
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
