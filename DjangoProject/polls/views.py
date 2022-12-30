from calendar import c
from tempfile import template
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import Question, Choice, Profile, Circle, Comments, DM, DmThrough, Notification
from django.template import loader, Context
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login,authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from polls.forms import UserSignUp, AdditionInfo, ImageForm
from django.contrib import messages
import datetime
import os
from django.core.mail import send_mail, BadHeaderError
from django.core.signals import request_finished
from PIL import Image
from django.db.models import Q
from blog.models import Article
from django.apps import apps
from io import BytesIO as IO
from polls.helper_functions import key, check_flag_n_comment
from django.core.mail import send_mail
import jwt
import smtplib, ssl
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.auth.hashers import make_password, check_password
import sqlite3
import pandas as pd

PATH = ''
############################## STATS #######################
def stats(request):
    
    if request.method == 'POST':
        uri = "../basketball.sqlite"
        connection = sqlite3.connect(database=uri, uri=True)
        df = pd.read_sql_query("SELECT * from Game", connection)
        df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
        r = request.POST.get("comparing","")
        hometeam = request.POST.get("home_team_v", "")
        awayteam = request.POST.get("away_team_v", "")
        type_match = request.POST.get("comparing2", "")

        if r == "ALL":

            if type_match == "ALL":
                q = f"SELECT * from Game LIMIT 500"

            elif type_match == 'TEAM_ABBREVIATION_HOME':
                q = f"SELECT * from Game where {type_match}='{hometeam}' LIMIT 500"

            elif type_match == 'TEAM_ABBREVIATION_AWAY':
                q = f"SELECT * from Game where {type_match}='{awayteam}' LIMIT 500"

            elif type_match == 'MATCHUP_HOME':

                if hometeam == awayteam:
                    messages.warning(request,message="The Hame Team Must Be Different Than The Away Team.")
                    return HttpResponseRedirect(reverse('polls:stats'))
            
                matchup = hometeam + 'vs.' + awayteam
                q = f"SELECT * from Game where {type_match}='{matchup}' LIMIT 500"

            query = pd.read_sql_query(q, connection)

        elif r == "BETWEEN":
            start = request.POST.get("start_date","")
            end = request.POST.get("end_date", "")

            if type_match == "ALL":
                q = f"SELECT * from Game where GAME_DATE {r} '{start}' and '{end}'"

            elif type_match == 'TEAM_ABBREVIATION_AWAY':
                q = f"SELECT * from Game where GAME_DATE {r} '{start}' and '{end}' AND  {type_match}='{awayteam}' LIMIT 500"

            elif type_match == "TEAM_ABBREVIATION_HOME":
                q = f"SELECT * from Game where GAME_DATE {r} '{start}' and '{end}' AND {type_match}='{hometeam}' LIMIT 500"

            elif type_match == 'MATCHUP_HOME':
                team_name_g = hometeam + ' vs. ' + awayteam
                q = f"SELECT * from Game where GAME_DATE {r} '{start}' and '{end}' AND {type_match}='{team_name_g}' LIMIT 500"

            query = pd.read_sql_query(q, connection)

        else:
            date = request.POST.get("only_date","")
            type_match = request.POST.get("comparing2", "")
            team_name_g = request.POST.get("team_name_g", "")

            if type_match == "ALL":
                q = "SELECT * from Game where GAME_DATE{r}\'{date}\' LIMIT 500".format(r=r,date=date)

            elif type_match == 'TEAM_ABBREVIATION_HOME':
                q = f"SELECT * from Game where GAME_DATE{r}\'{date}\' AND {type_match}='{hometeam}' LIMIT 500"

            elif type_match == 'TEAM_ABBREVIATION_AWAY':
                q = f"SELECT * from Game where GAME_DATE{r}\'{date}\'  AND  {type_match}='{awayteam}' LIMIT 500"

            else:
                team_name_g = hometeam + ' vs. ' + awayteam
                q = f"SELECT * from Game where GAME_DATE{r}\'{date}\' AND {type_match}=\'{team_name_g}\' LIMIT 500"

            query = pd.read_sql_query(q, connection)
    
        query = query.to_html()
        html_file = open('/Users/nefarioussmalls/MyWebApp/mysite/polls/templates/polls/nba.html','w')
        URL = reverse('polls:download', args=(q,))
        script = """
        <script>
        function Download() {
        var URL = document.getElementById("button1").getAttribute("data-url");
        fetch(URL)
        .then((res) => { 
            return res.blob(); 
        })
        .then((data) => {
            console.log("test")
        }
        </script>
        """
        # under then another element can be added document.createelement("a") a.href = value and a.download to specifiy the download file and then a.click.
        updated_html = "{{% extends 'polls/base.html' %}} \n {{% block content %}} {{% block styles %}} {{{{block.super}}}} <style> td, th {{border: 1.1px solid #666666; text-align:left; padding:8px;}} tr:nth-child(even) {{ background-color: #ddddff;}} </style> {{% endblock styles %}}<button id=\"button1\" onclick=\"Download()\" data-url=\"{URL}\" style='background-color:rgb(63, 167, 150); border-radius:10px;'> <a style='text-decoration:none; color:whitesmoke;' href=\"{{% url 'polls:download' \"{q}\" %}}\"> CSV </a> </button> \n {query} \n {script} \n {{% endblock %}}".format(q=q,query=query,URL=URL,script=script)
        html_file.write(updated_html)
        html_file.close()
        return render(request, 'polls/nba.html', context= {'query': q})

    NBA_TEAMS = ['ATL', 'BKN', 'BOS', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND',
    'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK','OKC','ORL','PHI','PHO',
    'POR', 'SAC', 'SAS', 'TOR', 'UTH', 'WAS' ]
 
    return render(request, 'polls/stats.html', context={'teams': NBA_TEAMS})

