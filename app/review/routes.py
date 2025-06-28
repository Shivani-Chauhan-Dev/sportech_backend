from flask import Flask, request, jsonify
from model.review import Review
# from model.athlete import Athlete
from model.user import User
from database.database import db
from . import bp
from sqlalchemy import func, extract
from sqlalchemy.orm.exc import NoResultFound
from app.auth.routes import token_required, secret_key
import jwt


@bp.route('/create_review', methods=['POST'],endpoint="create_review")
@token_required
def create_review():
    try:
        data = request.get_json()
        auth_header = request.headers.get("Authorization")
        payload = auth_header.split(" ")[1]
        # print(payload)
        token = jwt.decode(payload, secret_key, algorithms=["HS256"])
        # print(token)
        ath_id = token["id"]
        athlete_id = ath_id
        coach_id = data.get('coach_id')

        # Check if athlete_id exists
        # athlete = Athlete.query.get(athlete_id)
        # if not athlete:
        #     return jsonify({'success': False, 'message': 'Athlete not found'}), 404

        # Check if coach_id exists
        coach = User.query.get(coach_id)
        if not coach:
            return jsonify({'success': False, 'message': 'Coach not found'}), 404

        # Create a new review
        review = Review(
            athlete_id=athlete_id,
            coach_id=coach_id,
            rating=data.get('rating'),
            comment=data.get('comment')
        )
        db.session.add(review)
        db.session.commit()

        return jsonify({'success': True, 'review': {'id': review.id, 'athlete_id': review.athlete_id, 'coach_id': review.coach_id, 'rating': review.rating, 'comment': review.comment}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Route to get all reviews
@bp.route('/get_all_reviews', methods=['GET'],endpoint="get_review")
@token_required
def get_all_reviews():
    try:
        reviews = Review.query.all()

        if not reviews:
            return jsonify({'success': False, 'message': 'No reviews found'}), 404
        
        # Extract unique athlete IDs from reviews
        athlete_ids = {review.athlete_id for review in reviews}

        # Query all athletes in one go
        athletes = User.query.filter(User.id.in_(athlete_ids)).all()

        # Create a mapping of athlete_id to athlete_name
        athlete_map = {athlete.id: athlete.name for athlete in athletes}

        reviews_with_athlete_names = [{
            'id': review.id,
            'athlete_id': review.athlete_id,
            'athlete_name': athlete_map.get(review.athlete_id),  # Include the athlete name
            'coach_id': review.coach_id,
            'rating': review.rating,
            'comment': review.comment
        } for review in reviews]

        return jsonify({'success': True, 'reviews': reviews_with_athlete_names}), 200

        # return jsonify({'success': True, 'reviews': [{'id': review.id, 'athlete_id': review.athlete_id, 'coach_id': review.coach_id, 'rating': review.rating, 'comment': review.comment} for review in reviews]}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Route to get review by ID
@bp.route('/get_review/<int:id>', methods=['GET'],endpoint="get_review_by_id")
@token_required
def get_review_by_id(id):
    try:
        review = Review.query.get(id)

        if not review:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
         # Assuming the relationship is set up, fetch the athlete's name
        athlete = User.query.get(review.athlete_id)

        if not athlete:
            return jsonify({'success': False, 'message': 'Athlete not found'}), 404

        return jsonify({'success': True, 'review': {'id': review.id, 'athlete_id': review.athlete_id, 'coach_id': review.coach_id, 'rating': review.rating, 'comment': review.comment, 'athlete_name': athlete.name }}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Route to update review by ID
@bp.route('/update_review/<int:id>', methods=['PUT'],endpoint="update_review")
@token_required
def update_review_by_id(id):
    try:
        data = request.get_json()
        review = Review.query.get(id)

        if not review:
            return jsonify({'success': False, 'message': 'Review not found'}), 404

        review.rating = data.get('rating', review.rating)
        review.comment = data.get('comment', review.comment)
        db.session.commit()

        return jsonify({'success': True, 'review': {'id': review.id, 'athlete_id': review.athlete_id, 'coach_id': review.coach_id, 'rating': review.rating, 'comment': review.comment}}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Route to delete review by ID
@bp.route('/delete_review/<int:id>', methods=['DELETE'],endpoint="delete_review_by_id")
@token_required
def delete_review_by_id(id):
    try:
        review = Review.query.get(id)

        if not review:
            return jsonify({'success': False, 'message': 'Review not found'}), 404

        db.session.delete(review)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Review deleted successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    


def get_weekly_ratings():
    stats = (
        db.session.query(
            extract('dow', Review.timestamp).label('weekday'),
            func.count(Review.id).label('count')
        )
        .group_by('weekday')
        .all()
    )
    # Map numeric weekdays to abbreviated names
    weekdays = {
        0: 'SUN',
        1: 'MON',
        2: 'TUE',
        3: 'WED',
        4: 'THU',
        5: 'FRI',
        6: 'SAT'
    }
    weekday_counts = {i: 0 for i in range(7)}

    for day, count in stats:
        weekday_counts[int(day)] = count
    result = [
        {
            'day': weekdays[i],
            'count': weekday_counts[i]
        }
        for i in range(7)
    ]
    # result = [
    #     {
    #         'day': weekdays[int(day)],
    #         'count': count
    #     }
    #     for day, count in stats
    # ]
    
    # Sort by day (Sunday first)
    result.sort(key=lambda x: list(weekdays.values()).index(x['day']))
    
    return jsonify(result)  

@bp.route('/api/ratings/weekly', methods=['GET'])
def weekly_ratings():
    try:
        return get_weekly_ratings()
    except Exception as e:
        return jsonify({'error': str(e)}), 500