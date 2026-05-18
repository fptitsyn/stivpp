from django.contrib import admin
from .models import Kind, Kolbasa


@admin.register(Kind)
class KindAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Kolbasa)
class KolbasaAdmin(admin.ModelAdmin):
    list_display = ('article', 'brand', 'kind', 'weight', 'price_unit', 'precut', 'is_heavy')
    list_filter = ('kind', 'precut')
    search_fields = ('article', 'brand')
    readonly_fields = ('is_heavy',)
    fieldsets = (
        (None, {
            'fields': ('article', 'brand', 'kind')
        }),
        ('Характеристики', {
            'fields': ('weight', 'precut', 'num_of_slices')
        }),
        ('Цены', {
            'fields': ('price_unit', 'price_small_opt', 'qty_small_opt', 'price_large_opt', 'qty_large_opt')
        }),
    )
