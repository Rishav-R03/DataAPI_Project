import pandas as pd
import random
from faker import Faker

fake = Faker()

def generate_data(num): # method to generate random data 
    data = [] # array to store data
    for _ in range(num):
        row = {
            "author": random.choice(["dua","gracey","ipsitaa","camila"]),
            "content": fake.text(max_nb_chars=50),
            "likes": random.randint(100, 10000),
            "shares": random.randint(100, 10000),
            "language":random.choice(["eng","hindi","german","japanese"])
        }   
        data.append(row)
    return data

random_data = generate_data(50) # generate 50 random data
df = pd.DataFrame(random_data) # convert to dataframe
df.to_csv("random_data.csv", index=False) # save to csv