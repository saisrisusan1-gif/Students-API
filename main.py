from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field

app=FastAPI()

students_lis=[]
student_id=1
class StudentRequest(BaseModel):
    name:str =Field(...,min_length=3,max_length=50)
    age:int =Field(...,ge=18,le=30)
    marks:int=Field(...,ge=0,le=100)

@app.post("/student")
def create_student(student:StudentRequest):
    global student_id
    new_student=student.dict()
    new_student["student_id"]=student_id
    student_id+=1
    students_lis.append(new_student)
    return students_lis[-1]

app.get("/students")
def get_all_students(name: str | None = None, age: int | None = None):
    results = students_lis

    if name is not None:
        results = [s for s in results if s["name"] == name]

    if age is not None:
        results = [s for s in results if s["age"] == age]

    return results
     
@app.get("/student/{student_id}")
def get_student(student_id:int):
    for dict1 in students_lis:
        if dict1["student_id"]==student_id:
            return dict1
    raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/student/{student_id}")
def delete_student(student_id:int):
    for i,dict1 in enumerate(students_lis):
        if dict1["student_id"]==student_id:
            deleted=students_lis.pop(i)
            return {"deleted":deleted}
    raise HTTPException(status_code=404, detail="Student not found")
