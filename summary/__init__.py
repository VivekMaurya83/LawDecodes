"""
T5 Legal Summarization Engine

A lightweight, CPU-optimized legal document summarization system
using T5-Small with parameter-efficient fine-tuning.
"""

__version__ = "1.0.0"
__author__ = "Legal AI Team"

from summary.models.t5_summarizer import T5LegalSummarizer
from summary.models.trainer import LegalSummarizerTrainer

from .data.preprocessor import LegalTextPreprocessor
from .config.model_config import config

__all__ = [
    "T5LegalSummarizer",
    "LegalTextPreprocessor", 
    "config"
]
