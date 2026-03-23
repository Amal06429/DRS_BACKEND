from django.db import models


class HospitalInfo(models.Model):
    firm_name = models.CharField(max_length=200, blank=True, null=True)
    address1  = models.CharField(max_length=200, blank=True, null=True)
    synced_at = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "hms_hospital_info"
        managed   = False

    def __str__(self):
        return self.firm_name or "Hospital"


class Doctor(models.Model):
    code          = models.CharField(max_length=10, primary_key=True)
    name          = models.CharField(max_length=100, blank=True, null=True)
    rate          = models.FloatField(blank=True, null=True)
    department    = models.CharField(max_length=10, blank=True, null=True)
    avgcontime    = models.IntegerField(blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    photourl      = models.TextField(blank=True, null=True)
    synced_at     = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "hms_doctors"
        managed   = False

    def __str__(self):
        return f"{self.code} - {self.name}"


class DoctorTiming(models.Model):
    slno      = models.BigIntegerField(primary_key=True)
    code      = models.CharField(max_length=10, blank=True, null=True)
    t1        = models.FloatField(blank=True, null=True)
    t2        = models.FloatField(blank=True, null=True)
    synced_at = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "hms_doctorstiming"
        managed   = False

    def __str__(self):
        return f"Timing {self.slno} - Dr {self.code}"


class Department(models.Model):
    code      = models.CharField(max_length=10, primary_key=True)
    name      = models.CharField(max_length=200, blank=True, null=True)
    synced_at = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "hms_department"
        managed   = False

    def __str__(self):
          return f"{self.code} - {self.name}"

