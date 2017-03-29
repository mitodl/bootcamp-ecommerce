"""
Admin site bindings for profiles
"""

from django.contrib import admin

from profiles.models import Profile

admin.site.register(Profile)
