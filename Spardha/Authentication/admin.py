from django.contrib import admin
from .models import UserAccount
from django.http import HttpResponseRedirect


# Register your models here.

class UserAccountAdmin(admin.ModelAdmin):
    ...
    change_form_template = "admin/delete_user.html"


    def response_change(self, request, obj):
        if "_delete_user" in request.POST:
            try:
                obj.auth_token.delete()
            except:
                pass
            obj.is_active = False
            obj.is_staff = False
            obj.is_deleted = True
            obj.save()
            self.message_user(request, "This user is marked as deleted!")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    list_display = (
        '__str__', 'name',  'email', 'phone_no', 'institution_name', 'designation')
    search_fields = ('username', 'name', 'email', 'institution_name')
    list_filter = ('is_staff', 'institution_name')

admin.site.register(UserAccount, UserAccountAdmin)