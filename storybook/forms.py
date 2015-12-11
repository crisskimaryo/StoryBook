from django import forms
from tinymce.widgets import TinyMCE

class PageForm(forms.Form):
    short_desc = forms.CharField(
        min_length=2,
        max_length=40,
        label= '',
        initial=" Enter short description here",
        widget=forms.TextInput(attrs={'size':'40'}),
        )
    illustration = forms.ImageField(required=False, label="Image")
    video = forms.FileField(required=False, label="Video")
    long_desc = forms.CharField(widget=TinyMCE(attrs={'cols': 100, 'rows': 15}),
        max_length=6000, label="")
    
    def is_valid(self):
        valid = super(PageForm, self).is_valid()
        if not valid:
            return valid
        if self.cleaned_data['short_desc'] == self.fields['short_desc'].initial:
            self._errors['short_desc'] = 'No short description entered'
            return False
        if self.cleaned_data['video'] and self.cleaned_data['illustration']:
            self._errors['illustration'] = 'Can only have video OR illustration'
            self._errors['video'] = 'Can only have video OR illustration'
            return False

        return True