def download(request, query):

    conn = sqlite3.connect(database='/Users/nefarioussmalls/Documents/Da Portfolio/NBA DB SQlite3/basketball.sqlite',uri=True)
    html_df = pd.read_sql_query(query, conn)
    html_df = html_df.reset_index()
    raw_path = "nbagames"
    stream_file = IO()
    html_df.to_excel(stream_file)
    stream_file.seek(0)
    response = HttpResponse(stream_file)
    response["Content-Type"] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = 'attachment; filename={r}.xlsx'.format(r=raw_path)
    return response

##############################    SEND EMAIL   ##################################
KEY = "This is my motherfucking secret key.43423r234r24r2wrw4r4tfrsfsdffgedg"

def test_popup(request):

    return render(request, 'polls/popup.html')

##############################  RETURN USER LISTS  ###############################

class UserList(generic.ListView):
    
    template_name = 'polls/querylist.html'
    model = User
    context_object_name = 'search_list'

    def get_queryset(self):

        option = self.request.GET.get('option')
        query = self.request.GET.get('q')

        if option == 'User':
            q_list = User.objects.filter(Q(username__icontains = query) | Q(email__icontains = query))
            
        else:
            q_list = Question.objects.filter(Q(question_text__icontains = query) | Q(question_text__icontains = query))

        return q_list

def listUser(request):

    return render(request,'polls/listuser.html')

def getUser(request):

    lis = User.objects.all()
    return JsonResponse({'users': list(lis.values())})

################## ALL THIGNS RELATING TO PROFILE MANAGEMENT ##################

@login_required
def success(request):

    if request.method == 'POST':
        form = AdditionInfo(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('polls:index'))

    # form = AdditionInfo(initial={'bio': request.user.profile.bio, 'location':request.user.profile.location,'birthdate':request.user.profile.birthdate})
    form = AdditionInfo(instance=request.user.profile)
    return render(request, 'polls/success.html', {'form': form})

@login_required
def make_comment(request,user_id):

    user = User.objects.get(pk=user_id)
    check_flag_n_comment(request,user, True)
    return render(request, 'polls/view_profile.html', {'user': user})

