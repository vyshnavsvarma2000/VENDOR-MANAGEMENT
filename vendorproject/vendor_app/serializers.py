from rest_framework import serializers
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from django.contrib.auth.models import User


# class UserSerializer(serializers.ModelSerializer):
#     phone_number = serializers.CharField(max_length=20)
#     password = serializers.CharField(
#         write_only=True, required=True)
#     password2 = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ["id", 'username', 'password', 'password2',
#                   'first_name', 'last_name', 'email', 'phone_number']
#         extra_kwargs = {'first_name': {'required': True},
#                         'last_name': {'required': True}}

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError(
#                 {"password": "Password fields didn't match."})

#         return attrs

#     def validate_phone_number(self, value):
#         if not value.isdigit() or len(value) < 10:
#             raise serializers.ValidationError("Invalid phone number")
#         return value

#     def create(self, validated_data):
#         phone_number = validated_data.get('phone_number')
#         user = User.objects.create(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             first_name=validated_data['first_name'],
#             last_name=validated_data['last_name']
#         )
#         user.set_password(validated_data['password'])
#         if phone_number:
#             user.phone_number = phone_number
#         user.save()
#         return user


class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = ["name", "contact_details", "address", "vendor_code", "on_time_delivery_rate",
                  "quality_rating_avg", "average_response_time", "fulfillment_rate"]
        read_only = ['vendor_code']
    


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ["po_number", "vendor", "order_date", "delivery_date", "items",
                  "quantity", "status", "quality_rating", "issue_date", "acknowledgment_date"]
        read_only = ["po_number"]


class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalPerformance
        fields = ["vendor", "date", "on_time_delivery_rate",
                  "quality_rating_avg", "average_response_time", "fulfillment_rate",]
        

class PerformanceSerializer(serializers.ModelSerializer):
    on_time_delivery_rate = serializers.SerializerMethodField()
    quality_rating_avg = serializers.SerializerMethodField()
    average_response_time = serializers.SerializerMethodField()
    fulfillment_rate = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = ('on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate')

    def get_on_time_delivery_rate(self, vendor):
        completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        total_completed_pos = completed_pos.count()
        if total_completed_pos == 0:
            return 0.0
        on_time_delivered_pos = completed_pos.filter(delivery_date__lte=F('acknowledgment_date'))
        return on_time_delivered_pos.count() / total_completed_pos

    def get_quality_rating_avg(self, vendor):
        quality_ratings = PurchaseOrder.objects.filter(vendor=vendor, quality_rating__isnull=False)
        return quality_ratings.aggregate(avg_rating=Avg('quality_rating')).get('avg_rating', 0.0)

    def get_average_response_time(self, vendor):
        all_pos = PurchaseOrder.objects.filter(vendor=vendor)
        response_times = [(po.acknowledgment_date - po.issue_date).total_seconds()
                          for po in all_pos if po.acknowledgment_date]
        if not response_times:
            return 0.0
        return sum(response_times) / len(response_times) / 3600  

    def get_fulfillment_rate(self, vendor):
        all_pos = PurchaseOrder.objects.filter(vendor=vendor)
        successfully_fulfilled_pos = all_pos.filter(status='completed')
        total_pos_count = all_pos.count()
        if total_pos_count == 0:
            return 0.0
        return successfully_fulfilled_pos.count() / total_pos_count
