"""TrioStudio halftone views.

The studio page is rendered server-side and progressively enhanced with
HTMX:

* `studio`           - main canvas + sidebar (full page).
* `upload`           - HTMX endpoint that creates a HalftoneJob from the
                       uploaded file and returns a fragment that wires up
                       the live preview.
* `update_params`    - HTMX endpoint hit on every slider/input change;
                       persists the new parameters and queues a preview.
* `job_status`       - HTMX polling endpoint returning the current state
                       of a job (also used to swap in the preview img).
* `export_job`       - Queues the high-resolution export.
* `download_export`  - Streams the final PNG to the browser.
"""
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from app.halftone.forms import HalftoneParamsForm, HalftoneUploadForm
from app.halftone.models import HalftoneJob


def _schema_name():
    try:
        return connection.schema_name
    except AttributeError:
        return None


def _queue_preview(job):
    """Send a preview render to Celery; fall back to inline if Celery is down."""
    from app.halftone.tasks import process_halftone
    try:
        process_halftone.delay(job.pk, mode=HalftoneJob.MODE_PREVIEW,
                               schema_name=_schema_name())
    except Exception:
        # No broker available -> degrade gracefully so dev still works.
        process_halftone(job.pk, mode=HalftoneJob.MODE_PREVIEW)


def _queue_export(job):
    from app.halftone.tasks import process_halftone
    try:
        process_halftone.delay(job.pk, mode=HalftoneJob.MODE_EXPORT,
                               schema_name=_schema_name())
    except Exception:
        process_halftone(job.pk, mode=HalftoneJob.MODE_EXPORT)


# ---------------------------------------------------------------------------
# Page views
# ---------------------------------------------------------------------------

@login_required
def studio(request):
    """Main TrioStudio - Halftone studio page."""
    form = HalftoneParamsForm(instance=HalftoneJob())  # unbound, defaults
    upload_form = HalftoneUploadForm()
    return render(request, 'halftone/studio.html', {
        'form': form,
        'upload_form': upload_form,
    })


@login_required
@require_POST
def upload(request):
    upload_form = HalftoneUploadForm(request.POST, request.FILES)
    if not upload_form.is_valid():
        return render(request, 'halftone/_upload_errors.html', {
            'upload_form': upload_form,
        }, status=400)

    job = upload_form.save(commit=False)
    if request.user.is_authenticated:
        job.user = request.user
    job.save()
    _queue_preview(job)

    form = HalftoneParamsForm(instance=job)
    return render(request, 'halftone/_canvas.html', {
        'job': job, 'form': form,
    })


@login_required
@require_POST
def update_params(request, job_id):
    job = get_object_or_404(HalftoneJob, pk=job_id)
    form = HalftoneParamsForm(request.POST, instance=job)
    if not form.is_valid():
        return HttpResponse(status=400)
    form.save()
    _queue_preview(job)
    return render(request, 'halftone/_status.html', {'job': job})


@login_required
@require_http_methods(['GET'])
def job_status(request, job_id):
    job = get_object_or_404(HalftoneJob, pk=job_id)
    mode = request.GET.get('mode', HalftoneJob.MODE_PREVIEW)
    template = 'halftone/_status.html'
    if mode == HalftoneJob.MODE_EXPORT:
        template = 'halftone/_export_status.html'
    return render(request, template, {'job': job})


@login_required
@require_POST
def export_job(request, job_id):
    job = get_object_or_404(HalftoneJob, pk=job_id)
    # Reset export & queue
    job.export = None
    job.status = HalftoneJob.STATUS_PENDING
    job.last_mode = HalftoneJob.MODE_EXPORT
    job.save(update_fields=['export', 'status', 'last_mode', 'modified'])
    _queue_export(job)
    return render(request, 'halftone/_export_status.html', {'job': job})


@login_required
def download_export(request, job_id):
    job = get_object_or_404(HalftoneJob, pk=job_id)
    if not job.export:
        raise Http404('La exportación todavía no está lista.')
    response = FileResponse(
        job.export.open('rb'),
        as_attachment=True,
        filename=f'triostudio-halftone-{job.uid}.png',
        content_type='image/png',
    )
    return response


@login_required
def job_meta(request, job_id):
    """Tiny JSON endpoint useful for debugging from the JS console."""
    job = get_object_or_404(HalftoneJob, pk=job_id)
    return JsonResponse({
        'uid': str(job.uid),
        'status': job.status,
        'preview_url': job.preview.url if job.preview else None,
        'export_url': reverse('halftone:download_export', args=[job.pk]) if job.export else None,
        'error': job.error_message,
    })
