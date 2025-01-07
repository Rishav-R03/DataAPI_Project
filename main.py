# creating a basic api
from fastapi import FastAPI, HTTPException,Depends, Query, Request,requests,File,UploadFile,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing import Optional
import pandas as pd
from datetime import datetime,timedelta
from sqlalchemy import text
from jose import JWTError,jwt
# from passlib.context import CryptContext
import os
import schemas
import schemas
from passlib.hash import bcrypt
import models
from sqlalchemy.orm import Session
from models import User,CSVData
from database import Base, engine, SessionLocal
# import preprocess_data
from sqlalchemy.engine.row import Row
from schemas import user, loginReq
from dotenv import load_dotenv
from pydantic import BaseModel
# from passlib.context import CryptContext
from passlib.context import CryptContext
from fastapi import  File, UploadFile
from fastapi.responses import StreamingResponse
from io import StringIO, BytesIO
import random
Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

app=FastAPI()

#loading api key
load_dotenv()
API_KEY = os.getenv("API_KEY")

#home page
@app.get("/data")
def get_data(db: Session = Depends(get_session)):
    """
    Fetch all data from the csv_data table and return it as a list of records.
    """
    try:
        # Fetch all rows from the csv_data table
        result = db.execute(text("SELECT * FROM csv_data")).fetchall()

        # Convert SQLAlchemy result to a list of dictionaries
        all_data = [dict(row._mapping) for row in result]

        # Check if the table is empty
        if not all_data:
            return {"message": "No data found in the table."}

        return {"data": all_data}
    except Exception as e:
        return {"error": str(e)}


#using assignment operator in the path parameters makes it optional
#about page
@app.get("/about")
def about_project():
    return {"message":"This is a project to serve a csv data as an API"}


#data endpoints to get all data
@app.get("/") # test passed
def get_data():
    return {"message":"This is a project to serve a csv data as an API"}

# filter data by column
# testing : http://127.0.0.1:8000/data/filter?column=author&value=dua
# http://127.0.0.1:8000/data/filter?column=author&value=dua
'''
    the filter endpoint below works by filtering the data based on the column and value provided in the request.
    If no matching records are found, it returns a message indicating that no matching records were found.
    Otherwise, it returns the filtered data as a list of dictionaries.

'''
@app.get("/data/filter")
def filter_data(column: str, value: str, db: Session = Depends(get_session)):
    """
    Filter data in the database based on a column and its value.
    """
    try:
        # Validate column existence by querying information_schema
        valid_column = db.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'csv_data' AND column_name = :column"
            ),
            {"column": column},
        ).fetchone()

        if not valid_column:
            return {"error": f"Column '{column}' does not exist in the table."}

        # Use a dynamic query to filter data
        query = text(f"SELECT * FROM csv_data WHERE {column} = :value")
        result = db.execute(query, {"value": value}).fetchall()

        # Convert SQLAlchemy result to a list of dictionaries
        filtered_data = [dict(row._mapping) for row in result]  # Use _mapping for Row objects

        if not filtered_data:
            return {"message": "No matching records found."}

        return {"filtered_data": filtered_data}

    except Exception as e:
        return {"error": str(e)}



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
@app.get("/paginate_csv")
async def paginate_csv(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Paginate the processed CSV data.
    """
    offset = (page - 1) * page_size
    query = text(f"SELECT * FROM csv_data LIMIT :limit OFFSET :offset")
    result = db.execute(query, {"limit": page_size, "offset": offset}).fetchall()
    
    # Convert each SQLAlchemy Row object to a dictionary
    return [dict(row._mapping) for row in result]  # Use `_mapping` for Row objects


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

# @app.get("/data/secure") # test passed
# def get_secure_data(api_key: str = Query(...)):
#     print(f"Received api_key: {api_key}")
#     if api_key != API_KEY:
#         raise HTTPException(status_code=401, detail="Invalid API key")
#     return data.to_dict(orient="records")

# adding dynamic query parameters


# print(API_KEY)
#http://127.0.0.1:8000/data/query?api_key=rishav1439&department=Marketing&city=New%20York
#http://127.0.0.1:8000/data/query?api_key=rishav1439&author=dua&language=japanese
'''
    the query endpoint below works by validating the API key provided in the request.
    Here it takes 2 inputs api_key and request(which is initially none but later used to extract the query parameters)
    It will return data as per user's query
'''

@app.get("/query_csv")
async def query_csv(column: str, condition: str, value: str, db: Session = Depends(get_session)):
    """
    Perform advanced queries on the database.
    """
    try:
        # Validate column existence by querying information_schema
        valid_column = db.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'csv_data' AND column_name = :column"
            ),
            {"column": column},
        ).fetchone()

        if not valid_column:
            return {"error": f"Column '{column}' does not exist in the table."}

        # Allow only specific conditions for safety
        allowed_conditions = ["=", ">", "<", ">=", "<=", "<>"]
        if condition not in allowed_conditions:
            return {"error": f"Condition '{condition}' is not allowed."}

        # Use a dynamic query to filter data with parameterized value
        query = text(f"SELECT * FROM csv_data WHERE {column} {condition} :value")
        result = db.execute(query, {"value": value}).fetchall()

        # Convert SQLAlchemy result to a list of dictionaries
        data = [dict(row._mapping) for row in result]

        if not data:
            return {"message": "No matching records found."}

        return {"query_result": data}

    except Exception as e:
        return {"error": str(e)}

    # return {"message": "No matching records found"}


# import requests

def test_get_data():
    url = "http://127.0.0.1:8000/data"
    response = requests.get(url)
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Verify it returns a list of records

# get user by email

def get_hashed_password(password):
    return bcrypt.hash(password)

SECRET_KEY = "BSHLANMlnT575K7NKzxCD58mys8Deg58"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_db = {
    "tim":{
        "username":"tim",
        "email":"tim@tim",
        "hashed_password":"tim",
        "disabled":False
    }
}

@app.post("/register")
def register_user(user: schemas.user, session: Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password = get_hashed_password(user.password)

    new_user = models.User(username=user.username, email=user.email, password=encrypted_password )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message":"user created successfully"}


@app.post("/login")
def login_user(login_req: schemas.loginReq):
    pass

@app.get("/generateAPIKey")
def generate_api_key():
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    user_key = "".join(random.choice(letters) for _ in range(32))
    print(user_key)

generate_api_key()

@app.post("/process_csv")
async def process_csv(file: UploadFile = File(...),db:Session = Depends(get_session)):
    """
    Endpoint to upload and preprocess a CSV file.
    """
    global processed_data
    # Read the uploaded file
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        # Preprocessing: Example steps (customize as needed)
        df.dropna(inplace=True)  # Remove rows with missing values
        df.drop_duplicates(inplace=True)  # Remove duplicate rows
        df = df.rename(columns=lambda x: x.strip())  # Strip column names of extra spaces
        rows_to_insert = [
            CSVData(
                name=row["Name"],
                age=row["Age"],
                occupation=row["Occupation"],
                city=row["City"],
                salary=row["Salary"],
                married=row["Married"] == "T"
            )
            for _, row in df.iterrows()
        ]
        db.add_all(rows_to_insert)  # Add all rows at once
        db.commit() 
        return {"message": "Data processed successfully"}
        db.refresh()
        # output = BytesIO()
        # df.to_csv(output, index=False)
        # output.seek(0)

        # Return the processed CSV as a response
        # return StreamingResponse(
        #     output, 
        #     media_type="text/csv", 
        #     headers={"Content-Disposition": f"attachment; filename=cleaned_{file.filename}"}
        # )
    except Exception as e:
        return {"error": str(e)}


de
