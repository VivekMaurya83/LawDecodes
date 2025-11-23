import re
import json
from typing import Dict, List, Any
from summary.config.model_config import config


class LegalTextPreprocessor:
    def __init__(self):
        self.section_keywords = {
            'payment': ['payment', 'fee', 'cost', 'invoice', 'amount', '$', 'billing'],
            'termination': ['termination', 'terminate', 'end', 'expire', 'dissolution'],
            'liability': ['liability', 'liable', 'damages', 'responsible', 'limitation'],
            'confidentiality': ['confidential', 'non-disclosure', 'secret', 'proprietary'],
            'general': []
        }
    
    def extract_legal_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract key legal elements from text"""
        # Date patterns
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return {
            'dates': list(set(dates)),
            'sections': list(set(re.findall(r'Section\s+\d+(?:\.\d+)*', text, re.IGNORECASE))),
            'clauses': list(set(re.findall(r'Clause\s+\d+(?:\.\d+)*', text, re.IGNORECASE))),
            'amounts': list(set(re.findall(r'\$[\d,]+(?:\.\d{2})?', text))),
            'references': list(set(re.findall(r'(?:Exhibit|Schedule|Appendix)\s+[A-Z]\b', text, re.IGNORECASE)))
        }
    
#     def classify_section_type(self, text: str) -> str:
#         """Classify section type based on content"""
#         text_lower = text.lower()
        
#         for section_type, keywords in self.section_keywords.items():
#             if section_type == 'general':
#                 continue
#             if any(keyword in text_lower for keyword in keywords):
#                 return section_type
        
#         return 'general'

    def classify_section_type(self, text: str) -> str:
        """Enhanced classification with more categories"""
        text_lower = text.lower()
            
            # Enhanced patterns
        if any(word in text_lower for word in ['payment', 'fee', 'cost', 'invoice', 'amount', '$', 'billing']):
            return 'payment'
        elif any(word in text_lower for word in ['termination', 'terminate', 'end', 'expire', 'dissolution']):
            return 'termination'
        elif any(word in text_lower for word in ['liability', 'liable', 'damages', 'responsible', 'limitation']):
            return 'liability'
        elif any(word in text_lower for word in ['confidential', 'non-disclosure', 'secret', 'proprietary']):
            return 'confidentiality'
        elif any(word in text_lower for word in ['conduct', 'behavior', 'ethics', 'standards', 'policy', 'code']):
            return 'conduct'  # New category for your document
        elif any(word in text_lower for word in ['conflict', 'interest', 'personal']):
            return 'conflict_of_interest'
        elif any(word in text_lower for word in ['assets', 'property', 'equipment', 'company property']):
            return 'assets'
        else:
            return 'general'
    
    def format_training_input(self, legal_text: str, section_type: str = None) -> str:
        """Format input text for T5 training"""
        if section_type is None:
            section_type = self.classify_section_type(legal_text)
        
        elements = self.extract_legal_elements(legal_text)
        
        # Create structured prompt
        prompt = f"Summarize this legal {section_type} section in simple, easy to understand English while preserving key information:\n"
        
        # Add element preservation instructions
        preserve_items = []
        if elements['dates']:
            preserve_items.append(f"dates ({', '.join(elements['dates'])})")
        if elements['amounts']:
            preserve_items.append(f"amounts ({', '.join(elements['amounts'])})")
        if elements['sections']:
            preserve_items.append(f"sections ({', '.join(elements['sections'])})")
        if elements['clauses']:
            preserve_items.append(f"clauses ({', '.join(elements['clauses'])})")
        if elements['references']:
            preserve_items.append(f"references ({', '.join(elements['references'])})")
        
        if preserve_items:
            prompt += f"PRESERVE: {', '.join(preserve_items)}\n"
        
        prompt += f"\nText: {legal_text}"
        return prompt
    
    def load_training_data(self, json_file: str) -> List[Dict[str, Any]]:
        """Load and preprocess training data from JSON"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        processed_examples = []
        for example in data['training_examples']:
            formatted_input = self.format_training_input(
                example['legal_text'], 
                example['section_type']
            )
            
            processed_examples.append({
                'input_text': formatted_input,
                'target_text': example['summary'],
                'section_type': example['section_type'],
                'original_text': example['legal_text'],
                'key_elements': example.get('key_elements', {})
            })
        
        return processed_examples

# Usage example
if __name__ == "__main__":
    preprocessor = LegalTextPreprocessor()
    
    # Test with sample data
    sample_json = "../data/sample_training_data.json"
    examples = preprocessor.load_training_data(sample_json)
    
    print(f"Loaded {len(examples)} training examples")
    print("\nSample processed example:")
    print(f"Input: {examples[0]['input_text'][:200]}...")
    print(f"Target: {examples[0]['target_text']}")


