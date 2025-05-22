#  Receipt OCR Processing Web App

A Flask-based web application that allows users to:
- Upload scanned **PDF receipts**
- Validate and process them via **OCR (Tesseract)**
- Extract details like **merchant name**, **total amount**, and **purchase date**
- Store them in a **SQLite** database

---

##  Tech Stack

- **Backend**: Flask (Python)
- **OCR Engine**: Tesseract OCR via `pytesseract`
- **PDF to Image**: `pdf2image` using Poppler
- **Database**: SQLite (`receipts.db`)

---

##  Project Structure

receipt-ocr/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── ocr_utils.py
│   └── database.py
├── uploads/                 ← uploaded PDFs go here
├── receipts_raw/           ← raw PDFs (from GitHub or your own)
├── receipts.db             ← your SQLite database
├── run.py                  ← starts the Flask app
├── requirements.txt
└── README.md


---

## How to Set Up and Run the Project

### 1. Install Python Dependencies

Make sure you're using Python 3.7 or higher.

pip install -r requirements.txt

### 2. Install Poppler and Tesseract

On Windows:
Tesseract OCR:

Download from: https://github.com/tesseract-ocr/tesseract

Add installation path to System PATH

Poppler for Windows:

Download from: http://blog.alivate.com.au/poppler-windows/

Extract and add the bin/ folder to your System PATH

### 3. Run the App

python app.py
By default, it runs at: http://localhost:5000

### 4. API Endpoints
 1. Upload Receipt File
POST /upload

Request (form-data):
file: PDF file

Response:

{
  "message": "File uploaded successfully",
  "file_id": 1
}


 2. Validate Receipt File
POST /validate

Request Body:

{
  "id": 1
}
Response:

{
  "message": "File validated successfully"
}

3. Process Receipt and Extract Text
POST /process

Request Body:

{
  "id": 1
}
Response:

{
  "message": "Receipt processed successfully",
  "receipt_id": 1
}
 Sample Data
receipts.db contains:

receipt_files: List of uploaded files

receipts: Extracted data after OCR

### 5. Dependencies

Stored in requirements.txt. Includes:

Flask
SQLAlchemy
pytesseract
pdf2image
Pillow


Install using:

pip install -r requirements.txt