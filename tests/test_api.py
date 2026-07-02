"""
API Integration Tests

Tests the FastAPI application using TestClient.
"""

from fastapi.testclient import TestClient

from app.api.app import app


client = TestClient(app)


# ==========================================================
# Root
# ==========================================================

def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"

    assert "version" in data

    assert "name" in data


# ==========================================================
# Health
# ==========================================================

def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

    assert data["planner_ready"] is True

    assert data["retriever_ready"] is True

    assert data["generator_ready"] is True


# ==========================================================
# Ping
# ==========================================================

def test_ping():

    response = client.get("/ping")

    assert response.status_code == 200

    assert response.json()["message"] == "pong"


# ==========================================================
# Recommendation
# ==========================================================

def test_recommend_java():

    payload = {

        "query": "Need Java Developer assessment under 30 minutes",

        "conversation_history": [],

        "top_k": 5

    }

    response = client.post(

        "/recommend",

        json=payload

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert "message" in data

    assert "recommendations" in data

    assert "verified" in data

    assert isinstance(

        data["recommendations"],

        list

    )

    if data["recommendations"]:

        recommendation = data["recommendations"][0]

        assert "name" in recommendation

        assert "url" in recommendation

        assert "confidence" in recommendation

        assert "reason" in recommendation


# ==========================================================
# Empty Query
# ==========================================================

def test_empty_query():

    payload = {

        "query": "",

        "conversation_history": [],

        "top_k": 5

    }

    response = client.post(

        "/recommend",

        json=payload

    )

    # Depending on your planner this may return
    # either a clarification or a validation error.

    assert response.status_code in [

        200,

        422

    ]


# ==========================================================
# Missing Query
# ==========================================================

def test_invalid_request():

    response = client.post(

        "/recommend",

        json={}

    )

    assert response.status_code == 422


# ==========================================================
# Large top_k
# ==========================================================

def test_large_top_k():

    payload = {

        "query":"Java Developer",

        "top_k":50

    }

    response = client.post(

        "/recommend",

        json=payload

    )

    # Pydantic validation should reject this
    # because top_k <= 20.

    assert response.status_code == 422


# ==========================================================
# Conversation History
# ==========================================================

def test_conversation_history():

    payload = {

        "query":"Actually make it under 20 minutes",

        "conversation_history":[

            "Need Java Developer assessment",

            "English (USA)",

            "Mid Professional"

        ],

        "top_k":5

    }

    response = client.post(

        "/recommend",

        json=payload

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True