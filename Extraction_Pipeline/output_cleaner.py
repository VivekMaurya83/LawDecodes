import re
from typing import Dict

class SmartOutputCleaner:
    """Cleans and validates model outputs"""
    
    def __init__(self):
        self.malformed_indicators = [
            'Summarize this',
            'Text:',
            'while preserving',
            'section while',
            'key information:'
        ]
    
    def clean_summary_output(self, raw_summary: str, original_text: str) -> Dict:
        """Clean and validate summary output"""
        cleaned_summary = raw_summary.strip()
        confidence = 1.0
        fallback_used = False
        
        # Check for malformed output
        if self._is_malformed_output(cleaned_summary, original_text):
            print("⚠️ Detected malformed output, using fallback...")
            cleaned_summary = self._generate_fallback_summary(original_text)
            confidence = 0.6
            fallback_used = True
        
        # Apply post-processing
        cleaned_summary = self._apply_post_processing(cleaned_summary)
        
        return {
            'summary': cleaned_summary,
            'confidence': confidence,
            'fallback_used': fallback_used
        }
    
    def _is_malformed_output(self, summary: str, original_text: str) -> bool:
        """Detect if summary output is malformed"""
        summary_lower = summary.lower()
        
        # Check for prompt artifacts
        for indicator in self.malformed_indicators:
            if indicator.lower() in summary_lower:
                return True
        
        # Check if summary is too long (likely includes original)
        if len(summary.split()) > len(original_text.split()) * 0.8:
            return True
        
        return False
    
    def _generate_fallback_summary(self, text: str) -> str:
        """Generate fallback extractive summary"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if not sentences:
            return "Summary unavailable for this document."
        
        # Take first 2-3 most informative sentences
        selected_sentences = []
        for sentence in sentences[:5]:
            words = sentence.split()
            if len(words) > 5 and any(keyword in sentence.lower() for keyword in 
                ['section', 'clause', '$', '20', 'shall', 'party']):
                selected_sentences.append(sentence)
            if len(selected_sentences) >= 3:
                break
        
        if not selected_sentences:
            selected_sentences = sentences[:2]
        
        return '. '.join(selected_sentences) + '.'
    
    def _apply_post_processing(self, summary: str) -> str:
        """Apply final cleaning to summary"""
        # Remove artifacts
        for artifact in self.malformed_indicators:
            summary = summary.replace(artifact, '')
        
        # Clean formatting
        summary = re.sub(r'\s+', ' ', summary).strip()
        summary = re.sub(r'^\W+', '', summary)
        
        # Ensure proper ending
        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'
        
        return summary

# import re
# from typing import Dict

# class SmartOutputCleaner:
#     """Cleans, validates, and post-processes model-generated summaries"""
    
#     def __init__(self):
#         self.malformed_indicators = [
#             'Summarize this',
#             'Text:',
#             'while preserving',
#             'section while',
#             'key information:'
#         ]
    
#     def clean_summary_output(self, raw_summary: str, original_text: str) -> Dict:
#         """
#         Cleans the raw summary output and applies fallback if needed.
#         Returns a dict with cleaned summary, confidence score, and fallback flag.
#         """
#         cleaned_summary = raw_summary.strip()
#         confidence = 1.0
#         fallback_used = False
        
#         # Detect malformed or incomplete outputs
#         if self._is_malformed_output(cleaned_summary, original_text):
#             print("⚠️ Detected malformed output, using fallback extractive summary...")
#             cleaned_summary = self._generate_fallback_summary(original_text)
#             confidence = 0.6  # Reduced confidence for fallback
#             fallback_used = True
        
#         # Apply final post-processing
#         cleaned_summary = self._apply_post_processing(cleaned_summary)
        
#         return {
#             'summary': cleaned_summary,
#             'confidence': confidence,
#             'fallback_used': fallback_used
#         }
    
#     def _is_malformed_output(self, summary: str, original_text: str) -> bool:
#         """
#         Check whether the summary output is malformed based on:
#         - Presence of prompt-related artifacts
#         - Excessive length suggesting original text repetition
#         """
#         summary_lower = summary.lower()
        
#         for indicator in self.malformed_indicators:
#             if indicator.lower() in summary_lower:
#                 return True
        
#         # If summary length is close to or exceeds 80% of original, treat as malformed
#         if len(summary.split()) > len(original_text.split()) * 0.8:
#             return True
        
#         return False
    
#     def _generate_fallback_summary(self, text: str) -> str:
#         """
#         Generate a simple extractive fallback summary by picking important sentences:
#         - Looks for sentences containing legal keywords (like section, clause, shall)
#         - Returns up to 3 such sentences or first 2 sentences otherwise
#         """
#         sentences = [s.strip() for s in text.split('.') if s.strip()]
        
#         if not sentences:
#             return "Summary unavailable for this document."
        
#         selected_sentences = []
#         for sentence in sentences[:5]:  # Check first 5 sentences for best hits
#             words = sentence.split()
#             if len(words) > 5 and any(keyword in sentence.lower() for keyword in 
#                                      ['section', 'clause', '$', 'shall', 'party']):
#                 selected_sentences.append(sentence)
#             if len(selected_sentences) >= 3:
#                 break
        
#         if not selected_sentences:
#             selected_sentences = sentences[:2]
        
#         return '. '.join(selected_sentences) + '.'
    
#     def _apply_post_processing(self, summary: str) -> str:
#         """
#         Post-process the cleaned summary by:
#         - Removing residual artifacts or prompt fragments
#         - Normalizing whitespace
#         - Ensuring the summary ends with proper punctuation
#         """
#         for artifact in self.malformed_indicators:
#             summary = summary.replace(artifact, '')
        
#         # Normalize whitespace and strip non-word characters at start
#         summary = re.sub(r'\s+', ' ', summary).strip()
#         summary = re.sub(r'^[^\w]+', '', summary)
        
#         # Add period at end if missing for better readability
#         if summary and not summary.endswith(('.', '!', '?')):
#             summary += '.'
        
#         return summary
