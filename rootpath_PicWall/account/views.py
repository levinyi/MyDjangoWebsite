from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login # 1
from django.urls import reverse

from .forms import LoginForm, RegistrationForm, UserProfileForm


# Create your views here.
def user_login(request): #2
    if request.method =="POST": #3
        login_form = LoginForm(request.POST)  #4
        if login_form.is_valid():  #5
            cd = login_form.cleaned_data  #6
            user = authenticate(username=cd['username'], password=cd['password'])  #7
            if user:
                login(request, user) #8
                return HttpResponse("Wellcome you. you have been authenticated successfully")  #9
            else:
                return HttpResponse("Sorry, your username or password is not right.")
        else:
            return HttpResponse("Invalid login")
    if request.method =="GET":
        login_form = LoginForm()
        return render(request, "account/login.html", {"form":login_form})


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        userprofile_form = UserProfileForm(request.POST)
        if user_form.is_valid()*userprofile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_profile = userprofile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()
            return HttpResponseRedirect(reverse('account:user_login'))
        else:
            return HttpResponse('sorry, your username or password is not right')
    else:
        user_form = RegistrationForm()
        userprofile_form = UserProfileForm()
        return render(request, 'account/register.html',{'form':user_form, "profile":userprofile_form})