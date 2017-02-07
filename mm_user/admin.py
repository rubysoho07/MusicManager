from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from mm_user.forms import UserCreationForm, UserChangeForm
from mm_user.models import MmUser


# Register your models here.
class MmUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User
    list_display = ('email', 'name', 'nickname', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'nickname')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to user this attributes when creating a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'nickname', 'password1', 'password2'),
        })
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(MmUser, MmUserAdmin)
