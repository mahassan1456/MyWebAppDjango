from django import forms
from django.forms import ModelForm
from medical.models import TT, test, Hospital, Hospital2 as HP
from medical.arrays import STATES, COMMON_DOMAINS_LIST
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import validate_email, EmailValidator, MinLengthValidator, MaxLengthValidator, RegexValidator
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
import time



# def customEmailValidator(value):
#     pass

def customPasswordValidator(password1,password2):

    if password1 == password2:
        return False
    return True

class AddHospital(ModelForm):

    name = forms.CharField(label="Facility Name: ",min_length=2,max_length=50,required=True, widget=forms.TextInput(attrs={'id':'hspname', 'class':'form-input','placeholder':'Enter Hospital Name','autofocus':'true','required':'true','id':'input1'}))

    taxid = forms.CharField(label="Tax ID: ",max_length=10,min_length=9,widget=forms.TextInput(attrs={'class':'form-input','placeholder':'Enter Tax ID e.g 12-9434553','id':'input2'}), 
        error_messages={'unique':"Tax ID Already Exists.If this has occurred in error please email the administrator. "})

    bankaccount = forms.CharField(label="Bank Account #: ",min_length=5,max_length=17,widget=forms.TextInput(attrs={'class':'form-input', 'placeholder':'Enter 9-20 digit bank account','id':'input3'}),required=True)

    routing = forms.CharField(label="Routing #: ",max_length=9,min_length=9,widget=forms.TextInput(attrs={'class':'form-input','placeholder':'Enter 9 Digit Routing','id':'input4'}),required=True)

    street = forms.CharField(label="Street: ",max_length=50,widget=forms.TextInput(attrs={'class':'form-input','id':'toggle','id':'input5','placeholder': 'Enter Street Name'}),required=True)

    city = forms.CharField(label="City: ",max_length=50,widget=forms.TextInput(attrs={'class':'form-input','id':'toggle1','id':'input6', 'placeholder':'Enter a City'}),required=True)

    state = forms.Select(attrs={'class':'form-input','id':'is_staff_user22','id':'input7'})

    zip = forms.CharField(label="Zip: ",max_length=5,min_length=5,widget=forms.TextInput(attrs={'class':'form-input','id':'is_super_user1','id':'input8','placeholder':'Enter 5 digit Postal Code'}),required=True)

    website = forms.CharField(label="Website: ",min_length=4,widget=forms.TextInput(attrs={'class':'form-input','id':'is_super_user2','id':'input9','placeholder':'Enter Website e.g www.google.com'}),required=True)

    total_physicians = forms.IntegerField(label="Total Physicians: ",widget =forms.NumberInput(attrs={'class':'form-input','id':'is_super_user3','id':'input10','placeholder': 'Total Number of Physicians'}))
    
    class Meta:
        model = HP
        fields = ['name','taxid','bankaccount','routing','street','city','state','zip', 'website','total_physicians']
        # widgets = {

        #     'name':forms.CharField(attrs={'id':'hspname', 'class':'form-input','placeholder':'Enter Hospital Name','autofocus':'true','required':'true'}),
        #     'taxid':forms.TextInput(attrs={'class':'form-input','placeholder':'Enter Tax ID e.g 12-9434553','name':'taxid','required':'true'}),
        #     'bankaccount':forms.TextInput(attrs={'class':'form-input','placeholder':'Enter 9-20 digit bank account'}),
        #     'routing':forms.TextInput(attrs={'class':'form-input','placeholder':'Enter 9 Digit Routing'}),
        #     'street':forms.TextInput(attrs={'class':'form-input','id':'toggle'}),
        #     'city':forms.TextInput(attrs={'class':'form-input','id':'toggle1'}),
        #     'state':forms.Select(attrs={'class':'form-input','id':'is_staff_user22'}),
        #     'zip':forms.TextInput(attrs={'class':'form-input','id':'is_super_user1'}),
        #     'website':forms.TextInput(attrs={'class':'form-input','id':'is_super_user2'}),
        #     'total_physicians':forms.NumberInput(attrs={'class':'form-input','id':'is_super_user3'}),

        # }

        labels = {

            'name': 'Hospital Name *',
            'taxid': 'Tax ID *',
            'bankaccount': 'Bank Account *',
            'routing': 'Routing *',
            'street': 'Street *',
            'city': 'City *',
            'state': 'State *',
            'zip': 'Zip *',
            'website': 'Website *',
            'total_physicians *': 'Total Physicians *'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def clean(self, *args, **kwargs):
        print(self.cleaned_data,'CLEANF')
        
        for field in self.cleaned_data:
            if not self.cleaned_data.get(field,""):
                raise ValidationError(f"Please Provide a Value for {field}")
        
        # taxid = self.cleaned_data.get('taxid', '')
        # print('last print')
        # if taxid[2] == "-":
        #     self.cleaned_data['taxid'] = "".join(taxid.split('-'))

        cleaned = super().clean(*args,**kwargs)
        return cleaned

    def clean_taxid(self):
       
        taxid = self.cleaned_data.get('taxid','')
        print(self.cleaned_data,'taxid')
        print(taxid,"taxidddddd from func")
        result = re.match(pattern=r'^(\d){2}(-)?(\d){7}$',string=taxid)
        if not result:
            print(result,"RESULTTTTTTTTT")
            raise ValidationError("Invalid Format.The tax id should be 9 digits and provided in the format ##-#######")
        if taxid[2] == "-":
            taxid = "".join(taxid.split('-'))
        # try:
        #     pass
        # except Hospital.DoesNotExist as DNE:
        #     raise ValidationError("The taxid already exists with in our system. Please re-enter or Log In using credentials.")
        # else:
        return taxid
    
    def clean_bankaccount(self):
        print(self.cleaned_data,'bankaccount')
        bankaccount = self.cleaned_data.get('bankaccount','')
        result = re.match(pattern=r'^(\d){5,17}$', string=bankaccount)

        if not result:
            raise ValidationError("Bank account # is a numeric value consisting of 5-17 digits.")
        return bankaccount

    def clean_routing(self):
        print(self.cleaned_data,'routing')
        routing = self.cleaned_data.get('routing','')
        result = re.match(pattern=r'^(\d){9}$', string=routing)

        if not result:
            raise ValidationError("The routing number is a 9 digit numeric value.")
        return routing

    def clean_city(self):
        print(self.cleaned_data,'city')
        city = self.cleaned_data.get('city','')
        result = re.match(pattern=r'^[A-Za-z- ]{2,}$', string=city)

        if not result:
            raise ValidationError("Invalid Format.")
        return city

    def clean_state(self):

        state = self.cleaned_data.get('state','')
        if state:
            state = state.upper()
            return state
        else:
            return "N/A"

    def clean_zip(self):
        print(self.cleaned_data,'zip')
        zip = self.cleaned_data.get('zip','')
        result = re.match(pattern=r'(\d){5}', string=zip)

        if not result:
            raise ValidationError("Please input 5 digits for the zip code.")
    
        return zip

    def clean_website(self):
        print(self.cleaned_data,'web')
        website = self.cleaned_data.get('website','N/A')
        result = re.match(pattern=r'www\.(\w){2,}\.[A-Za-z]{3}$', string=website)
        if not result:
            raise ValidationError("Please input website in the correct format beginning with www and ending with a three letter domain e.g gov,com,net")
        website = 'http://' + website
        return website

    

class CredentialsForm(UserCreationForm):

    #########################
    first_name = forms.CharField(label='First Name *',min_length=2,widget=forms.TextInput(attrs={'id':'hspname1', 'class':'form-elements','placeholder':'First Name','autofocus':True, 'required':True}), 
    validators=[RegexValidator(regex='[a-zA-Z]+',message="Names should not Contain Numbers")], error_messages={'required': 'Please Enter Your First Name '})
    #########################

    last_name = forms.CharField(label="Last Name *",min_length=2,widget=forms.TextInput(attrs={'id':'hspname1', 'class':'form-elements','placeholder':'Last Name','autofocus':True, 'required':True}), 
    validators=[MinLengthValidator(limit_value=2,  message="Last Name must be Greater than 1 Character in Length."),
    RegexValidator(regex='[a-zA-Z]+',message="Last Names should not Contain Numbers")],error_messages={'required': 'Please Enter a Last Name'})

    email = forms.EmailField(label="Email *" ,widget=forms.EmailInput(attrs={'class':'form-elements','placeholder':'Email', 'required': True}), 
    validators=[],error_messages={'required': 'Please Enter an Email Address: '} )

    
    password1= forms.CharField(min_length=8,max_length=16,
    widget=forms.PasswordInput(attrs={'class':'form-elements', 'required': True}), label='Enter A Password  *', error_messages={'required': 'Please Enter a Password: '})

    password2= forms.CharField(min_length=8, max_length=16,
    widget=forms.PasswordInput(attrs={'class':'form-elements', 'required': True}), label='Re-enter Password *', error_messages={'required': 'Please Verify your Password. '})

    class Meta:

        model = User
        fields = ["first_name", "last_name", "email", "username", "password1","password2"]

    def __init__(self, *args, **kwargs):

        super().__init__(*args,**kwargs)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args,**kwargs)
        
        return cleaned_data

    def clean_email(self,*args,**kwargs):
        # result = validate_email(email)
        # RegexValidator(regex='[a-zA-Z0-9]{2,}@[a-zA-Z]+\.com',message="Please Input a Valid Email Address")
        email = self.cleaned_data.get('email')
        domain = email.split('@')[1].split('.')[0]
        email_object = User.objects.filter(email=email)

        if email_object:
            raise ValidationError("Email Already Exists")

        if domain in COMMON_DOMAINS_LIST:
            raise ValidationError("Please Enter a Corporate Email Domain.")

        return email
    
    def clean_username(self,*args,**kwargs):

        username = self.cleaned_data.get('username')
        username_object = User.objects.filter(username=username)

        if username_object:
            raise ValidationError("Username already Exists")

        result = re.match(pattern=r'[a-zA-Z]+[a-zA-Z0-9]{8,20}', string='allanjames24')

        if not result:
            raise ValidationError("Username already exists. Please select a unique username up to 20 characters long.")

        return username
        

    def clean_password2(self,*args,**kwargs):

        password1 = self.cleaned_data.get('password1', False)
        password2 = self.cleaned_data.get('password2', False)
        

        if password1 and password2:
            password_validate_result = customPasswordValidator(password1=password1,password2=password2)

            if password_validate_result:
                raise ValidationError("Please Input a Matching Password with the minimum complexity requirements."
            )
            # RegexValidator(regex='^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,16}$', message="Password must be a Minimum eight to sixteen characters, at least one letter and one number:")
            result = re.match(pattern=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,16}$',string=password2)
            if not result:
                raise ValidationError("Password must be a Minimum eight to sixteen characters, at least one letter and one number")

        return password2
        
    def clean_password1(self,*args,**kwargs):

        password = self.cleaned_data.get('password1', False) 
        password2 = self.cleaned_data.get('password2', False)

        if password and password2:
            password_validate_result = customPasswordValidator(password1=password,password2=password2)

            if password_validate_result:
                raise ValidationError("Please Input a Matching Password with the minimum complexity requirements."
            )
            result = re.match(pattern=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,16}$',string=password)
            
            if not result:
                raise ValidationError("Password must be a Minimum eight to sixteen characters, at least one letter and one number")

        return password

