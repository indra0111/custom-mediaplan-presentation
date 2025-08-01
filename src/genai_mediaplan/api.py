from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from genai_mediaplan.crew import GenaiMediaplan
from genai_mediaplan.utils.helper import extract_json_from_markdown_or_json, get_audience_data
from genai_mediaplan.utils.update_google_slides_content import get_copy_of_presentation

# Load environment variables
load_dotenv(override=True)

app = FastAPI(
    title="GenAI Mediaplan API",
    description="API for running CrewAI mediaplan generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify exact domains like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Or ["POST", "GET", "OPTIONS"]
    allow_headers=["*"],  # Or specific headers like ["Content-Type", "Authorization"]
)

# Pydantic models for request/response
class EmailRequest(BaseModel):
    email_subject: str
    email_body: str
    email_attachments: Optional[List[str]] = None
    abvrs: Optional[str] = None
    forecast_data: Optional[Dict[str, Any]] = None

class EmailResponse(BaseModel):
    status: str
    message: str
    google_slides_url: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str

# Global variable to store task status
task_status = {}

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.post("/generate-presentation-from-email", response_model=EmailResponse)
async def generate_presentation_from_email(request: EmailRequest):
    """
    Generate a presentation from email content.
    
    This endpoint will:
    1. Process the email subject and body
    2. Run the CrewAI agents to generate insights
    3. Create a Google Slides presentation
    4. Return the presentation URL
    """
    try:
        email_body = request.email_body
        if request.email_attachments:
            email_body += "\n\nAdditional attachments:"
            for attachment in request.email_attachments:
                email_body += attachment
        
        audience_data = get_audience_data(request.abvrs)
        # Prepare inputs for CrewAI
        inputs = {
            'email_subject': request.email_subject,
            'email_body': email_body,
            'audience_data': audience_data
        }
        
        # Run CrewAI
        crew = GenaiMediaplan().crew()
        result = crew.kickoff(inputs=inputs)
        
        # Extract JSON from the generated report
        model_output_json = extract_json_from_markdown_or_json("final_report.md")
        
        title = model_output_json.get("title", "")
        # Create Google Slides presentation
        google_slides_url = get_copy_of_presentation(
            title, 
            model_output_json, 
            request.forecast_data
        )
        
        return EmailResponse(
            status="success",
            message=f"Presentation generated successfully",
            google_slides_url=google_slides_url
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating presentation: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 