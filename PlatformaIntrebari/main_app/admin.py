from django.contrib import admin

from main_app.models import SubmittedQuestion, Answer

# Register your models here.
class AnswerInline(admin.TabularInline):  # or admin.StackedInline
    model = Answer
    extra = 1  # default number of empty forms to display

@admin.register(SubmittedQuestion)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

admin.site.register(Answer)