class Login(forms.Form):
    username = forms.CharField(required=True, label="Username", widget=forms.TextInput(attrs={'placeholder':'Please enter a username','required':True,
    'required':'true'}))
    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder':'Please enter a password.','required':True,'required':'true'}))
    class Meta:
        pass


class ContactForm(forms.Form):
    firstname = forms.CharField(label="First Name",max_length = 50, required=True)
    lastname = forms.CharField(label="Last Name",max_length = 50,required=True)
    emailaddress = forms.EmailField(label="Email Address",max_length = 150, required=True)
    message = forms.CharField(label="Message",widget = forms.Textarea(attrs={'class':'messagebox'}), max_length = 2000, required=True)
   
    def clean_firstname(self):
        pass
    def clean_lastname(self):
        pass
    def clean_emailaddress(self):
        pass
    def clean_message(self):
        pass


class Product(ModelForm):
    pass
class ContactForm(forms.Form):
    
    firstname = forms.CharField(max_length = 50, required=True)
    lastname = forms.CharField(max_length = 50,required=True)
    emailaddress = forms.EmailField(max_length = 150, required=True)
    message = forms.CharField(widget = forms.Textarea, max_length = 2000, required=True)
    def x(self):
        pass
    


# class UserSignUp(UserCreationForm):
#     email = forms.EmailField(error_messages={'required':'Invalid Email Please re-enter',}, help_text="Please enter added email.")
#     extra = forms.CharField(empty_value="Hello World", error_messages={'required':'Please enter some shit'})
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#     class Meta:
#         model = User
#         fields = ['first_name',"last_name","email",'username','email','password1','password2']

