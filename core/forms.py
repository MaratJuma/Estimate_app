from django import forms
from .models import Estimate, EstimateItem, Contractor, Service, EstimateDay, CompanyProfile
from django.contrib.auth import get_user_model

class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = ['client_name', 'comment', 'contract_number']
        labels = {
            'contract_number': 'Номер договора',
            'client_name': 'Клиент',
            'comment': 'Комментарий',
        }
        error_messages = {
            'contract_number': {
                'required': 'Укажите номер договора.',
            },
        }
        widgets = {
            'contract_number': forms.TextInput(attrs={
                'placeholder': 'Например: DOG-001',
            }),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["contract_number"].disabled = True

    def clean_contract_number(self):
        value = self.cleaned_data["contract_number"].strip()
        if not value:
            raise forms.ValidationError("Укажите номер договора.")
        return value


class EstimateDuplicateForm(forms.Form):
    contract_number = forms.CharField(
        label="Номер договора",
        max_length=100,
        error_messages={
            'required': 'Укажите номер договора.',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Например: DOG-001',
        }),
    )

    def clean_contract_number(self):
        value = self.cleaned_data["contract_number"].strip()
        if not value:
            raise forms.ValidationError("Укажите номер договора.")
        return value
    

class EstimateSearchForm(forms.Form):
    q = forms.CharField(
        label='Поиск',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Клиент, менеджер, комментарий, номер договора',
        }),
    )


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
            'name': 'Название услуги',
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



from .services.admin_users import ROLE_CHOICES, get_user_role

User = get_user_model()


class AdminUserCreateForm(forms.ModelForm):
    role = forms.ChoiceField(
        label='Роль',
        choices=ROLE_CHOICES,
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'is_active']
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'is_active': 'Активен',
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Пароли не совпадают.')

        return cleaned_data


class AdminUserUpdateForm(forms.ModelForm):
    role = forms.ChoiceField(
        label='Роль',
        choices=ROLE_CHOICES,
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput,
        required=False,
    )
    new_password2 = forms.CharField(
        label='Повторите новый пароль',
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'is_active']
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'is_active': 'Активен',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['role'].initial = get_user_role(self.instance)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 or new_password2:
            if new_password1 != new_password2:
                self.add_error('new_password2', 'Пароли не совпадают.')

        return cleaned_data
    


class DatabaseImportForm(forms.Form):
    file = forms.FileField(label='Excel-файл (.xlsx)')
    dry_run = forms.BooleanField(
        label='Только проверить и показать предпросмотр',
        required=False,
        initial=True,
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('Поддерживаются только файлы формата .xlsx')
        return file
    

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'name',
            'tagline',
            'phone',
            'email',
            'site',
            'address',
            'logo',
            'manager_title',
            'manager_name',
        ]
        labels = {
            'name': 'Название компании',
            'tagline': 'Слоган',
            'phone': 'Телефон',
            'email': 'E-mail',
            'site': 'Сайт',
            'address': 'Адрес',
            'logo': 'Логотип',
            'manager_title': 'Должность подписанта',
            'manager_name': 'Имя подписанта по умолчанию',
        }
        widgets = {
            'tagline': forms.TextInput(attrs={
                'placeholder': 'Например: Объединяя мечты',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+7 (...) ...',
            }),
            'site': forms.TextInput(attrs={
                'placeholder': 'www.example.com',
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'г. ..., ул. ..., д. ...',
            }),
        }