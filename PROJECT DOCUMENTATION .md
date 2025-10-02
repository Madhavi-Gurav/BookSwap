**PROJECT LIVE LINK: https://madhavig.pythonanywhere.com/**





**Book Swap** Application Documentation

Overview



The Book Swap Application is a Flask-based platform that enables users to share, borrow, and swap books. Admins have extra privileges to manage users, books, and swap requests. The app uses SQLAlchemy for database management and supports both SQLite (default) and MySQL.



Features



User Management: Create, update, delete users; assign books automatically; admin role support.



Book Management: Add, update, assign, return, and delete books; track availability.



Swap Requests: Users can request swaps, accept/reject them; admins can view all requests.



Admin Tools: Protected by an ADMIN\_TOKEN, allowing full control over users, books, and swaps.



API Endpoints



Users



GET /api/users → List users



POST /api/users → Create user



PUT/PATCH /api/users/<id> → Update user (admin)



DELETE /api/users/<id> → Delete user (admin)



Books



GET /api/books → List all books



GET /api/books/available → List available books



POST /api/books → Add book (admin)



PUT/PATCH /api/books/<id> → Update book (admin)



DELETE /api/books/<id> → Delete book (admin)



POST /api/books/assign → Assign book to user



POST /api/books/return → Return book to library



Swap Requests



POST /api/swap\_requests → Create swap request



GET /api/users/<id>/swap\_requests → User’s incoming requests



PUT /api/swap\_requests/<id>/accept → Accept request



PUT /api/swap\_requests/<id>/reject → Reject request



GET /api/swap\_requests → List all requests (admin)



Data Models



User: id, name, email, is\_admin



Book: id, title, author, owner\_id, available



SwapRequest: id, from\_user\_id, to\_user\_id, from\_book\_id, to\_book\_id, status (pending, accepted, rejected), created\_at



Future Scope



Add proper authentication (JWT or OAuth).



Notifications for swap requests.



Search/filter books by title, author, or availability.



Improved front-end with React or Vue.js.



Advanced swap logic (multi-book swaps, automatic suggestions).



Analytics: popular books, user activity, swap history.



Summary:

This lightweight book exchange system is ideal for small communities, classrooms, or libraries. It is designed for ease of use, flexibility, and future extension.

