import warnings
import os
import io
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import easyocr
from tqdm import tqdm
import logging

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

class UniversalTextExtractor:
    def __init__(self, languages=['en'], gpu=False, verbose=False):
        """
        Initializes the OCR reader. This is done once for efficiency.
        """
        logging.info("Initializing EasyOCR reader (this may take a moment)...")
        self.reader = easyocr.Reader(languages, gpu=gpu, verbose=verbose)
        logging.info("✅ EasyOCR reader initialized.")

    def _ocr_image_object(self, img: Image.Image) -> str:
        """
        This is the core OCR logic. It now uses paragraph mode for better layout detection.
        """
        # Preprocess the image for better OCR accuracy
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_np = np.array(img)
        
        try:
            # --- THE CRITICAL FIX IS HERE ---
            # We enable `paragraph=True` to preserve document structure.
            # `detail=0` makes the output a simple list of text strings, which is efficient.
            results = self.reader.readtext(img_np, paragraph=True, detail=0)
            
            # Join the resulting paragraphs with double newlines for proper spacing.
            return "\n\n".join(results)
            
        except Exception as e:
            error_msg = f"[OCR Error: {e}]"
            logging.error(error_msg)
            return error_msg

    def extract_text_from_image(self, image_path: str) -> str:
        """
        A dedicated function to handle standalone image files (PNG, JPG, etc.).
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        logging.info(f"📄 Processing Image file: {image_path}")
        try:
            img = Image.open(image_path)
            return self._ocr_image_object(img)
        except Exception as e:
            error_msg = f"❌ Error processing image {image_path}: {e}"
            logging.error(error_msg)
            return error_msg

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts text from a PDF, using direct text extraction with an OCR fallback.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        logging.info(f"📄 Processing PDF file: {pdf_path}")
        all_text = []
        try:
            doc = fitz.open(pdf_path)
            with open(os.devnull, 'w') as devnull:
                for page_num in tqdm(range(len(doc)), desc="Processing PDF pages", file=devnull):
                    page = doc[page_num]
                    page_content = ""

                    direct_text = page.get_text().strip()
                    
                    if len(direct_text) > 20: 
                        page_content = direct_text
                    else:
                        pix = page.get_pixmap(dpi=300)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        page_content = self._ocr_image_object(img)

                    all_text.append(f"--- Page {page_num + 1} ---\n{page_content}")
            
            doc.close()
            return "\n\n".join(all_text)
        except Exception as e:
            error_msg = f"❌ Error processing PDF {pdf_path}: {e}"
            logging.error(error_msg)
            return error_msg

    def save_text(self, text: str, output_path: str):
        """Saves the extracted text to a file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logging.info(f"✅ Text saved to: {output_path}")
        except Exception as e:
            logging.error(f"❌ Error saving file: {e}")