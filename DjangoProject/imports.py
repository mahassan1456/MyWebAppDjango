from medical.models import *
from medical.forms import Foray, AddHospital as ah, Hospital_Obj as hob, Hospital_Obj_2 as hob2, Forr2 as gor, json
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User
from medical.utility_functions import evaluate

