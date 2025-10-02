# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # convenience
    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "is_admin": self.is_admin}

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # null means library (not assigned)
    owner = db.relationship('User', backref='books', foreign_keys=[owner_id])

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "available": self.available,
            "owner_id": self.owner_id,
            "owner_name": self.owner.name if self.owner else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class SwapRequest(db.Model):
    __tablename__ = 'swap_requests'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)  # book owned by from_user (offered)
    to_book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)    # book owned by to_user (requested)
    status = db.Column(db.Enum('pending', 'accepted', 'rejected', name='swap_status'), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    from_user = db.relationship('User', foreign_keys=[from_user_id])
    to_user = db.relationship('User', foreign_keys=[to_user_id])
    from_book = db.relationship('Book', foreign_keys=[from_book_id])
    to_book = db.relationship('Book', foreign_keys=[to_book_id])

    def to_dict(self):
        return {
            "id": self.id,
            "from_user_id": self.from_user_id,
            "from_user_name": self.from_user.name if self.from_user else None,
            "to_user_id": self.to_user_id,
            "to_user_name": self.to_user.name if self.to_user else None,
            "from_book_id": self.from_book_id,
            "from_book_title": self.from_book.title if self.from_book else None,
            "to_book_id": self.to_book_id,
            "to_book_title": self.to_book.title if self.to_book else None,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
