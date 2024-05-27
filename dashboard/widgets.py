from django import forms
from django.forms.widgets import Textarea

class JSONWidget(Textarea):
    def __init__(self, attrs=None, placeholder=None):
        if placeholder:
            attrs = attrs or {}
            attrs['placeholder'] = placeholder
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        placeholder = self.attrs.get('placeholder')
        if placeholder:
            context['widget']['attrs']['placeholder'] = placeholder
        return context