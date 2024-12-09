# Library Management System

**Postman Documentation:** [Library Management API](https://documenter.getpostman.com/view/38648191/2sAYBd88Zd)

## Overview

The Library Management System is a Django-based backend application that provides a robust framework for managing library operations, including user management, book inventory management, book borrowing, and librarian-specific functionalities.

## Features

### User Management

- **User Registration:** Allows users to register with email and password.
- **User Login:** Authenticate users using email and password.
- **User Logout:** Securely log out authenticated users.

### Book Management

- **Add Books:** Librarians can add books to the library inventory.
- **List Books:** Retrieve a list of all available books with details.

### Borrowing System

- **Submit Book Request:** Users can request to borrow books within a specific date range.
- **User Borrow History:** View user's borrow history with book details and request status.

### Librarian Operations

- **View Book Requests:** Librarians can view all pending book requests.
- **Approve/Deny Requests:** Manage borrowing requests based on availability and other constraints.

### Bonus Features

- **Download Borrow History as CSV:** Users can download their borrow history in a CSV format.

---

## Models

### User

Custom user model extending `AbstractUser`:

- **Fields:**
  - `email (unique)`
  - `is_librarian`
  - Custom groups and permissions management

### Book

Represents individual book copies in the library:

- **Fields:**
  - `title`
  - `author`
  - `isbn (unique)`
  - `total_copies`
  - `available_copies`

### BookRequest

Tracks book borrowing requests:

- **Fields:**
  - `user`
  - `book`
  - `request_date`
  - `borrow_start_date`
  - `borrow_end_date`
  - `status` (choices: `PENDING`, `APPROVED`, `DENIED`, `RETURNED`)
- **Custom Validation:** Ensures no conflicts in borrowing periods.

---

## APIs

### Authentication

#### User Registration

**Endpoint:** `/api/register/`  
**Method:** `POST`

```json
{
  "email": "user@example.com",
  "password": "password123",
  "is_librarian": false
}
```

#### User Login

**Endpoint:** `/api/login/`  
**Method:** `POST`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### User Logout

**Endpoint:** `/api/logout/`  
**Method:** `GET`

### Book Management

#### Add Book (Librarian Only)

**Endpoint:** `/api/books/add/`  
**Method:** `POST`

```json
{
  "title": "Book Title",
  "author": "Author Name",
  "isbn": "1234567890",
  "total_copies": 5
}
```

#### List Books

**Endpoint:** `/api/books/`  
**Method:** `GET`

### Borrowing

#### Submit Book Request

**Endpoint:** `/api/books/request/`  
**Method:** `POST`

```json
{
  "book_id": 1,
  "borrow_start_date": "2024-01-01",
  "borrow_end_date": "2024-01-10"
}
```

#### User Borrow History

**Endpoint:** `/api/books/history/`  
**Method:** `GET`

### Librarian Operations

#### View Book Requests

**Endpoint:** `/api/librarian/book-requests/`  
**Method:** `GET`

#### Approve/Deny Requests

**Endpoint:** `/api/librarian/approve-request/`  
**Method:** `POST`

```json
{
  "request_id": 1,
  "status": "APPROVED"
}
```

### Bonus Feature

#### Download Borrow History (CSV)

**Endpoint:** `/api/books/history/download/`  
**Method:** `GET`

---

## Project Setup

### Prerequisites

- Python 3.8+
- Django 4.0+

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd library-management-system
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Run the server:
   ```bash
   python manage.py runserver
   ```

---

## URL Configuration

- **API Base URL:** `/api/`
- **Admin Panel:** `/admin/`
