from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignUpForm, LoginForm
from django.contrib.auth.decorators import login_required


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("round_entry:home")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = SignUpForm()
    return render(request, "users/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = (
                    request.POST.get("next")
                    or request.GET.get("next")
                    or "round_entry:home"
                )
                response = redirect(next_url)
                if request.headers.get("HX-Request"):
                    response["HX-Redirect"] = response.url
                return response
        messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(
        request, "users/login.html", {"form": form, "next": request.GET.get("next", "")}
    )


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("home")


@login_required
def profile_view(request):
    return render(request, "users/profile.html")
