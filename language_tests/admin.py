from django.contrib import admin

from .forms import QuestionAnswersInlineFormSet
from .models import (
    Answer,
    LanguageTestType,
    Question,
    QuestionAnswer,
    TestResult
)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer',)
    list_display_links = ('id', 'answer',)
    search_fields = ('answer',)


class LanguageTestTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_published',)
    list_display_links = ('id', 'name',)
    list_editable = ('is_published',)
    search_fields = ('name',)


class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'solution_date',)
    list_display_links = ('user', 'question',)
    list_filter = ('user',)
    search_fields = ('user__username', 'question__question',)


class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'is_right_answer',)
    list_display_links = ('question',)
    list_editable = ('is_right_answer',)
    search_fields = ('question__question', 'answer__answer',)


class QuestionAnswerInline(admin.StackedInline):
    can_delete = False
    formset = QuestionAnswersInlineFormSet
    max_num = 4
    min_num = 4
    model = QuestionAnswer


class QuestionAdmin(admin.ModelAdmin):
    inlines = (QuestionAnswerInline,)
    list_display = ('id', 'question', 'test_type', 'is_published',)
    list_display_links = ('id', 'question',)
    list_editable = ('is_published',)
    list_filter = ('is_published', 'test_type',)
    search_fields = ('question', 'test_type__name',)


admin.site.register(Answer, AnswerAdmin)
admin.site.register(LanguageTestType, LanguageTestTypeAdmin)
admin.site.register(TestResult, TestResultAdmin)
admin.site.register(QuestionAnswer, QuestionAnswerAdmin)
admin.site.register(Question, QuestionAdmin)
