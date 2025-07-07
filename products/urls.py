from django.urls import path
from .views import ProductDocumentView


urlpatterns = [
    path('', ProductDocumentView.as_view({'get': 'list'}), name='product-search'),
]