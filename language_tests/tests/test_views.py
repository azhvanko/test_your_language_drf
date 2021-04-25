import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .utils import LanguageTestMixin


User = get_user_model()


class LanguageTestViewsMixin(LanguageTestMixin):

    @classmethod
    def setUpTestData(cls):
        cls.active_user = User.objects.create_user(**cls.users['active_user'])
        cls.admin = User.objects.create_user(**cls.users['admin'])
        cls.active_user_token = Token.objects.create(user=cls.active_user)
        cls.admin_token = Token.objects.create(user=cls.admin)


class AnswerTest(LanguageTestViewsMixin, APITestCase):
    path_name = 'create_answer'
    new_answer = {'answer': 'new_answer'}

    def test_view_url_exists_at_desired_location(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )
        login = self.client.login(
            username=self.admin.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            '/tests/add/answer/',
            self.new_answer,
            format='json'
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['answer'], self.new_answer['answer'])

    def test_view_url_accessible_by_name(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )
        login = self.client.login(
            username=self.admin.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            reverse(self.path_name),
            self.new_answer,
            format='json'
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['answer'], self.new_answer['answer'])

    def test_HTTP403_if_not_superuser(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.active_user_token.key
        )
        login = self.client.login(
            username=self.active_user.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            reverse(self.path_name),
            self.new_answer,
            format='json'
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 403)


class LanguageTestTest(LanguageTestViewsMixin, APITestCase):
    path_name = 'language_test'

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/tests/1/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        url = reverse(self.path_name, kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_test_type(self):
        url = reverse(
            self.path_name,
            kwargs={'pk': self.default_number_all_test_types + 1}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_HTTP404_for_not_published_test_type(self):
        url = reverse(
            self.path_name,
            kwargs={'pk': self.number_published_test_types + 1}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_active_language_test_type_list(self):
        url = reverse(self.path_name, kwargs={'pk': 1})
        response = self.client.get(url)
        language_test = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(language_test['name'], 'test_type_1')
        self.assertEqual(
            len(language_test['questions']),
            self.default_number_test_questions
        )
        self.assertNotEqual(
            language_test['questions'],
            sorted(language_test['questions'], key=lambda x: x['id'])
        )


class LanguageTestTypeListTest(LanguageTestViewsMixin, APITestCase):
    path_name = 'language_test_type_list'

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/tests/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        url = reverse(self.path_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_active_language_test_type_list(self):
        url = reverse(self.path_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), self.number_published_test_types)


class LanguageTestTypeTest(LanguageTestViewsMixin, APITestCase):
    path_name = 'create_language_test_type'
    new_test_type = {'name': 'new_test_type', 'is_published': True}

    def test_view_url_exists_at_desired_location(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )
        login = self.client.login(
            username=self.admin.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            '/tests/add/test-type/',
            self.new_test_type,
            format='json'
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], self.new_test_type['name'])
        self.assertEqual(
            response.json()['is_published'],
            self.new_test_type['is_published']
        )

    def test_view_url_accessible_by_name(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )
        login = self.client.login(
            username=self.admin.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            reverse(self.path_name),
            self.new_test_type,
            format='json'
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], self.new_test_type['name'])
        self.assertEqual(
            response.json()['is_published'],
            self.new_test_type['is_published']
        )

    def test_HTTP403_if_not_superuser(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.active_user_token.key
        )
        login = self.client.login(
            username=self.active_user.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            reverse(self.path_name),
            self.new_test_type,
            format='json'
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 403)


class QuestionTest(LanguageTestViewsMixin, APITestCase):
    path_name = 'create_question'
    new_question = {
        'question': 'new question ___ 1',
        'is_published': True,
        'test_type': 1,  # id
        'answers': [
            {'answer': 'answer_1', 'is_right_answer': True, },
            {'answer': 'answer_2', 'is_right_answer': False, },
            {'answer': 'answer_3', 'is_right_answer': False, },
            {'answer': 'answer_4', 'is_right_answer': False, },
        ],
    }

    def test_view_url_exists_at_desired_location(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )
        login = self.client.login(
            username=self.admin.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            '/tests/add/question/',
            self.new_question,
            format='json'
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.new_question)

    def test_view_url_accessible_by_name(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )
        login = self.client.login(
            username=self.admin.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            reverse(self.path_name),
            self.new_question,
            format='json'
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.new_question)

    def test_HTTP403_if_not_superuser(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.active_user_token.key
        )
        login = self.client.login(
            username=self.active_user.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            reverse(self.path_name),
            self.new_question,
            format='json'
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 403)


class TestResultTest(LanguageTestViewsMixin, APITestCase):
    path_name = 'test_result'

    def get_answers(self, key: str) -> tuple[dict, list]:
        user_answers = {
            # all answers correct
            'correct': {
                'user_answers': [
                    {'question_id': i, 'answer_id': 1, }
                    for i in range(1, self.default_number_test_questions + 1)
                ]
            },
            # all answers wrong
            'wrong': {
                'user_answers': [
                    {'question_id': i, 'answer_id': 4, }
                    for i in range(1, self.default_number_test_questions + 1)
                ]
            },
            # all answers empty
            'empty': {
                'user_answers': [
                    {'question_id': i, }
                    for i in range(1, self.default_number_test_questions + 1)
                ]
            },
        }
        return user_answers[key], user_answers['correct']['user_answers']

    def test_HTTP404_for_GET_request(self):
        response = self.client.get('/tests/result/')
        self.assertEqual(response.status_code, 405)

    def test_HTTP404_for_GET_request_by_name(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 405)

    def test_empty_POST_request(self):
        response = self.client.post(
            reverse(self.path_name),
            {},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('user_answers', response.json())

    def test_list_correct_answers(self):
        for key in ('correct', 'wrong', 'empty'):
            user_answers, right_answers = self.get_answers(key)
            response = self.client.post(
                reverse(self.path_name),
                user_answers,
                format='json'
            )
            _right_answers = sorted(
                response.json()['right_answers'],
                key=lambda x: x['question_id']
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(right_answers, _right_answers)

    def test_correct_answers_in_response(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.active_user_token.key
        )
        user_answers, right_answers = self.get_answers('wrong')
        login = self.client.login(
            username=self.active_user.username,
            password=self.default_test_users_password
        )
        response = self.client.post(
            reverse(self.path_name),
            user_answers,
            format='json'
        )
        _right_answers = sorted(
            response.json()['right_answers'],
            key=lambda x: x['question_id']
        )
        self.assertTrue(login)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(right_answers, _right_answers)
