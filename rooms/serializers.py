from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Booking, Room


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["user", "status"]

    def validate(self, data):
        room = data["room"]
        date_from = data["date_from"]
        date_to = data["date_to"]

        if date_from >= date_to:
            raise serializers.ValidationError(
                "date_to должно быть больше date_from."
            )

        overlapping = Booking.objects.filter(
            room=room,
            status="active",
            date_from__lt=date_to,
            date_to__gt=date_from,
        ).exists()

        if overlapping:
            raise serializers.ValidationError(
                "Номер на эти даты уже забронирован."
            )

        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)