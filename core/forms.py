from django import forms
from .models import Estimate, EstimateItem, Contractor, Service, EstimateDay

class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = ['client_name', 'comment']
        labels = {
            'client_name': 'Клиент',
            'comment': 'Комментарий',
        }


class EstimateItemCreateForm(forms.ModelForm):
    class Meta:
        model = EstimateItem
        fields = ['service', 'qty']
        labels = {
            'service': 'Услуга',
            'qty': 'Количество',
        }
        # labels = {
        #     'client_name': 'Клиент',
        #     'manager_name': 'Менеджер',
        #     'comment': 'Комментарий',
        # }
        # widgets = {
        #     'comment': forms.Textarea(attrs={'rows': 4}),
        # }


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
        fields = ['name', 'contact_name', 'phone', 'email', 'notes']
        labels = {
            'name': 'Название поставщика',
            'contact_name': 'Контактное лицо',
            'phone': 'Телефон',
            'email': 'E-mail',
            'notes': 'Комментарий'
        }



class ServiceCreateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'contractor',
            'name',
            'category',
            'cost_price',
            'client_price',
            'description',
            'is_active',
            'image_url',
        ]
        widgets = {
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://...',
            }),
        }
        labels = {
            'contractor': 'Поставщик',
            'name': 'Название услуги',
            'category': 'Категория',
            'cost_price': 'Себестоимость',
            'client_price': 'Цена для клиента',
            'description': 'Комментарий',
            'image_url': 'Медиа',
            'is_active': 'Активна',
        }


class ServiceUpdateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'category',
            'cost_price',
            'client_price',
            'description',
            'is_active',
            'image_url',
        ]
        widgets = {
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://...',
            }),
        }
        labels = {
            'category': 'Категория',
            'cost_price': 'Себестоимость',
            'client_price': 'Цена для клиента',
            'description': 'Комментарий',
            'image_url': 'Медиа',
            'is_active': 'Активна',
        }


class ServiceForContractorCreateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'category', 'cost_price', 'client_price', 'description', 'is_active', 'image_url']
        widgets = {
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://...',
            }),
        }
        labels = {
            'name': 'Название услуги',
            'category': 'Категория',
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


from .models import ServiceCategory

class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'sort_order']
        labels = {
            'name': 'Название категории',
            'sort_order': 'Порядок сортировки',
        }