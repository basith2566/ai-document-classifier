# DocuSort – AI-Based Document Classification System

Upload PDF, DOCX or TXT files and the system extracts their text and predicts the document type
(Resume, Invoice, Research Paper, Legal Document, Email, Report, Other) using a **TF-IDF + Logistic
Regression** model trained with scikit-learn. Every prediction comes from real model inference.
When the model is not confident, the app shows **"Needs Manual Review"** instead of a shaky guess.

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, Recharts |
| Backend | Python, FastAPI |
| ML | scikit-learn (TF-IDF + Logistic Regression), Joblib |
| Documents | PyMuPDF (PDF), python-docx (DOCX), built-in decoding (TXT) |
| Database | SQLite (Python `sqlite3`) |

## Features
- Multi-file drag-and-drop upload with progress, per-file success/error results
- Automatic text extraction and preprocessing
- Predicted category, confidence, score for every category, extracted-text preview
- Low confidence or very short text -> "Needs Manual Review"
- Dashboard: totals, category distribution, activity chart, recent documents, model evaluation numbers
- History: search (name, category, text), filter by category, pagination, delete
- Handles unsupported types, empty files, oversized files, corrupted/password-protected PDFs, scanned PDFs with no text

## Project structure
```
ai-document-classifier/
├── backend/
│   ├── main.py                 # FastAPI app, CORS, startup (DB + model load)
│   ├── routes/                 # HTTP endpoints (documents.py, stats.py)
│   ├── services/               # extraction, classification, document + stats logic
│   ├── models/schemas.py       # API response models
│   ├── database/db.py          # SQLite schema + connection helper
│   ├── ml/                     # preprocess.py, train.py, classifier.py, artifacts/ (model.joblib, metrics.json)
│   ├── utils/                  # config (env vars), file helpers
│   ├── dataset/                # training_data.csv + generate_training_data.py  (data, kept separate from code)
│   ├── tests/test_core.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # React app (pages/, components/, api/client.js)
├── sample_documents/           # files for manual testing
└── render.yaml                 # backend deployment blueprint
```

### How a request flows
```
Browser --upload--> routes/documents.py --> document_service.process_upload()
   validate file -> extraction_service (PDF/DOCX/TXT -> text)
   -> classification_service (ml/classifier.py: TF-IDF + LogReg predict_proba)
   -> confidence check -> save to SQLite -> JSON response -> React UI
```

## Run locally

Requirements: Python 3.11+ and Node 18+.

