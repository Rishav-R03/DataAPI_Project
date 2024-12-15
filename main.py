# creating a basic api
from fastapi import FastAPI, HTTPException, Query, Request,requests,File,UploadFile
from typing import Optional
import pandas as pd
import os
import preprocess_data
from dotenv import load_dotenv
from pydantic import BaseModel
# from passlib.context import CryptContext
from passlib.context import CryptContext
from fastapi import  File, UploadFile
from fastapi.responses import StreamingResponse
from io import StringIO, BytesIO
import random
app = FastAPI()
registered_data = []
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class user(BaseModel):
    name:str
    email:str
    password:str

class loginReq(BaseModel):
    email:str
    password:str

#importing the data
data = pd.read_csv("random_data.csv")

#loading api key
load_dotenv()
API_KEY = os.getenv("API_KEY")

#home page
@app.get("/")
def home():
    return {"message":"Welcome to my data API project!"}

#about page
@app.get("/about")
def about_project():
    return {"message":"This is a project to serve a csv data as an API"}


#data endpoints to get all data
@app.get("/data") # test passed
def get_data():
    return data.to_dict(orient="records") # dict in python is json

# filter data by column
# testing : http://127.0.0.1:8000/data/filter?column=author&value=dua
# http://127.0.0.1:8000/data/filter?column=author&value=dua
'''
    the filter endpoint below works by filtering the data based on the column and value provided in the request.
    If no matching records are found, it returns a message indicating that no matching records were found.
    Otherwise, it returns the filtered data as a list of dictionaries.

'''
@app.get("/data/filter") # test passed
def filter_data(column: str, value: str):
    filtered_data = data[data[column] == value]
    if filtered_data.empty or column not in data.columns:
        return {"message": "No matching records found"}
    return filtered_data.to_dict(orient="records")


#pagination 
# testing : http://127.0.0.1:8000/data/paginate?limit=5&offset=0
# testing : http://127.0.0.1:8000/data/paginate?limit=5&offset=5
# testing : http://127.0.0.1:8000//data/paginate?limit=5&offset=100
'''
    Paginations is used to display a subset of data from a larger dataset.
    The limit parameter specifies the number of records to be returned per page.
    The offset parameter specifies the starting index of the records to be returned.
    here function/method takes 2 inputs integers limit and offset
'''
@app.get("/data/paginate") # test passed
# def get_data_by_page(page_number: int, page_size: int):
def get_data_by_page(limit:int = 10, offset: int = 0):
    paginated_data = data[offset:offset+ limit]
    return paginated_data.to_dict(orient="records")


# http://127.0.0.1:8000/data/secure?api_key=rishav1439
# testing : http://127.0.0.1:8000/data/secure?api_key=rishav1439
'''
    the secure endpoint below works by validating the API key provided in the request.
    If the API key is invalid, it raises an HTTPException with a status code of 401 and a detail message indicating that the API key is invalid.
    Otherwise, it returns the data as a list of dictionaries.
    Query parameters are used to pass the API key as a parameter to the endpoint.
    ... is a special syntax in Python that allows you to pass a variable number of arguments to a function.
    Here function/method takes 1 input api_key
'''

@app.get("/data/secure") # test passed
def get_secure_data(api_key: str = Query(...)):
    print(f"Received api_key: {api_key}")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return data.to_dict(orient="records")

# adding dynamic query parameters


# print(API_KEY)
#http://127.0.0.1:8000/data/query?api_key=rishav1439&department=Marketing&city=New%20York
#http://127.0.0.1:8000/data/query?api_key=rishav1439&author=dua&language=japanese
'''
    the query endpoint below works by validating the API key provided in the request.
    Here it takes 2 inputs api_key and request(which is initially none but later used to extract the query parameters)
    It will return data as per user's query
'''
@app.get("/data/query") # test passed
def query_data(
    api_key: Optional[str] = Query(None),  # Make API key optional
    request: Request = None  # Use FastAPI's Request object for query parameters
):
    # Validate API key
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Extract query parameters dynamically
    filters = dict(request.query_params)
    filters.pop("api_key", None)  # Remove API key from filters

    filtered_data = data
    for key, value in filters.items():
        if key in data.columns:
            filtered_data = filtered_data[filtered_data[key] == value]

    if filtered_data.empty:
        return {"message": "No matching records found"}
    return filtered_data.to_dict(orient="records")

# import requests

def test_get_data():
    url = "http://127.0.0.1:8000/data"
    response = requests.get(url)
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Verify it returns a list of records

# get user by email
def get_user_by_email(email: str):
    for users in registered_data:
        if users["email"]==email:
            return users
    return None


@app.post("/register")
def register_user(user:user):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400,detail="User already exists")
    
    hashed_password = pwd_context.hash(user.password)
    registered_data.append({"name":user.name,"email":user.email,"password":hashed_password})
    return {"message": "User registered successfully"}


@app.post("/login")
def login_user(login_req: loginReq):
    users = get_user_by_email(login_req.email)
    if not users or not pwd_context.verify(login_req.password,users["password"]):
        raise HTTPException(status_code=401,detail="Invalid credentials")
    return {"Message":"Login successful"}

@app.get("/generateAPIKey")
def generate_api_key():
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    user_key = "".join(random.choice(letters) for _ in range(32))
    print(user_key)

generate_api_key()

@app.post("/process_csv")
async def process_csv(file: UploadFile = File(...)):
    """
    Endpoint to upload and preprocess a CSV file.
    """
    # Read the uploaded file
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        # Preprocessing: Example steps (customize as needed)
        df.dropna(inplace=True)  # Remove rows with missing values
        df.drop_duplicates(inplace=True)  # Remove duplicate rows
        df = df.rename(columns=lambda x: x.strip())  # Strip column names of extra spaces

        # Convert back to CSV
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)

        # Return the processed CSV as a response
        return StreamingResponse(
            output, 
            media_type="text/csv", 
            headers={"Content-Disposition": f"attachment; filename=cleaned_{file.filename}"}
        )
    except Exception as e:
        return {"error": str(e)}
