from django.contrib import admin
from .models import Vendor, PurchaseOrder, HistoricalPerformance

class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "id",)

admin.site.register(Vendor, VendorAdmin)
admin.site.register(PurchaseOrder)
admin.site.register(HistoricalPerformance)
