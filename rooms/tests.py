# Create your tests here.
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Booking, Room


class RoomTests(APITestCase):

    def setUp(self):
        self.room = Room.objects.create(
            name="Room 101",
            price_per_day=1000,
            capacity=2
        )

    def test_room_list(self):
        url = "/api/rooms/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class RegisterTests(APITestCase):

    def test_user_registration(self):
        url = "/api/register/"
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)


class BookingTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123"
        )

        self.room = Room.objects.create(
            name="Room 101",
            price_per_day=1000,
            capacity=2
        )

        self.client.force_authenticate(user=self.user)

    def test_create_booking(self):
        url = "/api/bookings/"
        data = {
            "room": self.room.id,
            "date_from": "2026-06-10",
            "date_to": "2026-06-12"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

    def test_cancel_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            date_from="2026-06-10",
            date_to="2026-06-12"
        )

        url = f"/api/bookings/{booking.id}/cancel/"
        response = self.client.post(url)

        booking.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(booking.status, "cancelled")