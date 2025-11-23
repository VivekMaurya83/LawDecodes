"""
Advanced legal element parsing utilities
"""

import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class LegalElement:
    """Represents a legal element found in text"""
    element_type: str
    value: str
    position: Tuple[int, int]  # start, end positions
    confidence: float = 1.0

class LegalElementParser:
    """Advanced parser for extracting legal elements"""
    
    def __init__(self):
        self.patterns = {
            'date': [
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
            ],
            'amount': [
                r'\$[\d,]+(?:\.\d{2})?',
                r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD|usd)\b'
            ],
            'section': [
                r'Section\s+\d+(?:\.\d+)*',
                r'§\s*\d+(?:\.\d+)*'
            ],
            'clause': [
                r'Clause\s+\d+(?:\.\d+)*',
                r'Article\s+\d+(?:\.\d+)*'
            ],
            'reference': [
                r'(?:Exhibit|Schedule|Appendix|Attachment)\s+[A-Z]\b',
                r'(?:Schedule|Exhibit)\s+\d+\b'
            ],
            'party': [
                r'\b(?:Client|Contractor|Company|Party|Licensor|Licensee|Vendor|Supplier)\b'
            ]
        }
    
    def extract_all_elements(self, text: str) -> Dict[str, List[LegalElement]]:
        """Extract all legal elements with positions and confidence"""
        elements = {}
        
        for element_type, patterns in self.patterns.items():
            elements[element_type] = []
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    element = LegalElement(
                        element_type=element_type,
                        value=match.group(),
                        position=(match.start(), match.end()),
                        confidence=self._calculate_confidence(element_type, match.group())
                    )
                    elements[element_type].append(element)
        
        return elements
    
    def _calculate_confidence(self, element_type: str, value: str) -> float:
        """Calculate confidence score for extracted element"""
        # Simple confidence scoring - can be enhanced
        if element_type == 'date':
            return 0.9 if re.match(r'\d{4}-\d{2}-\d{2}', value) else 0.7
        elif element_type == 'amount':
            return 0.95 if '$' in value else 0.8
        else:
            return 0.8
    
    def get_context_around_element(self, text: str, element: LegalElement, context_words: int = 10) -> str:
        """Get context around a legal element"""
        words = text.split()
        element_text = element.value
        
        # Find element position in words
        for i, word in enumerate(words):
            if element_text in word:
                start_idx = max(0, i - context_words)
                end_idx = min(len(words), i + context_words + 1)
                return ' '.join(words[start_idx:end_idx])
        
        return element_text
