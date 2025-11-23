#!/usr/bin/env python3
"""
Inference script for testing trained T5 Legal Summarization Engine
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.t5_summarizer import T5LegalSummarizer
from data.preprocessor import LegalTextPreprocessor
from config.model_config import config

def test_inference():
    print("="*60)
    print("T5 Legal Summarization Engine - Inference Test")
    print("="*60)
    
    # Load trained model
    model_path = os.path.join(config.output_dir, "final_model")
    
    if not os.path.exists(model_path):
        print(f"❌ Trained model not found at {model_path}")
        print("Please run train.py first!")
        return
    
    summarizer = T5LegalSummarizer(model_path)
    summarizer.load_trained_model(model_path)
    
    # Initialize preprocessor
    preprocessor = LegalTextPreprocessor()
    
    # Test samples
    test_samples = [
        {
            "text": "Section 5.3 Intellectual Property Rights. All intellectual property rights in the deliverables created under this agreement shall remain with Company ABC. The Contractor grants Company ABC a perpetual, irrevocable license to use all work products. This provision survives termination as per Clause 12.1 and becomes effective on 2025-09-01.",
            "section_type": "general"
        },
        {
            "text": "Clause 4.7 Monthly Payment Schedule. The client shall pay $25,000 monthly by the 5th of each month starting 2025-09-05. Late payments after 15 days incur 1.5% monthly interest. Final payment of $30,000 due on 2025-12-31.",
            "section_type": "payment"
        }
    ]
    
    print("Testing inference on sample legal texts...\n")
    
    for i, sample in enumerate(test_samples, 1):
        print(f"Test {i}: {sample['section_type'].title()} Section")
        print("-" * 40)
        print(f"Original Text:\n{sample['text']}\n")
        
        # Format input using preprocessor
        formatted_input = preprocessor.format_training_input(
            sample['text'], 
            sample['section_type']
        )
        
        # Generate summary
        summary = summarizer.generate_summary(formatted_input)
        
        print(f"Generated Summary:\n{summary}\n")
        print("=" * 60)
        print()

if __name__ == "__main__":
    test_inference()
