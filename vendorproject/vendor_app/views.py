# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Vendor, PurchaseOrder
from .serializers import VendorSerializer, PurchaseOrderSerializer, PerformanceSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, authenticate
from django.contrib.auth.models import User

# class UserRegistrationView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'data': serializer.data, 
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserLoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             })
#         return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class VendorListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_token, created = Token.objects.get_or_create(user=request.user)
            return Response({
                "token": user_token.key,
                "vendor_data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_vendor(self, vendor_id):
        try:
            return Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return None

    def get(self, request, vendor_id):
        vendor = self.get_vendor(vendor_id)
        if vendor:
            serializer = VendorSerializer(vendor)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, vendor_id):
        vendor = self.get_vendor(vendor_id)
        if vendor:
            serializer = VendorSerializer(vendor, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, vendor_id):
        vendor = self.get_vendor(vendor_id)
        if vendor:
            vendor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

class PurchaseOrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        
        vendor_id = request.query_params.get('vendor')

        if vendor_id:
            try:
                purchase_orders = PurchaseOrder.objects.filter(vendor=vendor_id)
                serializer = PurchaseOrderSerializer(purchase_orders, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PurchaseOrder.DoesNotExist:
                return Response({"error": "Purchase orders not found for this vendor"}, status=status.HTTP_404_NOT_FOUND)
        else:
            purchase_orders = PurchaseOrder.objects.all()
            serializer = PurchaseOrderSerializer(purchase_orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, po_number):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            purchase_order = PurchaseOrder.objects.get(po_number=po_number)
            serializer = PurchaseOrderSerializer(purchase_order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "Purchase order not found"}, status=status.HTTP_404_NOT_FOUND)

 
    def put(self, request, po_number):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            purchase_order = PurchaseOrder.objects.get(po_number=po_number)
            serializer = PurchaseOrderSerializer(purchase_order, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "Purchase order not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, po_number):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            purchase_order = PurchaseOrder.objects.get(po_number=po_number)
            purchase_order.delete()
            return Response({'message': 'Purchase order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'Purchase order not found'}, status=status.HTTP_404_NOT_FOUND)


class VendorPerformanceView(APIView):
    permission_classes = [IsAuthenticated]
    
   
    def get(self, request, id):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            vendor = Vendor.objects.get(id=id)
            serializer = PerformanceSerializer(vendor)
            return Response({
                "Vendor_id": vendor.name,
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except Vendor.DoesNotExist:
            return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
        