from django.urls import path
from .views import ProductDocumentView


urlpatterns = [
    path('search/products/', ProductDocumentView.as_view({'get': 'list'}), name='product-search'),
]
