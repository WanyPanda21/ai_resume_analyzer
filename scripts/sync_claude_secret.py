# The script never prints the actual API key. AWS supports creating and updating secret values through these SDK operations.
# This script automatically creates or updates
# the Claude API key in AWS Secrets Manager.

import os
import sys
import boto3

from botocore.exceptions import ClientError


AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-southeast-2"
)

SECRET_NAME = os.getenv(
    "ANTHROPIC_SECRET_NAME",
    "ai-resume-analyzer/anthropic-api-key"
)

ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY"
)


def sync_claude_secret():

    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is missing from GitHub Actions secrets."
        )

    client = boto3.client(
        "secretsmanager",
        region_name=AWS_REGION
    )

    try:

        # Check whether the secret already exists.
        client.describe_secret(
            SecretId=SECRET_NAME
        )

        # Update existing secret.
        client.put_secret_value(
            SecretId=SECRET_NAME,
            SecretString=ANTHROPIC_API_KEY
        )

        print("Claude API secret updated successfully.")

    except client.exceptions.ResourceNotFoundException:

        # Create a new secret.
        client.create_secret(
            Name=SECRET_NAME,
            Description="Anthropic Claude API key for AI Resume Analyzer",
            SecretString=ANTHROPIC_API_KEY
        )

        print("Claude API secret created successfully.")


if __name__ == "__main__":

    try:
        sync_claude_secret()

    except Exception as exc:
        print(f"Secret synchronization failed: {exc}")
        sys.exit(1)
