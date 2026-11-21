from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False)  # spam trap: hidden from people, bots fill it in

    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "interest", "message"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = True  # as in the design: name and phone are required, email optional

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""
