from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from app import app, db
from app.models import ReceiptFile
from PyPDF2 import PdfReader

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