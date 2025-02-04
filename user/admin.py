from django.contrib import admin
from .models import User_Model, Complaint

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'user_type', 'is_approved')
    list_filter = ('user_type', 'is_approved')
    search_fields = ('email', 'full_name', 'reg_no')

admin.site.register(User_Model, UserAdmin)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'status', 'active_complaint', 'created_at', 'resolved_at')
    list_filter = ('category', 'status', 'active_complaint', 'created_at')  
    search_fields = ('user__username', 'description')  
    ordering = ('-created_at',)  
    list_editable = ('status', 'active_complaint')  
    date_hierarchy = 'created_at'  
    readonly_fields = ('created_at', 'resolved_at')  # Mark both created_at & resolved_at as read-only

    fieldsets = (
        ("User Information", {'fields': ('user',)}),
        ("Complaint Details", {'fields': ('category', 'description', 'status', 'active_complaint')}),
        ("Timestamps", {'fields': ('created_at', 'resolved_at')}),
    )

    def has_add_permission(self, request, obj=None):
        """ Disable add permission since complaints are created by users. """
        return False

    actions = ["mark_as_resolved"]

    def mark_as_resolved(self, request, queryset):
        """ Admin action to mark selected complaints as resolved. """
        for complaint in queryset:
            if complaint.status != "resolved":
                complaint.status = "resolved"
                complaint.save()
        self.message_user(request, "Selected complaints have been marked as resolved.")

    mark_as_resolved.short_description = "Mark selected complaints as resolved"
