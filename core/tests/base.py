"""Shared setup: a test database loaded with the full v3 content (photo links, no downloads)."""
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase


class SeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", no_download=True, stdout=StringIO(), stderr=StringIO())
        cls.admin_user = User.objects.create_superuser("tester", "tester@example.com", "pw-tester-123")

    def admin_client(self):
        c = Client()
        c.force_login(self.admin_user)
        return c


def section_post(section, **changes):
    """Everything the admin section form would submit for this section (and its cards), with some fields changed."""
    from core.adminpanel.forms import ItemFormSet, SectionForm

    form, formset = SectionForm(instance=section), ItemFormSet(instance=section)
    data = {}
    for field in list(form) + [f for sub in formset.forms for f in sub]:
        value = field.value()
        if isinstance(value, bool):
            if value:
                data[field.html_name] = "on"
        elif isinstance(value, (str, int)) and value != "":
            data[field.html_name] = value
    for key, value in formset.management_form.initial.items():
        data[f"{formset.prefix}-{key}"] = value
    data.update(changes)
    return data
