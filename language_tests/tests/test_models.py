from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import (
    Answer,
    LanguageTestType,
    Question,
    QuestionAnswer,
    TestResult
)
from ..validators import validate_question
from .utils import LanguageTestMixin


User = get_user_model()


class LanguageTestModelsTestCase(LanguageTestMixin, TestCase):
    """
    Helper base class for all the follow test cases.
    """

    @classmethod
    def setUpTestData(cls):
        cls.new_user = User.objects.create_user(**cls.users['new_user'])
        cls.test_results = [
            TestResult(
                question_id=i,
                answer_id=1,
                user=cls.new_user
            )
            for i in range(1, cls.default_number_test_questions + 1)
        ]

        cls.create_test_results(cls.test_results)


class LanguageTestTypeTest(LanguageTestModelsTestCase):

    def test_object_creation(self):
        language_test_type = LanguageTestType.objects.create(
            name='test_type_0',
            is_published=True
        )
        self.assertEqual(language_test_type.name, 'test_type_0')
        self.assertTrue(language_test_type.is_published)

    def test_objects_creation(self):
        all_test_types = LanguageTestType.objects.all()
        published_test_types = all_test_types.filter(is_published=True)
        self.assertEqual(
            len(all_test_types),
            self.default_number_all_test_types
        )
        self.assertEqual(
            len(published_test_types),
            self.number_published_test_types
        )

    def test_name(self):
        language_test_type = LanguageTestType.objects.get(id=1)
        field_label = language_test_type._meta.get_field('name').verbose_name
        max_length = language_test_type._meta.get_field('name').max_length
        unique = language_test_type._meta.get_field('name').unique
        self.assertEqual(field_label, 'Тип теста')
        self.assertEqual(max_length, 128)
        self.assertTrue(unique)

    def test_is_published(self):
        language_test_type = LanguageTestType.objects.get(id=1)
        field_label = language_test_type._meta.get_field('is_published').verbose_name
        default = language_test_type._meta.get_field('is_published').default
        self.assertEqual(field_label, 'Опубликован')
        self.assertTrue(default)

    def test_meta(self):
        self.assertEqual(LanguageTestType._meta.verbose_name, 'Тип теста')
        self.assertEqual(LanguageTestType._meta.verbose_name_plural, 'Типы тестов')

    def test_str_method(self):
        language_test_type = LanguageTestType.objects.get(id=1)
        self.assertEqual(str(language_test_type), 'test_type_1')


class AnswerTest(LanguageTestModelsTestCase):

    def test_object_creation(self):
        answer = Answer.objects.create(answer='answer_0')
        self.assertEqual(answer.answer, 'answer_0')

    def test_objects_creation(self):
        all_answers = Answer.objects.all()
        self.assertEqual(len(all_answers), self.number_answers)

    def test_answer(self):
        answer = Answer.objects.get(id=1)
        field_label = answer._meta.get_field('answer').verbose_name
        max_length = answer._meta.get_field('answer').max_length
        unique = answer._meta.get_field('answer').unique
        self.assertEqual(field_label, 'Ответ')
        self.assertEqual(max_length, 64)
        self.assertTrue(unique)

    def test_meta(self):
        self.assertEqual(Answer._meta.verbose_name, 'Ответ')
        self.assertEqual(Answer._meta.verbose_name_plural, 'Ответы')

    def test_str_method(self):
        answer = Answer.objects.get(id=1)
        self.assertEqual(str(answer), 'answer_1')


class QuestionTest(LanguageTestModelsTestCase):

    def test_object_creation(self):
        question = Question.objects.create(
            question='question ___ 0',
            is_published=True,
            test_type_id=1
        )
        self.assertEqual(question.question, 'question ___ 0')
        self.assertEqual(question.test_type.name, 'test_type_1')
        self.assertTrue(question.is_published)

    def test_objects_creation(self):
        all_questions = Question.objects.all()
        active_questions = all_questions.filter(is_published=True)
        self.assertEqual(len(all_questions), self.number_questions)
        self.assertEqual(len(active_questions), self.number_published_questions)

    def test_question(self):
        question = Question.objects.get(id=1)
        field_label = question._meta.get_field('question').verbose_name
        max_length = question._meta.get_field('question').max_length
        unique = question._meta.get_field('question').unique
        self.assertEqual(field_label, 'Вопрос')
        self.assertEqual(max_length, 256)
        self.assertTrue(unique)

    def test_question_validator(self):
        invalid_questions = [
            'question',
            'question __ 1',
            'question ____ 1',
            '1234567890',
            '12345 ___ 6789',
            'test question'
        ]
        for question in invalid_questions:
            with self.assertRaises(ValidationError):
                validate_question(question)

    def test_is_published(self):
        question = Question.objects.get(id=1)
        field_label = question._meta.get_field('is_published').verbose_name
        default = question._meta.get_field('is_published').default
        self.assertEqual(field_label, 'Опубликован')
        self.assertTrue(default)

    def test_test_type(self):
        question = Question.objects.get(id=1)
        field_label = question._meta.get_field('test_type').verbose_name
        null = question._meta.get_field('test_type').null
        fk = question._meta.get_field('test_type').many_to_one
        self.assertEqual(question.test_type_id, 1)
        self.assertEqual(field_label, 'Тип теста')
        self.assertTrue(null)
        self.assertTrue(fk)

    def test_answers(self):
        question = Question.objects.get(id=1)
        m2m = question._meta.get_field('answers').many_to_many
        self.assertTrue(m2m)

    def test_meta(self):
        self.assertEqual(Question._meta.verbose_name, 'Вопрос')
        self.assertEqual(Question._meta.verbose_name_plural, 'Вопросы')

    def test_str_method(self):
        question = Question.objects.get(id=1)
        self.assertEqual(str(question), 'question ___ 1')


