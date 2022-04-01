from django.contrib import admin
from .models import UserAccount
from django.http import HttpResponseRedirect
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe


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
        'username', 'name',  'email', 'phone_no', 'institution_name', 'designation', 'is_active', 'is_deleted')
    search_fields = ('username', 'name', 'email', 'institution_name', 'phone_no')
    list_filter = ('is_active', 'is_deleted', 'is_staff', 'is_admin')

admin.site.register(UserAccount, UserAccountAdmin)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_admin

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return mark_safe(link)
    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"
