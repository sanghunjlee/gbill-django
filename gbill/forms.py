from django import forms

from .models import Bill, Item, Person
from .widgets import ButtonWidget

class DetailForm(forms.ModelForm):
    
    class Meta:
        model = Bill
        fields = ('desc', 'payee', 'amount')

        widgets = {
            'payee': forms.Select(attrs={'class': 'person-select'}),
            'desc': forms.TextInput(attrs={'class': 'label-text-form', 'readOnly': 'readOnly', 'ondblClick': 'this.readOnly=!this.readOnly'}),
            'amount': forms.NumberInput(attrs={'class': 'number-form', 'step': '0.01', 'min': '0'}),
        }

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ('desc', 'payee', 'amount')

        widgets = {
            'payee': forms.Select(attrs={'class': 'person-select'}),
        }

    desc = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'desc-form'}))
    amount = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'number-form', 'step': '0.01', 'min': '0'}))

    def __init__(self, *args, **kwargs) -> None:
        super(BillForm, self).__init__(*args, **kwargs)
        self.fields['payee'].required = False

class ItemForm(forms.ModelForm):
    is_bound = False
    class Meta:
        model = Item
        fields = ('person', 'amount')

        widgets = {
            'person': forms.Select(attrs={'class': 'person-select'}),
            'amount': forms.NumberInput(attrs={'class': 'number-form', 'step': '1', 'min': '0'}),
            'DELETE': ButtonWidget(attrs={'class': 'del-btn', 'value': 'Delete'})
        }

class IndexPersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ('name',)
    
    name = forms.CharField(label=None,required=False, widget=forms.TextInput(attrs={
        'id':'name-input-form',
        'placeholder': '+',
    }))

class BaseItemFormSet(forms.BaseInlineFormSet):
    deletion_widget = ButtonWidget(attrs={
        'value': 'Delete', 
        'class': 'form-control'
    })

    def is_valid(self):
        return super().is_valid()

    def add_fields(self, form, index):
        super().add_fields(form, index)