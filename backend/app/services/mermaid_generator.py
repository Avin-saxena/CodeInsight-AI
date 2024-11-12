import openai
from typing import Dict, Any
from datetime import datetime
import logging
import json
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def prepare_mermaid_prompt(analysis_data: Dict[str, Any], diagram_type: str = "flowchart") -> str:
    """Prepare prompt for GPT-4 to generate Mermaid diagram."""
    try:
        if diagram_type == "flowchart":
            # extracting relevant information from analysis_data
            app_functions = analysis_data.get('app_analysis', {}).get('functions', [])
            api_functions = analysis_data.get('api_analysis', {}).get('functions', [])
            
            prompt = f"""Based on this code analysis, create a Mermaid flowchart showing the interaction between app.py and api.py.

Available functions:
App.py functions: {', '.join(app_functions)}
Api.py functions: {', '.join(api_functions)}

Requirements for the flowchart:
1. Use 'flowchart TD' for top-down layout
2. Show app.py and api.py in separate subgraphs
3. Show the API call flow between functions
4. Use appropriate shapes: 
   - Rectangles for regular functions
   - Rounded boxes for API endpoints
   - Diamonds for decision points
5. Use colors:
   - Light blue for app.py components
   - Light green for api.py components
6. Add clear labels and arrows showing data flow

Generate ONLY the Mermaid diagram code without any explanations."""

        elif diagram_type == "class":
            # extracting class-related information
            app_classes = analysis_data.get('app_analysis', {}).get('classes', [])
            api_classes = analysis_data.get('api_analysis', {}).get('classes', [])
            
            prompt = f"""Based on this code analysis, create a Mermaid class diagram showing the structure of the codebase.

Available classes:
App.py classes: {', '.join(app_classes)}
Api.py classes: {', '.join(api_classes)}

Requirements for the class diagram:
1. Start with 'classDiagram'
2. Show all classes with their methods and attributes
3. Include relationships between classes using proper notation:
   - Inheritance: --|>
   - Composition: *--
   - Association: -->
4. Add method parameters where available
5. Use proper visibility indicators (+, -, #)
6. Group related classes together

Generate ONLY the Mermaid diagram code without any explanations."""

        else:
            # Generic diagram type
            prompt = f"""Based on this code analysis, create a Mermaid {diagram_type} diagram showing the structure and relationships in the code.

Analysis data summary:
{json.dumps(analysis_data, indent=2)}

Requirements:
1. Show main components and their relationships
2. Use appropriate Mermaid syntax for {diagram_type}
3. Keep the diagram clear and readable
4. Show important connections and data flow
5. Use appropriate shapes and styles

Generate ONLY the Mermaid diagram code without any explanations."""

        logger.debug(f"Generated prompt for {diagram_type} diagram")
        return prompt

    except Exception as e:
        logger.exception("Error in prepare_mermaid_prompt")
        raise Exception(f"Failed to prepare prompt: {str(e)}")

def validate_analysis_data(analysis_data: Dict[str, Any]) -> bool:
    """Validate the structure of analysis data."""
    try:
        required_keys = ['app_analysis', 'api_analysis']
        if not all(key in analysis_data for key in required_keys):
            logger.error(f"Missing required keys in analysis_data. Found keys: {list(analysis_data.keys())}")
            return False

        return True
    except Exception as e:
        logger.exception("Error in validate_analysis_data")
        return False

def generate_mermaid_diagram(analysis_data: Dict[str, Any], api_key: str, diagram_type: str = "flowchart") -> Dict[str, Any]:
    """Generate Mermaid diagram using GPT-4."""
    try:
        if not api_key:
            logger.error("No API key provided")
            return {"error": "OpenAI API key is required", "type": diagram_type}

        if not validate_analysis_data(analysis_data):
            logger.error("Invalid analysis data structure")
            return {"error": "Invalid analysis data structure", "type": diagram_type}

        # Configuring OpenAI client
        logger.debug("Setting up OpenAI client")
        client = openai.OpenAI(api_key=api_key)

        # Preparing the prompt
        try:
            prompt = prepare_mermaid_prompt(analysis_data, diagram_type)
            logger.debug(f"Prompt length: {len(prompt)}")
        except Exception as e:
            logger.exception("Error preparing prompt")
            return {"error": f"Failed to prepare prompt: {str(e)}", "type": diagram_type}

        # Making the API call
        logger.debug("Making OpenAI API call")
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0
            )
            
            mermaid_code = response.choices[0].message.content.strip()
            logger.debug(f"Generated Mermaid code length: {len(mermaid_code)}")

            # Basic validation of generated code
            if not mermaid_code.startswith(('flowchart', 'classDiagram', 'sequenceDiagram')):
                logger.warning("Generated code might not be valid Mermaid syntax")

            return {
                "type": diagram_type,
                "mermaid_code": mermaid_code,
                "timestamp": datetime.now().isoformat()
            }

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {
                "error": f"OpenAI API error: {str(e)}",
                "type": diagram_type,
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.exception("Unexpected error in generate_mermaid_diagram")
        return {
            "error": f"Unexpected error: {str(e)}",
            "type": diagram_type,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":

    load_dotenv()
    
    # getting API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    

    example_data = {
        "app_analysis": {
            "functions": ["main", "process_data", "handle_request"],
            "classes": ["DataProcessor", "RequestHandler"]
        },
        "api_analysis": {
            "functions": ["get_data", "post_data", "update_record"],
            "classes": ["APIHandler", "DataManager"]
        }
    }
    
    # Generating diagram
    result = generate_mermaid_diagram(example_data, api_key)
    

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("Generated Mermaid Diagram Code:")
        print(result['mermaid_code'])