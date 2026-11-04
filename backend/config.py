#This file contains AWS configuration and environment variables.

import os

AWS_REGION = os.getenv(
    "AWS_REGION",
    os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2")
)

CANDIDATES_TABLE = os.getenv(
    "CANDIDATES_TABLE",
    "ResumeCandidates"
)

ANALYSES_TABLE = os.getenv(
    "ANALYSES_TABLE",
    "ResumeAnalyses"
)

RESUME_BUCKET = os.getenv("RESUME_BUCKET", "")

BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "apac.anthropic.claude-3-5-sonnet-20241022-v2:0"
)

MAX_PDF_BYTES = int(
    os.getenv("MAX_PDF_BYTES", "5242880")
)
