#!/usr/bin/env python3
"""
Main training script for T5 Legal Summarization Engine
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from summary.models.t5_summarizer import T5LegalSummarizer
from summary.models.trainer import LegalSummarizerTrainer
from models.trainer import LegalSummarizerTrainer
from data.preprocessor import LegalTextPreprocessor
from data.dataset_builder import LegalDatasetBuilder
from config.model_config import config

def main():
    print("="*60)
    print("T5 Legal Summarization Engine - Training")
    print("="*60)
    
    # Step 1: Initialize model
    summarizer = T5LegalSummarizer()
    model, tokenizer = summarizer.initialize_model()
    
    # Step 2: Setup LoRA
    model = summarizer.setup_lora()
    
    # Step 3: Load and preprocess data
    print("\nLoading training data...")
    preprocessor = LegalTextPreprocessor()
    training_data_path = os.path.join(config.data_dir, "sample_training_data.json")
    
    examples = preprocessor.load_training_data(training_data_path)
    print(f"Loaded {len(examples)} training examples")
    
    # Step 4: Create dataset
    dataset_builder = LegalDatasetBuilder(tokenizer)
    dataset = dataset_builder.tokenize_examples(examples)
    
    # Split dataset
    train_dataset, eval_dataset = dataset_builder.create_train_eval_split(dataset)
    print(f"Train samples: {len(train_dataset)}")
    print(f"Eval samples: {len(eval_dataset)}")
    
    # Step 5: Train model
    trainer = LegalSummarizerTrainer(model, tokenizer)
    trained_model = trainer.train(train_dataset, eval_dataset)
    
    print("\nTraining completed successfully!")
    print(f"Model saved to: {config.output_dir}")

if __name__ == "__main__":
    main()
