from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="Online Course Platform", description="Online Course Platform API")

# ==================== DATA MODELS ====================

courses = [
    {
        "id": 1,
        "title": "Full Stack Web Development",
        "instructor": "Rajesh Kumar",
        "category": "Web Dev",
        "level": "Intermediate",
        "price": 5999,
        "seats_left": 18
    },
    {
        "id": 2,
        "title": "Data Science Fundamentals",
        "instructor": "Priya Sharma",
        "category": "Data Science",
        "level": "Beginner",
        "price": 6999,
        "seats_left": 22
    },
    {
        "id": 3,
        "title": "Mobile App Development",
        "instructor": "Amit Patel",
        "category": "Mobile",
        "level": "Advanced",
        "price": 7999,
        "seats_left": 5
    },
    {
        "id": 4,
        "title": "Cloud Computing with AWS",
        "instructor": "Anjali Reddy",
        "category": "Cloud",
        "level": "Intermediate",
        "price": 8499,
        "seats_left": 12
    },
    {
        "id": 5,
        "title": "Blockchain Development",
        "instructor": "Vikram Singh",
        "category": "Blockchain",
        "level": "Advanced",
        "price": 9999,
        "seats_left": 0
    },
    {
        "id": 6,
        "title": "Digital Marketing Basics",
        "instructor": "Meera Joshi",
        "category": "Marketing",
        "level": "Beginner",
        "price": 2999,
        "seats_left": 35
    }
]

enrollments = []
enrollment_counter = 1

wishlist = []
wishlist_counter = 1

# ==================== PYDANTIC MODELS ====================

class EnrollRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    course_id: int = Field(..., gt=0)
    email: str = Field(..., min_length=5)
    payment_method: str = Field(default="card")
    coupon_code: str = Field(default="")
    gift_enrollment: bool = Field(default=False)
    recipient_name: str = Field(default="")

class NewCourse(BaseModel):
    title: str = Field(..., min_length=2)
    instructor: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    level: str = Field(..., min_length=2)
    price: int = Field(..., ge=0)
    seats_left: int = Field(..., gt=0)

class WishlistAdd(BaseModel):
    student_name: str
    course_id: int

class WishlistEnrollAll(BaseModel):
    student_name: str
    payment_method: str = "card"

# ==================== HELPER FUNCTIONS ====================

def find_course(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            return course
    return None

def calculate_enrollment_fee(price: int, seats_left: int, coupon_code: str):
    original_price = price
    discounts = []
    
    if seats_left > 5:
        early_bird = price * 0.10
        price -= early_bird
        discounts.append(f"Early-bird (10%): ₹{early_bird:.2f}")
    
    if coupon_code == "STUDENT20":
        discount = price * 0.20
        price -= discount
        discounts.append(f"Coupon STUDENT20 (20%): ₹{discount:.2f}")
    elif coupon_code == "FLAT500":
        discount = 500
        price -= discount
        discounts.append(f"Coupon FLAT500: ₹{discount:.2f}")
    
    return {
        "original_price": original_price,
        "discounts": discounts,
        "final_price": max(0, price)
    }

def filter_courses_logic(category: Optional[str] = None, level: Optional[str] = None, 
                         max_price: Optional[int] = None, has_seats: Optional[bool] = None):
    result = courses.copy()
    
    if category is not None:
        result = [c for c in result if c["category"].lower() == category.lower()]
    
    if level is not None:
        result = [c for c in result if c["level"].lower() == level.lower()]
    
    if max_price is not None:
        result = [c for c in result if c["price"] <= max_price]
    
    if has_seats is not None and has_seats:
        result = [c for c in result if c["seats_left"] > 0]
    
    return result

# ==================== DAY 1 - BEGINNER ====================

@app.get("/")
def home():
    return {"message": "Welcome to Online Course Platform"}

@app.get("/courses")
def get_all_courses():
    total_seats = sum(c["seats_left"] for c in courses)
    return {
        "courses": courses,
        "total": len(courses),
        "total_seats_available": total_seats
    }

@app.get("/courses/summary")
def get_courses_summary():
    total = len(courses)
    free_courses = len([c for c in courses if c["price"] == 0])
    most_expensive = max(courses, key=lambda x: x["price"]) if courses else None
    total_seats = sum(c["seats_left"] for c in courses)
    
    category_count = {}
    for c in courses:
        cat = c["category"]
        category_count[cat] = category_count.get(cat, 0) + 1
    
    return {
        "total_courses": total,
        "free_courses_count": free_courses,
        "most_expensive_course": most_expensive,
        "total_seats": total_seats,
        "count_by_category": category_count
    }

@app.get("/courses/filter")
def filter_courses(
    category: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    max_price: Optional[int] = Query(None),
    has_seats: Optional[bool] = Query(None)
):
    filtered = filter_courses_logic(category, level, max_price, has_seats)
    return {
        "courses": filtered,
        "total": len(filtered),
        "filters_applied": {
            "category": category,
            "level": level,
            "max_price": max_price,
            "has_seats": has_seats
        }
    }

@app.get("/courses/search")
def search_courses(keyword: str = Query(..., min_length=1)):
    keyword_lower = keyword.lower()
    
    results = [
        c for c in courses
        if (keyword_lower in c["title"].lower() or 
            keyword_lower in c["instructor"].lower() or 
            keyword_lower in c["category"].lower())
    ]
    
    return {
        "results": results,
        "total_found": len(results),
        "search_keyword": keyword
    }

@app.get("/courses/sort")
def sort_courses(sort_by: str = Query(default="price"), 
                 order: str = Query(default="asc")):
    valid_sort_fields = ["price", "title", "seats_left"]
    
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid sort_by field. Must be one of: {valid_sort_fields}"
        )
    
    sorted_courses = sorted(
        courses, 
        key=lambda x: x[sort_by],
        reverse=(order.lower() == "desc")
    )
    
    return {
        "sorted_courses": sorted_courses,
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_courses)
    }

