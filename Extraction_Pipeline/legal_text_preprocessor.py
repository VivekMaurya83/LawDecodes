import re
import json
from typing import Dict, List, Any

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
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
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

    def classify_section_type(self, text: str) -> str:
        text_lower = text.lower()
        if any(word in text_lower for word in ['payment', 'fee', 'cost', 'invoice', 'amount', '$', 'billing']):
            return 'payment'
        elif any(word in text_lower for word in ['termination', 'terminate', 'end', 'expire', 'dissolution']):
            return 'termination'
        elif any(word in text_lower for word in ['liability', 'liable', 'damages', 'responsible', 'limitation']):
            return 'liability'
        elif any(word in text_lower for word in ['confidential', 'non-disclosure', 'secret', 'proprietary']):
            return 'confidentiality'
        elif any(word in text_lower for word in ['conduct', 'behavior', 'ethics', 'standards', 'policy', 'code']):
            return 'conduct'
        elif any(word in text_lower for word in ['conflict', 'interest', 'personal']):
            return 'conflict_of_interest'
        elif any(word in text_lower for word in ['assets', 'property', 'equipment', 'company property']):
            return 'assets'
        else:
            return 'general'

    def format_training_input(self, legal_text: str, section_type: str = None, entities_summary: str = None) -> str:
        if section_type is None:
            section_type = self.classify_section_type(legal_text)

        prompt = f"""
Summarize the following legal {section_type} section in plain, simple English.
Avoid legal jargon and explain key points clearly.

Key Entities: {entities_summary or 'None'}

Text:
{legal_text}
"""
        return prompt.strip()