@login_required
def view_profile(request, user_id):

    user = User.objects.get(pk=user_id)
    check_flag_n_comment(request,user)
    return render(request, 'polls/view_profile.html', {'user': user})

@login_required
def profile_settings(request):

    if request.method == 'POST':
        answer = request.POST.get('answer','')
        request.user.profile.canView = answer
        request.user.save()
        return HttpResponseRedirect(reverse('polls:view_profile', args=(request.user.id,)))

    return render(request,'polls/profile_settings.html')

############################## LOG IN/LOG OUT/ HOME ################################

def forgot_password(request):

    result = False
    result1 = False

    if request.method == 'POST':
        email = request.POST.get('resetemail','')

        try:
            requested_user = User.objects.get(email=email)

        except (User.DoesNotExist, KeyError) as e:
            print(e)
            result1 = True

        else:
            payload = {
                "id": requested_user.id,
                "fir": requested_user.first_name,
                "lst": requested_user.last_name,
                'exp': datetime.datetime.now() + datetime.timedelta(minutes=1)
            }

            token = jwt.encode(key=KEY,payload=payload)
            link = f'127.0.0.1/polls/newpassword/?token={token}&id={requested_user.id}'
            result = True
            sender_email = 'accounts@randomthoughtz.com'
            receiver_email  = requested_user.email
            smtp_server = 'mail.privateemail.com'
            port = 465
            login = "accounts@randomthoughtz.com"
            password = "Iverson01"
            message = MIMEMultipart('alternative')
            message["Subject"] = "Reset Your Password for RandomThoughtz.Com"
            message["From"] = f"Accounts<{sender_email}>"
            message["To"] = receiver_email
            text = f"""\
                    Please copy and paste the following link in your browser \n
                    {link}
                    """
            html = """\
                    <html>
                        <head>
                        </head>
                        <body>
                            <p>Hi, {title}
                                <br>
                                Please Click the Link Below to securely reset your Password
                                <br>
                                <a href="{link}">Reset Password</a> 
                            </p>
                        </body>
                    </html>
                    """.format(title=requested_user.first_name, link=link)

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(smtp_server,port=port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())

        return render(request, 'polls/forgotpassword.html', context={'result':result,'result1':result1})

    return render(request, 'polls/forgotpassword.html', context={'result':result,'result1':result1})


def newpassword(request):

    #verify if jwt is okay and also
    user = User.objects.get(id=request.GET.get('id'))
    token = request.GET.get('token','')
    direct = 1

    try:
        result = jwt.decode(key=KEY,jwt=token,algorithms=['HS256',])

    except:
        messages.error(request,"Error Processing Link")
        result = False

    else:

        if result['exp'] > datetime.datetime.now():

            if request.method == 'POST':
                password1 = request.POST.get('password1','')
                password2 = request.POST.get('password2','')

                if password1 == password2:
                    password = make_password(password=password1)
                    user.password = password
                    user.save()
                    messages.success(request,"Password Succesfully Changed")
                    
                else:
                    messages.error(request, "Passwords Do Not Match")
             
            else:
                messages.info(request, "Please enter new Password")
                direct = 2
        else:
            messages.error(request,"Expiration date has expired. Please re-enter email address")
            return HttpResponseRedirect(redirect_to=reverse('polls:forgot_password'))
    
    return render(request,'polls/newpassword.html',{'direct':direct,'result':result})

def login_user(request):

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        url = request.GET.get('next', '')

        if user is not None:
            login(request, user)
            try:
                notification = user.notification

            except Notification.DoesNotExist as error:
                notif = Notification(user_n = user)
                notif.save()
                request.user.save()

            return HttpResponseRedirect(url if url else reverse('polls:view_profile', args=(user.id,)))

        else:
            messages.success(request, "Username or Password is Incorrect")
            return HttpResponseRedirect(reverse('polls:login_user'))
    
    user = False
    return render(request, 'polls/login.html', context={"user": user})

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('polls:login_user'))


