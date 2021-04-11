from django.http import HttpResponseRedirect


def redirect_on_auth(func):
    def wrapper(request):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/account/profile")
        return func(request)

    return wrapper
