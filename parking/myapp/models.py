from django.db import models

# Create your models here.
class parkingslots(models.Model):
    slot_number = models.IntegerField()
    is_available =models.BooleanField(default=True)
    is_reserved = models.BooleanField(default=False)
    
class ParkingSession(models.Model):
    slot = models.ForeignKey(parkingslots, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=10)
    owner_name = models.CharField(max_length=50, blank=True)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    fee = models.FloatField(default=0)
    
class ReserveSession(models.Model):
    slot = models.OneToOneField(parkingslots, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=20)
    owner_name = models.CharField(max_length=50)
    hours = models.IntegerField()
    vehicle_type = models.CharField(max_length=20)
    reserve_time = models.DateTimeField(auto_now_add=True)


