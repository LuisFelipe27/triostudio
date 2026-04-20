from django.contrib import admin

from app.halftone.models import HalftoneJob


@admin.register(HalftoneJob)
class HalftoneJobAdmin(admin.ModelAdmin):
    list_display = (
        'uid', 'user', 'status', 'dot_shape', 'dot_size', 'dot_angle',
        'print_width_cm', 'export_dpi', 'created',
    )
    list_filter = ('status', 'dot_shape', 'export_dpi')
    search_fields = ('uid',)
    readonly_fields = ('uid', 'created', 'modified', 'status', 'error_message')
