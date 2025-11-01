# API

This file documents the public endpoints exposed by the FastAPI service in this repo.

## GET /

- Purpose: Basic health/status check
- Response: JSON object with service status and configured max upload size (bytes)

Example response:

```json
{
  "status": "ok",
  "max_upload_size_bytes": 5242880
}
```

## POST /credit_card_info

- Purpose: Accepts a single file upload (multipart/form-data) containing an image of a credit card. The endpoint runs Azure Document Intelligence `prebuilt-creditCard` on the uploaded image and returns recognized fields.
- Form field: `file` — the image file to analyze
- Max upload size: 5 MB (FILE_MAX_UPLOAD_SIZE)

Request (curl):

```bash
curl -X POST "http://127.0.0.1:8000/credit_card_info" \
  -F "file=@/path/to/card-image.jpg"
```

Success response (example):

```json
{
  "card_holder_name": "JOHN DOE",
  "card_number": "4111111111111111",
  "expiriration_date": "12/2027",
  "bank_issuer": "EXAMPLE BANK"
}
```

Error responses:

- 413 Payload Too Large — file exceeds `FILE_MAX_UPLOAD_SIZE` (raised during streaming upload)
- 200 with `{ "error": "..." }` — when Azure returns no fields or when processing fails (the endpoint catches exceptions and returns an `error` key)

Notes and implementation hints

- The service writes the uploaded file to a temporary directory and then calls `app.services.azure.document_intelligence.analyze_credit_card(file_path)` which calls Azure Document Intelligence.
- The Azure client is created at module import time. In tests, mock `DocumentIntelligenceClient` or patch `analyze_credit_card`.

This file is a companion to the README and intended to be machine-consumable by developers testing or integrating with the service.
