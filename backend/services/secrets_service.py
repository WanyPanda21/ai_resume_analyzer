
# This service retrieves the Claude API key
# from AWS Secrets Manager.

import boto3

from functools import lru_cache
from botocore.exceptions import ClientError

from backend.config import (
    AWS_REGION,
    ANTHROPIC_SECRET_NAME
)


secrets_client = boto3.client(
    "secretsmanager",
    region_name=AWS_REGION
)


@lru_cache(maxsize=1)
def get_claude_api_key():

    try:

        response = secrets_client.get_secret_value(
            SecretId=ANTHROPIC_SECRET_NAME
        )

        api_key = response.get("SecretString")

        if not api_key:
            raise RuntimeError(
                "Claude API key is empty in Secrets Manager."
            )

        return api_key

    except ClientError as exc:

        raise RuntimeError(
            f"Unable to retrieve Claude API key: {exc}"
        ) from exc
