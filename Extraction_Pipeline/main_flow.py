import os
import google.generativeai as genai
import time
import logging
from run_extraction import extract_text_from_docx, format_text_with_gemini
from text_photo import UniversalTextExtractor 
from section_wise_summarizer import SectionWiseSummarizer

# (Logging and API Key configuration remains the same)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
API_KEY = os.environ.get("GOOGLE_API_KEY")

try:
    TEXT_EXTRACTOR = UniversalTextExtractor(languages=['en'], gpu=False)
except Exception as e:
    logging.critical(f"Could not initialize UniversalTextExtractor: {e}")
    TEXT_EXTRACTOR = None

# --- NEW FUNCTION 1: FAST, SYNCHRONOUS TEXT EXTRACTION ---
def initial_text_extraction(input_file_path: str, extracted_file_path: str) -> bool:
    """
    Performs only the initial text extraction from the source file (DOCX, PDF, Image)
    and saves the _extracted.txt file. This function is designed to be fast.
    """
    if not API_KEY:
        genai.configure(api_key=API_KEY)

    if not os.path.exists(input_file_path):
        logging.error(f"❌ Input file '{input_file_path}' not found for extraction.")
        return False

    file_extension = os.path.splitext(input_file_path)[1].lower()
    logging.info(f"Detected file type for extraction: {file_extension}")
    
    try:
        if file_extension == '.docx':
            logging.info("Routing to DOCX extractor...")
            extract_text_from_docx(input_file_path, extracted_file_path)

        elif file_extension == '.txt':
            logging.info("Routing to TXT normalizer (line-by-line processing)...")
            try:
                # --- THIS IS THE FINAL, ROBUST FIX ---
                with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as infile, \
                     open(extracted_file_path, 'w', encoding='utf-8') as outfile:
                    
                    # Process the file line by line to clean it thoroughly.
                    # This mimics the successful DOCX extraction process.
                    lines_written = 0
                    for line in infile:
                        # 1. Strip leading/trailing whitespace from each line.
                        # This removes invisible characters and extra spaces.
                        cleaned_line = line.strip()
                        
                        # 2. Only write lines that contain actual content.
                        if cleaned_line:
                            outfile.write(cleaned_line + '\n')
                            lines_written += 1
                
                if lines_written == 0:
                    logging.warning(f"Input file '{input_file_path}' was empty or contained only whitespace.")
                # The size check in main.py will handle the case of an empty output file.
                # --- END OF FIX ---
                
            except Exception as e:
                logging.error(f"❌ Failed to normalize .txt file: {e}")
                return False
                
            except Exception as e:
                logging.error(f"❌ Failed to standardize and clean .txt file: {e}")
                return False

        elif file_extension == '.pdf':
            logging.info("Routing to PDF extractor...")
            if TEXT_EXTRACTOR:
                text_content = TEXT_EXTRACTOR.extract_text_from_pdf(input_file_path)
                TEXT_EXTRACTOR.save_text(text_content, extracted_file_path)
            else:
                logging.error("❌ Text extractor not available for PDF.")
                return False
        elif file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            logging.info("Routing to Image (OCR) extractor...")
            if TEXT_EXTRACTOR:
                text_content = TEXT_EXTRACTOR.extract_text_from_image(input_file_path)
                TEXT_EXTRACTOR.save_text(text_content, extracted_file_path)
            else:
                logging.error("❌ Text extractor not available for Image.")
                return False
        else:
            logging.error(f"❌ Unsupported file type: '{file_extension}'.")
            return False
        
        logging.info("✅ Initial text extraction complete.")
        return True
    except Exception as e:
        logging.error(f"❌ An error occurred during initial text extraction: {e}", exc_info=True)
        return False

# --- NEW FUNCTION 2: BACKGROUND-SAFE SUMMARIZATION ---
def run_summarization_task(extracted_file_path: str, output_report_path: str):
    """
    Performs the AI-based formatting and summarization steps.
    This is designed to be run as a background task.
    """
    logging.info("🚀 Starting Summarization Task...")
    if not API_KEY:
        genai.configure(api_key=API_KEY)

    # Step 1: Format the text (optional)
    formatted_content = format_text_with_gemini(extracted_file_path)
    if formatted_content:
        with open(extracted_file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        logging.info("✅ Intermediate text file updated with formatted content.")
    else:
        logging.warning("Proceeding with unformatted text for summary.")

    # Step 2: Run the final summarizer
    try:
        logging.info("🧠 Starting final summarization step...")
        summarizer = SectionWiseSummarizer()
        summarizer.process_and_save_report(extracted_file_path, output_report_path)
        logging.info(f"🎉 Summarization Task complete! Report saved to {output_report_path}")
    except Exception as e:
        logging.error(f"❌ Summarization task failed critically: {e}", exc_info=True)