from random import randint
from typing import Union

from django.contrib.auth.models import AnonymousUser, User
from django.db.models import QuerySet

from .models import Question, TestResult


def generate_questions_list(
        test_type_id: int,
        user: Union[AnonymousUser, User],
        questions_limit: int = 10
) -> QuerySet:
    if not user.is_anonymous:
        prev_used_questions = TestResult.objects.values(
            'question__id'
        ).filter(
            user_id=user.pk
        ).distinct()
    else:
        prev_used_questions = []

    ids = _get_ids_list(test_type_id, prev_used_questions)
    if len(ids) < questions_limit:
        ids = _get_ids_list(test_type_id, [])

    random_ids = _get_random_ids(ids, questions_limit)

    unused_questions = Question.objects.prefetch_related(
        'answers'
    ).filter(
        id__in=random_ids
    ).only(
        'id',
        'question'
    )

    return unused_questions


def _get_ids_list(
        test_type_id: int,
        questions: Union[list, QuerySet]
) -> QuerySet:
    ids = Question.objects.values(
        'id'
    ).filter(
        test_type_id=test_type_id,
        is_published=True
    ).exclude(
        id__in=questions
    )

    return ids


def _get_random_ids(ids: QuerySet, limit: int) -> list[int]:
    values = [i['id'] for i in ids]
    result = []
    min_index, max_index = 0, len(values) - 1
    while len(result) < min(limit, len(values)):
        random_id = values[randint(min_index, max_index)]
        if random_id not in result:
            result.append(random_id)

    return result
