""" Write a Python function that takes a student ID as input and retrieves the corresponding student record from the Neon DB database. 
Expose this function as a GET API endpoint using FastAPI. Ensure proper error handling and return appropriate HTTP status codes 
(e.g., 404 if the student is not found)."""

from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from typing import List,Optional

load_dotenv()

conn_str = os.getenv("NEONDB_URL")

if not conn_str:
    raise ValueError("conn_str not found")

app = FastAPI()


def get_db_conn():
    return psycopg2.connect(conn_str)


class Students(BaseModel):
    id: int
    name: str
    age: int


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None


# ------------------ INSERT FUNCTION ------------------
def insert_record():
    connect = get_db_conn()
    cursor = connect.cursor()

    try:
        query = """
        INSERT INTO Students (id, name, age)
        VALUES (%s, %s, %s)
        """

        students_data = [
            (6, 'Ruipali', 45),
            (7, 'Mits', 30),
            (8, 'Anju', 28)
        ]

        cursor.executemany(query, students_data)
        connect.commit()

    except psycopg2.Error as e:
        connect.rollback()
        raise e

    finally:
        cursor.close()
        connect.close()


@app.post("/students/insert")
def insert_students():
    try:
        insert_record()
        return {
            "status": "success",
            "message": "3 student records inserted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ------------------ GET FUNCTION (YOUR TASK) ------------------
def get_student_by_id(student_id: int):
    connect = get_db_conn()
    cursor = connect.cursor()

    try:
        query = "SELECT * FROM Students WHERE id = %s;"
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()

        return student

    except psycopg2.Error as e:
        raise e

    finally:
        cursor.close()
        connect.close()


@app.get("/students/{student_id}")
def fetch_student(student_id: int):
    try:
        student = get_student_by_id(student_id)

        if not student:
            raise HTTPException(
                status_code=404,
                detail=f"Student with ID {student_id} not found"
            )

        return {
            "status": "success",
            "data": student
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def delete_student_by_id(student_id):
    connect = get_db_conn()
    cursor = connect.cursor(cursor_factory=RealDictCursor)

    try:
        query = "DELETE FROM Students WHERE id = %s;"
        cursor.execute(query,(student_id,))
        connect.commit()
        # rowcount tells how many rows were affected
        if cursor.rowcount == 0:
            return False   # student not found
        
        return True
    except psycopg2.Error as e:
        connect.rollback()
        raise e

    finally:
        cursor.close()
        connect.close()
    
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    try:
        deleted = delete_student_by_id(student_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail = f"Student with ID {student_id} not found"
            )
        
        return {
            "status": "success",
            "message": f"Student with ID {student_id} deleted successfully"
        }
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    connect = get_db_conn()
    cursor = connect.cursor()

    try:
        update_fields = []
        values = []

        if student.name is not None:
            update_fields.append("name = %s")
            values.append(student.name)

        if student.age is not None:
            update_fields.append("age = %s")
            values.append(student.age)

        if not update_fields:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        values.append(student_id)

        query = f"""
        UPDATE Students
        SET {', '.join(update_fields)}
        WHERE id = %s;
        """

        cursor.execute(query, tuple(values))
        connect.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Student with ID {student_id} not found"
            )

        return {
            "status": "success",
            "message": f"Student with ID {student_id} updated successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        connect.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        connect.close()


        
