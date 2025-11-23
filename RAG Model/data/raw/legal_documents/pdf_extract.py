"""
Access Control Report PDF Text Extraction using Gemini 2.5 Pro
Extracts structured table data and saves to TXT for embeddings
"""

import google.generativeai as genai
import json

def extract_access_control_pdf(pdf_path, output_txt_path, api_key):
    """
    Extract structured data from Access Control Report PDF using Gemini
    """
    print("=" * 70)
    print("Access Control Report - PDF Text Extraction with Gemini 2.5 Pro")
    print("=" * 70)
    
    # Configure Gemini API
    genai.configure(api_key=api_key)
    
    # Step 1: Read PDF file
    print(f"\n[Step 1] Reading PDF: {pdf_path}")
    try:
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        print(f"SUCCESS: PDF loaded ({len(pdf_data)} bytes)")
    except FileNotFoundError:
        print(f"ERROR: File '{pdf_path}' not found!")
        return None
    except Exception as e:
        print(f"ERROR: Error reading PDF: {e}")
        return None
    
    # Step 2: Extract text using Gemini with structured prompt
    print("\n[Step 2] Extracting structured text with Gemini 2.5 Flash...")
    
    prompt = """
    Extract ALL text from this Access Control Report PDF document.
    
    Requirements:
    1. Extract the report header and summary section completely
    2. Extract the entire table with ALL rows including:
       - Log ID
       - Name
       - Unique ID
       - Decision (Granted/Denied)
       - Time
       - Gate
    3. Extract any footer notes or additional text
    4. Preserve the structure and formatting
    5. Include all statistical information (Total Logs, Granted Entries, etc.)
    
    Format the output as clean, readable text that preserves the document structure.
    Make sure to include ALL entries from the table, not just sample rows.
    """
    
    try:
        # Create the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Upload the PDF file
        pdf_file = genai.upload_file(pdf_path, mime_type='application/pdf')
        
        # Generate content
        response = model.generate_content([prompt, pdf_file])
        
        extracted_text = response.text
        print(f"SUCCESS: Text extracted successfully ({len(extracted_text)} characters)")
        
    except Exception as e:
        print(f"ERROR: Error during extraction: {e}")
        return None
    
    # Step 3: Save to TXT file
    print(f"\n[Step 3] Saving to: {output_txt_path}")
    try:
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        print(f"SUCCESS: Text saved successfully")
    except Exception as e:
        print(f"ERROR: Error saving file: {e}")
        return None
    
    # Step 4: Display preview
    print("\n" + "=" * 70)
    print("EXTRACTED TEXT PREVIEW")
    print("=" * 70)
    print(extracted_text[:800])
    if len(extracted_text) > 800:
        print("\n... (truncated)")
    
    print("\n" + "=" * 70)
    print("Extraction completed successfully!")
    print("=" * 70)
    
    return extracted_text


def extract_structured_json(pdf_path, api_key):
    """
    Extract table data as structured JSON for embeddings
    """
    print("\n" + "=" * 70)
    print("BONUS: Extracting as Structured JSON")
    print("=" * 70)
    
    client = genai.Client(api_key=api_key)
    
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    # Define JSON schema for structured extraction
    schema = {
        "type": "object",
        "properties": {
            "report_title": {"type": "string"},
            "date": {"type": "string"},
            "summary": {
                "type": "object",
                "properties": {
                    "total_logs": {"type": "integer"},
                    "granted_entries": {"type": "integer"},
                    "denied_entries": {"type": "integer"},
                    "most_frequent_user": {"type": "string"}
                }
            },
            "access_logs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "log_id": {"type": "integer"},
                        "name": {"type": "string"},
                        "unique_id": {"type": "string"},
                        "decision": {"type": "string"},
                        "time": {"type": "string"},
                        "gate": {"type": "string"}
                    }
                }
            }
        }
    }
    
    prompt = """
    Extract all information from this Access Control Report and structure it according to the provided schema.
    Include ALL entries from the access logs table - do not omit any rows.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Part.from_bytes(data=pdf_data, mime_type='application/pdf'),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
        )
        
        structured_data = json.loads(response.text)
        
        # Save structured JSON
        with open("access_control_structured.json", 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2)
        
        print(f"SUCCESS: Structured JSON saved to: access_control_structured.json")
        print(f"SUCCESS: Total entries extracted: {len(structured_data.get('access_logs', []))}")
        print(f"\nPreview:")
        print(json.dumps(structured_data, indent=2)[:500])
        
        return structured_data
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def main():
    # Configuration
    API_KEY = "AIzaSyDgjGcsug9qVHXj9FmZmcxCQUybLtnuuWQ"  # Replace with your Gemini API key
    PDF_FILE = "Access_Control_Report.pdf"
    OUTPUT_TXT = "extracted_access_control.txt"
    
    # Method 1: Extract as formatted text (for embeddings)
    extracted_text = extract_access_control_pdf(PDF_FILE, OUTPUT_TXT, API_KEY)
    
    # Method 2: Extract as structured JSON (optional - for structured processing)
    if extracted_text:
        print("\n" + "=" * 70)
        choice = input("Extract as structured JSON too? (y/n): ").lower()
        if choice == 'y':
            structured_data = extract_structured_json(PDF_FILE, API_KEY)
    
    print("\nSUCCESS: All operations completed!")
    print(f"Text file ready for embeddings: {OUTPUT_TXT}")


if __name__ == "__main__":
    main()
