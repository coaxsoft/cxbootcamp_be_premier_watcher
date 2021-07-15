from django.contrib import admin

from premiers import models


@admin.register(models.Premier)
class PremierAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'is_active', 'premier_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('url',)
