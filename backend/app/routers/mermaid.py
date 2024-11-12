from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.mermaid_generator import generate_mermaid_diagram
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mermaid", tags=["mermaid"])

class MermaidRequest(BaseModel):
    analysis_data: Dict[str, Any]
    diagram_type: str = "flowchart"

@router.post("/")
async def mermaid_diagram(request: MermaidRequest):
    try:
        # Log incoming request
        logger.debug(f"Received request with diagram_type: {request.diagram_type}")
        
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        logger.debug(f"OpenAI API key present: {bool(openai_api_key)}")
        
        if not openai_api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not found in environment variables"
            )

        # Log analysis data structure
        logger.debug(f"Analysis data structure: {type(request.analysis_data)}")
        
        result = generate_mermaid_diagram(
            analysis_data=request.analysis_data,
            api_key=openai_api_key,
            diagram_type=request.diagram_type
        )
        
        # Log result
        logger.debug(f"Generated result: {result}")

        if "error" in result:
            logger.error(f"Error in result: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except Exception as e:
        logger.exception("Error in mermaid_diagram endpoint")
        raise HTTPException(status_code=500, detail=str(e))