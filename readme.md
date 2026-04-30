# 🧾 Receipt Tracker

> **Work in progress** — core pipeline is functional but actively being improved.

An AI-powered expense tracking app that extracts structured data from receipt photos and PDFs using a locally-run, fine-tuned vision-language model. Upload a receipt → get company, date, address, and total automatically.

---

## What it does

- Upload a receipt (JPG, PNG, or PDF) via a drag-and-drop UI
- The backend preprocesses the image (contrast enhancement, contour cropping) using OpenCV
- A fine-tuned **SmolVLM-256M** vision model extracts structured fields from the receipt
- Extracted data is stored in a local SQLite database
- The dashboard displays expense history with an interactive chart, a receipt list, and an average OCR confidence score
- Processing is queued asynchronously and results are pushed to the frontend over **WebSocket**

---

## Tech stack

### Backend
| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| Database | SQLite via SQLAlchemy |
| Image preprocessing | OpenCV, Pillow |
| PDF support | PyMuPDF (fitz) |
| OCR / ML | SmolVLM-256M (HuggingFace Transformers) |
| Model adapter | PEFT / LoRA (`gueye07/SmolVLM-256M-Instruct-FineTuned-Receipt-peft-model`) |
| Real-time push | WebSocket |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 19 + Vite + TypeScript |
| Styling | Tailwind CSS v4 |
| Components | shadcn/ui, Radix UI |
| Charts | Recharts |
| File upload | react-dropzone |
| Icons | lucide-react |

---

## Project structure

```
receipt-tracker/
├── backend/
│   ├── api/
│   │   └── receipts.py        # Upload & list endpoints, async queue
│   ├── core/
│   │   ├── database.py        # SQLite init, save & query helpers
│   │   └── websocket.py       # WebSocket manager + queue worker
│   ├── models/
│   │   └── receipt.py         # Pydantic response model
│   ├── services/
│   │   ├── ocr.py             # Model loading + inference (PEFT + generate)
│   │   ├── image_processing.py # OpenCV preprocessing pipeline
│   │   └── json_format.py     # JSON repair, normalize, extract helpers
│   ├── main.py                # FastAPI app, CORS, WebSocket route
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── FileUpload.tsx
│       │   ├── ReceiptTable.tsx
│       │   ├── ExpenseChart.tsx
│       │   ├── TimeGranularityToggle.tsx
│       │   └── ConfidenceBadge.tsx
│       ├── lib/
│       │   └── api.ts         # Typed fetch helpers
│       └── App.tsx
├── data/
│   └── receipts/              # Uploaded files (git-ignored)
├── receipts.db                # SQLite database (git-ignored)
└── package.json               # Monorepo scripts (pnpm)
```

---

## Getting started

### Prerequisites
- Python 3.10+
- Node.js 18+ and pnpm
- A CUDA GPU is **strongly recommended** for reasonable OCR speed (CPU inference takes several minutes per receipt)

### 1 — Clone and install

```bash
git clone <repo-url>
cd receipt-tracker

# Python virtualenv
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r backend/requirements.txt
pip install peft opencv-python

# Frontend
pnpm install
```

### 2 — Run the backend

```bash
pnpm backend
# or: uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 3 — Run the frontend

```bash
pnpm frontend
# or: cd frontend && pnpm dev
```

The app will be available at `http://localhost:3000`.

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/uploadReceipt` | Upload a receipt file (multipart) |
| `GET` | `/api/receipts` | List all stored receipts |
| `WS` | `/ws` | WebSocket for real-time processing updates |
| `GET` | `/health` | Health check |

---

## Model details

The OCR pipeline uses:
- **Base model**: [`HuggingFaceTB/SmolVLM-256M-Instruct`](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) — a 256M parameter vision-language model
- **Fine-tuned adapter**: [`gueye07/SmolVLM-256M-Instruct-FineTuned-Receipt-peft-model`](https://huggingface.co/gueye07/SmolVLM-256M-Instruct-FineTuned-Receipt-peft-model) — LoRA adapter trained on receipt data
- On **CUDA**: loaded in 4-bit (NF4) via BitsAndBytes for low VRAM usage
- On **CPU**: loaded in bfloat16 (no quantization — inference will be slow)

---

## Known limitations / in progress

- [ ] OCR accuracy is still being tuned — the model sometimes hallucinates field values on unseen receipt layouts
- [ ] CPU inference is very slow (2–8 min per receipt) — GPU recommended
- [ ] No authentication or multi-user support yet
- [ ] No ability to edit / correct extracted fields from the UI
- [ ] Chart grouping by week/month needs more receipt data to be meaningful
- [ ] PDF support extracts only the first page

---

## License

MIT
