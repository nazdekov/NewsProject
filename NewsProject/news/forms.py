from django import forms

from django.forms import ModelForm, Textarea, CheckboxSelectMultiple
from .models import *
# from tinymce import TinyMCE


class MultipleFileInput(forms.ClearableFileInput):
    #для множественного выбора изображений
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

from django.forms import inlineformset_factory
ImagesFormSet = inlineformset_factory(Article, Image, fields=("image",), extra=1, max_num=4,
    widgets={
        "image_field": MultipleFileField(),
    })


class ArticleForm(ModelForm):

    image_field = MultipleFileField()
    class Meta:
        model = Article
        fields = ['title', 'anouncement', 'text', 'tags', 'category']
        widgets = {
            'title': Textarea(attrs={'cols': 80, 'rows': 1, 'minlength': 10}),
            'anouncement': Textarea(attrs={'cols': 80, 'rows': 2, 'minlength': 10}),
            'text': Textarea(attrs={'cols': 80, 'rows': 5, 'minlength': 30}),
            'tags': CheckboxSelectMultiple(attrs={'cols': 50, 'rows': 3}),
            'category': forms.Select(attrs={"class": "form-control"}),
        }

