from django import forms
from .models import Transaction, Category
from .widgets import BootstrapDateTimePickerInput
from tempus_dominus.widgets import DateTimePicker


class FilterForm(forms.Form):
    priceFrom = forms.FloatField(required=False)
    priceTo = forms.FloatField(required=False)
    dateFrom = forms.DateField(required=False)
    dateTo = forms.DateField(required=False)
    timeFrom = forms.TimeField(required=False)
    timeTo = forms.TimeField(required=False)


class NewTransactionForm(forms.ModelForm):

    date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], widget=BootstrapDateTimePickerInput())

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

    def clean(self):
        cd = self.cleaned_data

        amount = cd.get("amount")

        if amount is not None:
            if amount <= 0:
                raise forms.ValidationError("Cena nie może być ujemna ani zerowa")

        return cd


class DateForm(forms.Form):
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )






