from django import forms
from .models import Expense, Category
from django.core.exceptions import ValidationError


class ExpenseSearchForm(forms.ModelForm):

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    sort_by = forms.ChoiceField(
        choices=[('category', 'Category'), ('date', 'Date')],
        required=False,
        initial='date'  
    )
    order = forms.ChoiceField(
        choices=[('asc', 'Ascending'), ('desc', 'Descending')],
        required=False,
        initial='asc'  
    )    

    class Meta:
        model = Expense
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_from > date_to:
                raise ValidationError(
                    "The start date (date_from) cannot be later than the end date (date_to)."
                )
        return cleaned_data