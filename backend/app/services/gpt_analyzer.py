# app/services/gpt_analyzer.py

import json
import os
from datetime import datetime
from functools import lru_cache
from typing import Dict, Any, Optional, List
from openai import OpenAI
import asyncio
from dotenv import load_dotenv
import logging
from pathlib import Path

#
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


load_dotenv()

# Initializing OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

GPT_CONFIG = {
    "model": "gpt-4",
    "seed": 0,
    "temperature": 0,
}
# Configuring storage settings
STORAGE_DIR = Path("storage/gpt_responses")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Cache for prompt templates
PROMPT_TEMPLATES = {
    "functions_api": """Analyze the following code information and list ONLY the functions defined in api.py.

Here is the code analysis data in JSON format:
{context}

Please provide a clear and numbered list of all functions found in api.py.""",

    "classes_api": """Analyze the following code information and identify all classes defined in api.py:

Here is the code analysis data in JSON format:
{context}

Please list all classes found in api.py. If there's only one class, specify that.""",

    "imports_app": """Analyze the following code information and count the number of imports in app.py:

Here is the code analysis data in JSON format:
{context}

Please provide the total number of imports and list them with their aliases if any.""",

    "related_functions": """Analyze the following code information about how functions in app.py and api.py are related:

1. Look specifically at the API calls made from app.py to api.py endpoints
2. Identify which functions in app.py make calls to which endpoints in api.py
3. Note that functions making API calls are related but not present in both files
4. Examine the relationships through HTTP endpoints

Here is the code analysis data in JSON format:
{context}

Please provide a clear answer that:
1. Identifies which functions in app.py make API calls
2. Identifies which endpoints in api.py receive these calls
3. Explains how these functions are related through API interactions
4. Clarifies that while these functions interact, they exist in separate files""",

    "default": """Analyze the following code information and answer this question: {question}

Here is the code analysis data in JSON format:
{context}

Please provide a clear and concise answer based only on the information provided."""
}

class ResponseStorage:
    def __init__(self):
        self.base_dir = STORAGE_DIR
        
    def generate_filename(self, question: str) -> str:
        """Generate a filename based on the question and timestamp."""
        safe_question = "".join(x for x in question if x.isalnum() or x in (" ", "-", "_"))
        safe_question = safe_question[:50]  # Limit length
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{safe_question}.json"
        
    def save_response(self, response_data: Dict[str, Any]) -> str:
        """Save a response to a JSON file."""
        try:
            date_dir = self.base_dir / datetime.now().strftime("%Y-%m-%d")
            date_dir.mkdir(exist_ok=True)
            
            filename = self.generate_filename(response_data["question"])
            file_path = date_dir / filename
            
            response_with_metadata = {
                **response_data,
                "saved_at": datetime.now().isoformat(),
                "file_path": str(file_path)
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response_with_metadata, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved response to {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving response: {str(e)}")
            raise

    def load_response(self, file_path: str) -> Dict[str, Any]:
        """Load a response from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading response: {str(e)}")
            raise

    def get_responses_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """Get all responses for a specific date (format: YYYY-MM-DD)."""
        try:
            date_dir = self.base_dir / date_str
            if not date_dir.exists():
                return []
                
            responses = []
            for file_path in date_dir.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    responses.append(json.load(f))
            return responses
        except Exception as e:
            logger.error(f"Error getting responses by date: {str(e)}")
            raise

# Initializing storage
storage = ResponseStorage()

@lru_cache(maxsize=128)
def get_prompt_template(question: str) -> str:
    """Get the appropriate prompt template based on the question."""
    question_mapping = {
        "What functions does api.py have?": "functions_api",
        "What are different classes present in api.py?": "classes_api",
        "How many imports are present in app.py?": "imports_app",
        "How many functions are related in both app.py and api.py?": "related_functions"
    }
    return PROMPT_TEMPLATES.get(question_mapping.get(question, "default"))

def prepare_analysis_prompt(analysis_data: Dict[str, Any], question: str) -> str:
    """Prepare the prompt for GPT based on analysis data and question."""
    try:
        context = json.dumps(analysis_data, indent=2)
        template = get_prompt_template(question)
        return template.format(context=context, question=question)
    except Exception as e:
        logger.error(f"Error preparing prompt: {str(e)}")
        raise

async def analyze_with_gpt(analysis_data: Dict[str, Any], question: str) -> Dict[str, Any]:
    """Process analysis data with GPT and save the response."""
    if not client.api_key:
        logger.error("OpenAI API key not found")
        return {"error": "OpenAI API key not found in environment variables."}

    try:
        prompt = prepare_analysis_prompt(analysis_data, question)
        logger.info(f"Analyzing question: {question}")
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=GPT_CONFIG["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=GPT_CONFIG["temperature"],
            seed=GPT_CONFIG["seed"]
        )
        
        answer = response.choices[0].message.content
        logger.info("Received response from GPT")
        
        response_data = {
            "question": question,
            "response": answer,
            "timestamp": datetime.now().isoformat(),
        }
        
        file_path = storage.save_response(response_data)
        response_data["file_path"] = file_path
        
        return response_data
    except Exception as e:
        logger.error(f"Error in GPT analysis: {str(e)}")
        return {
            "error": str(e),
            "question": question,
            "timestamp": datetime.now().isoformat()
        }

async def batch_analyze(analysis_data: Dict[str, Any], questions: List[str]) -> List[Dict[str, Any]]:
    """Process multiple questions in parallel."""
    tasks = [analyze_with_gpt(analysis_data, question) for question in questions]
    return await asyncio.gather(*tasks)

def prepare_analysis_prompt(analysis_data: Dict[str, Any], question: str) -> str:
    """Prepare the prompt for GPT based on analysis data and question."""
    try:
        context = json.dumps(analysis_data, indent=2)
        template = get_prompt_template(question)
        return template.format(context=context, question=question)
    except Exception as e:
        logger.error(f"Error preparing prompt: {str(e)}")
        raise

if __name__ == "__main__":
    async def test_analyze():
        analysis_data = {
            "file_structure": {},
            "dependencies": {},
            "functions": {}
        }
        question = "What functions does api.py have?"
        result = await analyze_with_gpt(analysis_data, question)
        print(json.dumps(result, indent=2))

    asyncio.run(test_analyze())