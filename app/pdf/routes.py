from flask import request, jsonify,jsonify
from model.pdf import PDFDocument
from database.database import db
from flask import send_file
from io import BytesIO
from . import bp
from app.auth.routes import token_required,secret_key
import jwt
from model.user import User



@bp.route('/upload', methods=['POST'],endpoint='upload_pdf')
@token_required
def upload_pdf():
    # data=request.get_json()
    auth_header = request.headers.get("Authorization")
    payload=auth_header.split(" ")[1]
    token=jwt.decode(payload,secret_key,algorithms=["HS256"])
    co_id=token["id"]
    coach_id=co_id

    coach=User.query.get(coach_id)
    if not coach:
        return jsonify({"success":False,"message":"Coach not found"})

    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        new_pdf = PDFDocument(
            filename=file.filename,
            data=file.read(),
            mimetype=file.mimetype,
            coach_id=coach_id

        )
        db.session.add(new_pdf)
        db.session.commit()
        return jsonify({"message": "PDF uploaded", "id": new_pdf.id}), 201

    return jsonify({"error": "Invalid file format. Only PDF allowed."}), 400


@bp.route('/getpdf/<int:pdf_id>', methods=['GET'],endpoint='get_pdf')
@token_required
def get_pdf(pdf_id):
    pdf = PDFDocument.query.get(pdf_id)
    if not pdf:
        return jsonify({"error": "PDF not found"}), 404

    return send_file(BytesIO(pdf.data),
                     download_name=pdf.filename,
                     mimetype=pdf.mimetype,
                     as_attachment=True)


@bp.route('/pdfs', methods=['GET'],endpoint='get_pdfs')
@token_required
def get_pdfs_by_coach():
    auth_header = request.headers.get("Authorization")
    payload = auth_header.split(" ")[1]
    token = jwt.decode(payload, secret_key, algorithms=["HS256"])
    coach_id = token["id"]

    coach = User.query.get(coach_id)
    if not coach:
        return jsonify({"success": False, "message": "Coach not found"}), 404

    pdfs = PDFDocument.query.filter_by(coach_id=coach_id).all()
    result = [{
        "id": pdf.id,
        "filename": pdf.filename,
        "mimetype": pdf.mimetype
    } for pdf in pdfs]

    return jsonify({"success": True, "pdfs": result}), 200