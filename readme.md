# 🧾 Receipt Tracker

> **Work in progress** — core pipeline is functional but actively being improved.

An AI-powered expense tracking app that extracts structured data from receipt photos and PDFs using a locally-run, fine-tuned vision-language model. Upload a receipt → get company, date, address, and total automatically.

---

## What it does

- Upload a receipt (JPG, PNG, or PDF) via a drag-and-drop UI
- The backend preprocesses the image (contrast enhancement, contour cropping) using OpenCV
- A fine-tuned **Qwen2-VL-2B** vision model extracts structured fields from the receipt
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
| OCR / ML | Qwen2-VL-2B (llama.cpp / GGUF) |

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

The OCR pipeline has transitioned to **Qwen2-VL-2B** for production due to superior accuracy and reliability.
- **Model**: Qwen2-VL-2B-Instruct — a 2B parameter vision-language model
- **Training Data**: Fine-tuned on 950 receipts using the [Receipt Dataset SSD300 v2](https://www.kaggle.com/datasets/dhiaznaidi/receiptdatasetssd300v2) from Kaggle.
- **Inference**: Run locally using `llama.cpp` and GGUF format for optimized execution.
- **Model finetuned huggiging face link**: https://huggingface.co/gueye07/Qwen-Receipt-FineTuned
- **Decision**: Selected over SmolVLM-256M due to a significantly higher F1 score (0.97 vs 0.61) and robust performance on unseen layouts.

---

## Model Comparison & Analysis: Qwen2-VL vs. SmolVLM

This analysis compares the raw accuracy metrics in a Cloud environment (Colab) before and after fine-tuning, highlighting the impact of training on models specialized for document extraction.

### Cloud Training Analysis (Colab)

#### 1. SmolVLM-256M: From Zero to Functional
- **Before Fine-Tuning:** The model was completely incapable of performing the task. A JSON failure rate of 1 (100%) and an F1 score of 0 indicate it could not follow instructions or output the required format. Its CER of 2.99 shows it was essentially generating gibberish.
- **After Fine-Tuning:** The improvement is massive. It reached a 0.61 F1 score, proving it learned both the JSON schema and the OCR task. The dramatic drop in CER (to 0.54) shows it became much more faithful to the actual text on the receipts.
- **The Limit:** Despite the progress, a 0.5 Precision confirms that while it "finds" data (High Recall), it often hallucinates or mislabels it on unseen layouts.

#### 2. Qwen2-VL-2B: Refinement to Industrial Standards
- **Before Fine-Tuning:** The model was already quite capable (0.86 F1), showing that its large-scale pre-training gave it a strong baseline for document understanding.
- **After Fine-Tuning:** It reached near-perfection with a 0.97 F1 score. It misses almost no fields (1.0 Recall) and makes very few classification errors.
- **The CER Paradox:** Interestingly, Qwen's CER (1.04) is higher than SmolVLM's (0.54) after fine-tuning. This suggests that while Qwen is better at finding the right data, it might include extra spaces, punctuation, or formatting noise that technically increases the character error rate without affecting the data's utility.

#### Comparison Summary
| Model | Stage | Reliability (F1) | Format (JSON Failure) | Accuracy (CER) |
|---|---|---|---|---|
| SmolVLM | Pre-FT | ❌ 0% | ❌ 100% | ❌ 2.99 |
| SmolVLM | Post-FT | ⚠️ 61% | ✅ 0% | ✅ 0.54 |
| Qwen2-VL | Pre-FT | ✅ 86% | ✅ 0% | ⚠️ 1.15 |
| Qwen2-VL | Post-FT | 🎯 97% | ✅ 0% | ⚠️ 1.04 |

**Key Insight:** Fine-tuning turned SmolVLM from a "broken" model into a "lightweight assistant," but it turned Qwen2-VL from a "smart generalist" into a "precise specialist." Even though Qwen takes longer to run locally, the accuracy gap (0.61 vs 0.97 F1) is too large to ignore for production.

### Local Inference Comparative Analysis (llama.cpp)

After testing 5 unseen receipt images in a local environment using GGUF format, the results highlight a clear trade-off between speed and reliability.

#### 1. Performance and Accuracy
- **Qwen2-VL-2B-Instruct:** Demonstrated high reliability. The model correctly extracted all fields into valid JSON formats. Human verification confirmed that the extracted values were accurate, maintaining the high performance seen during the fine-tuning phase even on unseen layouts.
- **SmolVLM-256M:** While it successfully produced valid JSON, the data integrity was poor. Key issues included:
  - **Logic Errors:** Hallucinating values (e.g., using a time/hour in the "Total" field or picking the price of the first item instead of the final sum).
  - **Formatting Issues:** Words were often "shrunk," disordered, or dropped entirely.
  - **Repetition:** The model struggled with successive identical words, often deleting them.

#### 2. Efficiency and Latency
- **Qwen2-VL-2B:**
  - Visual Analysis (Average): 2.84 minutes.
  - Response Generation (Average): 6.87 seconds.
  - *Observation:* The model is extremely heavy on the pre-processing/analysis phase, leading to a slow user experience.
- **SmolVLM-256M:**
  - Visual Analysis (Average): 2.64 seconds.
  - Response Generation (Average): 1.58 seconds.
  - *Observation:* It is exceptionally fast, offering near-instant results.

#### 3. Conclusion and Production Recommendation
A positive technical note for both models is that `truncated = 0` across all tests. This confirms that the entire image and context fit within the allocated memory, ensuring no data was lost due to buffer limits.

However, despite the impressive speed of SmolVLM, it fails the "reliability test" required for document extraction. In a production environment, data accuracy is paramount. Errors in "Total" amounts or "Company names" are critical failures for financial processing.

**Final Decision:** Qwen2-VL-2B is the superior choice for production. While the processing time (latency) is significantly longer, the necessity of having reliable, human-verified data outweighs the benefits of a faster but inaccurate response.

---

## Known limitations / in progress

- [ ] Processing time is long due to Qwen2-VL-2B's visual analysis phase (~2.8 minutes per receipt)
- [ ] CPU inference is very slow (2–8 min per receipt) — GPU recommended
- [ ] No authentication or multi-user support yet
- [ ] No ability to edit / correct extracted fields from the UI
- [ ] Chart grouping by week/month needs more receipt data to be meaningful
- [ ] PDF support extracts only the first page

---


