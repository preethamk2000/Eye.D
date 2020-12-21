from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    # path('result/', views.result, name='result'),
    path('search/<int:video_id>', views.search, name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# if settings.DEBUG:
    # urlpatterns += patterns('',
    #                         url(r'^media/(?P<path>.*)$',
    #                             'django.views.static.serve',
    #                             {'document_root': settings.MEDIA_ROOT,}),
    #                         )