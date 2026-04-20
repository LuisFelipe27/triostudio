from django.conf.urls import url

from app.halftone import views

app_name = 'halftone'

urlpatterns = [
    url(r'^$', views.studio, name='studio'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^job/(?P<job_id>\d+)/params/$', views.update_params, name='update_params'),
    url(r'^job/(?P<job_id>\d+)/status/$', views.job_status, name='job_status'),
    url(r'^job/(?P<job_id>\d+)/export/$', views.export_job, name='export_job'),
    url(r'^job/(?P<job_id>\d+)/download/$', views.download_export, name='download_export'),
    url(r'^job/(?P<job_id>\d+)/meta/$', views.job_meta, name='job_meta'),
    url(r'^job/(?P<job_id>\d+)/mask/$', views.mask_image, name='mask_image'),
    url(r'^job/(?P<job_id>\d+)/delete/$', views.delete_job, name='delete_job'),
]
