from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from app.transversal import views as transversal_views
from app.transversal.urls import router as transversal_router

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from two_factor_custom.urls import urlpatterns as two_factor_urls
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


admin.site.site_title = "TrioStudio Admin"
admin.site.site_header = "TrioStudio Admin"
admin.site.index_title = "Sitio Admin"

schema_url_authentication_patterns = [
    url(r'^token-login/', obtain_jwt_token),
    url(r'^token-refresh/', refresh_jwt_token),
    url(r'^token-verify/', verify_jwt_token)
]

schema_url_patterns = [
    url(r'^api/auth/', include(schema_url_authentication_patterns)),
    url(r'^api/transversal/', include(transversal_router.urls)),
]

urlpatterns = [
    url('', include(two_factor_urls)),
    url(r'^admin/', admin.site.urls),

    url('', include('app.transversal.urls', namespace='transversal')),

    # TrioStudio - Halftone DTF
    url(r'^halftone/', include('app.halftone.urls', namespace='halftone')),

    # SWAGGER - REDOC
    url('api/schema/', SpectacularAPIView.as_view(patterns=schema_url_patterns), name='schema'),
    url('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    url('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API
    url(r'^api/auth/', include(schema_url_authentication_patterns)),
    url(r'^api/transversal/', include(transversal_router.urls)),

    # Login URL
    url(r'^accounts/changed_password/$', auth_views.PasswordChangeView.as_view()),
    url(r'^accounts/password_change/done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),

] + static(settings.MEDIA_URL_SELF, document_root=settings.MEDIA_ROOT)
