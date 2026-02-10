from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from django.utils import timezone
from django.core.mail import send_mail
from reportlab.pdfgen import canvas
from django.contrib import messages
def home(request):
    return render(request,'myapp/home.html')


def avaliable_slots(request):
    slots = parkingslots.objects.all()

    # Create a dictionary: {slot_number: latest_session}
    session_map = {}
    for slot in slots:
        session = ParkingSession.objects.filter(slot=slot).order_by('-entry_time').first()
        session_map[slot.slot_number] = session

    return render(request, "myapp/avaliable_slots.html", {
        'slots': slots,
        'session_map': session_map
    })


def book_slot(request, id):
    slot = get_object_or_404(parkingslots, slot_number=id)

    if request.method == "POST":
        vehicle_number = request.POST['vehicle_number']
        vehicle_type = request.POST['vehicle_type']
        owner_name = request.POST.get('owner_name', '')

        # Create parking session
        parking_session = ParkingSession.objects.create(
            slot=slot,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            owner_name=owner_name,
        )

        # Mark slot as occupied
        slot.is_available = False
        slot.save()

        # Render confirmation page
        return render(request, 'myapp/booking_confirmation.html', {'session': parking_session})

    return render(request, 'myapp/book_slot_form.html', {'slot': slot})

   


def filled_slots(request):
    # Slots where is_available = False
    slots = parkingslots.objects.filter(is_available=False)
    return render(request, 'myapp/filled_slots.html', {'slots': slots})


def total_slots(request):
    # All slots (no filter)
    slots = parkingslots.objects.all()
    return render(request, 'myapp/total_slots.html', {'slots': slots})

def occupy_slot(request):
    slots = parkingslots.objects.filter(is_available=False)
    return render(request,'myapp/release.html',{'slots':slots})

import math

def release_slot(request, slot_id):
    slot = get_object_or_404(parkingslots, slot_number=slot_id)
    active_session = ParkingSession.objects.filter(slot=slot, exit_time__isnull=True).first()

    if active_session:
        active_session.exit_time = timezone.now()

        # Calculate fee
        duration_hours = math.ceil((active_session.exit_time - active_session.entry_time).total_seconds() / 3600)
        if active_session.vehicle_type == "2W":
            fee = duration_hours * 10
        elif active_session.vehicle_type == "4W":
            fee = duration_hours * 20
        elif active_session.vehicle_type == "EV":
            fee = duration_hours * 25
        else:
            fee = 0

        active_session.fee = fee  # You’ll need to add a `fee` field in ParkingSession
        active_session.save()

        slot.is_available = True
        slot.save()

        return render(request, 'myapp/slot_released.html', {'session': active_session, 'fee': fee})

    return redirect('occupy_slot')

def reserve_slot(request):
    slots = parkingslots.objects.all()
    
    return render(request,'myapp/reserve.html',{'slots':slots})




def reserve_form(request, slot_id):
    slot = get_object_or_404(parkingslots, slot_number=slot_id)

    if not slot.is_available:
        return HttpResponse("Slot already booked!")

    if slot.is_reserved:
        return HttpResponse("Slot already reserved!")

    if request.method == "POST":
        owner = request.POST.get("owner_name")
        vehicle_no = request.POST.get("vehicle_number")
        hours = request.POST.get("hours")
        vehicle_type = request.POST.get("vehicle_type")

        # Create reservation
        ReserveSession.objects.create(
            slot=slot,
            owner_name=owner,
            vehicle_number=vehicle_no,
            hours=hours,
            vehicle_type=vehicle_type
        )

        # Mark slot as reserved
        slot.is_reserved = True
        slot.save()

        return HttpResponse("hey..reservation done")

    return render(request, "myapp/reserve_form.html", {"slot": slot})




import io
#comment 1

def download_pdf(request, id):
    session = ParkingSession.objects.get(id=id)

    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    # PDF Title
    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 800, "Parking Receipt")

    p.setFont("Helvetica", 12)
    y = 760

    p.drawString(50, y, f"Slot Number: {session.slot.slot_number}")
    y -= 20
    p.drawString(50, y, f"Vehicle Number: {session.vehicle_number}")
    y -= 20
    p.drawString(50, y, f"Vehicle Type: {session.vehicle_type}")
    y -= 20
    p.drawString(50, y, f"Owner Name: {session.owner_name}")
    y -= 20
    p.drawString(50, y, f"Entry Time: {session.entry_time}")
    y -= 20
    p.drawString(50, y, f"Exit Time: {session.exit_time}")
    y -= 20
    p.drawString(50, y, f"Total Fee: ₹{session.fee}")

    # Finish PDF
    p.showPage()
    p.save()

    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/pdf')




def send_receipt_email(request,id):
    if request.method == "POST":
        to_email = request.POST["email"]
        session = get_object_or_404(ParkingSession, id=id)

        message = f"""
Parking Receipt

Vehicle        : {session.vehicle_number}
Owner          : {session.owner_name}
Slot           : {session.slot.slot_number}
Entry Time     : {session.entry_time.strftime('%d %b %Y, %I:%M %p')}
Exit Time      : {session.exit_time.strftime('%d %b %Y, %I:%M %p')}
Total Fee      : ₹{session.fee}

Thank you for using our parking!
        """

        send_mail(
            subject="Your Parking Receipt",
            message=message,
            from_email=None,           # ← this line = Django uses DEFAULT_FROM_EMAIL
            recipient_list=[to_email],
            fail_silently=False,
        )

        messages.success(request, f"Receipt sent to {to_email}")

    return redirect('release_slot', slot_id=session.slot.slot_number)