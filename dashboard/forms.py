from django import forms
from django.core.validators import MinValueValidator
from .widgets import JSONWidget

class EditForm(forms.Form):
  frequency = forms.IntegerField(required=True, validators=[MinValueValidator(0)])
class NewPostManuallyForm(forms.Form):
  OPTIONS1 = [
      ('Facebook', 'Facebook'),
      ('Twitter', 'Twitter'),
      ('Linkedin', 'Linkedin'),
      ('TikTok', 'TikTok'),
      ('Instagram', 'Instagram'),
      ('Youtube', 'Youtube'),
  ]

  OPTIONS2 = [
      ('Text', 'Text'),
      ('Picture', 'Picture'),
      ('Video', 'Video'),
  ]

  platform_id = forms.ChoiceField(choices=OPTIONS1)
  post_date = forms.DateField(label='Date')
  user_id = forms.CharField(max_length=255, required=True)
  username = forms.CharField(max_length=255, required=True)
  content_type = forms.ChoiceField(choices=OPTIONS2)
  content = forms.CharField(widget=forms.Textarea(), required=True)
  url = forms.URLField(widget=forms.TextInput(), required=True)
  post_id = forms.CharField(max_length=255, required=True)
  likes = forms.IntegerField(required=True, validators=[MinValueValidator(0)])
  shares = forms.IntegerField(required=True, validators=[MinValueValidator(0)])
  num_comments = forms.IntegerField(required=True, validators=[MinValueValidator(0)])
  comments = forms.JSONField()
    
class AddForm(forms.Form):
  OPTIONS1 = [
      ('Facebook', 'Facebook'),
      ('Twitter', 'Twitter'),
      ('Linkedin', 'Linkedin'),
      ('TikTok', 'TikTok'),
      ('Instagram', 'Instagram'),
      ('Youtube', 'Youtube'),
  ]
  OPTIONS = [
      ('Text', 'Text'),
      ('Picture', 'Picture'),
      ('Video', 'Video'),
  ]

  platform_id = forms.ChoiceField(choices=OPTIONS1)
  user_id = forms.CharField(max_length=255, required=True)
  username = forms.CharField(max_length=255, required=True)
  content_type = forms.CharField(max_length=255, required=True )
  content = forms.CharField(widget=forms.Textarea(), required=True)
  url = forms.URLField(widget=forms.TextInput(), required=True)
  post_id = forms.CharField(max_length=255, required=True)
  likes = forms.IntegerField(required=True, validators=[MinValueValidator(0)])
  shares = forms.IntegerField(required=True, validators=[MinValueValidator(0)])
  num_comments = forms.IntegerField(required=True, validators=[MinValueValidator(0)])
    