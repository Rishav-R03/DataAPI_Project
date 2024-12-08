# after setting project and creating a virtual environment, run this file to import data
# we start by installing important packages like pandas, numpy and matplotlib
# then we import the data

import pandas as pd
def preProcessData():
    data = pd.read_csv("random_data.csv")
    print(data.head())
    print(data.info())
# cleaning and processing data 
    data = data.dropna() # drops all rows with missing values
    return data.to_csv("cleaned_data.csv", index=False)

# create an api