class QuestionAnswerTest(LanguageTestModelsTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.new_test_type = LanguageTestType.objects.create(name='test_type_0')
        cls.new_question = Question.objects.create(
            question='question ___ 0',
            test_type=cls.new_test_type
        )
        cls.new_answer = Answer.objects.create(answer='answer_0')

    def test_object_creation(self):
        question_answer = QuestionAnswer.objects.create(
            question=self.new_question,
            answer=self.new_answer,
            is_right_answer=True
        )
        self.assertEqual(question_answer.question.question, 'question ___ 0')
        self.assertEqual(question_answer.answer.answer, 'answer_0')
        self.assertTrue(question_answer.is_right_answer)

    def test_objects_creation(self):
        all_question_answers = QuestionAnswer.objects.all()
        right_answers = all_question_answers.filter(is_right_answer=True)
        self.assertEqual(
            len(all_question_answers),
            self.number_question_answers
        )
        self.assertEqual(
            len(right_answers),
            self.number_question_answers // self.default_number_answers
        )

    def test_question(self):
        question_answer = QuestionAnswer.objects.get(id=1)
        fk = question_answer._meta.get_field('question').many_to_one
        self.assertTrue(fk)

    def test_answer(self):
        question_answer = QuestionAnswer.objects.get(id=1)
        fk = question_answer._meta.get_field('answer').many_to_one
        self.assertTrue(fk)

    def test_is_right_answer(self):
        question_answer = QuestionAnswer.objects.get(id=1)
        field_label = question_answer._meta.get_field('is_right_answer').verbose_name
        default = question_answer._meta.get_field('is_right_answer').default
        self.assertEqual(field_label, 'Правильный ответ')
        self.assertFalse(default)

    def test_meta(self):
        self.assertEqual(len(QuestionAnswer._meta.constraints), 2)
        self.assertEqual(QuestionAnswer._meta.verbose_name, 'Ответ на вопрос')
        self.assertEqual(
            QuestionAnswer._meta.verbose_name_plural,
            'Ответы на вопросы'
        )

    def test_str_method(self):
        question_answer = QuestionAnswer.objects.get(id=1)
        self.assertEqual(
            str(question_answer),
            (
                'Вопрос - "question ___ 1"; Ответ - "answer_1"; '
                'Правильный ответ - True'
            )
        )


class TestResultTest(LanguageTestModelsTestCase):

    def test_object_creation(self):
        question = Question.objects.first()
        answer = Answer.objects.first()
        test_result = TestResult.objects.create(
            question=question,
            answer=answer,
            user=self.new_user
        )
        self.assertEqual(test_result.user.username, 'test_user_1')
        self.assertEqual(test_result.question.question, 'question ___ 1')
        self.assertEqual(test_result.answer.answer, 'answer_1')
        self.assertIsInstance(test_result.solution_date, datetime)

    def test_objects_creation(self):
        test_results = TestResult.objects.all()
        self.assertEqual(len(test_results), len(self.test_results))

    def test_user(self):
        test_result = TestResult.objects.first()
        fk = test_result._meta.get_field('user').many_to_one
        self.assertTrue(fk)

    def test_question(self):
        test_result = TestResult.objects.first()
        fk = test_result._meta.get_field('question').many_to_one
        self.assertTrue(fk)

    def test_answer(self):
        test_result = TestResult.objects.first()
        fk = test_result._meta.get_field('answer').many_to_one
        self.assertTrue(fk)

    def test_meta(self):
        self.assertEqual(TestResult._meta.verbose_name, 'Результат теста')
        self.assertEqual(
            TestResult._meta.verbose_name_plural,
            'Результаты тестов'
        )

    def test_str_method(self):
        test_result = TestResult.objects.first()
        self.assertEqual(
            str(test_result),
            (
                'Пользователь - "test_user_1"; Вопрос - "question ___ 1"; '
                'Ответ - "answer_1"'
            )
        )
