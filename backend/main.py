
# This is the most important file.
# It connects PDF extraction, Claude AI, scoring, S3 and DynamoDB.
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from decimal import Decimal
import logging
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile
)

from mangum import Mangum

from backend.config import MAX_PDF_BYTES, RESUME_BUCKET

from backend.models.schemas import AnalysisResult
from backend.services.pdf_service import extract_text_from_pdf
from backend.services.s3_service import upload_pdf, delete_pdf
from backend.services.claude_service import analyze_with_claude
from backend.services.matching_service import calculate_match_percentage

from backend.repositories.dynamodb_repository import (
    save_candidate,
    save_analysis,
    get_candidate,
    get_analysis,
    list_candidates,
    delete_candidate
)


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI Resume Analyzer API",
    version="1.0.0"
)


# Convert Python float values into Decimal.
# DynamoDB does not support Python float values.
# This function also handles nested dictionaries and lists.

def convert_floats_to_decimal(data):

    if isinstance(data, float):

        return Decimal(str(data))

    if isinstance(data, dict):

        return {
            key: convert_floats_to_decimal(value)
            for key, value in data.items()
        }

    if isinstance(data, list):

        return [
            convert_floats_to_decimal(item)
            for item in data
        ]

    if isinstance(data, tuple):

        return tuple(
            convert_floats_to_decimal(item)
            for item in data
        )

    return data


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post(
    "/resumes/analyze",
    response_model=AnalysisResult
)
async def upload_and_analyze_resume(

    resume: UploadFile = File(...),

    job_description: str = Form(..., min_length=30)

):

    if not RESUME_BUCKET:

        raise HTTPException(
            status_code=500,
            detail="S3 bucket is not configured."
        )

    if not resume.filename or not resume.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    if len(job_description.strip()) < 30:

        raise HTTPException(
            status_code=400,
            detail="Please provide a valid Job Description."
        )

    pdf_bytes = await resume.read()

    if not pdf_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty."
        )

    if len(pdf_bytes) > MAX_PDF_BYTES:

        raise HTTPException(
            status_code=413,
            detail="PDF exceeds the 5 MB limit."
        )

    if not pdf_bytes.startswith(b"%PDF-"):

        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )

    candidate_id = str(uuid4())

    analysis_id = str(uuid4())

    now = datetime.now(
        timezone.utc
    ).isoformat()

    object_key = (
        f"resumes/{candidate_id}/"
        f"{resume.filename.replace('/', '_')}"
    )

    try:

        # STEP 1: Upload PDF to S3

        upload_pdf(
            pdf_bytes,
            object_key
        )

        # STEP 2: Extract PDF text

        resume_text = extract_text_from_pdf(
            pdf_bytes
        )

        # STEP 3: Send Resume and JD to Claude

        ai_result = analyze_with_claude(
            resume_text,
            job_description.strip()
        )

        # STEP 4: Calculate matching percentage

        category_scores = ai_result[
            "category_scores"
        ]

        match_percentage = calculate_match_percentage(
            category_scores
        )

        candidate_data = ai_result[
            "candidate"
        ]

        # STEP 5: Prepare candidate data

        candidate_item = {

            "candidate_id": candidate_id,

            "candidate_name": str(
                candidate_data.get("name", "Unknown")
            )[:200],

            "email": str(
                candidate_data.get("email", "Unknown")
            )[:200],

            "phone": str(
                candidate_data.get("phone", "Unknown")
            )[:80],

            "location": str(
                candidate_data.get("location", "Unknown")
            )[:200],

            "years_experience": float(
                candidate_data.get(
                    "years_experience", 0
                ) or 0
            ),

            "skills": candidate_data.get(
                "skills", []
            )[:100],

            "extracted_resume": candidate_data,

            "resume_text": resume_text[:45000],

            "s3_key": object_key,

            "created_at": now

        }

        # STEP 6: Prepare analysis data

        analysis_item = {

            "analysis_id": analysis_id,

            "candidate_id": candidate_id,

            "candidate_name": candidate_item[
                "candidate_name"
            ],

            "job_description": job_description.strip()[:20000],

            "match_percentage": match_percentage,

            "category_scores": category_scores,

            "matched_skills": ai_result.get(
                "matched_skills", []
            )[:100],

            "missing_skills": ai_result.get(
                "missing_skills", []
            )[:100],

            "strengths": ai_result.get(
                "strengths", []
            )[:50],

            "improvement_suggestions": ai_result.get(
                "improvement_suggestions", []
            )[:50],

            "experience_match": ai_result.get(
                "experience_match", "Fair"
            ),

            "summary": ai_result.get(
                "summary", ""
            )[:4000],

            "created_at": now

        }

        # STEP 7: Save candidate in DynamoDB
        # Convert all float values to Decimal before saving.

        save_candidate(
            convert_floats_to_decimal(candidate_item)
        )

        # STEP 8: Save analysis in DynamoDB
        # Convert all float values to Decimal before saving.

        save_analysis(
            convert_floats_to_decimal(analysis_item)
        )

        # STEP 9: Return response

        return AnalysisResult(

            analysis_id=analysis_id,

            candidate_id=candidate_id,

            candidate_name=analysis_item[
                "candidate_name"
            ],

            match_percentage=match_percentage,

            category_scores=category_scores,

            matched_skills=analysis_item[
                "matched_skills"
            ],

            missing_skills=analysis_item[
                "missing_skills"
            ],

            strengths=analysis_item[
                "strengths"
            ],

            improvement_suggestions=analysis_item[
                "improvement_suggestions"
            ],

            experience_match=analysis_item[
                "experience_match"
            ],

            summary=analysis_item[
                "summary"
            ],

            extracted_resume=candidate_data,

            created_at=now

        )

    except HTTPException:

        raise

    except Exception as exc:

        logger.exception(
            "Resume analysis failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Resume analysis failed. Check CloudWatch logs."
        ) from exc


@app.get("/resumes")
def get_resumes(limit: int = 50):

    if limit < 1 or limit > 100:

        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100."
        )

    items = list_candidates(limit)

    return [

        {
            key: value
            for key, value in item.items()
            if key not in (
                "resume_text",
                "extracted_resume"
            )
        }

        for item in items

    ]


@app.get("/resumes/{candidate_id}")
def get_resume(candidate_id: str):

    item = get_candidate(
        candidate_id
    )

    if not item:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found."
        )

    item.pop(
        "resume_text",
        None
    )

    return item


@app.get("/analyses/{analysis_id}")
def get_analysis_result(analysis_id: str):

    item = get_analysis(
        analysis_id
    )

    if not item:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found."
        )

    return item


@app.delete("/resumes/{candidate_id}")
def remove_resume(candidate_id: str):

    item = get_candidate(
        candidate_id
    )

    if not item:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found."
        )

    s3_key = item.get(
        "s3_key"
    )

    if s3_key:

        delete_pdf(
            s3_key
        )

    delete_candidate(
        candidate_id
    )

    return {

        "message": "Candidate record and PDF deleted.",

        "candidate_id": candidate_id

    }


handler = Mangum(app)
# Serve frontend files through FastAPI.

# Frontend folder is at the project root
FRONTEND_DIR = BASE_DIR / "frontend"

if not FRONTEND_DIR.is_dir():
    raise RuntimeError(...)

app.mount(
    "/",
    StaticFiles(...),
    name="frontend"
)

# AWS Lambda handler (keep this AFTER mounting the frontend)
handler = Mangum(app)
