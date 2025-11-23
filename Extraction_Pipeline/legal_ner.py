import spacy
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class LegalEntity:
    """Represents a legal entity with context"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0

class LegalNER:
    """Enhanced NER for legal documents"""
    
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Custom legal patterns
        self.legal_patterns = {
            'STATUTE': [
                r'Section\s+\d+(?:\.\d+)*',
                r'Clause\s+\d+(?:\.\d+)*',
                r'Article\s+\d+(?:\.\d+)*',
                r'§\s*\d+(?:\.\d+)*'
            ],
            'LEGAL_DATE': [
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
            ],
            'MONEY': [
                r'\$[\d,]+(?:\.\d{2})?',
                r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD)\b'
            ],
            'LEGAL_REFERENCE': [
                r'(?:Exhibit|Schedule|Appendix|Attachment)\s+[A-Z]\b',
                r'(?:Schedule|Exhibit)\s+\d+\b'
            ],
            'CONTRACT_PARTY': [
                r'(?:Client|Contractor|Company|Licensor|Licensee|Vendor|Supplier|Provider)\b',
                r'(?:"[^"]+"|\'[^\']+\')(?:\s+(?:Inc\.|LLC|Corp\.|Corporation|Ltd\.))?'
            ]

        }
    
    def extract_entities(self, text: str) -> Dict[str, List[LegalEntity]]:
        """Extract both spaCy and custom legal entities"""
        doc = self.nlp(text)
        entities = {
            'PERSON': [],
            'ORG': [],
            'DATE': [],
            'MONEY': [],
            'STATUTE': [],
            'LEGAL_DATE': [],
            'LEGAL_REFERENCE': [],
            'CONTRACT_PARTY': [],
            'GPE': [],  # Geopolitical entities
            'LAW': []
        }
        
        # Extract spaCy entities
        for ent in doc.ents:
            if ent.label_ in entities:
                legal_entity = LegalEntity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.9
                )
                entities[ent.label_].append(legal_entity)
        
        # Extract custom legal entities
        for label, patterns in self.legal_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    legal_entity = LegalEntity(
                        text=match.group(),
                        label=label,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.95
                    )
                    if label not in entities:
                        entities[label] = []
                    entities[label].append(legal_entity)
        
        return entities
    
    def create_entity_summary(self, entities: Dict[str, List[LegalEntity]]) -> str:
        """Create a structured summary of extracted entities"""
        summary_parts = []
        
        for label, entity_list in entities.items():
            if entity_list:
                unique_entities = list(set([e.text for e in entity_list]))
                summary_parts.append(f"{label}: {', '.join(unique_entities)}")
        
        return " | ".join(summary_parts) if summary_parts else "No key entities identified"
    
    def enhance_text_with_entities(self, text: str) -> Tuple[str, str]:
        """Add entity information to text for better summarization"""
        entities = self.extract_entities(text)
        entity_summary = self.create_entity_summary(entities)
        
        enhanced_text = f"Key Legal Entities: {entity_summary}\n\nDocument Text: {text}"
        
        return enhanced_text, entity_summary

# import spacy
# import re
# import json
# from typing import Dict, List
# from dataclasses import dataclass

# @dataclass
# class LegalEntity:
#     text: str
#     label: str
#     start: int
#     end: int
#     confidence: float = 1.0

# class LegalNER:
#     def __init__(self):
#         self.nlp = spacy.load("en_core_web_sm")

#         self.legal_patterns = {
#             'STATUTE': [
#                 r'Section\s+\d+(?:\.\d+)*',
#                 r'Clause\s+\d+(?:\.\d+)*',
#                 r'Article\s+\d+(?:\.\d+)*',
#                 r'§\s*\d+(?:\.\d+)*'
#             ],
#             'LEGAL_DATE': [
#                 r'\b\d{4}-\d{2}-\d{2}\b',
#                 r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
#                 r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
#             ],
#             'MONEY': [
#                 r'\$[\d,]+(?:\.\d{2})?',
#                 r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD)\b'
#             ],
#             'LEGAL_REFERENCE': [
#                 r'(?:Exhibit|Schedule|Appendix|Attachment)\s+[A-Z]\b',
#                 r'(?:Schedule|Exhibit)\s+\d+\b'
#             ],
#             'CONTRACT_PARTY': [
#                 r'(?:Client|Contractor|Company|Licensor|Licensee|Vendor|Supplier|Provider)\b',
#                 r'(?:"[^"]+"|\'[^\']+\')(?:\s+(?:Inc\.|LLC|Corp\.|Corporation|Ltd\.))?'
#             ]
#         }

#     def extract_entities(self, text: str) -> Dict[str, List[LegalEntity]]:
#         doc = self.nlp(text)
#         entities: Dict[str, List[LegalEntity]] = {
#             'PERSON': [],
#             'ORG': [],
#             'DATE': [],
#             'MONEY': [],
#             'STATUTE': [],
#             'LEGAL_DATE': [],
#             'LEGAL_REFERENCE': [],
#             'CONTRACT_PARTY': [],
#             'GPE': [],
#             'LAW': []
#         }

#         # Extract spaCy entities
#         for ent in doc.ents:
#             if ent.label_ in entities:
#                 entities[ent.label_].append(LegalEntity(ent.text, ent.label_, ent.start_char, ent.end_char, 0.9))

#         # Extract custom legal entities using regex
#         for label, patterns in self.legal_patterns.items():
#             for pattern in patterns:
#                 for match in re.finditer(pattern, text, re.IGNORECASE):
#                     entities.setdefault(label, []).append(
#                         LegalEntity(match.group(), label, match.start(), match.end(), 0.95)
#                     )

#         return entities

#     def create_entity_summary(self, entities: Dict[str, List[LegalEntity]]) -> str:
#         parts = []
#         for label, entity_list in entities.items():
#             if entity_list:
#                 unique_texts = list(set(e.text for e in entity_list))
#                 parts.append(f"{label}: {', '.join(unique_texts)}")
#         return " | ".join(parts) if parts else "None"
