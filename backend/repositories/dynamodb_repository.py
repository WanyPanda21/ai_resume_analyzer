# This file handles saving and retrieving data from DynamoDB.
import boto3

from backend.config import (
    AWS_REGION,
    CANDIDATES_TABLE,
    ANALYSES_TABLE
)


dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

candidates_table = dynamodb.Table(
    CANDIDATES_TABLE
)

analyses_table = dynamodb.Table(
    ANALYSES_TABLE
)


def save_candidate(candidate_item: dict):

    candidates_table.put_item(
        Item=candidate_item
    )


def save_analysis(analysis_item: dict):

    analyses_table.put_item(
        Item=analysis_item
    )


def get_candidate(candidate_id: str):

    response = candidates_table.get_item(
        Key={
            "candidate_id": candidate_id
        }
    )

    return response.get("Item")


def get_analysis(analysis_id: str):

    response = analyses_table.get_item(
        Key={
            "analysis_id": analysis_id
        }
    )

    return response.get("Item")


def list_candidates(limit: int = 50):

    response = candidates_table.scan(
        Limit=limit
    )

    return response.get("Items", [])


def delete_candidate(candidate_id: str):

    candidates_table.delete_item(
        Key={
            "candidate_id": candidate_id
        }
    )
