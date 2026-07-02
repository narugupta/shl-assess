from fastapi.testclient import TestClient

from app.api.app import app

client = TestClient(app)

# --------------------------------------------------------

response = client.get("/")

print(response.status_code)

print(response.json())

# --------------------------------------------------------

response = client.get("/health")

print(response.status_code)

print(response.json())

# --------------------------------------------------------

response = client.get("/ping")

print(response.status_code)

print(response.json())

# --------------------------------------------------------

response = client.post(

    "/recommend",

    json={

        "query":"Need Java Developer assessment",

        "top_k":5

    }

)

print(response.status_code)

print(response.json())