# class FormTest(forms.Form):
#     username = forms.CharField(max_length=30,required=True,label='Username')
#     name = forms.CharField(widget=forms.PasswordInput())

x = 12

# class Foray(ModelForm):
    
#     name = forms.CharField(max_length=7,required=True, label='uname')
#     hobbies = forms.CharField(validators=[MinLengthValidator(limit_value=2, message="Must be Greater than 111 Character in Length.")])
#     test = forms.CharField(max_length=5,)

#     def save(self):
#         cleaned_fields = self.cleaned_data

#         for fields in cleaned_fields:
#             if cleaned_fields[fields] == "" or not cleaned_fields[fields]:
#                 raise ValidationError("Please make sure to provide values")
#         return super().save(commit=True)

#     class Meta:
#         model = TT
#         fields = '__all__'
       
#         error_messages = {
#             'name': {
#                 'max_length': ['this is too long']
#             }
#         }

class ContactForm(forms.Form):
    
	firstname = forms.CharField(max_length = 50, required=True)
	lastname = forms.CharField(max_length = 50,required=True)
	emailaddress = forms.EmailField(max_length = 150, required=True)
	message = forms.CharField(widget = forms.Textarea, max_length = 2000, required=True)

    
    

    
class Forr2(ModelForm):

    tax_id = forms.CharField(label="Tax ID *",max_length=10,min_length=9,widget=forms.TextInput(attrs={'class':'form-input','placeholder':'Enter Tax ID e.g 12-9434553'}), 
        error_messages={'unique':"Tax ID Already Exists.If this has occurred in error please email the administrator. "})

    class Meta:
        model = test
        fields = ['tax_id']

    def clean(self,*args,**kwargs):
        cleaned_data = super().clean(*args,**kwargs)

        print(cleaned_data,"clean")


    def clean_tax_id(self):
        print("taxid")

        taxid = self.cleaned_data.get('tax_id',"")
        result = re.match(pattern=r'^(\d){2}(-)?(\d){7}$',string=taxid)
        if not result:
            raise ValidationError("Invalid Format.The tax id should be 9 digits and provided in the format ##-#######")
        return taxid

