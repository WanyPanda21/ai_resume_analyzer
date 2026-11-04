# This service uploads the PDF into S3.

import boto3

from backend.config import AWS_REGION, RESUME_BUCKET


s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)


def upload_pdf(
    pdf_bytes: bytes,
    object_key: str
):

    s3.put_object(

        Bucket=RESUME_BUCKET,

        Key=object_key,

        Body=pdf_bytes,

        ContentType="application/pdf",

        ServerSideEncryption="AES256"

    )


def delete_pdf(object_key: str):

    s3.delete_object(

        Bucket=RESUME_BUCKET,

        Key=object_key

    )
