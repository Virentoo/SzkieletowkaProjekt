from django import forms
from .models import Transaction, Category


class FilterForm(forms.Form):
    priceFrom = forms.FloatField(required=False)
    priceTo = forms.FloatField(required=False)
    dateFrom = forms.DateField(required=False)
    dateTo = forms.DateField(required=False)
    timeFrom = forms.TimeField(required=False)
    timeTo = forms.TimeField(required=False)


class NewTransactionForm(forms.ModelForm):

    date = forms.DateTimeField(widget=forms.DateTimeInput)

    class Meta:
        model = Transaction
        fields = [
            'name',
            'desc',
            'type',
            'category',
            'date',
            'amount'
        ]

    def __init__(self, user, *args, **kwargs):
        super(NewTransactionForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
    #
    # def clean(self, *args, **kwargs):
    #     # amount = self.cleaned_data.get('amount')
    #
    #     # if amount < 0:
    #     #     raise forms.ValidationError("Cena nie może być ujemna")
    #     return super(NewTransactionForm, self).clean(*args, **kwargs)