@app.get("/courses/page")
def paginate_courses(page: int = Query(default=1, ge=1),
                     limit: int = Query(default=3, ge=1)):
    total = len(courses)
    total_pages = (total + limit - 1) // limit
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_courses = courses[start_idx:end_idx]
    
    return {
        "courses": paginated_courses,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }

@app.get("/courses/browse")
def browse_courses(
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    max_price: Optional[int] = Query(None),
    sort_by: str = Query(default="price"),
    order: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=3, ge=1)
):
    result = courses.copy()
    
    if keyword:
        keyword_lower = keyword.lower()
        result = [
            c for c in result
            if (keyword_lower in c["title"].lower() or 
                keyword_lower in c["instructor"].lower() or 
                keyword_lower in c["category"].lower())
        ]
    
    if category:
        result = [c for c in result if c["category"].lower() == category.lower()]
    
    if level:
        result = [c for c in result if c["level"].lower() == level.lower()]
    
    if max_price:
        result = [c for c in result if c["price"] <= max_price]
    
    # Step 5: Sort
    valid_sort_fields = ["price", "title", "seats_left"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by field. Must be one of: {valid_sort_fields}"
        )
    
    result = sorted(
        result,
        key=lambda x: x[sort_by],
        reverse=(order.lower() == "desc")
    )
    
    # Step 6: Pagination
    total = len(result)
    total_pages = (total + limit - 1) // limit
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_result = result[start_idx:end_idx]
    
    return {
        "results": paginated_result,
        "filters_applied": {
            "keyword": keyword,
            "category": category,
            "level": level,
            "max_price": max_price
        },
        "sort": {
            "sort_by": sort_by,
            "order": order
        },
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }

@app.get("/courses/{course_id}")
def get_course_by_id(course_id: int):
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.get("/enrollments")
def get_all_enrollments():
    return {
        "enrollments": enrollments,
        "total": len(enrollments)
    }

# ==================== DAY 2-3 - EASY ====================

@app.post("/enrollments")
def create_enrollment(enrollment_data: EnrollRequest):
    global enrollment_counter
    
    course = find_course(enrollment_data.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course["seats_left"] <= 0:
        raise HTTPException(status_code=400, detail="No seats left in this course")
    
    fee_info = calculate_enrollment_fee(course["price"], course["seats_left"], 
                                        enrollment_data.coupon_code)
    
    course["seats_left"] -= 1
    
    enrollment = {
        "enrollment_id": enrollment_counter,
        "student_name": enrollment_data.student_name,
        "email": enrollment_data.email,
        "course_id": course["id"],
        "course_title": course["title"],
        "instructor": course["instructor"],
        "original_price": fee_info["original_price"],
        "discounts_applied": fee_info["discounts"],
        "final_fee": fee_info["final_price"],
        "payment_method": enrollment_data.payment_method,
        "gift_enrollment": enrollment_data.gift_enrollment,
        "recipient_name": enrollment_data.recipient_name if enrollment_data.gift_enrollment else None
    }
    
    enrollments.append(enrollment)
    enrollment_counter += 1
    
    return {
        "message": "Enrollment successful!",
        "enrollment": enrollment
    }

@app.get("/courses/filter")
def filter_courses(
    category: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    max_price: Optional[int] = Query(None),
    has_seats: Optional[bool] = Query(None)
):
    filtered = filter_courses_logic(category, level, max_price, has_seats)
    return {
        "courses": filtered,
        "total": len(filtered),
        "filters_applied": {
            "category": category,
            "level": level,
            "max_price": max_price,
            "has_seats": has_seats
        }
    }

# ==================== DAY 4 - CRUD ====================

@app.post("/courses", status_code=201)
def create_course(new_course: NewCourse):
    for course in courses:
        if course["title"].lower() == new_course.title.lower():
            raise HTTPException(status_code=400, detail="Course with this title already exists")
    
    course_dict = new_course.model_dump()
    course_dict["id"] = max([c["id"] for c in courses], default=0) + 1
    courses.append(course_dict)
    
    return {"message": "Course created successfully", "course": course_dict}

@app.put("/courses/{course_id}")
def update_course(course_id: int, 
                  price: Optional[int] = Query(None),
                  seats_left: Optional[int] = Query(None)):
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if price is not None:
        course["price"] = price
    if seats_left is not None:
        course["seats_left"] = seats_left
    
    return {"message": "Course updated successfully", "course": course}

@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    global courses
    
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    for enrollment in enrollments:
        if enrollment["course_id"] == course_id:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete course with enrolled students"
            )
    
    courses = [c for c in courses if c["id"] != course_id]
    return {"message": "Course deleted successfully"}

