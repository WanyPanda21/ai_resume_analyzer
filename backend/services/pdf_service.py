#This service extracts text from the uploaded PDF.

import fitz

from fastapi import HTTPException


def extract_text_from_pdf(pdf_bytes: bytes) -> str:

    try:

        with fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as document:

            if document.is_encrypted:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported."
                )

            text = "\n".join(
                page.get_text("text")
                for page in document
            )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail="Could not read the PDF file."
        ) from exc

    text = text.strip()

    if not text:

        raise HTTPException(
            status_code=422,
            detail="No selectable text found in PDF. Scanned PDF OCR is not supported yet."
        )

    return text
