#This file defines the response structure.

from pydantic import BaseModel, Field
from typing import Any


class AnalysisResult(BaseModel):

    analysis_id: str

    candidate_id: str

    candidate_name: str

    match_percentage: float = Field(
        ge=0,
        le=100
    )

    category_scores: dict[str, float]

    matched_skills: list[str]

    missing_skills: list[str]

    strengths: list[str]

    improvement_suggestions: list[str]

    experience_match: str

    summary: str

    extracted_resume: dict[str, Any]

    created_at: str
