import os
import sys
import django
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chavara_living.settings')
django.setup()

from accounts.models import CustomUser
from students.models import Student
from rooms.models import Room, Booking
from complaints.models import Complaint
from fees.models import FeeRecord

def seed():
    # 1. Admin User
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@chavaraliving.com',
            'role': 'admin',
            'phone': '9876543210',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created or not admin_user.check_password('Admin@123'):
        admin_user.set_password('Admin@123')
        admin_user.save()
    print("Admin user ready: admin / Admin@123")

    # 2. Rooms
    rooms_data = [
        {"room_no": "101", "capacity": 1, "room_type": "Single", "floor": 1, "block": "Block A"},
        {"room_no": "102", "capacity": 2, "room_type": "Double", "floor": 1, "block": "Block A"},
        {"room_no": "103", "capacity": 3, "room_type": "Triple", "floor": 1, "block": "Block A"},
        {"room_no": "201", "capacity": 1, "room_type": "Single", "floor": 2, "block": "Block B"},
        {"room_no": "202", "capacity": 2, "room_type": "Double", "floor": 2, "block": "Block B"},
    ]
    for rdata in rooms_data:
        Room.objects.get_or_create(room_no=rdata["room_no"], defaults=rdata)
    print("Rooms seeded.")

    # 3. Student 1: Rahul
    user1, _ = CustomUser.objects.get_or_create(
        username='rahul',
        defaults={'email': 'rahul.s@example.com', 'role': 'student', 'phone': '9812345678'}
    )
    user1.set_password('Student@123')
    user1.save()

    student1, s1_created = Student.objects.get_or_create(
        user=user1,
        defaults={
            'name': 'Rahul Sharma',
            'contact': '9812345678',
            'email': 'rahul.s@example.com',
            'course': 'B.Tech Computer Science',
            'year': 2,
            'address': 'MG Road, Kochi, Kerala',
            'date_of_admission': date.today() - timedelta(days=180)
        }
    )

    # 4. Student 2: Ananya
    user2, _ = CustomUser.objects.get_or_create(
        username='ananya',
        defaults={'email': 'ananya.v@example.com', 'role': 'student', 'phone': '9898765432'}
    )
    user2.set_password('student123')
    user2.save()

    student2, s2_created = Student.objects.get_or_create(
        user=user2,
        defaults={
            'name': 'Ananya Verma',
            'contact': '9898765432',
            'email': 'ananya.v@example.com',
            'course': 'B.Tech Electronics',
            'year': 3,
            'address': 'Civil Line Road, Kakkanad, Kochi',
            'date_of_admission': date.today() - timedelta(days=365)
        }
    )
    print("Students seeded.")

    # 5. Bookings
    room101 = Room.objects.get(room_no="101")
    if not Booking.objects.filter(student=student1, status="Active").exists():
        Booking.objects.create(
            student=student1,
            room=room101,
            arrival_date=date.today() - timedelta(days=180),
            status="Active"
        )

    room102 = Room.objects.get(room_no="102")
    if not Booking.objects.filter(student=student2, status="Active").exists():
        Booking.objects.create(
            student=student2,
            room=room102,
            arrival_date=date.today() - timedelta(days=365),
            status="Active"
        )
    print("Bookings created.")

    # 6. Fee Records
    FeeRecord.objects.get_or_create(
        student=student1,
        description="September 2025 Hostel Fee",
        defaults={
            "fee_type": "Monthly",
            "amount": 7500.00,
            "due_date": date.today() + timedelta(days=10),
            "status": "Pending"
        }
    )
    FeeRecord.objects.get_or_create(
        student=student1,
        description="August 2025 Hostel Fee",
        defaults={
            "fee_type": "Monthly",
            "amount": 7500.00,
            "due_date": date.today() - timedelta(days=20),
            "pay_date": date.today() - timedelta(days=22),
            "status": "Paid"
        }
    )
    FeeRecord.objects.get_or_create(
        student=student2,
        description="September 2025 Hostel Fee",
        defaults={
            "fee_type": "Monthly",
            "amount": 6500.00,
            "due_date": date.today() + timedelta(days=5),
            "status": "Pending"
        }
    )
    print("Fee records seeded.")

    # 7. Complaints
    Complaint.objects.get_or_create(
        student=student1,
        title="Wi-Fi connectivity issue in Room 101",
        defaults={
            "description": "Signal drops frequently during study hours between 8 PM and 11 PM.",
            "status": "In Progress",
            "admin_notes": "IT team notified to inspect router on 1st floor."
        }
    )
    Complaint.objects.get_or_create(
        student=student2,
        title="Study table light bulb replacement",
        defaults={
            "description": "The reading table light bulb flickers constantly.",
            "status": "Pending"
        }
    )
    print("Complaints seeded successfully!")

if __name__ == "__main__":
    seed()
