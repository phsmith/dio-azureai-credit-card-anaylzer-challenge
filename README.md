# dio-azureai-credit-card-anaylzer-challenge

A small FastAPI service that accepts an uploaded image of a credit card, sends it to Azure Document Intelligence's prebuilt credit card model, and returns structured card data (cardholder, card number, expiration, issuing bank).

## Project overview

- Framework: FastAPI
- ASGI server: Uvicorn (run via `app.py`)
- Purpose: Accept image uploads, run Azure Document Intelligence `prebuilt-creditCard` analysis, and return structured fields

## Repository structure

- `app.py` — local entrypoint that runs Uvicorn: `app.api.main:app`
- `app/api/main.py` — FastAPI application, endpoints and request lifecycle
- `app/services/file_upload.py` — streaming file upload handler (writes to a temporary directory, enforces chunking and max size)
- `app/services/azure/document_intelligence.py` — wrapper client to call Azure Document Intelligence `prebuilt-creditCard`
- `app/utils/config.py` — environment-driven configuration (API keys, endpoints, file limits, temp dir)
- `requirements.txt` — Python dependencies

## Quick start

1. Create a virtual environment and activate it (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root (or export env vars) with these values:

```env
AZUREAI_DOCUMENTINTELLIGENCE_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
AZUREAI_DOCUMENTINTELLIGENCE_API_KEY=<your-key>
```

4. Run the app:

```bash
python app.py
```

The service will be available at http://0.0.0.0:8000 by default.

## Configuration

Configuration lives in `app/utils/config.py` and is loaded from environment variables via `dotenv`:

- `AZUREAI_DOCUMENTINTELLIGENCE_ENDPOINT` — Azure Document Intelligence endpoint
- `AZUREAI_DOCUMENTINTELLIGENCE_API_KEY` — API key for Document Intelligence
- `FILE_CHUNK_SIZE` — chunk size used to stream uploads (default 1 MB)
- `FILE_MAX_UPLOAD_SIZE` — maximum accepted upload size (default 5 MB)

Notes:
- Uploaded files are temporarily stored in a temporary directory (`tempfile.TemporaryDirectory()`), and the files are removed after processing.

## API

Base URL: `/` (root)

1) GET `/`

- Returns a small health/status object and the configured max upload size (in bytes).

Response example:

```json
{ "status": "ok", "max_upload_size_bytes": 5242880 }
```

2) POST `/credit_card_info`

- Accepts a single file field named `file` (multipart/form-data). The API expects an image containing a credit card.
- The endpoint streams the uploaded file to disk in `FILE_CHUNK_SIZE` chunks and enforces `FILE_MAX_UPLOAD_SIZE` (5 MB by default). If a file exceeds the limit, the server responds with HTTP 413.

Request (curl example):

```bash
curl -X POST "http://127.0.0.1:8000/credit_card_info" \
	-H "Content-Type: multipart/form-data" \
	-F "file=@/path/to/card-image.jpg"
```

Successful response example:

```json
{
	"card_holder_name": "JOHN DOE",
	"card_number": "4111111111111111",
	"expiriration_date": "12/2027",
	"bank_issuer": "EXAMPLE BANK"
}
```

Error response example (no fields detected):

```json
{ "error": "The uploaded file is not a valid credit card image." }
```

If something goes wrong during processing an `error` key with details is returned.

## Implementation notes

- The app calls Azure's Document Intelligence client (see `app/services/azure/document_intelligence.py`). It uses the `prebuilt-creditCard` built-in model.
- The client is created at import time with `DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))`.
- The endpoint function `analyze_credit_card(file_path)` opens the file and calls the long-running operation `begin_analyze_document(...).result()` synchronously.
- The upload logic in `app/services/file_upload.py` streams to disk and raises a `HTTPException(status_code=413)` if the file exceeds `FILE_MAX_UPLOAD_SIZE`.

## Security and privacy

- Store Azure keys securely and do not commit `.env` files into source control. Use environment variables or a secrets manager in production.
- The app writes temporary files to a temp directory and removes them after processing; still consider encrypting or securing disk access on shared hosts.

## Troubleshooting

- If you see authentication errors from Azure, verify `AZUREAI_DOCUMENTINTELLIGENCE_ENDPOINT` and `AZUREAI_DOCUMENTINTELLIGENCE_API_KEY` values.
- If uploads fail with 413, resize the image or increase `FILE_MAX_UPLOAD_SIZE` in `app/utils/config.py` (also update any hosting limits).
- If the model returns empty `documents[0].fields`, the image may not contain a readable card or may be low-quality; try higher-resolution images.

## Next steps / Improvements

- Add unit tests and integration tests that mock Azure responses.
- Add OpenAPI examples and better response schemas (use Pydantic models for the response).
- Add request authentication (API key or OAuth) for production.
