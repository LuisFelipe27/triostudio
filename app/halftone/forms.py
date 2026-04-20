from django import forms

from app.halftone.models import HalftoneJob


class HalftoneUploadForm(forms.ModelForm):
    """Upload form: only the image is required at this stage."""

    class Meta:
        model = HalftoneJob
        fields = ('original',)


class HalftoneParamsForm(forms.ModelForm):
    """Bound to the studio sidebar (knockout, halftone & size settings)."""

    class Meta:
        model = HalftoneJob
        fields = (
            'knockout_enable', 'knockout_color', 'bg_color',
            'dot_shape', 'dot_size', 'dot_angle',
            'print_width_cm', 'export_dpi', 'contrast_boost',
        )
        widgets = {
            'knockout_color': forms.TextInput(attrs={'type': 'color'}),
            'bg_color': forms.TextInput(attrs={'type': 'color'}),
            'dot_size': forms.NumberInput(attrs={
                'type': 'range', 'min': 2, 'max': 60, 'step': 0.5,
            }),
            'dot_angle': forms.NumberInput(attrs={
                'type': 'range', 'min': 0, 'max': 90, 'step': 1,
            }),
            'print_width_cm': forms.NumberInput(attrs={
                'type': 'range', 'min': 5, 'max': 60, 'step': 0.5,
            }),
            'contrast_boost': forms.NumberInput(attrs={
                'type': 'range', 'min': 0.5, 'max': 2.5, 'step': 0.05,
            }),
        }