def sign_up(request):

    if request.method == 'POST':
        first = request.POST['first']
        last = request.POST['last']
        email = request.POST['email'].lower()
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            new_user = User.objects.create_user(email=email,username=email, password=password,first_name=first, last_name=last)
            new_user.save()
            return HttpResponseRedirect(reverse('polls:login_user'))

        else:
            return render(request, 'polls/sign_up.html', context= {'error_message': "Please enter the same unique password"} )

    return render(request, 'polls/sign_up.html' )

################## FUNCTIONS RELATED TO FRIEND REQUESTS FR-7 ##################

@login_required
def cancel_request(request, user_id):

    request.user.user.unrequest(user_id)
    return render(request, 'polls/friend_request.html')

@login_required
def add_friend(request, user_id):
    request.user.user.send_request(user_id)
    friend = User.objects.get(pk=user_id)
    friend.notification.request_flag = True
    friend.notification.friend_last_time = timezone.now()
    friend.notification.save()
    friend.save()
    messages.success(request,f"You have sent a request to {friend.username} ")
    
    return HttpResponseRedirect(reverse('polls:index'))   

@login_required
def accept_request(request, user_id):

    request.user.user.accept(user_id)
    messages.success(request, f"You are now friends with {User.objects.get(pk=user_id).username}")
    return render(request, 'polls/friend_request.html')

def remove_friend(request,user_id):

    request.user.user.remove_friend(user_id)
    messages.success(request, f"You are no longer friends with {User.objects.get(pk=user_id).username}")
    return render(request, 'polls/friend_request.html')

def view_requests(request):

    notif = []
    mutuals = request.user.user.is_mutual()

    for req in request.user.user.requests.all():

        if req.user.to_notify:
            notif.append((req,True))
            req.user.to_notify = False
            req.user.save()

        else:
            notif.append((req,False))

        req.user.save()

    return render(request, 'polls/friend_request.html', {'mutuals': mutuals, "notify": notif, "loop":range(len(notif))})

######## FUNCTIONS RELATED TO VOTING/CREATING QUESTION/ ANSWERING VT-1 ########

@login_required
def index(request):
    
    latest_question_list = Question.objects.order_by('-pub_date')
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
        'Users' : User.objects.all()
    }

    return HttpResponse(template.render(context, request))

def chart(request, question_id):

    labels =[]
    data = []
    qset = Choice.objects.filter(question= question_id)

    for dat in qset:
        labels.append(dat.choice_text)
        data.append(dat.votes)
    

    return render(request, 'polls/chart.html', {
    'labels': labels,
    'data': data,
    'question': Question.objects.get(pk=question_id).question_text
})

@login_required
def detail(request, question_id):

    try:
        question = Question.objects.get(pk=question_id)

    except Question.DoesNotExist:
        raise Http404("This Question Does Not Exist")

    return render(request,'polls/details.html', context={'question': question})

@login_required
def results(request, question_id):

    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def vote(request,question_id):

    question = get_object_or_404(Question, pk=question_id)
    if request.POST.get('edit','') == 'Edit':
        return HttpResponseRedirect(reverse('polls:edit', args=(question_id,)))
    
    elif request.POST.get('delete',''):
        print(request.POST.get('delete'))
        question.delete()
        return HttpResponseRedirect(reverse('polls:index'))
    
    try:
        choice = question.choice_set.get(pk=request.POST['choice'])

    except (KeyError, Choice.DoesNotExist):
        context = {
            'question': question,
            'error_message': 'You did not submit a vote'
        }
        return render(request, 'polls/details.html', context)

    else:

        for item in request.user.choice_set.filter(question=choice.question):

            if choice.question == item.question:
                item.votes -= 1
                item.save()
                request.user.choice_set.remove(item)
                break
            
        choice.users.add(request.user)
        choice.save()
        choice.votes += 1
        choice.save()
        
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

