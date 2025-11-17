from django.http import JsonResponse
from rest_framework import viewsets, status
from rapidfuzz import fuzz

from main_app.models import SubmittedQuestion, Answer
from main_app.api.serializers import SubmittedQuestionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class SubmittedQuestionViewSet(viewsets.ModelViewSet):
    queryset = SubmittedQuestion.objects.all()
    serializer_class = SubmittedQuestionSerializer

    '''Metoda de validare. Se verifica payloadul pentru valori nule sau numar incorect de valori de adevar'''

    @staticmethod
    def submission_is_valid(request_data):
        question = request_data.get('question')
        first_answer = request_data.get('first_answer')
        second_answer = request_data.get('second_answer')
        third_answer = request_data.get('third_answer')
        fourth_answer = request_data.get('fourth_answer')

        if None in [question, first_answer, second_answer, third_answer, fourth_answer]:
            return None, False, "Missing question or answers"

        answer_tuples = [
            (first_answer.get("answer"), first_answer.get("truth_value")),
            (second_answer.get("answer"), second_answer.get("truth_value")),
            (third_answer.get("answer"), third_answer.get("truth_value")),
            (fourth_answer.get("answer"), fourth_answer.get("truth_value")),
        ]

        if any(ans is None or ans[0] is None or ans[1] is None for ans in answer_tuples):
            return None, False, "Answer text or truth_value is missing"

        truth_values = [ans[1] for ans in answer_tuples]
        true_count = sum(1 for val in truth_values if val is True)
        false_count = sum(1 for val in truth_values if val is False)
        if true_count != 1 or false_count != 3:
            return None, False, "There must be exactly 1 correct answer and 3 incorrect answers"

        for existing_question in SubmittedQuestion.objects.all():
            similarity = fuzz.token_sort_ratio(existing_question.question_text, question)
            print(similarity)
            if similarity > 75:
                return None, False, f"Question is too similar to an existing question: '{existing_question.question_text}'"

        return answer_tuples, True, "Valid submission"

    '''Endpointul de submit
        Exemplu de body payload:
                            {
                          "question": "Care este capitala Franței?",
                          "first_answer": {
                            "answer": "Berlin",
                            "truth_value": null
                          },
                          "second_answer": {
                            "answer": "Madrid",
                            "truth_value": false
                          },
                          "third_answer": {
                            "answer": "Paris",
                            "truth_value": true
                          },
                          "fourth_answer": {
                            "answer": "Roma",
                            "truth_value": false
                          }
                        }
'''
    @action(detail=False, methods=['post'], url_name='submit', url_path='submit')
    def submit(self, request):
        question = request.data.get('question')
        answer_tuples, is_valid, message= self.submission_is_valid(request.data)
        if is_valid:
            new_question = SubmittedQuestion(question_text=question)
            new_question.save()
            for answer, truth_value in answer_tuples:
                Answer.objects.create(question=new_question, answer_text=answer, truth_value=truth_value)
            return JsonResponse({'message': message}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': message}, status=status.HTTP_400_BAD_REQUEST)
