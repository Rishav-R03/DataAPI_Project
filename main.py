# creating a basic api
from fastapi import FastAPI, HTTPException, Query, Request,requests
from typing import Optional
import pandas as pd
app = FastAPI()

# data = pd.read_csv("testData.csv")
data = pd.read_csv("random_data.csv")
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")
print(f"API_KEY: {API_KEY}")
@app.get("/")
def home():
    return {"hello":"world"}

@app.get("/data") # test passed
def get_data():
    return data.to_dict(orient="records") # dict in python is json

# basic features

# filter data by column

# testing : http://127.0.0.1:8000/data/filter?column=author&value=dua
# http://127.0.0.1:8000/data/filter?column=author&value=dua
@app.get("/data/filter") # test passed
def filter_data(column: str, value: str):
    filtered_data = data[data[column] == value]
    if filtered_data.empty:
        return {"message": "No matching records found"}
    return filtered_data.to_dict(orient="records")


#pagination 
# testing : http://127.0.0.1:8000/data/paginate?limit=5&offset=0
# testing : http://127.0.0.1:8000/data/paginate?limit=5&offset=5
# testing : http://127.0.0.1:8000//data/paginate?limit=5&offset=100
@app.get("/data/paginate") # test passed
# def get_data_by_page(page_number: int, page_size: int):
def get_data_by_page(limit:int = 10, offset: int = 0):
    paginated_data = data[offset:offset+ limit]
    return paginated_data.to_dict(orient="records")
#http://127.0.0.1:8000/data/query?api_key=API_KEY&department=Marketing&city=New%20York


# http://127.0.0.1:8000/data/secure?api_key=rishav1439
# testing : http://127.0.0.1:8000/data/secure?api_key=rishav1439

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
