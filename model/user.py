from datetime import datetime
from sqlalchemy.exc import IntegrityError
from database.database import db
from model.services import coach_services  # Make sure path matches your project structure

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # 'coach' or 'athlete'

    # Common fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    name = db.Column(db.String(255))
    dob = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Coach-specific fields
    detail_experience = db.Column(db.Text)
    languages = db.Column(db.String(160))
    age = db.Column(db.String(10))
    gender = db.Column(db.String(10))

    # Athlete-specific fields
    detail_health = db.Column(db.Text)

    # New: Coach service domains (many-to-many)
    services = db.relationship(
        "Services",
        secondary=coach_services,
        backref="users",  # Backref to access all users linked to a service
        lazy=True
    )

    def to_dict(self):
        data = {
            "id": self.id,
            "role": self.role,
            "email": self.email,
            "phone": self.phone,
            "name": self.name,
            "dob": self.dob,
            "address": self.address,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        if self.role == "coach":
            data.update({
                "detail_experience": self.detail_experience,
                "languages": self.languages,
                "age": self.age,
                "gender": self.gender,
                "services": [s.services for s in self.services]  # Return service names
            })

        elif self.role == "athlete":
            data.update({
                "detail_health": self.detail_health
            })

        return data

    @staticmethod
    def create_user(payload):
        user = User(
            role=payload["role"],
            email=payload["email"],
            password=payload["password"],
            phone=payload.get("phone"),
            name=payload.get("name"),
            dob=payload.get("dob"),
            address=payload.get("address"),
            created_at=payload.get("created_at", datetime.utcnow()),
            updated_at=payload.get("updated_at", datetime.utcnow()),
            detail_experience=payload.get("detail_experience"),
            languages=payload.get("languages"),
            age=payload.get("age"),
            gender=payload.get("gender"),
            detail_health=payload.get("detail_health"),
        )

        try:
            db.session.add(user)
            db.session.flush()

            # Only handle services if user is coach
            if user.role == "coach" and payload.get("domains"):
                cleaned_service = payload["domains"].strip().lower()
                from model.services import Services  # Avoid circular imports
                service = Services.query.filter_by(services=cleaned_service).first()
                if not service:
                    service = Services(services=cleaned_service)
                    db.session.add(service)
                    db.session.flush()

                user.services.append(service)

            db.session.commit()
            return user

        except IntegrityError:
            db.session.rollback()
            return None
