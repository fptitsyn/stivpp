from django.contrib import admin
from .models import Kolbasa

@admin.register(Kolbasa)
class KolbasaAdmin(admin.ModelAdmin):
    list_display = ('brand', 'kind', 'weight', 'precut', 'num_of_slices')
    list_filter = ('kind', 'precut')
    search_fields = ('brand',)