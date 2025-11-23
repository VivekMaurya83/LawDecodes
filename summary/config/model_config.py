import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ModelConfig:
    # Model parameters
    model_name: str = "t5-small"
    max_input_length: int = 512
    max_target_length: int = 128
    
    # Training parameters
    num_epochs: int = 5
    batch_size: int = 8
    learning_rate: float = 3e-4
    warmup_steps: int = 100
    weight_decay: float = 0.01
    
    # LoRA parameters
    lora_r: int = 8
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    
    # Paths
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir: str = os.path.join(base_dir, "outputs", "models")
    log_dir: str = os.path.join(base_dir, "outputs", "logs")
    data_dir: str = os.path.join(base_dir, "data")
    
    # Special tokens for legal documents
    special_tokens: List[str] = None
    
    def __post_init__(self):
        if self.special_tokens is None:
            self.special_tokens = [
                "[SECTION]", "[/SECTION]",
                "[CLAUSE]", "[/CLAUSE]", 
                "[DATE]", "[/DATE]",
                "[PARTY]", "[/PARTY]",
                "[AMOUNT]", "[/AMOUNT]",
                "[REFERENCE]", "[/REFERENCE]"
            ]
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

# Global config instance
config = ModelConfig()
