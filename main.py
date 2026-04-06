from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from typing import Optional


app=FastAPI()

students_lis=[]
student_id=1
class StudentRequest(BaseModel):
    name:str =Field(...,min_length=3,max_length=50)
    age:int =Field(...,ge=18,le=30)
    marks:int=Field(...,ge=0,le=100)
    password:str

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    age: Optional[int] = Field(None, ge=18, le=30)
    marks: Optional[int] = Field(None, ge=0, le=100)
    password:Optional[str]
    
class StudentResponse(BaseModel):
    name: str
    age: int
    marks: int
    
    
@app.post("/student",response_model=StudentResponse)
def create_student(student:StudentRequest):
    global student_id
    new_student=student.dict()
    new_student["student_id"]=student_id
    student_id+=1
    students_lis.append(new_student)
    return students_lis[-1]

@app.get("/students",response_model=list[StudentResponse])
def get_all_students(name: str | None = None, age: int | None = None):
    results = students_lis

    if name is not None:
        results = [s for s in results if s["name"] == name]

    if age is not None:
        results = [s for s in results if s["age"] == age]

    return results
     
@app.get("/student/{student_id}",response_model=StudentResponse)
def get_student(student_id:int):
    for dict1 in students_lis:
        if dict1["student_id"]==student_id:
            return dict1
    raise HTTPException(status_code=404, detail="Student not found")

@app.put("/student/{student_id}",response_model=StudentResponse)
def update_student(student_id:int,student:StudentRequest):
    for dict1 in students_lis:
        if dict1["student_id"]==student_id:
            dict1["age"]=student.age
            dict1["name"]=student.name
            dict1["marks"]=student.marks
            dict1["password"]=student.password
            return dict1
    raise HTTPException(status_code=404,detail="student_id is not found")
    
@app.patch("/student/{student_id}",response_model=StudentResponse)
def partial_update_student(student_id: int, student: StudentUpdate):
    for dict1 in students_lis:
        if dict1["student_id"] == student_id:
            
            if student.name is not None:
                dict1["name"] = student.name
            if student.age is not None:
                dict1["age"] = student.age
            if student.marks is not None:
                dict1["marks"] = student.marks
            if student.password is not None:
                dict1["password"] = student.password

            return dict1

    raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/student/{student_id}")
def delete_student(student_id:int):
    for i,dict1 in enumerate(students_lis):
        if dict1["student_id"]==student_id:
            deleted=students_lis.pop(i)
            return {"deleted":deleted}
    raise HTTPException(status_code=404, detail="Student not found")
