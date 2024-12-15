import random
def generate_api_key():
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    user_key = "".join(random.choice(letters) for _ in range(32))
    print(user_key)

generate_api_key()