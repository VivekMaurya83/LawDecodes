import os
import sys

# Add Summary folder to path
summary_path = os.path.join(os.path.dirname(__file__), '..', 'summary')
sys.path.append(summary_path)

from models.t5_summarizer import T5LegalSummarizer
from data.preprocessor import LegalTextPreprocessor
from input_validator import RobustInputValidator
from output_cleaner import SmartOutputCleaner

class RobustTextFileSummarizer:
    """Production-ready robust legal document summarizer"""
    
    def __init__(self):
        # Load your trained T5 model
        model_path = os.path.join(os.path.dirname(__file__), '..', 'Summary', 'outputs', 'models', 'final_model')
        
        print("🔄 Loading T5 Legal Summarizer...")
        self.summarizer = T5LegalSummarizer(model_path)
        self.summarizer.load_trained_model(model_path)
        
        # Initialize robust components
        self.validator = RobustInputValidator()
        self.output_cleaner = SmartOutputCleaner()
        self.preprocessor = LegalTextPreprocessor()
        
        print("✅ Robust Summarization System loaded!")
    
    def summarize_text_file(self, txt_file_path: str, output_file: str = None) -> dict:
        """
        Robust summarization of any text file
        """
        print(f"📄 Processing: {os.path.basename(txt_file_path)}")
        
        try:
            # Step 1: Read file
            with open(txt_file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            
            # Step 2: Validate and clean input
            validation_result = self.validator.validate_and_clean(raw_text)
            
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': 'Input validation failed',
                    'quality_score': validation_result['quality_score']
                }
            
            cleaned_text = validation_result['cleaned_text']
            print(f"✅ Input validated (Quality: {validation_result['quality_score']:.2f})")
            
            # Step 3: Classify and format
            section_type = self.preprocessor.classify_section_type(cleaned_text)
            formatted_input = self.preprocessor.format_training_input(cleaned_text, section_type)
            
            # Step 4: Generate summary with T5
            try:
                raw_summary = self.summarizer.generate_summary(
                    formatted_input, 
                    max_length=min(200, max(50, len(cleaned_text.split()) // 4))
                )
            except Exception as e:
                print(f"⚠️ T5 generation failed: {e}")
                raw_summary = f"Generation error: {cleaned_text[:200]}..."
            
            # Step 5: Clean output
            output_result = self.output_cleaner.clean_summary_output(raw_summary, cleaned_text)
            
            # Step 6: Extract metadata
            key_elements = self.preprocessor.extract_legal_elements(cleaned_text)
            
            # Step 7: Compile results
            final_results = {
                'success': True,
                'file_path': txt_file_path,
                'section_type': section_type,
                'summary': output_result['summary'],
                'confidence': output_result['confidence'],
                'fallback_used': output_result['fallback_used'],
                'key_elements': key_elements,
                'quality_metrics': {
                    'input_quality': validation_result['quality_score'],
                    'output_confidence': output_result['confidence'],
                    'overall_quality': (validation_result['quality_score'] + output_result['confidence']) / 2
                },
                'processing_stats': {
                    'original_words': len(raw_text.split()),
                    'cleaned_words': len(cleaned_text.split()),
                    'summary_words': len(output_result['summary'].split()),
                    'compression_ratio': len(output_result['summary'].split()) / len(cleaned_text.split())
                }
            }
            
            # Step 8: Save results
            if output_file:
                self._save_results(final_results, output_file)
            
            print(f"✅ Processing completed (Confidence: {output_result['confidence']:.2f})")
            return final_results
            
        except Exception as e:
            print(f"❌ Critical error: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': txt_file_path
            }
    
    def _save_results(self, results: dict, output_file: str):
        """Save comprehensive results to file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== ROBUST LEGAL DOCUMENT SUMMARY ===\n\n")
            f.write(f"📄 Source: {results['file_path']}\n")
            f.write(f"🏷️ Document Type: {results['section_type']}\n")
            f.write(f"📊 Overall Quality: {results['quality_metrics']['overall_quality']:.2f}/1.0\n")
            f.write(f"🔧 Fallback Used: {results['fallback_used']}\n\n")
            
            f.write("🤖 AI SUMMARY:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{results['summary']}\n\n")
            
            f.write("🔍 KEY ELEMENTS:\n")
            f.write("-" * 50 + "\n")
            for element_type, elements in results['key_elements'].items():
                if elements:
                    f.write(f"• {element_type.title()}: {', '.join(elements)}\n")
            
            f.write(f"\n📊 PROCESSING STATISTICS:\n")
            f.write("-" * 50 + "\n")
            stats = results['processing_stats']
            f.write(f"Original words: {stats['original_words']}\n")
            f.write(f"Summary words: {stats['summary_words']}\n")
            f.write(f"Compression ratio: {stats['compression_ratio']:.2f}\n")

# Simple function for easy use
def robust_summarize_txt_file(txt_file_path: str, save_summary: bool = True) -> dict:
    """One-line robust summarization"""
    summarizer = RobustTextFileSummarizer()
    
    # Auto-generate output filename
    base_name = os.path.splitext(txt_file_path)[0]
    output_file = f"{base_name}_ROBUST_SUMMARY.txt" if save_summary else None
    
    return summarizer.summarize_text_file(txt_file_path, output_file)

if __name__ == "__main__":
    # Test with your extracted text file
    test_file = "extracted_docx.txt"
    
    if os.path.exists(test_file):
        result = robust_summarize_txt_file(test_file)
        
        if result['success']:
            print(f"\n🎯 ROBUST RESULTS:")
            print(f"📄 File: {result['file_path']}")
            print(f"🏷️ Type: {result['section_type']}")
            print(f"📊 Quality: {result['quality_metrics']['overall_quality']:.2f}")
            print(f"🤖 Summary: {result['summary']}")
        else:
            print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
    else:
        print(f"❌ File '{test_file}' not found. Run your text_docx.py first!")
