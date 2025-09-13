import os
import requests
import random
import time
from faker import Faker

fake = Faker()
API = os.getenv("API_HOST", "http://api:5000")

def create():
    payload = {"name": fake.first_name(), "email": fake.email(), "value": random.randint(1,100)}
    r = requests.post(f"{API}/api/users", json=payload)
    return r

def update(name):
    payload = {"value": random.randint(100,1000)}
    requests.put(f"{API}/api/users/{name}", json=payload)

def delete(name):
    requests.delete(f"{API}/api/users/{name}")

names = []

while True:
    op = random.choices(["create","update","delete"], weights=[0.6,0.25,0.15])[0]
    if op == "create":
        r = create()
        try:
            if r.status_code in (200,201):
                data = r.json()
                # store name for updates/deletes
                if "id" in data:
                    # fetch created entry name - but we only need name for update/delete; hack: generate names list
                    pass
        except:
            pass
    elif op == "update" and names:
        name = random.choice(names)
        update(name)
    elif op == "delete" and names:
        name = random.choice(names)
        delete(name)
    time.sleep(random.uniform(0.5,2.5))
