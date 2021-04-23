from typing import OrderedDict

from rest_framework import serializers

from .models import Answer, LanguageTestType, Question, TestResult


class LanguageTestTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LanguageTestType
        exclude = ('is_published',)
        read_only_fields = ('name',)


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = '__all__'
        read_only_fields = ('name',)


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(read_only=True, many=True)

    class Meta:
        model = Question
        fields = ('id', 'question', 'answers',)
        read_only_fields = ('question',)


class LanguageTestSerializer(LanguageTestTypeSerializer):
    questions = QuestionSerializer(read_only=True, many=True)


class QuestionAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    answer_id = serializers.IntegerField(min_value=1, required=False)


class TestResultSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1, required=False)
    user_answers = QuestionAnswerSerializer(many=True)

    @staticmethod
    def validate_user_answers(user_answers: list[OrderedDict]) -> list[OrderedDict]:
        all_questions = {
            user_answer.get('question_id'): user_answer.get('answer_id', None)
            for user_answer in user_answers
        }
        if len(user_answers) != len(all_questions):
            raise serializers.ValidationError(
                'Invalid data. Got duplicate questions.'
            )

        filled_questions = {
            key: value
            for key, value in all_questions.items()
            if value is not None
        }
        question_answers = Question.objects.select_related(
            'answers'
        ).filter(
            id__in=filled_questions.keys()
        ).values(
            'id',
            'answers__id'
        )
        valid_answers_count = sum(
            question_answer['answers__id'] == filled_questions[question_answer['id']]
            for question_answer in question_answers
        )
        if len(filled_questions) != valid_answers_count:
            raise serializers.ValidationError(
                'Invalid data. Got invalid question answer id.'
            )

        return user_answers

    def save(self):
        user_id = self.validated_data.get('user_id', None)
        user_answers = self.validated_data.get('user_answers')
        if user_id is not None:
            self._save_user_answers(user_id, user_answers)

    @staticmethod
    def _save_user_answers(user_id: int, user_answers: list[OrderedDict]) -> None:
        valid_answers = []
        for user_answer in user_answers:
            answer_id = user_answer.get('answer_id', None)
            if answer_id is not None:
                valid_answers.append(
                    TestResult(
                        user_id=user_id,
                        question_id=user_answer.get('question_id'),
                        answer_id=answer_id
                    )
                )
        TestResult.objects.bulk_create(valid_answers)
