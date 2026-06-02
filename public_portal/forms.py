import re

from django import forms

from customers.models import Client


RESERVED_SUBDOMAINS = {
    'www',
    'admin',
    'mail',
    'smtp',
    'api',
    'app',
    'public',
    'support',
    'help',
    'docs',
    'static',
    'media',
    'root',
    'sistemasmet',
}


class PublicTenantRegistrationForm(forms.Form):
    company_name = forms.CharField(
        label='Название компании',
        max_length=255,
    )
    subdomain = forms.CharField(
        label='Субдомен',
        max_length=63,
        help_text='Например: sakhtravel → sakhtravel.sistemasmet.online',
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=50,
        required=False,
    )
    company_email = forms.EmailField(
        label='E-mail компании',
        required=False,
    )
    website = forms.CharField(
        label='Сайт',
        max_length=255,
        required=False,
    )
    address = forms.CharField(
        label='Адрес',
        max_length=255,
        required=False,
    )
    admin_username = forms.CharField(
        label='Логин администратора',
        max_length=150,
    )
    admin_email = forms.EmailField(
        label='E-mail администратора',
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput,
    )

    def clean_subdomain(self):
        subdomain = self.cleaned_data['subdomain'].strip().lower()

        if not re.fullmatch(r'[a-z0-9-]+', subdomain):
            raise forms.ValidationError(
                'Субдомен может содержать только латинские буквы, цифры и дефис.'
            )

        if subdomain.startswith('-') or subdomain.endswith('-'):
            raise forms.ValidationError('Субдомен не должен начинаться или заканчиваться дефисом.')

        if subdomain in RESERVED_SUBDOMAINS:
            raise forms.ValidationError('Этот субдомен зарезервирован.')

        if Client.objects.filter(schema_name=subdomain).exists():
            raise forms.ValidationError('Компания с таким субдоменом уже существует.')

        return subdomain

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Пароли не совпадают.')

        return cleaned_data