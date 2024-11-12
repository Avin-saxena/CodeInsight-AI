# app/routers/gpt.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from app.services.gpt_analyzer import analyze_with_gpt, batch_analyze, storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gpt", tags=["gpt"])
GPT_CONFIG = {
    "model": "gpt-4",
    "seed": 0,
    "temperature": 0,
}
class GPTRequest(BaseModel):
    analysis_data: Dict[str, Any] = Field(..., description="Code analysis data to be processed")
    question: str = Field(..., description="Question to be answered about the code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_data": {
                    "file_structure": {},
                    "dependencies": {},
                    "functions": {}
                },
                "question": "What functions does api.py have?"
            }
        }

class BatchGPTRequest(BaseModel):
    analysis_data: Dict[str, Any] = Field(..., description="Code analysis data to be processed")
    questions: List[str] = Field(..., description="List of questions to be answered")

class ResponseFilter(BaseModel):
    start_date: Optional[str] = Field(None, description="Start date for filtering responses (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date for filtering responses (YYYY-MM-DD)")
    question_contains: Optional[str] = Field(None, description="Filter responses by question content")

@router.post("/", response_model=Dict[str, Any])
async def gpt_analyze(request: GPTRequest, background_tasks: BackgroundTasks):
    """
    Analyze code using GPT-4 with fixed parameters:
    - Model: GPT-4
    - Temperature: 0 (deterministic)
    - Seed: 0 (consistent)
    """
    try:
        logger.info(f"Received analysis request with question: {request.question}")
        logger.info(f"Using GPT config: {GPT_CONFIG}")
        
        if not request.analysis_data or not request.question:
            raise HTTPException(
                status_code=400,
                detail="Both analysis_data and question are required"
            )
            
        result = await analyze_with_gpt(request.analysis_data, request.question)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Add background task to clean up old responses if needed
        background_tasks.add_task(cleanup_old_responses)
            
        return result
        
    except HTTPException as he:
        logger.error(f"HTTP Exception: {str(he)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/batch", response_model=List[Dict[str, Any]])
async def batch_gpt_analyze(request: BatchGPTRequest):
    """
    Analyze multiple questions in parallel.
    
    Args:
        request (BatchGPTRequest): The request containing analysis_data and list of questions
    
    Returns:
        List[Dict[str, Any]]: List of analysis results with metadata
    """
    try:
        logger.info(f"Received batch analysis request with {len(request.questions)} questions")
        
        if not request.analysis_data or not request.questions:
            raise HTTPException(
                status_code=400,
                detail="Both analysis_data and questions are required"
            )
            
        results = await batch_analyze(request.analysis_data, request.questions)
        
        if any("error" in result for result in results):
            errors = [result["error"] for result in results if "error" in result]
            raise HTTPException(status_code=500, detail=str(errors))
            
        return results
        
    except HTTPException as he:
        logger.error(f"HTTP Exception: {str(he)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/responses/{date}")
async def get_responses_by_date(date: str):
    """
    Get all GPT responses for a specific date.
    
    Args:
        date (str): Date in YYYY-MM-DD format
    
    Returns:
        Dict containing date and list of responses
    """
    try:
        responses = storage.get_responses_by_date(date)
        return {"date": date, "responses": responses}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving responses: {str(e)}"
        )

@router.get("/response/{file_path:path}")
async def get_response_by_path(file_path: str):
    """
    Get a specific GPT response by its file path.
    
    Args:
        file_path (str): Path to the response file
    
    Returns:
        Dict containing the response data
    """
    try:
        response = storage.load_response(file_path)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Response not found: {str(e)}"
        )

async def cleanup_old_responses():
    """Background task to clean up old responses."""
    # Implement your cleanup logic here
    # For example, delete responses older than X days
    pass

