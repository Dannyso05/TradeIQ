from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from models import StockPrice
from services.stock import process_extracted_text
import pytesseract
from PIL import Image
import io

router = APIRouter()

@router.post("/upload-portfolio", response_model=dict)
async def upload_portfolio(file: UploadFile = File(...)):
    # Read the uploaded image file
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    # Use OCR to extract text from the image
    extracted_text = pytesseract.image_to_string(image)

    # Process the extracted text to fetch stock symbols and prices
    stock_data = process_extracted_text(extracted_text)

    return JSONResponse(content={"extracted_data": stock_data})


