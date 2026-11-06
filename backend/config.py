
# This file contains AWS configuration and environment variables.

import os


AWS_REGION = os.getenv(
    "AWS_REGION",
    os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2")
)


CANDIDATES_TABLE = os.getenv(
    "CANDIDATES_TABLE",
    "CandidatesTable"
)


ANALYSES_TABLE = os.getenv(
    "ANALYSES_TABLE",
    "AnalysesTable"
)


RESUME_BUCKET = os.getenv(
    "RESUME_BUCKET",
    "ai-resume-analyzer-897545289521-ap-southeast-2"
)


# Anthropic Claude configuration.
# The actual API key is retrieved from Secrets Manager.

ANTHROPIC_SECRET_NAME = os.getenv(
    "ANTHROPIC_SECRET_NAME",
    "ai-resume-analyzer/anthropic-api-key"
)


CLAUDE_MODEL = os.getenv(
    "CLAUDE_MODEL",
    "claude-sonnet-5"
)


MAX_PDF_BYTES = int(
    os.getenv("MAX_PDF_BYTES", "5242880")
)
