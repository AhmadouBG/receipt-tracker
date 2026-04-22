import os
import uuid
import fitz
import base64
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..core.database import init_db, save_receipt_record, get_all_receipts
from ..core.websocket import manager
from ..models.receipt import ReceiptResponse
from ..services.ocr import ocr_receipt
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "data/receipts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()

SUPPORTED_TYPES = ["image/png", "image/jpeg", "image/jpg", "application/pdf"]

def convert_pdf_to_image(pdf_path: str, output_dir: str) -> str:
    doc = fitz.open(pdf_path)
    page = doc[0]
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)
    output_path = os.path.join(
        output_dir, os.path.basename(pdf_path).replace(".pdf", ".jpg")
    )
    pix.save(output_path)
    doc.close()
    return output_path

@router.post("/uploadReceipt")
async def upload_receipt(file: UploadFile = File(...)):
    # Case-insensitive extension check
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    
    # Validation based on content_type OR extension
    is_valid = (file.content_type in SUPPORTED_TYPES) or (ext in ["png", "jpg", "jpeg", "pdf"])
    
    if not is_valid:
        print(f"DEBUG: Rejected upload with content_type='{file.content_type}' and filename='{file.filename}'")
        raise HTTPException(
            status_code=400, detail=f"Format non supporté ({file.content_type}). Utilisez PNG, JPG ou PDF."
        )

    receipt_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1].lower()
    filename = f"{receipt_id}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        abs_path = os.path.abspath(file_path)
        print(abs_path)
        
        # Convert PDF if necessary
        if extension == "pdf":
            image_path = convert_pdf_to_image(abs_path, UPLOAD_DIR)
        else:
            image_path = abs_path

        # Perform OCR synchronously
        start_time = time.time()
        ocr_result = ocr_receipt(image_path)
        processing_time = round(time.time() - start_time, 2)
        print(f"⏱️ OCR Processing Time: {processing_time}s")

        # Encode preprocessed image to base64 for debug
        # We read the file created by the ocr service in debug mode
        debug_image_path = os.path.join(UPLOAD_DIR, "debug_last_processed.png")
        img_base64 = None
        if os.path.exists(debug_image_path):
            with open(debug_image_path, 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode()

        if ocr_result:
            # Save in DB with 'parsed' status and all data
            save_receipt_record(receipt_id, filename, ocr_result)
            
            result = {
                "receipt_id": receipt_id,
                "status": "parsed",
                "filename": filename,
                "datetime": datetime.now(),
                "company": ocr_result.get("company"),
                "date": ocr_result.get("date"),
                "total": ocr_result.get("total"),
                "address": ocr_result.get("address"),
                "confidence": ocr_result.get("confidence"),
                "processing_time": processing_time,
                "processed_image": img_base64
            }
            await manager.emit_receipt_parsed(result)
        else:
            # Fallback if OCR fails
            save_receipt_record(receipt_id, filename)
            result = {
                "receipt_id": receipt_id,
                "status": "failed",
                "filename": filename,
                "datetime": datetime.now(),
                "processing_time": processing_time,
                "processed_image": img_base64
            }
            await manager.emit_receipt_failed(receipt_id, "OCR processing failed")
            
        return result
                
    except Exception as e:
        await manager.emit_receipt_failed(receipt_id if 'receipt_id' in locals() else "unknown", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/receipts")
async def list_receipts():
    return get_all_receipts()
