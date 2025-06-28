from database.database import db
from flask import request,jsonify,send_file
from model.user import User
from . import bp
from database.database import db
import os
from model.image import Image
from app.auth.routes import token_required ,secret_key
import jwt


UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@bp.route('/upload_image', methods=['POST'],endpoint="create_image")
@token_required
def upload_image():
    auth_header = request.headers.get("Authorization")
    payload = auth_header.split(" ")[1]
    token = jwt.decode(payload, secret_key, algorithms=['HS256'])

    coach_id = token["id"]
    coach = User.query.get(coach_id)
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Save the image metadata to the database
        new_image = Image(filename=file.filename,coach_id=coach_id)
        db.session.add(new_image)
        db.session.commit()

        return jsonify({'message': 'Image uploaded successfully', 'image_id': new_image.id,"coach_id":coach_id}), 200


@bp.route('/get_all_images', methods=['GET'],endpoint="get_all_images")
@token_required
def get_all_images():
    try:
        images = Image.query.all()
        
        if not images:
            return jsonify({'message': 'No images found'}), 404

    
        images_data = []
        for image in images:
            images_data.append({
                'image_id': image.id,
                'filename': image.filename,
                'coach_id':image.coach_id
            })

        return jsonify({'images': images_data}), 200

    except Exception as e:

        return jsonify({'error': str(e)}), 500
    

@bp.route('/get_image/<int:image_id>', methods=['GET'], endpoint="get_image_by_id")
@token_required
def get_image_by_id(image_id):
    """
    Fetch an image by its ID.
    """
    try:
        # Query the image from the database by ID
        image = Image.query.get(image_id)

        if not image:
            return jsonify({'message': 'Image not found'}), 404

        # Return the image details as JSON
        image_data = {
            'image_id': image.id,
            'filename': image.filename,
            'coach_id': image.coach_id
        }

        return jsonify({'image': image_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route("/delete_image/<int:image_id>",methods=['DELETE'],endpoint="delete_image_by_id")
@token_required
def delete_image(image_id):
    try:
        # Query the image from the database by ID
        image = Image.query.get(image_id)

        if not image:
            return jsonify({'message': 'Image not found'}), 404

        # Delete the image from the database
        db.session.delete(image)
        db.session.commit()

        return jsonify({'message': f'Image with ID {image_id} has been deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/get_image_coach/<int:coach_id>', methods=['GET'], endpoint="get_image_by_coach")
@token_required
def get_image_by_id(coach_id):
    """
    Fetch an image by its ID.
    """
    try:
       
        # Query the image from the database by ID
        images = Image.query.filter_by(coach_id=coach_id).all()

        if not images:
            return jsonify({'message': 'image not found'}), 404

        # Return the image details as JSON
        image_data = [
            {
            'image_id': image.id,
            'filename': image.filename,
            'coach_id': image.coach_id
        }
        for image in images
        ]

        return jsonify({'images': image_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500