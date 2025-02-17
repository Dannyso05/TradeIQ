from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from models import StockPrice
from pdf2image import convert_from_bytes
from services.stock import process_extracted_text
import pytesseract
import cv2
import numpy as np
import io
from PIL import Image

router = APIRouter()

def preprocess_image(image_bytes):
    # Convert uploaded bytes to OpenCV image
    image = np.array(Image.open(io.BytesIO(image_bytes)))

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise removal
    denoised = cv2.fastNlMeansDenoising(gray, h=30)

    # Adaptive thresholding for better contrast
    binary = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Deskewing (straighten tilted text)
    coords = cv2.findNonZero(binary)
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = binary.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(binary, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return deskewed

@router.post("/upload-portfolio", response_model=dict)
async def upload_portfolio(file: UploadFile = File(...)):
    # Read the uploaded image file
    image_bytes = await file.read()

    # Preprocess the image with OpenCV
    preprocessed = preprocess_image(image_bytes)

    # Use OCR to extract text
    extracted_text = pytesseract.image_to_string(preprocessed, config="--psm 6")
    print(extracted_text)

    # Process the extracted text to fetch stock symbols and prices
    stock_data = process_extracted_text(extracted_text)
    return JSONResponse(content={"extracted_data": stock_data})
