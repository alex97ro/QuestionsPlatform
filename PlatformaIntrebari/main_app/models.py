from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class SubmittedQuestion(models.Model):
    class Meta:
        verbose_name = _('Submitted Question')
        verbose_name_plural = _('Submitted Questions')

    question_text = models.CharField(max_length=200, verbose_name=_('Question Text'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    dt_submitted = models.DateTimeField(auto_now_add=True)
    dt_edited = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.question_text


class Answer(models.Model):
    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')

    question = models.ForeignKey(SubmittedQuestion, related_name='answers', on_delete=models.CASCADE)
    answer_text = models.TextField(verbose_name=_('Answer Text'))
    truth_value = models.BooleanField(verbose_name=_('Truth Value'))
    def __str__(self):
        return self.answer_text
