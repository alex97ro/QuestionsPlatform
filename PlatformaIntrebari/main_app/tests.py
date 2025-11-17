import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from main_app.models import SubmittedQuestion, Answer

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def existing_question(db):
    return SubmittedQuestion.objects.create(question_text="What is the density of water?")

@pytest.mark.django_db
def test_submit_valid_question(api_client):
    url = reverse('questions-submit')
    payload = {
        "question": "What is the capital of France?",
        "first_answer": {"answer": "Berlin", "truth_value": False},
        "second_answer": {"answer": "Madrid", "truth_value": False},
        "third_answer": {"answer": "Paris", "truth_value": True},
        "fourth_answer": {"answer": "Rome", "truth_value": False}
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Valid submission"
    question = SubmittedQuestion.objects.get(question_text="What is the capital of France?")
    answers = Answer.objects.filter(question=question)
    assert answers.count() == 4
    assert answers.get(answer_text="Paris").truth_value

@pytest.mark.django_db
def test_submit_missing_answer(api_client):
    url = reverse('questions-submit')
    payload = {
        "question": "Incomplete question?",
        "first_answer": {"answer": "Option 1", "truth_value": True},
        "second_answer": {"answer": "Option 2", "truth_value": False},
        "third_answer": None,
        "fourth_answer": {"answer": "Option 4", "truth_value": False}
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Missing question or answers" in response.json()["message"]

@pytest.mark.django_db
def test_submit_similar_question(api_client, existing_question):
    url = reverse('questions-submit')
    payload = {
        "question": "The density of water is?",
        "first_answer": {"answer": "1 g/cm³", "truth_value": True},
        "second_answer": {"answer": "0.5 g/cm³", "truth_value": False},
        "third_answer": {"answer": "2 g/cm³", "truth_value": False},
        "fourth_answer": {"answer": "0 g/cm³", "truth_value": False}
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "too similar to an existing question" in response.json()["message"]

@pytest.mark.django_db
def test_submit_invalid_answer_counts(api_client):
    url = reverse('questions-submit')
    payload = {
        "question": "Invalid counts question?",
        "first_answer": {"answer": "A", "truth_value": True},
        "second_answer": {"answer": "B", "truth_value": True},
        "third_answer": {"answer": "C", "truth_value": False},
        "fourth_answer": {"answer": "D", "truth_value": False}
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "exactly 1 correct answer and 3 incorrect answers" in response.json()["message"]

@pytest.mark.django_db
def test_submit_answer_with_missing_value(api_client):
    url = reverse('questions-submit')

    payload = {
        "question": "Question with missing answer value",
        "first_answer": {"answer": "Option 1", "truth_value": False},
        "second_answer": {"answer": "Option 2", "truth_value": False},
        "third_answer": {"answer": None, "truth_value": True},  # triggers the check
        "fourth_answer": {"answer": "Option 4", "truth_value": False}
    }

    response = api_client.post(url, payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Answer text or truth_value is missing" in response.json()["message"]