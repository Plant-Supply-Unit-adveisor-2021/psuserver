from django.contrib import admin

from authentification.models import User

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    This class allows to export, filter and search for users
    """
    model = User

    list_display = ['email', 'last_name', 'first_name',
                    'is_active']
    search_fields = ['first_name', 'last_name', 'email']