from django import forms


class FilterForm(forms.Form):
    priceFrom = forms.FloatField(required=False)
    priceTo = forms.FloatField(required=False)
    dateFrom = forms.DateField(required=False)
    dateTo = forms.DateField(required=False)
    timeFrom = forms.TimeField(required=False)
    timeTo = forms.TimeField(required=False)
    transaction_type = forms.CharField(required=False)
    recCategory = forms.CharField(required=False)
    remCategory = forms.CharField(required=False)
    monthly2= forms.CharField(required=False)








