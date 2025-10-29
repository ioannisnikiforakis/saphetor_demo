"""
All the VcfAPI urls that represent the implemented endpoints reside here.
These route to classes implemented on the views.py file.
"""
from django.urls import path

from . import views

urlpatterns = [
    path('VcfRows', views.VcfRowsList.as_view({'get': 'list', 'post': 'create'}),name='vcfrow-list'),
    path('VcfRows/id=<str:id>', views.VcfRowsDetail.as_view({'get': 'retrieve', 'put': 'update',
        'patch': 'partial_update', 'delete': 'destroy'}),name='vcfrow-detail'),
]
