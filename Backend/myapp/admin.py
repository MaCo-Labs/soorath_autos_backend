# admin.py
# Register your models here.
from django.contrib import admin
from .models import Vehicle, VehicleImage

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1  # Allows adding multiple images in the admin panel

class VehicleAdmin(admin.ModelAdmin):
    inlines = [VehicleImageInline]

# ✅ Correct way to register the admin model
admin.site.register(Vehicle, VehicleAdmin)  # Register Vehicle with VehicleAdmin
admin.site.register(VehicleImage)  # Register VehicleImage separately
