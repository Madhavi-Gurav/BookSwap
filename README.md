# 📚 Book Swap Application

**PROJECT LIVE LINK:** [Book Swap on PythonAnywhere](https://madhavig.pythonanywhere.com/)

---

## 🔎 Overview
The **Book Swap Application** is a Flask-based platform that enables users to **share, borrow, and swap books** within a community.  
Admins have extended privileges to manage users, books, and swap requests. The application uses **SQLAlchemy** for database management and supports both **SQLite (default)** and **MySQL**.

---

## ✨ Features

- **User Management**  
  - Create, update, delete users  
  - Assign books automatically  
  - Admin role support  

- **Book Management**  
  - Add, update, assign, return, and delete books  
  - Track availability  

- **Swap Requests**  
  - Users can request swaps  
  - Accept/reject swap requests  
  - Admins can view all requests  

- **Admin Tools**  
  - Protected by an `ADMIN_TOKEN`  
  - Full control over users, books, and swaps  

---

## 🛠 API Endpoints

### 👤 Users
- `GET /api/users` → List users  
- `POST /api/users` → Create user  
- `PUT /api/users/<id>` → Update user (admin)  
- `DELETE /api/users/<id>` → Delete user (admin)  

### 📖 Books
- `GET /api/books` → List all books  
- `GET /api/books/available` → List available books  
- `POST /api/books` → Add book (admin)  
- `PUT /api/books/<id>` → Update book (admin)  
- `DELETE /api/books/<id>` → Delete book (admin)  
- `POST /api/books/assign` → Assign book to user  
- `POST /api/books/return` → Return book to library  

### 🔄 Swap Requests
- `POST /api/swap_requests` → Create swap request  
- `GET /api/users/<id>/swap_requests` → User’s incoming requests  
- `PUT /api/swap_requests/<id>/accept` → Accept request  
- `PUT /api/swap_requests/<id>/reject` → Reject request  
- `GET /api/swap_requests` → List all requests (admin)  

---

## 🗂 Data Models

- **User** → `id, name, email, is_admin`  
- **Book** → `id, title, author, owner_id, available`  
- **SwapRequest** → `id, from_user_id, to_user_id, from_book_id, to_book_id, status (pending/accepted/rejected), created_at`  

---

## 🚀 Future Scope
- Add proper authentication (JWT or OAuth)  
- Notifications for swap requests  
- Search/filter books by title, author, or availability  
- Improved front-end with React or Vue.js  
- Advanced swap logic (multi-book swaps, automatic suggestions)  
- Analytics: popular books, user activity, swap history  

---

## 📌 Summary
This lightweight **Book Exchange System** is ideal for **small communities, classrooms, or libraries**.  
It is designed for **ease of use, flexibility, and future extension**.  

---
💡 *Contributions are welcome!*
