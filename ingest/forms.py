from django import forms

class DumpUploadForm(forms.Form):
    device_name = forms.CharField(label='Имя устройства', max_length=255)
    dump_folder = forms.FileField(label='Папка дампа (ZIP или TAR)', widget=forms.ClearableFileInput(attrs={'multiple': False}))