@login_required
def add_question(request):

    if request.method == 'POST':
        question = request.POST.get('question','')

        if question:
            request.user.question_set.create(question_text=question, pub_date=timezone.now())
            request.user.save()
            array = []

            for x in range(1,10):
                name = "choice" + str(x)
                word = request.POST.get(name,"nada")

                if word == "nada":
                    break
                array.append(word)
            
            for x in array:
                request.user.question_set.get(question_text=question).choice_set.create(choice_text=x, votes=0)
                request.user.save()

            return HttpResponseRedirect(reverse('polls:index'))

    return render(request, 'polls/add_question.html')

@login_required
def edit(request, question_id):

    question = request.user.question_set.get(pk=question_id)

    if request.method == 'POST':
        question.deleteChoices(request.POST.get('question'), request.POST.get('choices',''))
        return HttpResponseRedirect(reverse('polls:index'))
    
    return render(request, 'polls/edit.html', {'question':question})



####################### MESSAGES AND ALL OTHER NOTIFICATIONS ####################


@login_required
def dm(request, id):
    
    # User first enters a private Chat
    #1) if user is making a post request then we know that the friend is the other user
    # and his notification flag should automatically be set
    friend = User.objects.get(pk=id)
    # query = str(request.user.id) + '-' + str(friend.id) if request.user.id < friend.id else str(friend.id) + '-' + str(request.user.id)
    # helper function designed to create key for parent chat conversation object.
    key1 = key(request.user.id,id)

    if request.method == 'POST':

        if friend not in request.user.user.chats.all():
            request.user.user.chats.add(friend)
            friend.user.chats.add(request.user)

        # Try to pull from table if conversation exists
        try:
            print("try get DmThrough")
            dmt = DmThrough.objects.get(pk=key1)
        # create new entry for conversation if key does not exist

        except (KeyError, DmThrough.DoesNotExist):
            print('error')
            dmt = DmThrough.objects.create(id = key1,new_messages=True, 
            who_last = request.user.username, who_last_u= friend)
            # dmt.create_key(request.user.id, id)
        # reset the new_messages flag after new message

        else:
            dmt.new_messages = True
            # dmt.who_last_u == friend
        # input new message into message table and reset flag to indicate new_messages 
        # are available.

        message = request.POST.get('message')
        dm = DM(comp=dmt, mb=request.user,fw=friend, message=message, usermade=request.user.username)
        dmt.new_messages = True
        friend.notification.chat_flag = True
        friend.notification.save()
        dmt.who_last_u = friend
        dm.save()
        dmt.save()                   

        return HttpResponseRedirect(reverse('polls:dm', args=(friend.id,)))

    dm = DM.objects.filter(comp=key1)
    # does not enter  the "if block" and comes here and if the Request is a GET
    # if the request.user is not equal to friend then we know we should do nothign and
    # 

    try:
        dmt = DmThrough.objects.filter(pk=key1)[0]

        if dmt.who_last_u == request.user:

            if len(DmThrough.objects.filter(who_last_u=request.user)) == 1:
                request.user.notification.chat_flag = False
                request.user.notification.save()

            dmt.new_messages = False
            dmt.who_last_u = None
            dmt.save()

    except (KeyError, DmThrough.DoesNotExist) as e:
        print('error')

    finally:
        return render(request,'polls/dm.html', {'dm':dm, 'friend': friend, 'yes': len(dm)})

def updatechat(request, id, id2):

    query = key(id,id2)

    if request.user == User.objects.get(pk=id2):
        pass

    notifics = DmThrough.objects.filter(who_last_u = request.user)
    
    if (request.user.notification.chat_flag and len(notifics) == 1):
        notifics = notifics[0]
        notifics.who_last_u = None
        notifics.save()
        request.user.notification.chat_flag = False
        request.user.notificiation.save()
    ###################### END DANGER ########################

    query = str(id) + '-' + str(id2) if id < id2 else str(id2) + '-' + str(id)
    #call key function to generate message thread ID

    query = key(id,id2)
    #fetch all messages for current thread

    chats_r = DM.objects.filter(comp=query)
    #return JsonResponse as Javascript response object
    return JsonResponse({'chats': list(chats_r.values()), 'current_u': request.user.username})

