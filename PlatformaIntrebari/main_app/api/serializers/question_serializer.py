from rest_framework import serializers
from main_app.models import SubmittedQuestion, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['answer_text', 'truth_value']


class SubmittedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmittedQuestion
        fields = '__all__'

    answers = serializers.SerializerMethodField()

    def get_answers(self, obj):
        return AnswerSerializer(obj.answers.all(), many=True).data
