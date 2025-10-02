# app.py
import os
from flask import Flask, request, jsonify, render_template, abort
from models import db, User, Book, SwapRequest
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Config - use SQLITE by default for simple local setup; override SQLALCHEMY_DATABASE_URI to use MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bookswap.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Admin token (simple root management). For production replace with real auth.
    app.config['ADMIN_TOKEN'] = os.environ.get('ADMIN_TOKEN', 'change-me-secret-token')

    db.init_app(app)

    with app.app_context():
        db.create_all()
        # ensure at least one admin user exists (you can change email)
        admin_email = os.environ.get('ADMIN_EMAIL', None)
        if admin_email:
            if not User.query.filter_by(email=admin_email).first():
                admin = User(name='root', email=admin_email, is_admin=True)
                db.session.add(admin)
                db.session.commit()

    # ------------------------------------------------------------
    # Utilities
    def require_admin():
        token = request.headers.get('X-Admin-Token')
        if not token or token != app.config['ADMIN_TOKEN']:
            abort(403, description="Admin token required")

    # ------------------------------------------------------------
    # Basic UI route
    @app.route('/')
    def index():
        return render_template('index.html')

    # ------------------------------------------------------------
    # USERS
    @app.route('/api/users', methods=['GET'])
    def list_users():
        users = User.query.order_by(User.id).all()
        return jsonify([u.to_dict() for u in users])

    @app.route('/api/users', methods=['POST'])
    def create_user():
        data = request.json or {}
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        if not name or not email:
            return jsonify({"error": "name and email required"}), 400
        u = User(name=name, email=email, is_admin=bool(data.get('is_admin', False)))
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "email already exists"}), 400

        # optional: auto-assign a book if requested (flag assign_first_available true)
        assigned = None
        if data.get('assign_first_available'):
            book = Book.query.filter_by(available=True).first()
            if book:
                book.owner_id = u.id
                book.available = False
                db.session.commit()
                assigned = {"book_id": book.id}

        return jsonify({"message": "User created", "user": u.to_dict(), "assigned_book": assigned}), 201

    @app.route('/api/users/<int:user_id>', methods=['PUT', 'PATCH'])
    def update_user(user_id):
        require_admin()
        u = User.query.get_or_404(user_id)
        data = request.json or {}
        if 'name' in data:
            u.name = data['name']
        if 'email' in data:
            u.email = data['email']
        if 'is_admin' in data:
            u.is_admin = bool(data['is_admin'])
        db.session.commit()
        return jsonify({"message": "Updated", "user": u.to_dict()})

    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        require_admin()
        u = User.query.get_or_404(user_id)
        # when deleting user, return their books to library (owner=None, available=True)
        for book in u.books:
            book.owner_id = None
            book.available = True
        db.session.delete(u)
        db.session.commit()
        return jsonify({"message": "User and related ownerships cleaned up"})

    # ------------------------------------------------------------
    # BOOKS
    @app.route('/api/books', methods=['GET'])
    def list_books():
        books = Book.query.order_by(Book.id).all()
        return jsonify([b.to_dict() for b in books])

    @app.route('/api/books/available', methods=['GET'])
    def available_books():
        books = Book.query.filter_by(available=True).all()
        return jsonify([b.to_dict() for b in books])

    @app.route('/api/books', methods=['POST'])
    def create_book():
        require_admin()
        data = request.json or {}
        title = (data.get('title') or '').strip()
        author = (data.get('author') or '').strip()
        if not title or not author:
            return jsonify({"error": "title and author required"}), 400
        b = Book(title=title, author=author)
        # optional direct assignment
        if data.get('owner_id'):
            owner = User.query.get(data['owner_id'])
            if owner:
                b.owner_id = owner.id
                b.available = False
        db.session.add(b)
        db.session.commit()
        return jsonify({"message": "Book created", "book": b.to_dict()}), 201

    @app.route('/api/books/<int:book_id>', methods=['PUT', 'PATCH'])
    def update_book(book_id):
        require_admin()
        b = Book.query.get_or_404(book_id)
        data = request.json or {}
        if 'title' in data:
            b.title = data['title']
        if 'author' in data:
            b.author = data['author']
        # set owner via admin route
        if 'owner_id' in data:
            owner_id = data.get('owner_id')
            if owner_id is None:
                b.owner_id = None
                b.available = True
            else:
                user = User.query.get(owner_id)
                if not user:
                    return jsonify({"error": "owner not found"}), 400
                b.owner_id = user.id
                b.available = False
        db.session.commit()
        return jsonify({"message": "Book updated", "book": b.to_dict()})

    @app.route('/api/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        require_admin()
        b = Book.query.get_or_404(book_id)
        db.session.delete(b)
        db.session.commit()
        return jsonify({"message": "Book deleted"})

    # assign book to user (user borrows book)
    @app.route('/api/books/assign', methods=['POST'])
    def assign_book():
        data = request.json or {}
        book_id = data.get('book_id')
        user_id = data.get('user_id')
        if not book_id or not user_id:
            return jsonify({"error":"book_id and user_id required"}), 400
        book = Book.query.get_or_404(book_id)
        if not book.available:
            return jsonify({"error":"book not available"}), 400
        user = User.query.get_or_404(user_id)
        book.owner_id = user.id
        book.available = False
        db.session.commit()
        return jsonify({"message":"Assigned", "book": book.to_dict()})

    # return book to library
    @app.route('/api/books/return', methods=['POST'])
    def return_book():
        data = request.json or {}
        book_id = data.get('book_id')
        if not book_id:
            return jsonify({"error":"book_id required"}), 400
        book = Book.query.get_or_404(book_id)
        book.owner_id = None
        book.available = True
        db.session.commit()
        return jsonify({"message":"Returned to library", "book": book.to_dict()})

    # ------------------------------------------------------------
    # SWAP REQUESTS
    @app.route('/api/swap_requests', methods=['POST'])
    def create_swap_request():
        data = request.json or {}
        from_user_id = data.get('from_user_id')
        to_user_id = data.get('to_user_id')
        from_book_id = data.get('from_book_id')
        to_book_id = data.get('to_book_id')

        if not all([from_user_id, to_user_id, from_book_id, to_book_id]):
            return jsonify({"error":"all fields required"}), 400
        # Basic validation: ensure ownership
        from_book = Book.query.get_or_404(from_book_id)
        to_book = Book.query.get_or_404(to_book_id)
        if from_book.owner_id != int(from_user_id):
            return jsonify({"error":"from_user does not own from_book"}), 400
        if to_book.owner_id != int(to_user_id):
            return jsonify({"error":"to_user does not own to_book"}), 400
        # create request
        sr = SwapRequest(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            from_book_id=from_book_id,
            to_book_id=to_book_id
        )
        db.session.add(sr)
        db.session.commit()
        return jsonify({"message":"Swap request created", "request": sr.to_dict()}), 201

    @app.route('/api/users/<int:user_id>/swap_requests', methods=['GET'])
    def get_user_requests(user_id):
        # return requests where user is the recipient (to_user) ordered by pending first
        rs = SwapRequest.query.filter_by(to_user_id=user_id).order_by(SwapRequest.status, SwapRequest.created_at.desc()).all()
        return jsonify([r.to_dict() for r in rs])

    # accept swap - must be invoked by recipient (to_user) or admin
    @app.route('/api/swap_requests/<int:req_id>/accept', methods=['PUT'])
    def accept_swap(req_id):
        sr = SwapRequest.query.get_or_404(req_id)
        if sr.status != 'pending':
            return jsonify({"error":"request not pending"}), 400

        # Re-validate ownership before swapping
        from_book = Book.query.get_or_404(sr.from_book_id)
        to_book = Book.query.get_or_404(sr.to_book_id)
        if from_book.owner_id != sr.from_user_id or to_book.owner_id != sr.to_user_id:
            return jsonify({"error":"ownership changed since request - cannot accept"}), 400

        try:
            # swap owners atomically
            tmp_owner = from_book.owner_id
            from_book.owner_id = to_book.owner_id
            to_book.owner_id = tmp_owner

            # both are now assigned (available = False)
            from_book.available = False
            to_book.available = False

            sr.status = 'accepted'
            db.session.commit()
            return jsonify({"message":"Swap accepted and ownership updated", "request": sr.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/api/swap_requests/<int:req_id>/reject', methods=['PUT'])
    def reject_swap(req_id):
        sr = SwapRequest.query.get_or_404(req_id)
        if sr.status != 'pending':
            return jsonify({"error":"request not pending"}), 400
        sr.status = 'rejected'
        db.session.commit()
        return jsonify({"message":"Swap rejected", "request": sr.to_dict()})

    # admin: list all swap requests
    @app.route('/api/swap_requests', methods=['GET'])
    def list_swaps():
        require_admin()
        swaps = SwapRequest.query.order_by(SwapRequest.created_at.desc()).all()
        return jsonify([s.to_dict() for s in swaps])

    # ------------------------------------------------------------
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
