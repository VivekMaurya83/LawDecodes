"""
Evaluation utilities for summarization quality assessment
"""

import re
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class SummaryMetrics:
    """Container for summary evaluation metrics"""
    rouge1: float
    rouge2: float
    rougeL: float
    legal_element_preservation: float
    length_ratio: float
    readability_score: float

class SummarizationEvaluator:
    """Comprehensive evaluation for legal summarization"""
    
    def __init__(self):
        self.legal_keywords = [
            'section', 'clause', 'agreement', 'contract', 'party',
            'liability', 'termination', 'payment', 'confidential'
        ]
    
    def evaluate_summary(self, original_text: str, summary: str, reference_summary: str = None) -> SummaryMetrics:
        """Comprehensive evaluation of summary quality"""
        
        # Legal element preservation
        legal_preservation = self._calculate_legal_element_preservation(original_text, summary)
        
        # Length ratio
        length_ratio = len(summary.split()) / len(original_text.split())
        
        # Readability (simplified)
        readability = self._calculate_readability_score(summary)
        
        # If reference summary is provided, calculate ROUGE scores
        rouge_scores = {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}
        if reference_summary:
            rouge_scores = self._calculate_rouge_scores(summary, reference_summary)
        
        return SummaryMetrics(
            rouge1=rouge_scores['rouge1'],
            rouge2=rouge_scores['rouge2'],
            rougeL=rouge_scores['rougeL'],
            legal_element_preservation=legal_preservation,
            length_ratio=length_ratio,
            readability_score=readability
        )
    
    def _calculate_legal_element_preservation(self, original: str, summary: str) -> float:
        """Calculate how well legal elements are preserved"""
        # Extract key legal elements from both texts
        original_elements = self._extract_key_elements(original)
        summary_elements = self._extract_key_elements(summary)
        
        if not original_elements:
            return 1.0
        
        preserved_count = 0
        for element in original_elements:
            if any(element.lower() in se.lower() for se in summary_elements):
                preserved_count += 1
        
        return preserved_count / len(original_elements)
    
    def _extract_key_elements(self, text: str) -> List[str]:
        """Extract key legal elements from text"""
        elements = []
        
        # Dates
        elements.extend(re.findall(r'\b\d{4}-\d{2}-\d{2}\b', text))
        
        # Amounts
        elements.extend(re.findall(r'\$[\d,]+(?:\.\d{2})?', text))
        
        # Sections and clauses
        elements.extend(re.findall(r'(?:Section|Clause)\s+\d+(?:\.\d+)*', text, re.IGNORECASE))
        
        # References
        elements.extend(re.findall(r'(?:Exhibit|Schedule|Appendix)\s+[A-Z]\b', text, re.IGNORECASE))
        
        return list(set(elements))
    
    def _calculate_readability_score(self, text: str) -> float:
        """Simple readability score based on sentence and word length"""
        sentences = text.split('.')
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simplified readability score (lower is better for legal text)
        readability = 100 - (avg_sentence_length * 1.5 + avg_word_length * 2)
        return max(0, min(100, readability)) / 100
    
    def _calculate_rouge_scores(self, summary: str, reference: str) -> Dict[str, float]:
        """Simple ROUGE score calculation (simplified version)"""
        # This is a simplified implementation
        # In production, use the rouge-score library
        
        summary_words = set(summary.lower().split())
        reference_words = set(reference.lower().split())
        
        if not reference_words:
            return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}
        
        intersection = summary_words.intersection(reference_words)
        rouge1 = len(intersection) / len(reference_words)
        
        return {
            'rouge1': rouge1,
            'rouge2': rouge1 * 0.8,  # Simplified
            'rougeL': rouge1 * 0.9   # Simplified
        }
    
    def batch_evaluate(self, evaluations: List[Dict[str, str]]) -> Dict[str, float]:
        """Evaluate multiple summaries and return average metrics"""
        all_metrics = []
        
        for eval_data in evaluations:
            metrics = self.evaluate_summary(
                eval_data['original'],
                eval_data['summary'],
                eval_data.get('reference')
            )
            all_metrics.append(metrics)
        
        # Calculate averages
        avg_metrics = {
            'avg_rouge1': np.mean([m.rouge1 for m in all_metrics]),
            'avg_rouge2': np.mean([m.rouge2 for m in all_metrics]),
            'avg_rougeL': np.mean([m.rougeL for m in all_metrics]),
            'avg_legal_preservation': np.mean([m.legal_element_preservation for m in all_metrics]),
            'avg_length_ratio': np.mean([m.length_ratio for m in all_metrics]),
            'avg_readability': np.mean([m.readability_score for m in all_metrics])
        }
        
        return avg_metrics