**1. Backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
python -m ml.train                 # trains the model (a few seconds); re-run any time
uvicorn main:app --reload          # http://127.0.0.1:8000  (API docs at /docs)
```

**2. Frontend** (new terminal)
```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```
In development, Vite forwards `/api` to the backend, so no URL configuration is needed.

**3. Try it:** open http://localhost:5173/upload and drop in files from `sample_documents/`
(see `sample_documents/README.txt` for what to expect).

**4. Tests**
```bash
cd backend
python -m unittest discover -s tests -t .
```

## The model, explained
1. **Data** – `backend/dataset/training_data.csv` has two columns: `text`, `label`.
2. **Preprocessing** (`ml/preprocess.py`) – lowercase; URLs, emails and numbers become tokens; punctuation removed. The same function is used in training and prediction.
3. **Features** – TF-IDF over 1- and 2-word phrases, English stop words removed. TF-IDF scores words that are frequent in a document but rare overall, which is exactly what distinguishes e.g. "invoice", "subtotal", "due date".
4. **Classifier** – Logistic Regression, which outputs a probability for each category. The highest probability is the **confidence**.
5. **Evaluation** (`ml/train.py`) – stratified 80/20 train/test split, plus 5-fold cross-validation on the training part. It prints and saves accuracy, per-class precision/recall/F1 and a confusion matrix to `ml/artifacts/metrics.json`. Exact duplicates are removed first so test documents never appear in training.
6. **Saved with Joblib** – `ml/artifacts/model.joblib` is loaded once when the API starts.
7. **Manual review rule** – if confidence is below `CONFIDENCE_THRESHOLD` (default 0.45) or the document has fewer than 15 words, the UI shows "Needs Manual Review" and the closest match.

### Add a new category and retrain
1. Add at least ~30 rows to `training_data.csv` with the new name in the `label` column (use real examples if you can).
2. Run `python -m ml.train` in `backend/`.
3. Restart the API. The new category appears in results, filters and charts automatically. No code changes.

To use your own data, replace the CSV with your own labelled documents (`--data other.csv` also works).

### Honest notes about accuracy
- The starter dataset is **synthetic** (generated from templates by `dataset/generate_training_data.py`). It scores ~100% on its own test split because the test documents resemble the training ones. **That number does not predict real-world accuracy.** The dashboard says this too.
- As a more realistic check, the files in `sample_documents/` were written by hand separately from the training data. In development, all seven categories were classified correctly, but several with only moderate confidence (about 62-63% for the resume, report and research paper).
- Very short texts can still get overconfident predictions (a 22-word note was labelled "Email" at 70% in testing). The minimum-word rule only catches extremely short documents.
- For a trustworthy system, train on real labelled documents and tune `CONFIDENCE_THRESHOLD` using a validation set.
- Scanned (image-only) PDFs contain no text; OCR is not included.

## API reference
Base path `/api`. Interactive docs are at `/docs`.

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Status and whether the model is loaded |
| POST | `/api/documents/upload` | Multipart field `files` (one or many). Returns a result or error per file |
| GET | `/api/documents` | Query: `search`, `category`, `page`, `page_size` |
| GET | `/api/documents/{id}` | Full details including extracted text |
| DELETE | `/api/documents/{id}` | Delete a record |
| GET | `/api/stats` | Dashboard numbers |
| GET | `/api/model` | Categories, threshold, evaluation metrics |

## Configuration

**Backend** (`backend/.env`, see `.env.example`)

| Variable | Default | Purpose |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated frontend URLs allowed to call the API |
| `DATABASE_PATH` | `backend/data/documents.db` | SQLite file location |
| `CONFIDENCE_THRESHOLD` | `0.45` | Below this -> Needs Manual Review |
| `MAX_UPLOAD_MB` | `10` | Per-file size limit |
| `MAX_FILES_PER_REQUEST` | `20` | Files per upload |

**Frontend** – `VITE_API_URL` (production only): the backend's public URL.

No API keys or secrets are used. `.env` files are git-ignored.

## Deployment

### 1. Push to GitHub
Push the whole `ai-document-classifier` folder as one repository.

### 2. Backend on Render
1. Render dashboard -> **New + -> Blueprint** -> select the repository (it reads `render.yaml`).
   *Or create a Web Service manually:* Root Directory `backend`, Build `pip install -r requirements.txt && python -m ml.train`, Start `uvicorn main:app --host 0.0.0.0 --port $PORT`, Health Check `/api/health`.
2. **Persistent storage:** the blueprint attaches a 1 GB disk at `/var/data` and sets `DATABASE_PATH=/var/data/documents.db`. Render disks need a paid instance (Starter). On the free plan, remove the `disk:` block; the app still works but history resets on each restart or redeploy.
3. After the first deploy note the URL, e.g. `https://doc-classifier-api.onrender.com`. Check `/api/health` returns `"model_ready": true`.
4. You will set `CORS_ORIGINS` in step 4 below.

### 3. Frontend on Vercel
1. Vercel -> **Add New Project** -> import the repository.
2. **Root Directory:** `frontend` (framework: Vite is detected; build `npm run build`, output `dist`).
3. **Environment Variable:** `VITE_API_URL` = your Render URL (no trailing slash).
4. Deploy. `vercel.json` makes page refreshes on `/history` etc. work.

### 4. Connect them
In Render -> your service -> Environment, set `CORS_ORIGINS` to your Vercel URL (e.g. `https://your-app.vercel.app`; separate several with commas) and save; the service restarts. If you change `VITE_API_URL` later, redeploy the frontend, because Vite bakes it in at build time.

### Notes
- Render's free/starter web services may cold-start after idling; the first request can be slow.
- SQLite suits a single instance. For multiple instances or heavy use, switch to PostgreSQL.

## Troubleshooting
| Symptom | Fix |
|---|---|
| Upload says "model is not available" | Run `python -m ml.train` in `backend/`, then restart the API |
| "Could not load model" in logs | scikit-learn version differs from the one that saved the model; re-run `python -m ml.train` |
| Browser shows a CORS error | Add the exact frontend URL to `CORS_ORIGINS` (no trailing slash) |
| Frontend shows "API URL is not configured" | Set `VITE_API_URL` in Vercel and redeploy |
| "No readable text found" | The PDF is a scan/image. Use a text-based PDF |

## Ideas for next steps
OCR for scanned files, user accounts, PostgreSQL, a labelled-data upload page that retrains the model, calibrating probabilities.
