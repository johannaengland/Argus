"""aas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView, RedirectView
from rest_framework.authtoken import views as rest_views

from . import views as aas_views

urlpatterns = [
    path('admin/', admin.site.urls),

   # path('dataporten/', TemplateView.as_view(template_name='dataporten.html'), name='dataporten'),
    path('dataporten/', RedirectView.as_view(url="http://localhost:3000"), name='dataporten'),
    path('api-token-auth/', rest_views.obtain_auth_token, name='api-token-auth'),

    path('', RedirectView.as_view(url="http://localhost:3000"), name='index'),  # temporary URL
    path('', include('aas.site.auth.urls')),
    path('alert/', include('aas.site.alert.urls')),
    path('notificationprofile/', include('aas.site.notificationprofile.urls')),
]

urlpatterns += [
    path('', include('social_django.urls', namespace='social')),
]