from django.urls import path, include
from rest_framework.routers import DefaultRouter

from main_app.api.viewsets.submitted_question_viewset import SubmittedQuestionViewSet

router = DefaultRouter()
router.register('questions', SubmittedQuestionViewSet)
urlpatterns = [path('', include(router.urls))]
