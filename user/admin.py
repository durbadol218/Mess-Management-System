from django.contrib import admin
from .models import User_Model, Complaint, CustomToken, Bill, ContactMessage

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_approved')
    list_filter = ('user_type', 'is_approved')
    search_fields = ('email','reg_no')

admin.site.register(User_Model, UserAdmin)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'status', 'active_complaint', 'created_at', 'resolved_at')
    list_filter = ('category', 'status', 'active_complaint', 'created_at')  
    search_fields = ('user__username', 'description')  
    ordering = ('-created_at',)  
    list_editable = ('status', 'active_complaint')  
    date_hierarchy = 'created_at'  
    readonly_fields = ('created_at', 'resolved_at')

    fieldsets = (
        ("User Information", {'fields': ('user',)}),
        ("Complaint Details", {'fields': ('category', 'description', 'status', 'active_complaint')}),
        ("Timestamps", {'fields': ('created_at', 'resolved_at')}),
    )

    def has_add_permission(self, request, obj=None):
        return False

    actions = ["mark_as_resolved"]

    def mark_as_resolved(self, request, queryset):
        for complaint in queryset:
            if complaint.status != "resolved":
                complaint.status = "resolved"
                complaint.save()
        self.message_user(request, "Selected complaints have been marked as resolved.")
    mark_as_resolved.short_description = "Mark selected complaints as resolved"




@admin.register(CustomToken)
class CustomTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created')

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('user', 'bill_type','total_amount','due_date','transaction_id', 'status')
    list_filter = ('bill_type', 'status')
    search_field = ('user__username')

admin.site.register(ContactMessage)
# from django.contrib import admin
# from .models import Bill
# from django.utils.html import format_html

# class BillAdmin(admin.ModelAdmin):
#     list_display = ('user', 'bill_type', 'total_amount', 'due_date', 'status', 'transaction_id')
#     search_fields = ('user__username', 'transaction_id', 'status')
#     list_filter = ('status', 'bill_type', 'due_date')
#     readonly_fields = ('transaction_id', 'total_amount')

#     actions = ['mark_paid']

#     # def view_transaction(self, obj):
#     #     return format_html("<a href='https://example.com/transaction/{0}'>{0}</a>", obj.transaction_id)

#     def mark_paid(self, request, queryset):
#         queryset.update(status='Paid')
#         self.message_user(request, f"{queryset.count()} bills were successfully marked as paid.")
        
#     mark_paid.short_description = "Mark selected bills as Paid"
    
#     def save_model(self, request, obj, form, change):
#         if not obj.total_amount:
#             obj.total_amount = obj.calculate_total_bill()
#         super().save_model(request, obj, form, change)

# admin.site.register(Bill, BillAdmin)
