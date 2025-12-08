# chapters/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Feedback, Module, Chapter, Section  # ДОБАВЛЯЕМ ЭТУ СТРОЧКУ


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'subject', 'message', 'module', 'chapter', 'section']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тема обращения'}),
            'message': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Подробное описание...'}),
            'module': forms.Select(attrs={'class': 'form-control'}),
            'chapter': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля модуля, главы и раздела необязательными
        self.fields['module'].required = False
        self.fields['chapter'].required = False
        self.fields['section'].required = False

        # Фильтруем главы по выбранному модулю и разделы по выбранной главе
        if 'module' in self.data:
            try:
                module_id = int(self.data.get('module'))
                self.fields['chapter'].queryset = Chapter.objects.filter(module_id=module_id).order_by('order')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['chapter'].queryset = self.instance.module.chapters.order_by('order')

        if 'chapter' in self.data:
            try:
                chapter_id = int(self.data.get('chapter'))
                self.fields['section'].queryset = Section.objects.filter(chapter_id=chapter_id).order_by('order')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['section'].queryset = self.instance.chapter.sections.order_by('order')