from django.db import models
from django.contrib.auth.models import User
from medical.arrays import STATES
from django.core.validators import validate_email, EmailValidator, MinLengthValidator, MaxLengthValidator, RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib import messages


# Create your models here.

class userProfile(models.Model):
    user = models.OneToOneField(User,null=True,on_delete=models.CASCADE)
    mobile_contact = models.CharField(max_length=12, null=True, default="999-999-9999", 
        validators=[RegexValidator(regex='[0-9]{3}-[0-9]{3}-[0-9]{4}', message='Please input a Contact number in a Valid Format e.g 713-293-0949')])
    job_title = models.CharField(max_length=40, null=True, default="N/A", validators=[MinLengthValidator(limit_value=2, message="Please input a Position of at least 2 chracters")])
    additional_information = models.TextField(max_length=250, null=True, default=" ")


class Hospital(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.TextField(max_length=50, null=False,default="")
    taxid = models.CharField(max_length=10,null=True,unique=True, default="")
    bankaccount = models.CharField(max_length=17,null=False, default="", unique=True)
    routing = models.CharField(max_length=9,null=False,default="")
    street = models.TextField(max_length=50, null=False,default="")
    city = models.TextField(max_length=50,default="")
    state = models.CharField( max_length=5, null=False, choices=STATES,blank=False)
    zip = models.TextField(max_length=5, null=False,default="")
    total_physicians = models.IntegerField(null=False,default="",blank=False)
    website = models.URLField(null=False,default="")
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

class Hospital2(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.TextField(max_length=50, null=False,default="")
    taxid = models.CharField(max_length=10,unique=True,blank=False,null=True)
    bankaccount = models.CharField(max_length=17,blank=False, unique=True)
    routing = models.CharField(max_length=9,null=False,default="")
    street = models.TextField(max_length=100, null=False,default="")
    city = models.TextField(max_length=50,default="")
    state = models.CharField( max_length=5, null=False, choices=STATES,blank=False)
    zip = models.TextField(max_length=12, null=False,default="")
    total_physicians = models.IntegerField(null=False,default="",blank=False)
    website = models.URLField(null=False,default="")
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(null=False,default=False)
    approved_at =  models.DateTimeField(null=True,blank=True)
    approved_by = models.CharField(max_length=35,null=False,blank=True,default='')

    def approve(self, username):
        self.approved = True
        self.approved_at = timezone.now()
        self.approved_by = username
        self.save()
    

class test(models.Model):
    tax_id = models.CharField(max_length=20,null=True,unique=True,blank=True)
    

class Physician(models.Model):
    pass
    # facility = models.ForeignKey(Hospital,on_delete=models.CASCADE, null=True)
    # firstName = models.CharField(max_length=40, null=False, default=" ")
    # lastName = models.CharField(max_length=40, null=False, default=" ")
    # specialty = models.CharField(max_length=50, null=False, default=" ")
    # services = models.CharField(max_length=100, null=True)
    

class Product(models.Model):
    pass
    # name = models.CharField(max_length=100, null=True)
    # description = models.TextField(null=True)
    # price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # quantity = models.PositiveIntegerField(null=True)
    # category = models.CharField(max_length=50, null=True)
    # image = models.ImageField(upload_to='products/', blank=True, null=True)
    # manufacturer = models.CharField(max_length=30,null=True,default="")
    # UPC = models.CharField(max_length=25,null=True, default="")
    # SKU = models.CharField(max_length=30,null=True, )
    # created_at = models.DateTimeField(default=timezone.now)
    # updated_at = models.DateTimeField(auto_now=True)



# class BodyPart(models.Model):
#     products = models.ManyToManyField(Product, related_name='products', null=True, default="none")
#     bodyPart = models.CharField(max_length=50, null=True, default="")

    # def save(self):
    #     for field in BodyPart._meta.get_fields():
    #         if getattr(self,field.name) == "":
    #             messages.ERROR(f"Please insert a value for {field.name}.")
    #             raise ValidationError(f"Please Enter Value for {field.name}.")
    #     return super().save(*args, **kwargs)

        #force_insert=True,force_update=True,using=True,update_fields=[]



    # def save(self):
    #     return
    #      for field in x._meta.get_fields():
    #         if getattr(self, field.name) == "":
    #             raise ValidationError(f"The field {field.name} must be provided.")
    #         return super().save(force_insert=True, force_update=True, using=True, update_fields=[])

# @receiver(post_save, sender=Hospital)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#         Circle.objects.create(user=instance)
#         Notification.objects.create(user=instance)
        
# @receiver(post_save, sender=User)
# def save_user_profile(sender,instance,**kwargs):
#     instance.profile.save()
#     instance.user.save()
#     instance.notification.save()

class TT(models.Model):
    name = models.CharField(max_length=20,null=False,blank=False, default="")
    age = models.IntegerField(null=False, blank=False, default="")
    hobbies = models.CharField(max_length=30)

# class Good(models.Model):
#     tax = models.CharField(max_length=20,null=False,unique=True)

