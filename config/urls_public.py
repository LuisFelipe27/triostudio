from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from app.multi_tenant.urls import router
from app.transversal import views as transversal_views
from rest_framework import routers
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url('', include('app.multi_tenant.urls', namespace='multi_tenant')),

    url(r'^api/', include(router.urls)),

	# Login URL
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/changed_password/$', auth_views.PasswordChangeView.as_view()),
    url(r'^logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),

] + static(settings.MEDIA_URL_SELF, document_root=settings.MEDIA_ROOT)
