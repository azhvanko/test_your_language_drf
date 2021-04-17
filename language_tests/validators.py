import re

from django.core.exceptions import ValidationError


def validate_question(question: str) -> None:
    underscore_pattern = r'^(?:[^_]+)?(?:___){1}(?:[^_]+)?$'
    content_pattern = r'^(?:[^a-z]*[a-z]+[^a-z]*)+$'

    if len(question) <= 8:
        raise ValidationError(
            'Длина вопроса должна быть больше 8 символов.',
            code='invalid_question_length'
        )
    if not re.search(underscore_pattern, question, re.IGNORECASE):
        raise ValidationError(
            'Вопрос должен содержать 1 разделитель, состоящий из 3 нижних '
            'подчёркиваний (другое количество подчёркиваний не допускается).',
            code='invalid_question_underscore'
        )
    if not re.search(content_pattern, question, re.IGNORECASE):
        raise ValidationError(
            'Вопрос не должен состоять только из нижних подчёркиваний, '
            'пробелов или знаков препинания.',
            code='invalid_question_text'
        )
