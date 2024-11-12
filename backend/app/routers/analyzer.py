# app/routers/analyzer.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.code_analyzer import analyze_code
import traceback

router = APIRouter(prefix="/analyze", tags=["analyzer"])

@router.post("/")
async def analyze(app_file: UploadFile = File(...), api_file: UploadFile = File(...)):
    try:
        app_code = (await app_file.read()).decode('utf-8')
        api_code = (await api_file.read()).decode('utf-8')

        analysis_result = analyze_code(app_code, api_code)
        return analysis_result
    except Exception as e:
        traceback.print_exc()  # Prints the stack trace to the console
        raise HTTPException(status_code=500, detail=str(e))
