import re
from typing import Dict, List

class RobustInputValidator:
    """Cleans and validates text before summarization"""
    
    def __init__(self):
        self.noise_patterns = {
            'urls': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone_numbers': r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}',
            'excessive_whitespace': r'\s{3,}',
            'repeated_chars': r'(.)\1{4,}',
            'page_numbers': r'Page\s+\d+|^\d+$',
            'extraction_artifacts': r'--- Extracted Text ---|ACME CORPORATION|\f|\x0c'
        }
    
    def validate_and_clean(self, text: str) -> Dict:
        """Clean text and return quality metrics"""
        if not text or not text.strip():
            return {
                'cleaned_text': '',
                'quality_score': 0.0,
                'is_valid': False
            }
        
        cleaned_text = text
        issues_found = []
        
        # Remove noise patterns
        for pattern_name, pattern in self.noise_patterns.items():
            matches_before = len(re.findall(pattern, cleaned_text, re.IGNORECASE))
            if matches_before > 0:
                cleaned_text = re.sub(pattern, ' ', cleaned_text, flags=re.IGNORECASE)
                issues_found.append(f"{pattern_name}_{matches_before}_removed")
        
        # Normalize whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(cleaned_text, issues_found)
        
        return {
            'cleaned_text': cleaned_text,
            'quality_score': quality_score,
            'is_valid': quality_score > 0.3,
            'issues_found': issues_found
        }
    
    def _calculate_quality_score(self, text: str, issues: List) -> float:
        """Calculate text quality score (0-1)"""
        base_score = 1.0
        
        # Penalize based on issues found
        issue_penalty = min(0.1 * len(issues), 0.6)
        base_score -= issue_penalty
        
        # Bonus for legal keywords
        legal_keywords = ['section', 'clause', 'agreement', 'contract', 'shall']
        legal_matches = sum(1 for keyword in legal_keywords if keyword.lower() in text.lower())
        base_score += min(legal_matches * 0.05, 0.2)
        
        return max(0.0, min(1.0, base_score))
