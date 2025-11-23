@echo off
echo RAG Model Pipeline Runner
echo ========================
echo.
echo This will run the complete RAG pipeline:
echo 1. PDF text extraction
echo 2. Summary generation  
echo 3. RAG model execution
echo.
pause
echo.
python orchestrator.py
pause
