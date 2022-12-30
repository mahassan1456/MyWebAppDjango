from django.shortcuts import render
from medical.forms import AddHospital, CredentialsForm, Hospital, ContactForm, Login
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import re
from medical.models import Hospital as H, Hospital2 as Hospital
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout as logout_user
from django.contrib.auth import login as login_user
from django.contrib.auth.models import User
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils import timezone
from medical.utility_functions import send_msg_email, evaluate, send_sms
# Create your views here.
from smtplib import  SMTPResponseException as SMTPExc
import time
from twilio.base.exceptions import TwilioException, TwilioRestException 

def login(request):

    if request.method == 'POST':
        
        username = request.POST['username'].lower()
        password = request.POST['password']
        print('username', username)
        print('password',password)

        if not evaluate(username) or not evaluate(password):
            messages.error(request,message="Please provide login credentials",extra_tags='code')
            return HttpResponseRedirect(reverse('medical:login'))

        user = authenticate(request,username=username,password=password)
        url = request.GET.get('next', '')

        if user is not None:
            login_user(request, user)
            return HttpResponseRedirect(url if url else reverse('medical:dashboard'))
        else:
            messages.error(request, "Username or Password is Incorrect", extra_tags='code')
            return HttpResponseRedirect(reverse('medical:login'))

    user = False
    header = "Welcome Back"
    form = Login()
    return render(request, 'medical/login1.html',context={'form': form,'header':header})

def logout(request):

    logout_user(request)
    return HttpResponseRedirect(reverse('medical:login'))

@login_required
def success(request):
    
    return render(request=request, template_name="medical/blank.html",context={'head':'testifworks','vb': 'seeifiwork'})

def products(request):
    
    return render(request=request, template_name='medical/products2.html',context={})

def landing(request):
    form = AddHospital()
    header = "Add Facility"
    return render(request=request, template_name='medical/createcredentials.html', context={'form':form,'header':header})

def register(request):
    header = "Add Facility"
    if request.method == 'POST':
        print("request method")

        form = AddHospital(request.POST)
        
        if form.is_valid():
            print("errorr line")
            form.save(commit=True)
            messages.success(request, "HOSPITAL ADDED SUCCESFULLY. PLEASE CREATE LOG IN CREDENTIALS", extra_tags='code')
            hospital = Hospital.objects.latest('created_at')
            return HttpResponseRedirect(reverse('medical:createuser', args=(hospital.id,) ))
        
        
        return render(request, 'medical/contactus1.html', context={'form':form,'header':header})

            
    form = AddHospital()
    
    return render(request, 'medical/contactus1.html', context={'form':form,'header':header})

@login_required
def dashboard(request):
    
    return render(request=request, template_name='medical/dashboard.html')

def createuser(request, hospital_id = 0):

    header = "Create Log In Credentials"

    if request.method == "POST":
        bound_form = CredentialsForm(request.POST)

        if bound_form.is_valid() and hospital_id:
            try:
                hospital = Hospital.objects.get(id = hospital_id)
            except Hospital.DoesNotExist as hdne:
                messages.error(request,message="AN Error Occcured while processing  your request. Please try again later")
                #Log Error
                return HttpResponseRedirect(reverse('medical:contactus'))
            else:
                bound_form.save(commit=True)
                hospital.user = bound_form.instance
                hospital.save()
            msg = f"A new Account for {hospital.name} has been added at {timezone.now()} and is awaiting approval."
            try:
                send_msg_email(message=msg)
                send_sms(message=msg)
            except SMTPExc as wtf:
                messages.error(request=request, message="There was an error processing your request. Please try again later.")
                #LOG Error
            except TwilioRestException as te:
                messages.error(request=request, message="There was an error sending the SMS message.")
                #Log Error
            else:
                messages.success(request = request, message="Succesfully created Account")
                return HttpResponseRedirect(reverse('medical:success'))
            
            return HttpResponseRedirect(reverse('medical:contactus'))

        messages.error(request, message='There was an error processing your request. Please check data for valid input and try again.')
        return render(request=request, template_name='medical/contactus1.html', context={'form': bound_form, 'header': header})
        
    form = CredentialsForm()
    
    return render(request=request, template_name='medical/contactus1.html', context={'form': form,'header':header})

def contact_us(request):
    header = "Contact Us"
    if request.method == 'POST':
        bound_form = ContactForm(request.POST)

        if bound_form.is_valid():
            first_name = bound_form.cleaned_data.get('first_name','')
            last_name = bound_form.cleaned_data.get('last_name','')
            email_address = bound_form.cleaned_data.get('email_address','')
            message = bound_form.cleaned_data.get('message','')
            message = f"{first_name} {last_name} at {email_address} sent you a message at {timezone.now()} \n \n ### \n{message} \n ###"
            try:
                send_msg_email(message=message)
            except SMTPExc as wtf: 
                error_code = wtf.smtp_code
                error_message = wtf.smtp_error
                messages.error(request=request, message=error_message, extra_tags='code')
            except Exception as err:
                messages.error(request=request, message=error_message, extra_tags='code')
            else:
                messages.success(request,"Email Succesfully Sent", extra_tags='code')
                return HttpResponseRedirect(reverse('medical:success'))
            
            return HttpResponseRedirect(reverse('medical:contactus'))
        else:
            messages.error(request,"Please provide First Name, Last Name, Email Address, Message.", extra_tags='code')
            return render(request, template_name='medical/contactus1.html',context={'form': bound_form,'header':header})

    contact_form = ContactForm()
    return render(request=request,template_name='medical/contactus1.html', context={'form': contact_form,'header':header})
