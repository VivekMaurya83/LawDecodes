import os
from docx import Document
import google.generativeai as genai
import logging

def extract_text_from_docx(docx_path, output_path):
    """Extracts raw text from a DOCX file."""
    logging.info(f"📄 1. Extracting raw text from {docx_path}...")
    try:
        doc = Document(docx_path)
        with open(output_path, "w", encoding="utf-8") as f:
            for para in doc.paragraphs:
                if para.text.strip():
                    f.write(para.text + "\n")
        logging.info(f"✅ Raw text saved to {output_path}")
        return True
    except Exception as e:
        logging.error(f"❌ Error during text extraction: {e}")
        return False

def format_text_with_gemini(file_path):
    """
    Reads text from a file and formats it using the Gemini API.
    Returns the formatted text (str) on success, or None on failure.
    """
    logging.info(f"🤖 2. Attempting to format text in {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        
        if not raw_text.strip():
            logging.warning("⚠️ File is empty, skipping formatting.")
            return None

        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        prompt = f"""
Reformat the following extracted document text. Your task is to ensure it is clean and well-structured.
Rules:
1. Preserve all original content.
2. Place a blank line before and after every major section header.
3. Ensure paragraphs are separated by a single newline.

--- BEGIN TEXT ---
{raw_text}
--- END TEXT ---
"""
        response = model.generate_content(prompt)
        formatted_text = response.text.strip()
            
        logging.info("✅ Text formatting successful.")
        return formatted_text # <-- CORRECT: Returns the string
        
    except Exception as e:
        logging.warning(f"⚠️ Formatting failed: {e}. Proceeding with raw text.")
        return None # <-- CORRECT: Returns None