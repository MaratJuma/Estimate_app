from django import forms
from .models import Estimate, EstimateItem, Contractor, Service, EstimateDay

class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = ['client_name', 'manager_name', 'comment']


class EstimateItemCreateForm(forms.ModelForm):
    class Meta:
        model = EstimateItem
        fields = ['service', 'qty']
        labels = {
            'service': 'Услуга',
            'qty': 'Количество',
        }
        labels = {
            'client_name': 'Клиент',
            'manager_name': 'Менеджер',
            'comment': 'Комментарий',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }


class EstimateItemUpdateForm(forms.ModelForm):
    class Meta:
        model = EstimateItem
        fields = ['qty', 'client_price']
        labels = {
            'qty': 'Количество',
            'client_price': 'Цена для клиента за единицу',
        }
        widgets = {
            'qty': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'client_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }


class EstimateDayCreateForm(forms.ModelForm):
    class Meta:
        model = EstimateDay
        fields = ['title', 'description']
        labels = {
            'title': 'Название дня',
            'description': 'Описание',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: День прилёта'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Описание программы дня'}),
        }


class EstimateDayUpdateForm(forms.ModelForm):
    class Meta:
        model = EstimateDay
        fields = ['title', 'description']
        labels = {
            'title': 'Название дня',
            'description': 'Описание',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: День прилёта'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Описание программы дня'}),
        }


class ContractorForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = ['name', 'category', 'contact_name', 'phone', 'email', 'notes']
        labels = {
            'name': 'Название поставщика',
            'category': 'Категория',
            'contact_name': 'Контактное лицо',
            'phone': 'Телефон',
            'email': 'E-mail',
            'notes': 'Комментарий'
        }


# class ServiceForm(forms.ModelForm):
#     class Meta:
#         model = Service
#         fields = ['contractor', 'name', 'description', 'cost_price', 'client_price', 'is_active']
#         labels = {
#             'contractor': 'Поставщик',
#             'name': 'Название услуги',
#             'description': 'Описание',
#             'cost_price': 'Себестоимость',
#             'client_price': 'Цена для клиента',
#             'is_active': 'Активна',
#         } 


class ServiceCreateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['contractor', 'name', 'cost_price', 'client_price', 'description', 'is_active', 'image_url',]
        widgets = {
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://...',
            }),
        }
        labels = {
            'contractor': 'Поставщик',
            'name': 'Название услуги',
            'cost_price': 'Себестоимость',
            'client_price': 'Цена для клиента',
            'description': 'Комментарий',
            'image_url': 'Медиа',
            'is_active': 'Активна',
        }


class ServiceUpdateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['cost_price', 'client_price', 'description', 'is_active', 'image_url',]
        widgets = {
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://...',
            }),
        }
        labels = {
            'cost_price': 'Себестоимость',
            'client_price': 'Цена для клиента',
            'description': 'Комментарий',
            'image_url': 'Медиа',
            'is_active': 'Активна',
        }


class ServiceForContractorCreateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'cost_price', 'client_price', 'description', 'is_active', 'image_url']
        widgets = {
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://...',
            }),
            
        }
        labels = {
            'name': 'Название услуги',
            'cost_price': 'Себестоимость',
            'client_price': 'Цена для клиента',
            'description': 'Комментарий',
            'image_url': 'Медиа',
            'is_active': 'Активна',
        }


class EstimateItemQtyForm(forms.ModelForm):
    class Meta:
        model = EstimateItem
        fields = ['qty']
        labels = {
            'qty': 'Количество',
        }
        widgets = {
            'qty': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }