"""

Design a Pydantic model for representing course information, including attributes like course ID (integer), course name (string), 
credits (integer), and instructor (string). Create a FastAPI POST endpoint that accepts a list of course objects conforming to 
this model and stores them in a JSON file. Implement appropriate validation to ensure data integrity.
Answer--
Whenever you see a question like this, think:
What is the data model?
What validation rules apply?
What HTTP method fits? (POST for create)
Single object or list?
Where will data be stored?
What errors can occur? 
"""

from fastapi import FastAPI, HTTPException
import os
import json
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

COURSE_FILE = "courses.json"

# ------------------ Pydantic Model ------------------

class Course(BaseModel):
    course_id: int = Field(..., gt=0, description="Course ID must be positive")
    course_name: str = Field(..., min_length=1)
    credits: int = Field(..., gt=0, le=10)
    instructor: str = Field(..., min_length=1)


# ------------------ Helper Function ------------------

def save_courses_to_file(courses: List[Course]):
    existing_courses = []

    if os.path.exists(COURSE_FILE):
        try:
            with open(COURSE_FILE, "r") as file:
                existing_courses = json.load(file)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Error reading existing course file"
            )

    # Convert Pydantic objects to dict
    new_courses = [course.dict() for course in courses]

    existing_courses.extend(new_courses)

    with open(COURSE_FILE, "w") as file:
        json.dump(existing_courses, file, indent=4)


# ------------------ POST API ------------------

@app.post("/courses")
def create_courses(courses: List[Course]):
    if not courses:
        raise HTTPException(
            status_code=400,
            detail="Course list cannot be empty"
        )

    save_courses_to_file(courses)

    return {
        "status": "success",
        "message": f"{len(courses)} courses saved successfully"
    }
