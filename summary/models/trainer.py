from transformers import TrainingArguments, Trainer
import evaluate
import numpy as np
import torch
from summary.config.model_config import config
import os

class LegalSummarizerTrainer:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        try:
            self.rouge_metric = evaluate.load("rouge")
        except Exception as e:
            print(f"Warning: Could not load ROUGE metric: {e}")
            self.rouge_metric = None
        
    def compute_metrics(self, eval_pred):
        """Compute evaluation metrics"""
        predictions, labels = eval_pred
        
        # ✅ FIX: Handle tuple predictions (logits, other_outputs)
        if isinstance(predictions, tuple):
            predictions = predictions[0]  # Extract logits from tuple
        
        # Convert logits to token IDs
        if hasattr(predictions, 'ndim') and predictions.ndim == 3:
            predictions = np.argmax(predictions, axis=-1)
        
        # Decode predictions
        decoded_preds = self.tokenizer.batch_decode(predictions, skip_special_tokens=True)
        
        # Replace -100 in labels (padding token)
        labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
        decoded_labels = self.tokenizer.batch_decode(labels, skip_special_tokens=True)
        
        # Clean up text
        decoded_preds = [pred.strip() for pred in decoded_preds]
        decoded_labels = [label.strip() for label in decoded_labels]
        
        # Print sample predictions for debugging
        if len(decoded_preds) > 0:
            print(f"\n--- Sample Prediction ---")
            print(f"Predicted: {decoded_preds[0]}")
            print(f"Expected:  {decoded_labels[0]}")
            print("------------------------\n")
        
        # Compute ROUGE scores
        if self.rouge_metric is not None:
            try:
                rouge_result = self.rouge_metric.compute(
                    predictions=decoded_preds,
                    references=decoded_labels,
                    use_stemmer=True
                )
                
                result = {
                    "rouge1": rouge_result["rouge1"],
                    "rouge2": rouge_result["rouge2"], 
                    "rougeL": rouge_result["rougeL"]
                }
            except Exception as e:
                print(f"Warning: ROUGE computation failed: {e}")
                result = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
        else:
            result = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
        
        return result
    
    def setup_training_arguments(self):
        """Setup training arguments"""
        return TrainingArguments(
            output_dir=config.output_dir,
            num_train_epochs=config.num_epochs,
            per_device_train_batch_size=config.batch_size,
            per_device_eval_batch_size=config.batch_size,
            warmup_steps=config.warmup_steps,
            weight_decay=config.weight_decay,
            logging_dir=config.log_dir,
            logging_steps=10,
            save_strategy="epoch",
            eval_strategy="epoch",
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="rouge1",
            greater_is_better=True,
            learning_rate=config.learning_rate,
            fp16=False,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
            report_to=None
        )
    
    def train(self, train_dataset, eval_dataset):
        """Train the model"""
        training_args = self.setup_training_arguments()
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=self.compute_metrics,
            processing_class=self.tokenizer
        )
        
        print("Starting training...")
        trainer.train()
        
        # Save final model
        final_model_path = os.path.join(config.output_dir, "final_model")
        trainer.save_model(final_model_path)
        
        print(f"Training completed! Model saved to {final_model_path}")
        
        return trainer
