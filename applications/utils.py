"""
Application utils
"""
import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    """Check the file extension is allowed"""
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', 'odt']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')