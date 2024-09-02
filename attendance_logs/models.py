from django.db import models

# Create your models here.
class Member(models.Model):

    employee_ID = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    mobile_number = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    image = models.ImageField(null=True)
    religion = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    date_hired = models.DateField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.lastname