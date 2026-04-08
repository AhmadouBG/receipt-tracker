import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..core.database import init_db, save_receipt_record
from ..models.receipt import ReceiptResponse
from ..services.ocr import ocr_receipt
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "data/receipts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()

@router.post("/receipts", response_model=ReceiptResponse)
async def upload_receipt(file: UploadFile = File(...)):
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Format non supporté.")

    receipt_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1]
    filename = f"{receipt_id}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        abs_path = os.path.abspath(file_path)
        ocr_result = ocr_receipt(abs_path)

        if ocr_result:
            save_receipt_record(receipt_id, filename, ocr_result)
            return ReceiptResponse(
                receipt_id=receipt_id,
                status="parsed",
                filename=filename,
                datetime=datetime.now(),
                company=ocr_result.get("company"),
                date=ocr_result.get("date"),
                total=ocr_result.get("total"),
                address=ocr_result.get("address"),
                confidence=ocr_result.get("confidence"),
            )
        else:
            save_receipt_record(receipt_id, filename)
            return ReceiptResponse(
                receipt_id=receipt_id, status="failed", filename=filename, datetime=datetime.now()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
