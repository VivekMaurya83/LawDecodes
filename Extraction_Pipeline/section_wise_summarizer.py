import re
import os
import sys

import time
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'summary')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Dict, Tuple
from dataclasses import dataclass

from summary.models.t5_summarizer import T5LegalSummarizer
from summary.data.preprocessor import LegalTextPreprocessor
from Extraction_Pipeline.legal_ner import LegalNER

@dataclass
class DocumentSection:
    """Represents a document section"""
    section_id: str
    title: str
    content: str
    section_type: str
    start_pos: int
    end_pos: int

class SectionWiseSummarizer:
    """Advanced section-wise legal document summarizer"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or self._get_model_path()
        
        # Initialize components
        self.summarizer = T5LegalSummarizer(self.model_path)
        self.summarizer.load_trained_model(self.model_path)
        self.preprocessor = LegalTextPreprocessor()
        self.ner = LegalNER()
        
        print("✅ Section-wise Summarizer initialized!")
    
    def _get_model_path(self):
        """Get model path"""
        return os.path.join(os.path.dirname(__file__), '..', 'Summary', 'outputs', 'models', 'final_model')
    
    def split_document_into_sections(self, text: str) -> List[DocumentSection]:
        """
        Splits the document into logical sections. Uses a robust regex for structured 
        documents and falls back to paragraph-based splitting for unstructured letters/memos.
        """
        sections = []
        
        # Primary Regex: Optimized for structured, numbered documents (A/B testing two previous patterns)
        header_pattern = re.compile(
            r'^(?:'
            # Group 1: Explicit 'SECTION X. TITLE' format 
            r'SECTION\s+\d+\.\s+.*'
            r'|'
            # Group 2: Single-level numbering (e.g., 1. Services, 2. Term)
            r'\s*\d+\.\s+[A-Z].*' 
            r'|'
            # Group 3: Specific Named Sections (General safety net)
            r'\b(?:Parties\s+and\s+Purpose|Definition\s+of\s+Confidential\s+Information|Obligations\s+of\s+Receiving\s+Party|Exclusions|Term\s+and\s+Return\s+of\s+Information|Remedies\s+for\s+Breach)\b.*'
            r')', 
            re.IGNORECASE | re.MULTILINE
        )

        headers = list(header_pattern.finditer(text))
        
        # --- ROBUST FALLBACK STRATEGY ---
        if not headers:
            print("⚠️ Falling back to unstructured document paragraph splitting.")
            
            # 1. Strip out headers/footers often found in letters
            document_body = re.sub(r'(^.*(Dear|To|From|Subject|RE):.*|IN WITNESS WHEREOF.*$|Sincerely.*$)', '', text, flags=re.IGNORECASE | re.MULTILINE).strip()
            
            # 2. Split by two or more newlines (major paragraph breaks)
            major_paragraphs = [p.strip() for p in re.split(r'\n\s*\n+', document_body) if p.strip()]

            if not major_paragraphs:
                return [DocumentSection("section_1", "Complete Document (No Paragraphs Found)", text, "general", 0, len(text))]

            # 3. Create generic sections
            for i, content in enumerate(major_paragraphs):
                # Simple heuristic to name the section based on its content or index
                if i == 0:
                    title = "Opening Statement"
                elif "Demand is hereby made" in content:
                    title = "Demand for Action"
                elif "Failure to comply" in content:
                    title = "Consequences and Legal Threat"
                else:
                    title = f"Body Paragraph {i + 1}"
                    
                sections.append(DocumentSection(
                    f"unstructured_{i+1}", 
                    title, 
                    content, 
                    self.preprocessor.classify_section_type(title), 
                    -1, -1 # Position tracking is less meaningful here
                ))
            return sections
        # --- END FALLBACK ---

        # If headers were found (Structured Document Logic)
        
        # Handle the introductory text before the first formal section
        intro_end = headers[0].start()
        intro_content = text[:intro_end].strip()
        if intro_content:
            sections.append(DocumentSection(
                "section_1", "Introduction/Preamble", intro_content, "introduction", 0, intro_end
            ))

        for i, header in enumerate(headers):
            start_pos = header.start()
            end_pos = headers[i+1].start() if i + 1 < len(headers) else len(text)
            
            section_full_text = text[start_pos:end_pos]
            section_title = header.group(0).strip()
            
            # The section content starts after the section_title, replace only the first occurrence
            section_content = section_full_text.replace(section_title, '', 1).strip()
            
            sections.append(DocumentSection(
                f"section_{len(sections) + 1}", 
                section_title,
                section_content,
                self.preprocessor.classify_section_type(section_title),
                start_pos,
                end_pos
            ))

        return sections
    

    def summarize_section(self, section: DocumentSection) -> Dict:
        """Summarize individual section with a self-contained, robust prompt."""
        entities = self.ner.extract_entities(section.content)
        entity_summary = self.ner.create_entity_summary(entities)
        
        # A much better prompt that tells the model HOW to behave
        prompt = f"""
