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
    date = forms.DateTimeField(localize=False,
                               input_formats=['%d/%m %H:%M'],

                               widget=forms.DateTimeInput(attrs={
                                   'class': 'form-control datetimepicker-input',
                                   'data-target': '#datetimepicker1'}, )
                               )

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
        self.fields['name'].label = "Tytuł tranzakcji"
        self.fields['desc'].label = "Opis"
        self.fields['type'].label = "Typ"
        self.fields['category'].label = "Kategoria"
        self.fields['date'].label = "Data"
        self.fields['amount'].label = "Kwota"


    def clean(self):
        cd = self.cleaned_data

        amount = cd.get("amount")

        if amount is not None:
            if amount <= 0:
                raise forms.ValidationError("Cena nie może być ujemna ani zerowa")

        return cd
