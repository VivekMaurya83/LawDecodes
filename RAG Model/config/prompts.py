class LegalPrompts:
    
    LEGAL_CONDENSE_PROMPT = """
    Given the following conversation history and a follow-up legal question, 
    rephrase the follow-up question to be a standalone question that captures 
    all relevant legal context from the conversation history.

    Chat History:
    {chat_history}

    Follow Up Input: {question}
    
    Standalone Legal Question:"""
    
    # LEGAL_QA_PROMPT = """
    # You are an expert legal AI assistant. Using the provided legal documents, 
    # answer the question with detailed analysis and proper citations.

    # INSTRUCTIONS:
    # 1. Provide accurate legal analysis based solely on the provided documents
    # 2. Include specific citations with document names, sections, and page numbers
    # 3. Maintain professional legal terminology
    # 4. If information is insufficient, clearly state limitations
    # 5. Structure your response with clear legal reasoning

    # Legal Documents:
    # {context}

    # Question: {question}

    # Please provide your response in the following format:

    # **Legal Analysis:**
    # [Your detailed legal analysis here]

    # **Sources:**
    # [List numbered sources with exact citations and relevant quotes]

    # **Confidence Level:** [High/Medium/Low]
    # """

    
    LEGAL_QA_PROMPT = """
    You are an expert legal AI assistant. Answer the question based ONLY on the provided legal documents.

    IMPORTANT INSTRUCTIONS:
    1. Be concise and direct in your answer
    2. Quote specific text from the documents when relevant
    3. If the answer is not in the documents, clearly state that
    4. Use proper legal formatting and terminology
    5. Do not repeat information

    Legal Documents:
    {context}

    Question: {question}
    Chat History: {chat_history}

    Please provide a clear, direct answer:
    """
        
        # ... rest of prompts remain the same

    
    MEMORY_SUMMARIZATION_PROMPT = """
    Summarize the following legal conversation while preserving all important 
    legal context including:
    - Case names and citations referenced
    - Legal principles discussed  
    - Jurisdictions mentioned
    - Key legal conclusions reached
    - Ongoing legal matters or questions

    Conversation to summarize:
    {conversation}

    Legal Context Summary:"""

legal_prompts = LegalPrompts()
