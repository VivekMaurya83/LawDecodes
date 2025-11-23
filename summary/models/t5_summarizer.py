import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from peft import LoraConfig, get_peft_model, TaskType
from summary.config.model_config import config

import os


class T5LegalSummarizer:
    def __init__(self, model_path: str = None):
        self.config = config
        self.model_path = model_path or self.config.model_name
        self.tokenizer = None
        self.model = None
        
    def initialize_model(self):
        """Initialize T5 model and tokenizer"""
        print(f"Initializing {self.config.model_name}...")
        
        # Load tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(self.config.model_name)
        
        # Add special tokens
        special_tokens_dict = {
            'additional_special_tokens': self.config.special_tokens
        }
        self.tokenizer.add_special_tokens(special_tokens_dict)
        
        # Load model
        self.model = T5ForConditionalGeneration.from_pretrained(self.config.model_name)
        
        # Resize embeddings for new tokens
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        print(f"Model loaded with {self.model.num_parameters():,} parameters")
        print(f"Vocabulary size: {len(self.tokenizer)}")
        
        return self.model, self.tokenizer
    
    def setup_lora(self):
        """Setup LoRA for parameter-efficient fine-tuning"""
        lora_config = LoraConfig(
            task_type=TaskType.SEQ_2_SEQ_LM,
            inference_mode=False,
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=["q", "v", "k", "o", "wi_0", "wi_1", "wo"]
        )
        
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
        return self.model
    
    def generate_summary(self, input_text: str, max_length: int = 128) -> str:
        """Generate summary for input text"""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not initialized. Call initialize_model() first.")
        
        # Tokenize input
        inputs = self.tokenizer(
            input_text,
            max_length=self.config.max_input_length,
            truncation=True,
            return_tensors="pt"
        )
        
        # Generate summary with named arguments for PEFT models
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_length=max_length,
                min_length=20,
                num_beams=4,
                early_stopping=True,
                do_sample=False,  # ✅ Remove temperature when do_sample=False
                no_repeat_ngram_size=2,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # ✅ FIXED: Use batch_decode and take first result
        summary = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return summary.strip()


    
    def save_model(self, save_path: str):
        """Save trained model and tokenizer"""
        os.makedirs(save_path, exist_ok=True)
        
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        
        print(f"Model saved to {save_path}")
    
    
    def load_trained_model(self, model_path: str):
        """Load a trained model with proper token handling"""
        print(f"Loading trained model from {model_path}...")
        
        # First load the tokenizer to get the correct vocabulary size
        self.tokenizer = T5Tokenizer.from_pretrained(model_path)
        
        # Load base model
        self.model = T5ForConditionalGeneration.from_pretrained(self.config.model_name)
        
        # Resize embeddings to match the saved tokenizer
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        # Now load the trained adapter
        from peft import PeftModel
        self.model = PeftModel.from_pretrained(self.model, model_path)
        
        self.model.eval()
        print("Trained model loaded successfully")
