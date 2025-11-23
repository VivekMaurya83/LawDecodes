#!/usr/bin/env python3
"""
RAG Model Orchestrator
======================

This script orchestrates the execution of the RAG model pipeline:
1. Runs pdf_extract.py to extract text from PDF documents
2. Runs summary_extracted_audit.py to generate summaries
3. Runs main.py with the extracted text file to enable RAG Q&A

Usage:
    python orchestrator.py

The script will automatically handle the execution sequence and provide
status updates for each step.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RAGOrchestrator:
    """Orchestrates the execution of RAG model pipeline components."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data" / "raw" / "legal_documents"
        self.pdf_extract_script = self.data_dir / "pdf_extract.py"
        self.summary_script = self.data_dir / "summary_extracted_audit.py"
        self.main_script = self.base_dir / "main.py"
        self.target_file = self.data_dir / "extracted_access_control.txt"
        
        # Validate paths
        self._validate_paths()
    
    def _validate_paths(self) -> None:
        """Validate that all required files exist."""
        required_files = [
            self.pdf_extract_script,
            self.summary_script,
            self.main_script
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}")
        
        logger.info("All required files validated successfully")
    
    def run_script(self, script_path: Path, description: str) -> Tuple[bool, str]:
        """
        Run a Python script and return success status and output.
        
        Args:
            script_path: Path to the Python script to run
            description: Human-readable description of what the script does
            
        Returns:
            Tuple of (success: bool, output: str)
        """
        logger.info(f"Starting: {description}")
        logger.info(f"Executing: python {script_path}")
        
        try:
            # Change to the script's directory to ensure relative imports work
            script_dir = script_path.parent
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(script_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"SUCCESS: Successfully completed: {description}")
                if result.stdout:
                    logger.debug(f"Output: {result.stdout}")
                return True, result.stdout
            else:
                logger.error(f"ERROR: Failed: {description}")
                logger.error(f"Error output: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"TIMEOUT: {description} took too long to complete")
            return False, "Script execution timed out"
        except Exception as e:
            logger.error(f"EXCEPTION: Exception during {description}: {str(e)}")
            return False, str(e)
    
    def check_target_file(self) -> bool:
        """
        Check if the target file exists and has content.
        
        Returns:
            bool: True if file exists and has content, False otherwise
        """
        if not self.target_file.exists():
            logger.warning(f"Target file does not exist: {self.target_file}")
            return False
        
        file_size = self.target_file.stat().st_size
        if file_size == 0:
            logger.warning(f"Target file is empty: {self.target_file}")
            return False
        
        logger.info(f"SUCCESS: Target file exists and has content ({file_size} bytes): {self.target_file}")
        return True
    
    def run_pipeline(self) -> bool:
        """
        Run the complete RAG pipeline.
        
        Returns:
            bool: True if all steps completed successfully, False otherwise
        """
        logger.info("Starting RAG Model Pipeline")
        logger.info("=" * 50)
        
        # Step 1: Run PDF extraction
        logger.info("\nStep 1: PDF Text Extraction")
        success, output = self.run_script(
            self.pdf_extract_script,
            "PDF text extraction from legal documents"
        )
        
        if not success:
            logger.error("ERROR: PDF extraction failed. Stopping pipeline.")
            return False
        
        # Step 2: Run summary generation
        logger.info("\nStep 2: Summary Generation")
        success, output = self.run_script(
            self.summary_script,
            "Summary generation from extracted text"
        )
        
        if not success:
            logger.error("ERROR: Summary generation failed. Stopping pipeline.")
            return False
        
        # Step 3: Verify target file exists
        logger.info("\nStep 3: Verifying Target File")
        if not self.check_target_file():
            logger.error("ERROR: Target file verification failed. Stopping pipeline.")
            return False
        
        # Step 4: Run RAG model
        logger.info("\nStep 4: Starting RAG Model")
        success, output = self.run_script(
            self.main_script,
            f"RAG model execution with {self.target_file}"
        )
        
        if not success:
            logger.error("ERROR: RAG model execution failed.")
            return False
        
        logger.info("\nSUCCESS: Pipeline completed successfully!")
        return True
    
    def run_rag_only(self) -> bool:
        """
        Run only the RAG model (assuming previous steps are already completed).
        
        Returns:
            bool: True if RAG model runs successfully, False otherwise
        """
        logger.info("🤖 Running RAG Model Only")
        logger.info("=" * 30)
        
        # Verify target file exists
        if not self.check_target_file():
            logger.error("❌ Target file not found. Please run the full pipeline first.")
            return False
        
        # Run RAG model
        success, output = self.run_script(
            self.main_script,
            f"RAG model execution with {self.target_file}"
        )
        
        if success:
            logger.info("SUCCESS: RAG model completed successfully!")
        else:
            logger.error("ERROR: RAG model execution failed.")
        
        return success

def main():
    """Main entry point for the orchestrator."""
    print("RAG Model Orchestrator")
    print("=" * 50)
    print("This script will run the complete RAG pipeline:")
    print("1. PDF text extraction")
    print("2. Summary generation")
    print("3. RAG model execution")
    print("=" * 50)
    
    try:
        orchestrator = RAGOrchestrator()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--rag-only":
                logger.info("Running RAG model only (skipping extraction and summary)")
                success = orchestrator.run_rag_only()
            elif sys.argv[1] == "--help":
                print("\nUsage:")
                print("  python orchestrator.py           # Run full pipeline")
                print("  python orchestrator.py --rag-only # Run RAG model only")
                print("  python orchestrator.py --help     # Show this help")
                return
            else:
                logger.error(f"Unknown argument: {sys.argv[1]}")
                print("Use --help for usage information")
                return
        else:
            # Run full pipeline
            success = orchestrator.run_pipeline()
        
        if success:
            logger.info("SUCCESS: Orchestrator completed successfully!")
            print("\nSUCCESS: All done! The RAG model is ready for Q&A.")
        else:
            logger.error("ERROR: Orchestrator failed!")
            print("\nERROR: Pipeline failed. Check the logs for details.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"FATAL ERROR: {str(e)}")
        print(f"\nFATAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
