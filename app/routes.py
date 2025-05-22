from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from app import app, db
from app.models import ReceiptFile
from PyPDF2 import PdfReader
from app.ocr_utils import extract_text_from_pdf
from app.models import Receipt
import re
from datetime import datetime

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(file_path)

        # Save metadata to database
        receipt_file = ReceiptFile(
            file_name=filename,
            file_path=file_path,
            is_valid=False,
            is_processed=False
        )
        db.session.add(receipt_file)
        db.session.commit()

        return jsonify({'message': 'File uploaded successfully', 'id': receipt_file.id}), 201
    else:
        return jsonify({'error': 'Invalid file type'}), 400


@app.route('/validate', methods=['POST'])
def validate_pdf():
    data = request.json
    file_id = data.get('id')

    receipt_file = ReceiptFile.query.get(file_id)
    if not receipt_file:
        return jsonify({'error': 'File ID not found'}), 404

    try:
        with open(receipt_file.file_path, 'rb') as f:
            reader = PdfReader(f)
            _ = reader.pages  # Try accessing pages to validate
        receipt_file.is_valid = True
        receipt_file.invalid_reason = None
    except Exception as e:
        receipt_file.is_valid = False
        receipt_file.invalid_reason = str(e)
    
    db.session.commit()

    return jsonify({'message': 'Validation complete', 'is_valid': receipt_file.is_valid})

@app.route('/process', methods=['POST'])
def process_receipt():
    data = request.json
    file_id = data.get('id')

    receipt_file = ReceiptFile.query.get(file_id)
    if not receipt_file or not receipt_file.is_valid:
        return jsonify({'error': 'Invalid or non-existent file'}), 400

    text = extract_text_from_pdf(receipt_file.file_path)
    if not text:
        return jsonify({'error': 'OCR failed'}), 500

    # Extract data using simple regex or text logic
    merchant_name = text.split('\n')[0][:100]  # naive assumption
    total_match = re.search(r'Total[:\s]+(\d+\.\d+)', text, re.IGNORECASE)
    total_amount = total_match.group(1) if total_match else "0.00"

    date_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
    purchased_at = date_match.group(0) if date_match else None

    receipt = Receipt(
        merchant_name=merchant_name,
        total_amount=total_amount,
        purchased_at=purchased_at,
        file_path=receipt_file.file_path
    )
    db.session.add(receipt)

    receipt_file.is_processed = True
    db.session.commit()

    return jsonify({'message': 'Receipt processed successfully', 'receipt_id': receipt.id})

@app.route('/receipts', methods=['GET'])
def get_receipts():
    receipts = Receipt.query.all()
    result = []
    for r in receipts:
        result.append({
            'id': r.id,
            'purchased_at': r.purchased_at,
            'merchant_name': r.merchant_name,
            'total_amount': r.total_amount,
            'file_path': r.file_path,
            'created_at': r.created_at,
            'updated_at': r.updated_at,
        })
    return jsonify(result)

@app.route('/receipts/<int:receipt_id>', methods=['GET'])
def get_receipt_by_id(receipt_id):
    r = Receipt.query.get(receipt_id)
    if not r:
        return jsonify({'error': 'Receipt not found'}), 404
    return jsonify({
        'id': r.id,
        'purchased_at': r.purchased_at,
        'merchant_name': r.merchant_name,
        'total_amount': r.total_amount,
        'file_path': r.file_path,
        'created_at': r.created_at,
        'updated_at': r.updated_at,
    })
