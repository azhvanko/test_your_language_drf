from typing import Sequence

from django.contrib.auth import get_user_model

from ..models import TestResult


User = get_user_model()


class LanguageTestMixin:
    app_name = 'language_tests'
    default_number_all_test_types = 10
    default_number_answers = 4  # for 1 question
    default_number_questions = 20  # for 1 test type
    default_number_test_questions = 10  # for 1 test
    default_test_users_password = 'test_password'
    number_answers = default_number_all_test_types * default_number_answers
    number_published_test_types = default_number_all_test_types // 2
    number_questions = default_number_all_test_types * default_number_questions
    number_published_questions = int(number_questions * 0.8)
    number_question_answers = number_questions * default_number_answers
    users = {
        'new_user': {
            'username': 'test_user_1',
            'password': default_test_users_password,
            'email': 'test_user_1@example.com',
            'is_active': False,
            'last_login': None
        },
    }

    fixtures = [
        'language_test_types',
        'questions',
        'answers',
        'question_answers',
    ]

    @staticmethod
    def create_test_results(
            test_results: Sequence[TestResult]
    ) -> list[TestResult]:
        return TestResult.objects.bulk_create(test_results)
