import re
from typing import List, Optional, Dict
from datetime import datetime
from langchain.schema import Document

class DateHandler:
    
    @staticmethod
    def extract_dates_from_text(text: str) -> List[Dict[str, str]]:
        """Extract all dates from text with context"""
        date_patterns = {
            'effective_date': r'effective\s+date:?\s*([^\n\.]+)',
            'execution_date': r'(?:executed|signed|dated).*?(?:on|this)\s*([^\n\.]+)',
            'standard_dates': r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            'written_dates': r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{2,4})',
            'formal_dates': r'this\s+(\d{1,2}\w*\s+day\s+of\s+\w+,?\s+\d{2,4})'
        }
        
        found_dates = []
        for date_type, pattern in date_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                found_dates.append({
                    'type': date_type,
                    'date': match.group(1).strip(),
                    'context': match.group(0),
                    'position': match.start()
                })
        
        return found_dates
    
    @staticmethod
    def enhance_date_query(query: str) -> List[str]:
        """Generate multiple variations of date queries"""
        date_keywords = ['date', 'effective', 'execution', 'signed', 'when', 'time']
        
        variations = [query]
        
        # Add specific legal date terms
        if any(keyword in query.lower() for keyword in date_keywords):
            variations.extend([
                query + " effective date",
                query + " contract date",
                query + " agreement date",
                "effective date " + query,
                "execution date " + query,
                "when was this " + query.replace('date', '').strip() + " signed"
            ])
        
        return list(set(variations))