class Foray(ModelForm):
    name = forms.CharField(max_length=7,label='uname',required=False)
    tax = forms.CharField(validators=[MinLengthValidator(limit_value=2, message="Must be Greater than 1 Character in Length.")])
    test = forms.CharField(max_length=5)


    def save(self,commit=True,*args,**kwargs):
        cleaned_fields = self.cleaned_data

        for field in cleaned_fields:
            if not cleaned_fields.get(field,""):
                raise ValidationError("Please make sure to provide values")
        return super().save(commit=commit)
    

    def clean_name(self,*args,**kwargs):
        print("This is clean_name function",timezone.now())
        return self.cleaned_data.get('name','')
    # def validate(self,*args,**kwargs):
    #     print("to_python")
    #     super().to_python(*args,**kwargs)
    def clean(self, *args,**kwargs):

        print(f"this is clean function",timezone.now())
        return super().clean(*args,**kwargs)



    class Meta:
        model = TT
        fields = ['name','age','hobbies','test']


obj = {
    'name': "MOHA",
    'hobbies': 'ball',
    'age': 12,
    'test': 'Abcd'
}

error_messages = {
    'name': {
        'max_length': ['this is too long']
    }
}

Hospital_Obj = {
    'name': 'New World Medical',
    'website': 'www.newworl.com',
    'total_physicians': 25,
    'zip': '77420',
    'taxid': '12-12112974',
    'bankaccount': '1233643412342',
    'routing': '123456789',
    'street': '485 Jackson Lane',
    'state:': 'tx',
    'city': 'Houston'

}

Hospital_Obj_2= {'name': 'qrwerwer', 'taxid': '123466689', 'bankaccount': '1342342523123', 'routing': '132123123', 'street': '123 dada', 'city': 'adedwed', 'state': 'AS', 'zip': '12312', 'website': 'www.espn.com', 'total_physicians': 12}
    
json = {"tax_id":"123456789"}    
    


