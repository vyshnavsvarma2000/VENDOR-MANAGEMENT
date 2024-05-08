# urls.py

from django.urls import path
from .views import VendorListCreateAPIView, VendorDetailAPIView, PurchaseOrderListCreateAPIView, PurchaseOrderDetailAPIView, VendorPerformanceView

urlpatterns = [
    path('vendors/', VendorListCreateAPIView.as_view(), name='vendor-list-create'),
    path('vendors/<int:vendor_id>/', VendorDetailAPIView.as_view(), name='vendor-detail'),
    path('purchase_orders/', PurchaseOrderListCreateAPIView.as_view(), name='purchase-order-list-create'),
    path('purchase_orders/<int:po_id>/', PurchaseOrderDetailAPIView.as_view(), name='purchase-order-detail'),
    path('performance/<int:id>', VendorPerformanceView.as_view(), name='vendor-performance'),
    # path('register/', UserRegistrationView.as_view(), name='user_registration'),
    # path('login/', UserLoginView.as_view(), name='user_login'),
]
