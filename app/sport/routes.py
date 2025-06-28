from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from model.services import Services
from database.database import db
from . import bp
from app.auth.routes import token_required,secret_key



@bp.route('/get_all_services', methods=['GET'], endpoint='get_all_services')
@token_required 
def get_all_services():
    try:
        services = Services.query.all()
        if not services:
            return jsonify([]), 200 

        return jsonify([s.to_dict() for s in services]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500  




@bp.route('/get_service/<int:id>', methods=['GET'], endpoint='get_service_by_id')
@token_required
def get_service_by_id(id):
    try:
        service = Services.query.get(id)
        if not service:
            return jsonify({'success': False, 'message': 'Service not found'}), 404

        return jsonify({'success': True, 'service': service.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/update_service/<int:id>', methods=['PUT'], endpoint='update_service')
@token_required
def update_service_by_id(id):
    try:
        data = request.get_json()
        new_name = data.get('services')

        service = Services.query.get(id)
        if not service:
            return jsonify({'success': False, 'message': 'Service not found'}), 404

        service.services = new_name
        db.session.commit()

        return jsonify({'success': True, 'service': service.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/delete_service/<int:id>', methods=['DELETE'], endpoint='delete_service')
@token_required
def delete_service_by_id(id):
    try:
        service = Services.query.get(id)
        if not service:
            return jsonify({'success': False, 'message': 'Service not found'}), 404

        # Automatically removes links from coach_services table
        db.session.delete(service)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Service deleted successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

