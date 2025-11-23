from datasets import Dataset
from transformers import T5Tokenizer
from typing import List, Dict, Any
from summary.config.model_config import config


class LegalDatasetBuilder:
    def __init__(self, tokenizer: T5Tokenizer):
        self.tokenizer = tokenizer
        self.max_input_length = config.max_input_length
        self.max_target_length = config.max_target_length
    
    def tokenize_examples(self, examples: List[Dict[str, Any]]) -> Dataset:
        """Convert examples to tokenized dataset"""
        def tokenize_function(batch):
            # Tokenize inputs
            model_inputs = self.tokenizer(
                batch['input_text'],
                max_length=self.max_input_length,
                truncation=True,
                padding=True,
                return_tensors='pt'
            )
            
            # Tokenize targets
            labels = self.tokenizer(
                batch['target_text'],
                max_length=self.max_target_length,
                truncation=True,
                padding=True,
                return_tensors='pt'
            )
            
            # Set labels for loss calculation
            model_inputs['labels'] = labels['input_ids']
            
            return model_inputs
        
        # Create dataset from examples
        dataset_dict = {
            'input_text': [ex['input_text'] for ex in examples],
            'target_text': [ex['target_text'] for ex in examples],
            'section_type': [ex['section_type'] for ex in examples]
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=['input_text', 'target_text', 'section_type']
        )
        
        return tokenized_dataset
    
    def create_train_eval_split(self, dataset: Dataset, eval_ratio: float = 0.2):
        """Split dataset into train and eval"""
        dataset = dataset.shuffle(seed=42)
        split_dataset = dataset.train_test_split(test_size=eval_ratio)
        return split_dataset['train'], split_dataset['test']