# ==================== DAY 5 - MULTI-STEP WORKFLOW ====================

@app.post("/wishlist/add")
def add_to_wishlist(student_name: str, course_id: int):
    global wishlist_counter
    
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    for item in wishlist:
        if item["student_name"] == student_name and item["course_id"] == course_id:
            raise HTTPException(status_code=400, detail="Course already in wishlist")
    
    wishlist_item = {
        "wishlist_id": wishlist_counter,
        "student_name": student_name,
        "course_id": course_id,
        "course_title": course["title"],
        "price": course["price"]
    }
    
    wishlist.append(wishlist_item)
    wishlist_counter += 1
    
    return {"message": "Added to wishlist", "wishlist_item": wishlist_item}

@app.get("/wishlist")
def get_wishlist():
    total_value = sum(item["price"] for item in wishlist)
    return {
        "wishlist": wishlist,
        "total": len(wishlist),
        "total_wishlist_value": total_value
    }

@app.delete("/wishlist/remove/{course_id}")
def remove_from_wishlist(course_id: int, student_name: str):
    global wishlist
    
    found = False
    for i, item in enumerate(wishlist):
        if item["course_id"] == course_id and item["student_name"] == student_name:
            wishlist.pop(i)
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    
    return {"message": "Removed from wishlist"}

@app.post("/wishlist/enroll-all", status_code=201)
def enroll_all_from_wishlist(data: WishlistEnrollAll):
    global enrollment_counter, wishlist
    
    student_items = [w for w in wishlist if w["student_name"] == data.student_name]
    
    if not student_items:
        raise HTTPException(status_code=400, detail="No wishlist items found for this student")
    
    enrollments_created = []
    grand_total = 0
    removed_from_wishlist = []
    
    for item in student_items:
        course = find_course(item["course_id"])
        
        if not course or course["seats_left"] <= 0:
            continue
        
        fee_info = calculate_enrollment_fee(course["price"], course["seats_left"], "")
        
        course["seats_left"] -= 1
        
        enrollment = {
            "enrollment_id": enrollment_counter,
            "student_name": data.student_name,
            "email": f"{data.student_name}@student.com",
            "course_id": course["id"],
            "course_title": course["title"],
            "instructor": course["instructor"],
            "original_price": fee_info["original_price"],
            "discounts_applied": fee_info["discounts"],
            "final_fee": fee_info["final_price"],
            "payment_method": data.payment_method,
            "gift_enrollment": False,
            "recipient_name": None
        }
        
        enrollments.append(enrollment)
        enrollment_counter += 1
        enrollments_created.append(enrollment)
        grand_total += fee_info["final_price"]
        removed_from_wishlist.append(item["course_id"])
    
    wishlist = [w for w in wishlist if w["course_id"] not in removed_from_wishlist 
                or w["student_name"] != data.student_name]
    
    return {
        "message": f"Successfully enrolled in {len(enrollments_created)} courses",
        "total_enrolled": len(enrollments_created),
        "grand_total_fee": grand_total,
        "enrollments": enrollments_created
    }

@app.get("/enrollments/search")
def search_enrollments(student_name: str = Query(..., min_length=1)):
    results = [
        e for e in enrollments
        if student_name.lower() in e["student_name"].lower()
    ]
    
    return {
        "results": results,
        "total_found": len(results),
        "search_name": student_name
    }

@app.get("/enrollments/sort")
def sort_enrollments(sort_by: str = Query(default="final_fee"),
                     order: str = Query(default="asc")):
    valid_sort_fields = ["final_fee", "student_name", "enrollment_id"]
    
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by field. Must be one of: {valid_sort_fields}"
        )
    
    sorted_enrollments = sorted(
        enrollments,
        key=lambda x: x[sort_by],
        reverse=(order.lower() == "desc")
    )
    
    return {
        "sorted_enrollments": sorted_enrollments,
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_enrollments)
    }

@app.get("/enrollments/page")
def paginate_enrollments(page: int = Query(default=1, ge=1),
                         limit: int = Query(default=3, ge=1)):
    total = len(enrollments)
    total_pages = (total + limit - 1) // limit
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_enrollments = enrollments[start_idx:end_idx]
    
    return {
        "enrollments": paginated_enrollments,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }