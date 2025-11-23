#!/usr/bin/env python3
"""
Test script to validate the complete pipeline
"""

import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_data():
    """Create additional test data for validation"""
    test_data = {
        "test_cases": [
            {
                "id": 1,
                "section_type": "liability",
                "legal_text": "Section 6.2 Indemnification. Each party agrees to indemnify and hold harmless the other party from any claims, damages, or expenses arising from breach of this agreement. Maximum liability is limited to $500,000 per incident. This section remains in effect until 2027-08-31.",
                "expected_elements": ["Section 6.2", "$500,000", "2027-08-31"]
            },
            {
                "id": 2,
                "section_type": "confidentiality",
                "legal_text": "Clause 11.4 Data Protection. All customer data must be protected according to GDPR standards. Data retention period is 7 years from contract termination on 2025-11-15. Violations result in $10,000 daily penalties per Clause 11.5.",
                "expected_elements": ["Clause 11.4", "Clause 11.5", "2025-11-15", "$10,000"]
            }
        ]
    }
    
    # Save test data
    test_file = os.path.join("data", "test_cases.json")
    with open(test_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"Test data created at {test_file}")

def run_tests():
    """Run comprehensive tests"""
    print("Running T5 Legal Summarizer Tests...")
    
    # Test 1: Data preprocessing
    print("\n1. Testing data preprocessing...")
    from data.preprocessor import LegalTextPreprocessor
    
    preprocessor = LegalTextPreprocessor()
    sample_text = "Section 1.1 Payment of $1000 due on 2025-10-01 per Clause 2.3"
    elements = preprocessor.extract_legal_elements(sample_text)
    
    print(f"   ✓ Extracted elements: {elements}")
    
    # Test 2: Model initialization (if available)
    print("\n2. Testing model initialization...")
    try:
        from models.t5_summarizer import T5LegalSummarizer
        summarizer = T5LegalSummarizer()
        model, tokenizer = summarizer.initialize_model()
        print(f"   ✓ Model initialized with {model.num_parameters():,} parameters")
    except Exception as e:
        print(f"   ❌ Model initialization failed: {e}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--create-test-data", action="store_true", help="Create test data")
    parser.add_argument("--run-tests", action="store_true", help="Run tests")
    
    args = parser.parse_args()
    
    if args.create_test_data:
        create_test_data()
    
    if args.run_tests:
        run_tests()
    
    if not args.create_test_data and not args.run_tests:
        print("Usage: python test_samples.py [--create-test-data] [--run-tests]")
