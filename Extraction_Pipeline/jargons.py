import json
import google.generativeai as genai
import os
import sys
import logging
import re
import time
from typing import List, Dict

# This file assumes that the Gemini API has already been configured by its caller.

def load_legal_dictionary(json_path: str) -> Dict[str, str]:
    """Loads a dictionary of terms from a JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            legal_terms = json.load(f)
        # We only care about the legal-specific terms for the fallback
        return {item['term'].lower(): item['definition'] for item in legal_terms if ' ' in item['term'] or item['term'].endswith('ae')}
    except Exception as e:
        logging.error(f"Error loading legal dictionary: {e}")
        return {}

def extract_jargon_with_gemini(text_content: str) -> List[str]:
    """
    MODIFIED: Uses a much more specific prompt to get only relevant legal jargon.
    """
    try:
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        # This prompt is specifically tuned to ignore common words.
        prompt = f"""
        Analyze the following legal text. Extract only the specialized legal terminology,
        phrases of art, and Latin terms. Ignore common, everyday words (e.g., 'Agreement',
        'Services', 'Term', 'Compensation'). Return ONLY the specialized terms as a single,
        comma-separated list.

        Examples of what to extract: "Ipso Facto", "Habeas Corpus", "Breach of Contract", "Fiduciary Duty", "Statute of Limitations".
        Examples of what to IGNORE: "Parties agree", "includes", "in writing", "taxes".
        
        Text to analyze:
        {text_content}
        """
        response = model.generate_content(prompt)
        terms = [term.strip() for term in response.text.split(',') if term.strip()]
        return list(set(terms)) # Return a list of unique terms
    except Exception as e:
        logging.warning(f"Jargon extraction failed: {e}. Using fallback.")
        return []

def fallback_extract_from_dictionary(text_content: str, legal_dict: Dict[str, str]) -> List[str]:
    """A more targeted fallback that looks for multi-word phrases or Latin terms."""
    terms_found = set()
    text_lower = text_content.lower()
    for term in legal_dict.keys():
        if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
            terms_found.add(term.title())
    return sorted(list(terms_found))

def get_definitions_in_batch(terms: List[str], legal_dict: Dict[str, str]) -> Dict[str, Dict]:
    """
    MODIFIED: Gets all definitions in a single, efficient Gemini API call.
    """
    definitions = {}
    terms_to_define_with_gemini = []

    # Step 1: Get all available definitions from our fast local dictionary
    for term in terms:
        term_lower = term.lower().strip()
        if term_lower in legal_dict:
            definitions[term] = {'source': 'dictionary', 'definition': legal_dict[term_lower]}
        else:
            terms_to_define_with_gemini.append(term)
    
    # Step 2: If there are any remaining terms, ask Gemini to define them all at once
    if terms_to_define_with_gemini and genai.get_model("models/gemini-2.5-flash"):
        logging.info(f"Asking to define {len(terms_to_define_with_gemini)} terms in a single batch...")
        try:
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")

            # Create a numbered list of terms for the prompt
            term_list_str = "\n".join([f"{i+1}. {term}" for i, term in enumerate(terms_to_define_with_gemini)])
            
            # A prompt designed for structured JSON output
            prompt = f"""
            For each term in the following numbered list, provide a concise, one-sentence definition in plain language.
            Return the output as a valid JSON object where the keys are the exact terms from the list and the values are their definitions.

            TERMS:
            {term_list_str}
            """
            
            response = model.generate_content(prompt)
            
            # Clean and parse the JSON response
            cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
            gemini_definitions = json.loads(cleaned_response)
            
            for term, definition in gemini_definitions.items():
                # Find the original casing of the term to use as the key
                original_term = next((t for t in terms_to_define_with_gemini if t.lower() == term.lower()), term)
                definitions[original_term] = {'source': 'gemini', 'definition': definition}

        except Exception as e:
            logging.error(f"Batch definition failed: {e}")
            # Mark the remaining terms as failed
            for term in terms_to_define_with_gemini:
                definitions[term] = {'source': 'error', 'definition': 'Could not generate definition due to an API error.'}
    
    return definitions

def process_and_extract_jargon(text_file_path: str, json_dict_path: str) -> Dict:
    """Main library function to process a text file and return a dictionary of jargon."""
    logging.info("🔬 Starting Jargon Extraction Process...")
    try:
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except Exception as e:
        logging.error(f"Could not read text file for jargon extraction: {e}")
        return {}
    
    legal_dict = load_legal_dictionary(json_dict_path)
    
    extracted_terms = extract_jargon_with_gemini(text_content)
    if not extracted_terms:
        logging.info("No terms, running dictionary-based fallback extractor...")
        extracted_terms = fallback_extract_from_dictionary(text_content, legal_dict)
    
    logging.info(f"Found {len(extracted_terms)} potential terms. Getting definitions...")
    # --- Use the new batch function ---
    term_definitions = get_definitions_in_batch(extracted_terms, legal_dict)
    
    output_data = {'terms': []}
    # Sort terms alphabetically for consistent output
    for term in sorted(term_definitions.keys()):
        info = term_definitions[term]
        output_data['terms'].append({
            'term': term,
            'definition': info['definition'],
            'source': info['source']
        })
    
    logging.info("✅ Jargon extraction and definition process complete.")
    return output_data