def chats(request):
    
    request.user.notification.save_chat_time()
    # this is where I ws before I deleted.
    ##############
    ##############
    # once chats page is visited clear notifications for the notified user
    notify = []
    spl= None
    flag = False
    x= 0
    limit = len(request.user.user.chats.all())
    # Loop Through Every chat and match them to the chats which have who_last_u set to me

    for thread_x in request.user.user.chats.all():
        spl=True

        for chat in DmThrough.objects.filter(who_last_u = request.user):
            # if not chat.new_messages:
            #     break
            spl = int(chat.id.split('-')[0] if int(chat.id.split('-')[0]) != request.user.id else chat.id.split('-')[1])
            
            if spl == thread_x.id:
                notify.append((thread_x,True))
                spl = False
                flag = True
                chat.new_messages = False
                chat.save()
                break

        if spl:
            notify.append((thread_x,False))
            x += 1

    if x >= limit:
        print(request.user, "enter in", x , "-", limit)
        request.user.notification.chat_flag = False
        request.user.notification.save() 

    return render(request, 'polls/chats.html', {"chats": notify})

@login_required
def chat_notify(request):

    if (len(DmThrough.objects.filter(who_last_u = request.user)) == 1 and request.user.notification.chat_flag):
        pass
    test = False

    if request.user.notification.chat_flag:
        test = True

    query = DmThrough.objects.filter(who_last_u = request.user)
    notify = False
   
    if len(query) >= 1:
        notify = True
        
    return JsonResponse({"notify": notify,"test": test})
  
def fr_request_notify(request):

    if len(request.user.user.requests.all()):
        return JsonResponse({'notify': True})
        
    return JsonResponse({'notify': False})

def comment_notif(request,user_id):

    user = User.objects.get(pk=user_id)
    notify = check_flag_n_comment(request,user)
    
    return JsonResponse({'notify': notify})

def check_profile_flag(request):
    
    notify = False

    if request.user.notification.comment_flag:
        notify = True

    return JsonResponse({"notify": notify})

def clear_chat_notify(request):

    for notif_chat in DmThrough.objects.filter(who_last_u = request.user):
        notif_chat.who_last_u = None
        notif_chat.save()

    request.user.notification.chat_flag = False
    request.user.notification.save() 
    return HttpResponseRedirect(reverse('polls:chats',))
    
def clear_notifi(request, id):

    flag = False
    kkey = key(request.user.id, id)

    for chat in DmThrough.objects.filter(who_last_u = request.user):

        if chat.id == kkey:
            chat.who_last_u = None
            chat.save()
            flag = True
            break

    return HttpResponseRedirect(reverse('polls:chats',))

#####################################  END ##########################################################

### TEST FUNCTON ####
def test123(request):

    articles = Article.objects.all()
    return render(request,'admin/test123.html',context={'articles':articles})

# Another way of getting Models from apps and helps to avoid circular imports

# Article = apps.get_model('blog','Article')

# def finished(sender, **kwargs):
#     print("testing if request finished")
#     print(sender)

# request_finished.connect(finished)
# def image(request):
#     if request.method == 'POST':
#         print('tttt')
#         form = ImageForm(request.POST or None, request.FILES or None)
#         if form.is_valid():
#             print("valid")
#             form.save()
   
#     form = ImageForm()
#     return render(request, 'polls/images.html', {'form': form} )


# @login_required
# def other_profile(request, user_id):


# def test(request):
#     if request.method == 'POST':
#         form = UserSignUp(request.POST)
#         if form.is_valid():
#             form.save()
#             print(form.cleaned_data.get('extra',''))
#             messages.success(request, "You have successfully signed up")
#         else:
#             messages.error(request, "Username already exists")

#     else:
#         form = UserSignUp()
    # return render(request, 'polls/test.html', {'form': form })