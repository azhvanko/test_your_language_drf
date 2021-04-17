from django import forms


class QuestionAnswersInlineFormSet(forms.BaseInlineFormSet):

    def clean(self):
        super().clean()
        if self.total_error_count() > 0:
            raise forms.ValidationError(self.errors)

        number_right_answers = 0
        for answer in self.cleaned_data:
            if answer['is_right_answer']:
                number_right_answers += 1
        if number_right_answers != 1:
            if number_right_answers > 1:
                message = 'У вопроса может быть только 1 правильный ответ.'
            else:
                message = 'У вопроса должен быть 1 правильный ответ.'
            raise forms.ValidationError(
                message,
                code='invalid_number_right_answers'
            )
