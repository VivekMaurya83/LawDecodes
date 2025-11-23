import json
import os
from typing import List, Dict
from transformers import T5ForConditionalGeneration, T5Tokenizer, TrainingArguments, Trainer
from datasets import Dataset
import torch

class EnhancedLegalTrainer:
    """Enhanced trainer with more legal data and NER integration"""
    
    def __init__(self, base_model_path: str, legal_ner=None):
        self.base_model_path = base_model_path
        self.legal_ner = legal_ner
        
        # Load existing model and tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(base_model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(base_model_path)
    
    def load_enhanced_training_data(self, json_files: List[str]) -> List[Dict]:
        """Load multiple training data files"""
        all_examples = []
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_examples.extend(data['training_examples'])
        
        print(f"Loaded {len(all_examples)} total training examples")
        return all_examples
    
    def create_enhanced_prompts(self, examples: List[Dict]) -> List[Dict]:
        """Create prompts enhanced with NER information"""
        enhanced_examples = []
        
        for example in examples:
            text = example['legal_text']
            section_type = example['section_type']
            target = example['summary']
            
            # Add NER enhancement if available
            if self.legal_ner:
                enhanced_text, entity_summary = self.legal_ner.enhance_text_with_entities(text)
                prompt = f"Summarize this {section_type} section preserving all key legal entities:\n{enhanced_text}"
            else:
                # Fallback to basic enhancement
                key_elements = example.get('key_elements', {})
                elements_str = ", ".join([f"{k}: {v}" for k, v in key_elements.items() if v])
                prompt = f"Summarize this {section_type} section preserving: {elements_str}\n\nText: {text}"
            
            enhanced_examples.append({
                'input_text': prompt,
                'target_text': target,
                'section_type': section_type
            })
        
        return enhanced_examples
    
    def prepare_dataset(self, examples: List[Dict]) -> Dataset:
        """Prepare dataset for training"""
        def tokenize_function(batch):
            model_inputs = self.tokenizer(
                batch['input_text'],
                max_length=512,
                truncation=True,
                padding=True
            )
            
            labels = self.tokenizer(
                batch['target_text'],
                max_length=128,
                truncation=True,
                padding=True
            )
            
            model_inputs['labels'] = labels['input_ids']
            return model_inputs
        
        dataset = Dataset.from_dict({
            'input_text': [ex['input_text'] for ex in examples],
            'target_text': [ex['target_text'] for ex in examples],
            'section_type': [ex['section_type'] for ex in examples]
        })
        
        return dataset.map(tokenize_function, batched=True)
    
    def enhanced_fine_tune(self, training_data_files: List[str], output_dir: str):
        """Fine-tune with enhanced data"""
        print("🔄 Starting enhanced fine-tuning...")
        
        # Load and enhance training data
        examples = self.load_enhanced_training_data(training_data_files)
        enhanced_examples = self.create_enhanced_prompts(examples)
        
        # Prepare dataset
        dataset = self.prepare_dataset(enhanced_examples)
        train_dataset, eval_dataset = dataset.train_test_split(test_size=0.2).values()
        
        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=5,
            per_device_train_batch_size=4,  # Reduced for stability
            per_device_eval_batch_size=4,
            warmup_steps=100,
            weight_decay=0.01,
            logging_steps=50,
            eval_strategy="epoch",
            save_strategy="epoch",
            save_total_limit=3,
            load_best_model_at_end=True,
            learning_rate=2e-5,  # Lower learning rate for fine-tuning
            report_to=None
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            processing_class=self.tokenizer
        )
        
        # Train
        trainer.train()
        
        # Save enhanced model
        enhanced_model_path = os.path.join(output_dir, "enhanced_model")
        trainer.save_model(enhanced_model_path)
        self.tokenizer.save_pretrained(enhanced_model_path)
        
        print(f"✅ Enhanced model saved to {enhanced_model_path}")
        return enhanced_model_path

# Usage script
def run_enhanced_training():
    from extraction_pipeline.legal_ner import LegalNER
    
    # Initialize NER
    ner = LegalNER()
    
    # Initialize trainer
    base_model_path = "../Summary/outputs/models/final_model"
    trainer = EnhancedLegalTrainer(base_model_path, ner)
    
    # Training data files
    training_files = [
        "../Summary/data/sample_training_data.json",
        "../Summary/data/enhanced_training_data.json"
    ]
    
    # Fine-tune
    enhanced_model_path = trainer.enhanced_fine_tune(
        training_files, 
        "../Summary/outputs/models/enhanced"
    )
    
    print(f"🎉 Enhanced training completed! Model at: {enhanced_model_path}")

if __name__ == "__main__":
    run_enhanced_training()
