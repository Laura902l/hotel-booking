from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Booking, Room
from .serializers import BookingSerializer, RegisterSerializer, RoomSerializer


def index(request):
    return render(request, "index.html")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({"username": request.user.username})


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["price_per_day", "capacity"]
    ordering_fields = ["price_per_day", "capacity"]
    ordering = ["price_per_day"]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "available", "bookings"]:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=["get"])
    def bookings(self, request, pk=None):
        room = self.get_object()

        bookings = Booking.objects.filter(
            room=room,
            status="active"
        ).values("date_from", "date_to")

        return Response(bookings)

    @action(detail=False, methods=["get"])
    def available(self, request):
        start_date = parse_date(request.query_params.get("date_from"))
        end_date = parse_date(request.query_params.get("date_to"))
        if not start_date or not end_date:
            return Response(
                {"error": "Provide date_from and date_to in format YYYY-MM-DD"},
                status=400,
            )
        booked_rooms = Booking.objects.filter(
            status="active",
            date_from__lt=end_date,
            date_to__gt=start_date,
        ).values_list("room_id", flat=True)

        available_rooms = Room.objects.exclude(id__in=booked_rooms)
        serializer = self.get_serializer(available_rooms, many=True)
        return Response(serializer.data)


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status == "cancelled":
            return Response(
                {"error": "Booking already cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = "cancelled"
        booking.save()
        return Response({"status": "Booking cancelled"})