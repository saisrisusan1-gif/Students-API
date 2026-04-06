from fastapi import FastAPI,HTTPException,status,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,field_validator
from typing import Optional


app = FastAPI(
    title="Student Management API",
    description="API for managing students with validation, filtering, sorting, pagination, and nested address",
    version="1.0.0"
)

students_lis=[]
student_id=1
class AddressRequest(BaseModel):
    city: str = Field(..., min_length=3, max_length=50)
    state: str = Field(..., min_length=3, max_length=50)
class StudentRequest(BaseModel):
    name:str =Field(...,min_length=3,max_length=50)
    age: int = Field(..., ge=5, le=100)
    marks:int=Field(...,ge=0,le=100)
    password:str
    address:AddressRequest
    @field_validator("name")
    def name_should_not_have_numbers(cls,value):
        if any(char.isdigit() for char in value):
            raise ValueError("Name should not contain number")
        return value
    
    @field_validator("password")
    def password_strength(cls,value):
        if len(value)<6:
            raise ValueError("password must be atleast 6 characters")
        return value
class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    age: Optional[int] = Field(None, ge=5, le=100)
    marks: Optional[int] = Field(None, ge=0, le=100)
    password: Optional[str]
    address: Optional[AddressRequest] 
class StudentResponse(BaseModel):
    name: str
    age: int
    marks: int
    address: AddressRequest
    
class StudentNotFoundError(Exception):
    def __init__(self, student_id: int):
        self.student_id = student_id
        
@app.exception_handler(StudentNotFoundError)
def student_not_found_handler(request, exc: StudentNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": f"Student with id {exc.student_id} not found",
            "status": 404
        }
    )
     
@app.post("/student",response_model=StudentResponse,status_code=status.HTTP_201_CREATED,tags=["Students"],
    summary="Create a new student",
    description="Creates a student with name, age, marks, password, and address.",
    responses={
        201: {"description": "Student created successfully"},
        400: {"description": "Validation error"}
    })
def create_student(student:StudentRequest):
    global student_id
    new_student=student.dict()
    new_student["student_id"]=student_id
    student_id+=1
    students_lis.append(new_student)
    return students_lis[-1]

@app.get("/students", response_model=list[StudentResponse],tags=["Students"],
    summary="Get all students",
    description="Retrieve students with filtering, sorting, and pagination.",
    responses={
        200: {"description": "List of students"},
        400: {"description": "Invalid query parameters"}
    })
def get_all_students(
    page: int = 1,
    limit: int = 10,
    sort_by: str = "marks",
    order_by: str = Query("asc", pattern="^(asc|desc)$"),
    name: str | None = None,
    age: int | None = None,
):
    results = students_lis

    # 🔍 Filtering
    if name is not None:
        results = [s for s in results if s["name"] == name]

    if age is not None:
        results = [s for s in results if s["age"] == age]

    # 🔽 Sorting
    reverse = True if order_by == "desc" else False

    try:
        results = sorted(results, key=lambda x: x[sort_by], reverse=reverse)
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    # 📄 Pagination
    start = (page - 1) * limit
    end = start + limit
    results = results[start:end]

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
            dict1["address"] = student.address.dict()
            return dict1
    raise StudentNotFoundError(student_id)
    
@app.patch("/student/{student_id}", response_model=StudentResponse)
def partial_update_student(student_id: int, student: StudentUpdate):
    
    if student.dict(exclude_unset=True) == {}:
        raise HTTPException(status_code=400, detail="No data provided for update")

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
            if student.address is not None:
                dict1["address"] = student.address.dict()
            return dict1

    raise StudentNotFoundError(student_id)
@app.delete("/student/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    for i, dict1 in enumerate(students_lis):
        if dict1["student_id"] == student_id:
            students_lis.pop(i)
            return
    raise StudentNotFoundError(student_id)