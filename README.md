# Online Course Platform

A production-ready FastAPI backend system for managing online courses, student enrollments, and wishlists. This platform provides a comprehensive API for course browsing, enrollment management, and advanced search capabilities.

## Overview

Online Course Platform is a complete backend solution built with FastAPI that handles the entire lifecycle of an online course management system - from course discovery and filtering to enrollment processing and wishlist management.

## Features

### Core Capabilities

**Course Management**
- Browse all available courses with detailed information
- Search courses by keyword across title, instructor, and category
- Filter courses by category, level, price, and seat availability
- Sort courses by price, title, or seats remaining
- Paginated course listing for efficient data retrieval
- Combined browse endpoint with multiple filters

**Enrollment System**
- Student enrollment with Pydantic validation
- Automatic discount calculations (early-bird and coupon-based)
- Gift enrollment option for sending courses to others
- Enrollment history tracking and retrieval

**Wishlist Functionality**
- Add courses to personal wishlist
- Bulk enrollment from wishlist in a single operation
- Wishlist management with duplicate prevention

**Advanced Features**
- Multi-criteria search across course attributes
- Dynamic sorting with ascending/descending order
- Pagination with metadata (total pages, has_next, has_previous)
- Complex business logic for pricing and discounts

## Technical Implementation

### Discount Engine

The platform implements a sophisticated discount calculation system:

- **Early-bird Discount**: 10% automatic discount when seats_left > 5
- **Coupon Codes**: 
  - `STUDENT20` - 20% additional discount
  - `FLAT500` - ₹500 flat reduction
- Discounts are applied sequentially (early-bird first, then coupon)

### API Architecture

Following REST best practices and FastAPI conventions:

- Fixed routes positioned before variable routes to prevent shadowing
- Proper HTTP status codes (200, 201, 400, 404)
- Comprehensive error handling with descriptive messages
- Pydantic models for request/response validation
- Type-safe query and path parameters

### Data Models

```python
Course {
    id: int
    title: str
    instructor: str
    category: str  # Web Dev, Data Science, Design, DevOps
    level: str     # Beginner, Intermediate, Advanced
    price: int
    seats_left: int
}

Enrollment {
    enrollment_id: int
    student_name: str
    email: str
    course_id: int
    course_title: str
    instructor: str
    original_price: float
    discounts_applied: list
    final_fee: float
    payment_method: str
}
```

## Project Structure

```
Online_Course_Platform/
├── main.py              # FastAPI application with all endpoints
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── screenshots/        # API documentation screenshots
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Navigate to project directory:
```bash
cd Online_Course_Platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the development server:
```bash
uvicorn main:app --reload
```

4. Access the interactive API documentation:
```
http://127.0.0.1:8000/docs
```

## API Endpoints

### Public Endpoints (GET)

| Endpoint | Description |
|----------|-------------|
| `GET /` | Welcome message and API info |
| `GET /courses` | List all courses with totals |
| `GET /courses/{course_id}` | Get specific course details |
| `GET /courses/summary` | Aggregate statistics and analytics |
| `GET /enrollments` | List all enrollments |

### Filter & Search Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /courses/filter` | Filter by category, level, price, seats |
| `GET /courses/search` | Keyword search across multiple fields |
| `GET /courses/sort` | Sort by price, title, or seats |
| `GET /courses/page` | Paginated course listing |
| `GET /courses/browse` | Combined filter + sort + paginate |

### Enrollment Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /enrollments` | Create new enrollment with validation |
| `GET /enrollments/search` | Search enrollments by student name |
| `GET /enrollments/sort` | Sort enrollments by various fields |
| `GET /enrollments/page` | Paginated enrollment listing |

### Course Management (CRUD)

| Endpoint | Description |
|----------|-------------|
| `POST /courses` | Create new course (with duplicate check) |
| `PUT /courses/{course_id}` | Update course price or seats |
| `DELETE /courses/{course_id}` | Delete course (if no enrollments) |

### Wishlist Operations

| Endpoint | Description |
|----------|-------------|
| `POST /wishlist/add` | Add course to wishlist |
| `GET /wishlist` | View wishlist with total value |
| `DELETE /wishlist/remove/{course_id}` | Remove from wishlist |
| `POST /wishlist/enroll-all` | Bulk enroll from wishlist |

## Sample Data

The platform comes pre-loaded with 6 diverse courses:

1. **Full Stack Web Development** - Web Development, Intermediate, ₹5999
2. **Data Science Fundamentals** - Data Science, Beginner, ₹6999
3. **Mobile App Development** - Mobile, Advanced, ₹7999
4. **Cloud Computing with AWS** - Cloud, Intermediate, ₹8499
5. **Blockchain Development** - Blockchain, Advanced, ₹9999
6. **Digital Marketing Basics** - Marketing, Beginner, ₹2999

Categories represented: Web Development (1), Data Science (1), Mobile (1), Cloud (1), Blockchain (1), Marketing (1)

## Key Design Decisions

### Route Ordering
Fixed routes are defined before variable routes to prevent FastAPI route shadowing:
- `/courses/summary` → defined before `/courses/{course_id}`
- `/courses/filter` → defined before `/courses/{course_id}`

### Business Logic
Helper functions encapsulate complex operations:
- `find_course(course_id)` - Efficient course lookup
- `calculate_enrollment_fee(price, seats_left, coupon_code)` - Discount calculations
- `filter_courses_logic(...)` - Dynamic filtering based on multiple criteria

### Error Handling
Comprehensive validation and error responses:
- 404 Not Found for invalid course IDs
- 400 Bad Request for validation failures
- Duplicate prevention for course creation
- Seat availability checks before enrollment
- Protection against deleting courses with active enrollments

## Testing

All endpoints have been tested using Swagger UI at `http://127.0.0.1:8000/docs`. Each endpoint returns appropriate HTTP status codes and follows REST conventions.

### Test Coverage

- Basic CRUD operations on courses
- Enrollment creation with various discount scenarios
- Wishlist workflow including bulk enrollment
- Search functionality across multiple fields
- Sorting algorithms (price, title, seats)
- Pagination with edge cases
- Combined browse endpoint with all filters

## Technologies Used

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server for running FastAPI
- **Python 3.8+** - Core programming language

---

**Built with FastAPI** 