def reviewAccount(request):
     
    view_type = request.GET.get('viewtype','')
    if view_type == '' or view_type == 'all':
        hospitals = Hospital.objects.all()
    elif view_type == 'approved':
        hospitals = Hospital.objects.filter(approved=True)
    else:
        hospitals = Hospital.objects.filter(approved=False)
    
    fields = [f.name for f in Hospital._meta.get_fields()]
    
    return render(request, template_name='medical/approveacct.html', context={'fields':fields, 'hospital':hospitals, 'margin': '61vw', 'view': view_type})


def confirmhospital(request, id):
    try:
            hospital = Hospital.objects.get(id=id)
    except Hospital.DoesNotExist as dne:
        #log error
        messages.error(request=request, message="We are sorry, but we are unable to complete your request right now. Please try again later.")
        return HttpResponseRedirect(reverse('medical:reviewaccount'))
    
    if request.method == 'POST':

        approval_code = request.POST.get('app_butt','DNE')

        if approval_code == 'unapprove':
            hospital_name = hospital.name
            hospital.delete()
            messages.success(request=request, message=f"The facility {hospital_name} was succesfully unapproved. This facility will no longer appear in the Facilities list.")
        else:
            hospital.approve(username = request.user.username)
            messages.success(request=request, message=f"The facility {hospital.name} has been succesfully approved.")

        return HttpResponseRedirect(reverse('medical:reviewaccount'))

    approval_code = request.GET.get('app_butt','n/a')   
    return render(request=request, template_name='medical/approvalconfirm.html', context={'approval_code':approval_code,'hospital':hospital})
      
def details(request,id):
    try:
        hospital = Hospital.objects.get(id=id).__dict__.items()

    except Hospital.DoesNotExist as dne:
        #log error
        messages.error(request, message="There was an error processing your request. Please try again later, or contact the site administrator at accounts@medhova.com")
        return HttpResponseRedirect(reverse('medical:'))
    return render(request, template_name='medical/details.html', context={'hospital': hospital})
# def approvehospital(request, id):
#     try:
#         hospital = Hospital.objects.get(id=id)
#     except Hospital.DoesNotExist as dne:
#         #log error
#         messages.error(request=request, message="We are sorry, but we are unable to complete your request right now. Please try again later.")
#         return HttpResponseRedirect(reverse('medical:reviewaccount'))

#     messages.success(request=request, message=f"The facility {hospital.name} has been succesfully approved.")
#     return HttpResponseRedirect(reverse('polls:reviewaccount'))

# def removehospital(request, id):
#     try:
#         hospital = Hospital.objects.get(id=id)
#         facility_name = hospital.name

#     except Hospital.DoesNotExist as dne:
#         #log error
#         messages.error(request=request, message="We are sorry, but we are unable to complete your request right now. Please try again later.")
#         return HttpResponseRedirect(reverse('medical:reviewaccount'))
#     else:
#         hospital.delete()

#     messages.success(request=request, message=f"The facility {facility_name} has been succesfully removed.")
#     return HttpResponseRedirect(reverse('polls:reviewaccount'))

# def work(request):

#     return render(request, 'medical/work.html', context={})
# def app_rem(request, id):
    
#     if request.method == 'POST':
#         result = request.POST.get('appbutton',"n/a")
#         try:
#                 hospital = Hospital.objects.get(id=id)
#         except Hospital.DoesNotExist as dne:
#             #log error
#             messages.error(request=request, message="We are sorry, but we are unable to complete your request right now. Please try again later.")
#             return HttpResponseRedirect(reverse('medical:reviewaccount'))

#         if result == 'unapprove':
#             hospital.delete()
#             messages.success(request=request, message=f"The facility {hospital.name} has been succesfully unapproved.")
#         else:
#             messages.success(request=request, message=f"The facility {hospital.name} has been succesfully approved.")

#         return HttpResponseRedirect(reverse('polls:reviewaccount'))


# def send_msg_email(message):
#     sender_email = 'accounts@randomthoughtz.com'
#     smtp_server = 'mail.privateemail.com'
#     port = 465
#     login = "accounts@randomthoughtz.com"
#     password = "Iverson01"
#     to_email = 'specialreminder@gmail.com'
#     context = ssl.create_default_context()

#     with smtplib.SMTP_SSL(smtp_server,port=port, context=context) as server:
#         server.login(sender_email, password)
#         server.sendmail(sender_email, to_email, message)