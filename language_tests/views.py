from typing import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch, QuerySet
from django.http import Http404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Answer, LanguageTestType, Question, QuestionAnswer
from .serializers import (
    AnswerSerializer,
    LanguageTestSerializer,
    LanguageTestTypeReadOnlySerializer,
    LanguageTestTypeSerializer,
    QuestionSerializer,
    TestResultSerializer
)
from .services import generate_questions_list


class AnswerView(generics.CreateAPIView):
    queryset = Answer.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = AnswerSerializer


class LanguageTestTypeListView(generics.ListAPIView):
    queryset = LanguageTestType.objects.filter(is_published=True)
    permission_classes = (permissions.AllowAny,)
    serializer_class = LanguageTestTypeReadOnlySerializer


class LanguageTestTypeView(generics.CreateAPIView):
    queryset = LanguageTestType.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = LanguageTestTypeSerializer


class LanguageTestView(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LanguageTestSerializer

    def get(self, request, *args, **kwargs):
        try:
            LanguageTestType.objects.get(pk=kwargs['pk'], is_published=True)
        except ObjectDoesNotExist:
            raise Http404 from None
        setattr(request, 'test_type_id', kwargs['pk'])

        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        test_type_id, user = self.request.test_type_id, self.request.user
        questions = generate_questions_list(test_type_id, user)
        prefetch = Prefetch('questions', queryset=questions)
        language_test = LanguageTestType.objects.only(
            'id',
            'name'
        ).prefetch_related(
            prefetch
        )

        return language_test


class QuestionView(generics.CreateAPIView):
    queryset = Question.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = QuestionSerializer


class TestResultView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TestResultSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_answers = serializer.data.get('user_answers')
        right_answers = self._get_right_question_answers(user_answers)

        return Response(right_answers, status=status.HTTP_201_CREATED)

    @staticmethod
    def _get_right_question_answers(
            user_answers: list[OrderedDict]
    ) -> dict[str, list[dict]]:
        question_ids = [i.get('question_id') for i in user_answers]
        right_answers = QuestionAnswer.objects.values(
            'question_id',
            'answer_id'
        ).filter(
            question_id__in=question_ids,
            is_right_answer=True
        )

        return {'right_answers': list(right_answers)}


answer = AnswerView.as_view()
language_test = LanguageTestView.as_view()
language_test_type = LanguageTestTypeView.as_view()
language_test_type_list = LanguageTestTypeListView.as_view()
question = QuestionView.as_view()
test_result = TestResultView.as_view()
