from django.db import models
from django_prose_editor.fields import ProseEditorField

option = ProseEditorField(
    extensions={
        # Core text formatting
        "Bold": True,
        "Italic": True,
        "Strike": True,
        "Underline": True,
        "HardBreak": True,

        # Structure
        "Heading": {
            "levels": [1, 2, 3, 4, 5, 6]
        },

        # Lists
        "BulletList": True,
        "OrderedList": True,
        "ListItem": True,  # MUST be separate

        # Blockquote
        "Blockquote": True,

        # Links
        "Link": {
            "enableTarget": True,
            "protocols": ["http", "https", "mailto"],
        },

        # Tables
        "Table": True,
        "TableRow": True,
        "TableHeader": True,
        "TableCell": True,

        # Editor capabilities
        "History": True,
        "HTML": True,
        "Typographic": True,
    },
    sanitize=True
)


class PrivacyPolicy(models.Model):
    content = option

    class Meta:
        verbose_name_plural = 'Privacy Policy'

    def __str__(self):
        return "Privacy Policy"

class TermsConditions(models.Model):
    content = option

    class Meta:
        verbose_name_plural = 'Terms & Conditions'

    def __str__(self):
        return "Terms & Conditions"
