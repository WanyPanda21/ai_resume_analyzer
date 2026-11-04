
# AI Resume Analyzer

AI Resume Analyzer using FastAPI, Claude AI through Amazon Bedrock,
AWS Lambda, API Gateway, S3 and DynamoDB.

## Features

- PDF resume upload
- PDF text extraction
- Resume information extraction using Claude
- Job Description comparison
- Matching percentage calculation
- Matched and missing skills
- Candidate data stored in DynamoDB
- PDF stored in S3
- REST APIs to retrieve candidate and analysis information
- AWS SAM deployment
- GitHub Actions CI/CD

## API Endpoints

| Method | Endpoint |
|---|---|
| POST | /resumes/analyze |
| GET | /resumes |
| GET | /resumes/{candidate_id} |
| GET | /analyses/{analysis_id} |
| DELETE | /resumes/{candidate_id} |
| GET | /health |

## Local Setup

```powershell
cd backend

python -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn main:app --reload
```

Open Swagger UI:

http://127.0.0.1:8000/docs

## AWS Deployment

From the project root:

```powershell
sam build

sam deploy --guided
```

AWS credentials must be configured.
Bedrock model access must be enabled in the selected region.
