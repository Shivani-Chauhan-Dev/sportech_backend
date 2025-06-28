from flask import Flask, request, jsonify
from model.meeting import Meeting
from datetime import datetime,timedelta
# from model.athlete import Athlete
# from model.coach import Coach
from database.database import db
from . import bp
from sqlalchemy import func, extract,or_,and_
from sqlalchemy.orm.exc import NoResultFound
from app.auth.routes import token_required, secret_key
import jwt


@bp.route('/meetings', methods=['POST'],endpoint="create_meeting")
@token_required
def schedule_meeting():
    data = request.get_json()
    auth_header = request.headers.get("Authorization")
    payload = auth_header.split(" ")[1]
        # print(payload)
    token = jwt.decode(payload, secret_key, algorithms=["HS256"])
        # print(token)
    ath_id = token["id"]
    athlete_id = ath_id
    meeting = Meeting(
        athlete_id=athlete_id,
        coach_id=data.get('coach_id'),
        start_time=datetime.fromisoformat(data.get('start_time')),
        status='pending'  # Coach decides later
    )
    print(type("start_time"))
    db.session.add(meeting)
    db.session.commit()
    return jsonify(meeting.to_dict()), 201


@bp.route('/meetings/status', methods=['POST'])
@token_required
def update_meeting_status():
    data = request.json
    meeting_id = data.get('meeting_id')
    new_status = data.get('status')

    if not meeting_id or new_status not in ['accepted', 'declined']:
        return jsonify({'error': 'meeting_id and valid status are required'}), 400

    meeting = Meeting.query.get_or_404(meeting_id)

    # Assume meetings are 30 minutes long
    duration = timedelta(minutes=60)
    meeting_end = meeting.start_time + duration

    if new_status == 'accepted':
        # Check if coach has another accepted meeting that overlaps this time slot
        conflict = Meeting.query.filter(
            Meeting.coach_id == meeting.coach_id,
            Meeting.status == 'accepted',
            Meeting.id != meeting.id
        ).filter(
            # Check overlap: existing_start < new_end and existing_end > new_start
            and_(
                Meeting.start_time < meeting_end,
                (Meeting.start_time + duration) > meeting.start_time
            )
        ).first()

        if conflict:
            db.session.delete(meeting)
            db.session.commit()
            return jsonify({'error': 'Coach is busy. Meeting automatically declined and removed.'}), 409

    if new_status == 'declined':
        db.session.delete(meeting)
        db.session.commit()
        return jsonify({'message': 'Meeting declined and deleted.'}), 200

    meeting.status = new_status
    db.session.commit()
    return jsonify(meeting.to_dict()), 200

@bp.route('/getmeetings', methods=['GET'])
def get_all_meetings():
    meetings = Meeting.query.all()
    return jsonify([meeting.to_dict() for meeting in meetings]), 200