Summarize the key legal points of the following section titled '{section.title}'.
Explain the main obligations, rights, and definitions in simple, clear English.
Use the provided key entities to inform the summary but do not simply list them.

Key Entities: {entity_summary or 'None'}

Text:
{section.content}
"""
        formatted_prompt = prompt.strip()
        
        try:
            # **FINAL TWEAK**: Increased the max_length to give the model more room
            max_length = min(500, max(70, int(len(section.content.split()) * 0.8)))
            summary = self.summarizer.generate_summary(formatted_prompt, max_length=max_length)
            confidence = 0.95
        except Exception as e:
            print(f"⚠️ Error summarizing {section.section_id}: {e}")
            summary = "Could not generate summary due to an error."
            confidence = 0.1
        
        return {
            'section_id': section.section_id,
            'title': section.title,
            'section_type': section.section_type,
            'summary': summary,
            'entities': entities,
            'entity_summary': entity_summary,
            'confidence': confidence,
            'original_length': len(section.content.split()),
            'summary_length': len(summary.split()),
            'compression_ratio': len(summary.split()) / len(section.content.split()) if section.content else 0
        }

    def create_executive_summary(self, section_summaries: List[Dict]) -> str:
        # (This function is now correct)
        if not section_summaries:
            return "No sections available for executive summary."
        
        executive_points = [f"{s['summary']}" for s in section_summaries]
        combined_text = "\n".join(executive_points)
        
        if len(combined_text.split()) > 400:
            try:
                executive_prompt = f"Create a concise, high-level executive summary of a legal document based on the following section summaries:\n\n{combined_text}"
                return self.summarizer.generate_summary(executive_prompt, max_length=250)
            except:
                return "This is a multi-section legal document. Please refer to the detailed section-by-section analysis."
        return combined_text

    def process_document_sections(self, file_path: str) -> Dict:
        # (This function is now correct)
        print(f"🔄 Processing document sections: {os.path.basename(file_path)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().replace("--- Extracted Text ---", "").strip()
        except Exception as e:
            return {'error': f"Failed to read file: {e}"}
        
        if not text:
            return {'error': 'No content found in document'}
        
        sections = self.split_document_into_sections(text)
        print(f"📋 Identified {len(sections)} sections")
        
        section_summaries = []
        for i, section in enumerate(sections, 1):
            print(f"📝 Processing section {i}/{len(sections)}: {section.title}")
            section_summary = self.summarize_section(section)
            section_summaries.append(section_summary)
        
        executive_summary = self.create_executive_summary(section_summaries)
        
        results = {
            'document_path': file_path,
            'document_name': os.path.basename(file_path),
            'total_sections': len(sections),
            'executive_summary': executive_summary,
            'section_summaries': section_summaries,
            'processing_stats': {
                'total_original_words': sum(s['original_length'] for s in section_summaries),
                'total_summary_words': sum(s['summary_length'] for s in section_summaries),
                'average_compression': sum(s['compression_ratio'] for s in section_summaries) / len(section_summaries) if section_summaries else 0,
                'average_confidence': sum(s['confidence'] for s in section_summaries) / len(section_summaries) if section_summaries else 0
            }
        }
        
        print(f"✅ Section-wise processing completed!")
        return results

    def save_detailed_report(self, results: Dict, output_file: str):
        # (This function is now correct)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\nCOMPREHENSIVE LEGAL DOCUMENT ANALYSIS REPORT\n" + "=" * 80 + "\n\n")
            f.write(f"📄 Document: {results['document_name']}\n")
            f.write(f"📊 Total Sections: {results['total_sections']}\n")
            f.write(f"📈 Average Confidence: {results['processing_stats']['average_confidence']:.2f}\n")
            f.write(f"📉 Average Compression: {results['processing_stats']['average_compression']:.2f}\n\n")
            f.write("🎯 EXECUTIVE SUMMARY\n" + "-" * 50 + "\n")
            f.write(f"{results['executive_summary']}\n\n")
            f.write("📋 SECTION-BY-SECTION ANALYSIS\n" + "-" * 50 + "\n")
            
            for i, section in enumerate(results['section_summaries'], 1):
                f.write(f"\n{i}. {section['title'].upper()}\n")
                f.write(f"   Type: {section['section_type']}\n")
                f.write(f"   Confidence: {section['confidence']:.2f}\n")
                f.write(f"   Compression: {section['original_length']} → {section['summary_length']} words\n")
                f.write(f"   Key Entities: {section['entity_summary']}\n")
                f.write(f"   Summary: {section['summary']}\n")
        
        print(f"📄 Detailed report saved to: {output_file}")

# In section_wise_summarizer.py, replace the entire process_and_save_report function with this:

    def process_and_save_report(self, input_path: str, output_path: str):
        """
        MODIFIED: High-level function to run the full analysis and save a CLEAN, FOCUSED report
        containing only the overall summary and section-wise summaries.
        """
        logging.info(f"🔄 3. Starting focused summarization for: {os.path.basename(input_path)}")
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            logging.error(f"❌ Error reading file for summarization: {e}")
            return
        
        sections = self.split_document_into_sections(text)
        logging.info(f"📋 Identified {len(sections)} sections.")
        
        # Generate summaries for each section using a loop for robustness
        section_summaries = []
        for section in sections:
            # Skip summarizing very short, non-substantive sections
            if len(section.content.split()) < 15:
                continue
            
            summary_data = self.summarize_section(section)
            section_summaries.append(summary_data)
            
            # Add a very small delay to be kind to the CPU on long documents
            time.sleep(0.1)

        # Create the high-level executive summary
        executive_summary = self.create_executive_summary(section_summaries)
        
        logging.info(f"📄 Saving focused analysis report to: {output_path}")
        
        # --- THIS IS THE MODIFIED REPORT WRITING LOGIC ---
        with open(output_path, 'w', encoding='utf-8') as f:
            # Part 1: Write the Overall Summary
            f.write("## Overall Summary\n\n")
            f.write(f"{executive_summary}\n\n")
            f.write("---\n\n")
            
            # Part 2: Write the Section-wise Breakdown
            f.write("## Section-by-Section Breakdown\n")
            
            if not section_summaries:
                f.write("\nNo detailed sections were available for summary.\n")
            else:
                for i, section_summary in enumerate(section_summaries, 1):
                    # Write ONLY the title and the summary, excluding all other metadata
                    f.write(f"\n{section_summary['title']}\n\n")
                    f.write(f"{section_summary['summary']}\n")

        logging.info("✅ Focused summarization and report generation complete.")    


def process_legal_document_sections(file_path: str):
    # (This function is now correct)
    summarizer = SectionWiseSummarizer()
    results = summarizer.process_document_sections(file_path)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    print(f"\n🎯 SECTION-WISE ANALYSIS RESULTS:")
    print(f"Document: {results['document_name']}")
    print(f"Sections: {results['total_sections']}")
    print(f"Average Confidence: {results['processing_stats']['average_confidence']:.2f}")
    print(f"\n📊 EXECUTIVE SUMMARY:\n{results['executive_summary']}")
    print(f"\n📋 INDIVIDUAL SECTIONS:")
    
    for section in results['section_summaries']:
        print(f"\n• {section['title']} ({section['section_type']})")
        print(f"  {section['summary']}")
        if section['entity_summary'] != "No key entities identified":
            print(f"  Key Entities: {section['entity_summary']}")
    
    base_name, ext = os.path.splitext(file_path)
    report_file = f"{base_name}_final_ANALYSIS.txt"
    summarizer.save_detailed_report(results, report_file)
    
    return results

if __name__ == "__main__":
    # (This function is now correct)
    test_file = "extracted_text.txt"
    if os.path.exists(test_file):
        process_legal_document_sections(test_file)
    else:
        print(f"❌ File '{test_file}' not found!")
