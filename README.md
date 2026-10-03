# Faculty Leave AI

Web MVP for reading **faculty leave-form images** (or visually similar arrangement tables), extracting handwritten assignment rows, supporting human review, and generating grouped substitute-email drafts.

This is not a general-purpose document reader. Unrelated photos, arbitrary PDFs, and non-leave forms are out of scope.

## What it does

1. Upload a JPG/PNG leave form.
2. Normalize the page and locate the arrangement table (grid detection, then lower-page fallback).
3. Detect filled rows (line detection, then relative-layout fallback from the original template).
4. Run the existing TrOCR pipeline: class OCR, subject second pass, room parse, timetable ranking, staff matching.
5. Store every row for **mandatory human review**.
6. Generate grouped email previews after corrections. Mail is **not sent**.

## Project layout

- `backend/app/` — FastAPI, OCR pipeline, SQLite models
- `frontend/` — React (Vite) review desk
- `data/forms/<form-id>/` — per-form originals, table crops, row crops, OCR debug images
- `data/faculty_leave.db` — SQLite (created on first backend start)

## Requirements

- Python 3.10+
- Node.js 18+
- Optional GPU for faster TrOCR
- First real OCR run downloads `microsoft/trocr-base-handwritten`

If you do not want to install PyTorch yet, use **demo mode**. Demo mode still exercises upload, review, and grouped emails.

## Start (Windows)

From the repo root:

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install -r backend\requirements-dev.txt
```

If PyTorch is too heavy for a first run:

```powershell
$env:DEMO_MODE="1"
pip install fastapi uvicorn python-multipart sqlalchemy pydantic opencv-python-headless numpy pillow httpx pytest
```

Backend:

```powershell
.\scripts\start-backend.ps1
```

Frontend (second terminal):

```powershell
.\scripts\start-frontend.ps1
```

Open `http://localhost:5173`.

Manual commands:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --app-dir app --host 127.0.0.1 --port 8000
```

Wait: the backend must be started with `app` on `PYTHONPATH`. The startup script does this. Equivalent:

```powershell
cd backend\app
..\ .venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="app"
pytest tests -q
```

## Demo without OCR

On the Upload page, click **Run demo without an image**, or:

```http
POST /demo/run
{ "applicant_name": "Anand K. Patel", "year": 2026 }
```

Then open Review, save corrections, and generate grouped emails.

## Existing CLI OCR scripts

The original modules still run from `backend/app`, for example:

```powershell
cd backend\app
python multi_row_pipeline.py
python ocr_fields.py
```

They now write through repository-relative `paths.py`. Per-form web processing does not overwrite those CLI folders unless you still point at `data/crops`.

## API sketch

- `POST /upload` — multipart image + applicant name + year
- `POST /forms/{id}/process` — queue OCR
- `GET /forms/{id}/review` — assignment payload for the UI
- `PUT /forms/{id}/assignments/{row}` — save human corrections
- `POST /forms/{id}/emails` — grouped drafts
- `GET /master/staff|subjects|rooms|timetable`

## Limits

- Table/row detection is hybrid, not a generic layout model.
- TrOCR on handwriting remains noisy; review is required.
- Applicant name is entered at upload, not reliably OCR’d from the header.
- Emails are previews only.
- SQLite is local-demo storage, not a multi-user production database.
- The generated timetable is the existing demo generator, not an official college timetable import.
