from typing import OrderedDict

from rest_framework import serializers

from .models import (
    Answer,
    LanguageTestType,
    Question,
    QuestionAnswer,
    TestResult
)


class LanguageTestTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LanguageTestType
        fields = '__all__'


class LanguageTestTypeReadOnlySerializer(serializers.ModelSerializer):

    class Meta:
        model = LanguageTestType
        exclude = ('is_published',)
        read_only_fields = ('name',)


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = '__all__'


class AnswerReadOnlySerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = '__all__'
        read_only_fields = ('name',)


class QuestionAnswerSerializer(serializers.Serializer):
    answer = serializers.CharField(min_length=1, max_length=64, required=True)
    is_right_answer = serializers.BooleanField(required=True)


class QuestionAnswerReadOnlySerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    answer_id = serializers.IntegerField(min_value=1, required=False)


class QuestionReadOnlySerializer(serializers.ModelSerializer):
    answers = AnswerReadOnlySerializer(read_only=True, many=True)

    class Meta:
        model = Question
        fields = ('id', 'question', 'answers',)
        read_only_fields = ('question',)


class QuestionSerializer(serializers.ModelSerializer):
    answers = QuestionAnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = '__all__'

    @staticmethod
    def validate_answers(answers: list[OrderedDict]) -> list[OrderedDict]:
        _answers = {
            answer.get('answer'): answer.get('is_right_answer')
            for answer in answers
        }
        if len(_answers) != 4:
            raise serializers.ValidationError(
                'Invalid data. The question must have 4 answers.'
            )
        if sum(is_right_answer for is_right_answer in _answers.values()) != 1:
            raise serializers.ValidationError(
                'Invalid data. The question must have 1 correct answer. '
            )
        return answers

    def save(self, **kwargs) -> None:
        self._save_question()
        self._save_answers()
        self._save_question_answers()

    def _save_question(self) -> None:
        question = self.validated_data.get('question')
        is_published = self.validated_data.get('is_published')
        test_type = self.validated_data.get('test_type')
        Question.objects.create(
            question=question,
            is_published=is_published,
            test_type=test_type
        )

    def _save_answers(self) -> None:
        answers = {
            answer.get('answer'): answer.get('is_right_answer')
            for answer in self.validated_data.get('answers')
        }
        db_answers = Answer.objects.values('answer').filter(
            answer__in=answers.keys()
        )
        for answer in db_answers:
            answers.pop(answer['answer'])
        if answers:
            new_answers = [Answer(answer=answer) for answer in answers.keys()]
            Answer.objects.bulk_create(new_answers)

    def _save_question_answers(self) -> None:
        question = self.validated_data.get('question')
        answers = {
            answer.get('answer'): answer.get('is_right_answer')
            for answer in self.validated_data.get('answers')
        }
        db_question = Question.objects.get(question=question)
        db_answers = Answer.objects.filter(answer__in=answers.keys())
        question_answers = []
        for answer, is_right_answer in answers.items():
            for db_answer in db_answers:
                if db_answer.answer == answer:
                    question_answers.append(
                        QuestionAnswer(
                            question=db_question,
                            answer=db_answer,
                            is_right_answer=is_right_answer
                        )
                    )
                    break
        QuestionAnswer.objects.bulk_create(question_answers)


class LanguageTestSerializer(LanguageTestTypeReadOnlySerializer):
    questions = QuestionReadOnlySerializer(read_only=True, many=True)


class TestResultSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1, required=False)
    user_answers = QuestionAnswerReadOnlySerializer(many=True)

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

    def save(self) -> None:
        user_id = self.validated_data.get('user_id', None)
        if user_id is not None:
            user_answers = self.validated_data.get('user_answers')
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
