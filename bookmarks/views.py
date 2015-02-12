from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

import json

from bookmarks import forms
from bookmarks import models

from bookmarks.models import debug

real_client_id = "1234"
real_secret_key = "5678"

# Create your views here.
def register(request):
    debug("register view")
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_c = len(models.User.objects.filter(email__exact=data['email']))
            if user_c > 0:
                return HttpResponse("User with this email is existing")
            user = models.User(name=data['name'], password=data['password'], email=data['email'], phone=data['phone'])
            user.save()
            return render(request, "table.html", {'users': list(models.User.objects.all())})
    else:
        form = forms.RegisterForm()
    return render(request, 'registration.html', {'form': form})

def errorInvalidRequest(redirect_uri):
    res = redirect_uri + "?error=" + "invalid_request"
    debug(res)
    return res


def errorResponceType(redirect_uri):
    res = redirect_uri + "?error=" + "unsupported_responce_type"
    debug(res)
    return res


def errorAccessDenied(redirect_uri):
    res = redirect_uri + "?error=" + "access_denied"
    debug(res)
    return res


def errorUnathourized(redirect_uri):
    res = redirect_uri + "?error=" + "unauthorized_client"
    debug(res)
    return res


def errorInvalidRequestJSON(redirect_uri=None):
    j = json.dumps({"error": "invalid_request"})
    debug("invalid_request")
    return HttpResponseBadRequest(j, content_type="application/json")
    if redirect_uri is None:
        return HttpResponseBadRequest(j, content_type="application/json")
    else:
        return HttpResponseRedirect(redirect_uri, j, content_type="application/json")

def errorUnsupportedGrantJSON(redirect_uri=None):
    j = json.dumps({"error": "unsupported_grant_type"})
    debug("unsupp_grant_type")
    return HttpResponseBadRequest(j, content_type="application/json")
    if redirect_uri is None:
        return HttpResponseBadRequest(j, content_type="application/json")
    else:
        return HttpResponseRedirect(redirect_uri, j, content_type="application/json")

def errorInvalidGrantJSON(redirect_uri=None):
    j = json.dumps({"error": "invalid_grant"})
    debug("invalid_grant")
    return HttpResponseBadRequest(j, content_type="application/json")
    if redirect_uri is None:
        return HttpResponseBadRequest(j, content_type="application/json")
    else:
        return HttpResponseRedirect(redirect_uri, j, content_type="application/json")

def errorInvalidClientJSON(redirect_uri=None):
    j = json.dumps({"error": "invalid_client"})
    debug("invalid_client")
    return HttpResponseBadRequest(j, content_type="application/json")
    if redirect_uri is None:
        return HttpResponseBadRequest(j, content_type="application/json")
    else:
        return HttpResponseRedirect(redirect_uri, j, content_type="application/json")


def authcode(request):
    if request.method == 'GET':
        get = request.GET
        resp_type = get.get('response_type')
        client_id = get.get('client_id')
        redirect_uri = get.get('redirect_uri')

        if redirect_uri is None:
            return HttpResponseBadRequest('Redirect uri is missing')


        if resp_type is None or client_id is None:
            return HttpResponseRedirect(errorInvalidRequest(redirect_uri))

        if resp_type != 'code':
            return HttpResponseRedirect(errorResponceType(redirect_uri))

        if client_id != real_client_id:
            return HttpResponseRedirect(errorAccessDenied(redirect_uri))

        debug("client_id = " + client_id)

        form = forms.SigninForm()
        form.fields['redirect_uri'].initial = redirect_uri
        form.fields['client_id'].initial = client_id
        return render(request, 'signin.html', {'form': form})

    form = forms.SigninForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        if models.authorizeUser(data['email'], data['password']):
            user = models.getUser(data['email'])
            code = models.Authcode(user=user)
            code.redirect_uri = data['redirect_uri']
            code.generateCode()
            code.save()
            url = data['redirect_uri'] + '?code=' + code.code
            return HttpResponseRedirect(url)

    return HttpResponseRedirect(errorUnathourized(data['redirect_uri']))


def httpBasicAuth(request):
    if 'HTTP_AUTHORIZATION' in request.META.keys():
        basic, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
        if basic.lower() == 'basic':
            auth = auth.strip().decode('base64')
            username, password = auth.split(':', 1)
            if username == real_client_id and password == real_secret_key:
                return True
    return False

def getBearerToken(request):
    debug("token request")
    bearer = None

    if "HTTP_AUTHORIZATION" in request.META.keys():
        b_list = request.META["HTTP_AUTHORIZATION"].split(' ')

        if len(b_list) > 1 and b_list[0].lower() == 'bearer':
            bearer = b_list[1]
            debug("Bearer: " + bearer)

    if bearer is not None:
        return models.getAccessToken(bearer)

    return None


def handleRefreshTokenRequest(request):
    debug("handle refresh request")
    post = request.POST
    refresh_token = post.get('refresh_token')

    if refresh_token is None:
        return errorInvalidRequestJSON()

    token = models.getToken(refresh_token)
    if token is not None:
        token.init()
        token.save()
        return HttpResponse(token.json(), content_type="application/json")

    return errorInvalidGrantJSON()


def handleAccessTokenRequest(request):
    debug("handle access token request")
    post = request.POST
    code = post.get('code')
    redirect_uri = post.get('redirect_uri')

    if redirect_uri is None:
        debug("redirect uri is missing")
        return HttpResponseBadRequest('Redirect uri is missing')

    if code is None:
        return errorInvalidRequestJSON(redirect_uri)

    code = models.getAuthcode(code)
    if code is None:
        return errorInvalidGrantJSON(redirect_uri)

    if code.redirect_uri != redirect_uri:
        return errorInvalidGrantJSON(None)

    token = models.Token(user=code.user)
    token.init()
    token.save()

    code.delete()

    debug("access_token = " + token.accessToken)

    return HttpResponse(content=token.json(), content_type="application/json")


def handleMeRequest(request):
    debug("me request")
    token = getBearerToken(request)

    if token is None:
        debug("invalid auth")
        return HttpResponseBadRequest("Invalid auth")


    if not token.isValid():
        debug("token expired")
        return HttpResponseBadRequest("token is expired")

    print "sending user info "
    return HttpResponse(token.user.json(), content_type="application/json")


def handleStatusRequest(request):
    debug("status request")

    count = len(models.Bookmark.objects.all())
    result = {"bookmark_count": count}
    debug("count = " + str(count))
    return HttpResponse(json.dumps(result), content_type="application/json")

def handleBookmarksPaginationRequest(request, page):
    debug("bookmarks request")
    token = getBearerToken(request)
    if token is None:
        print("invalid auth")
        return HttpResponseBadRequest("Invalid auth")

    if not token.isValid():
        print "token expired"
        return HttpResponseBadRequest("token is expired")

    get = request.GET
    perpage = get.get('perpage')

    debug("perpage: " + str(perpage))
    if perpage is None:
        return HttpResponseBadRequest("invalid request")

    user = token.user
    result = [x.shortJson() for x in user.bookmark_set.all()]

    count = len(result)
    page = int(page)
    perpage = int(perpage)
    debug("page:" + str(page))
    if page <= 0 or perpage <= 0:
        return HttpResponseBadRequest("page must be > 0 and perpage must be > 0")

    leftBorder = perpage * (page - 1)

    rightBorder = perpage * page - 1

    debug("count: " + str(count))
    debug("l:" + str(leftBorder) + "  r:" + str(rightBorder))

    if count == 0:
        return json.dumps({"page": 0, "pages": 0, "bookmarks": []})

    if leftBorder >= count:
        return HttpResponseBadRequest("out of range")

    if rightBorder >= count:
        rightBorder = count - 1

    debug("l:" + str(leftBorder) + "  r:" + str(rightBorder))

    result = result[leftBorder:rightBorder]

    debug("result is choosen")

    return HttpResponse(json.dumps({"page": page, "pages": (perpage - 1 + count)/perpage, "bookmarks": result}), content_type="application/json")


def handleBookmarksRequest(request):
    debug("pagination request")
    token = getBearerToken(request)
    if token is None:
        print("invalid auth")
        return HttpResponseBadRequest("Invalid auth")

    if not token.isValid():
        print "token expired"
        return HttpResponseBadRequest("token is expired")

    print "sending user info "
    user = token.user
    result = {"bookmarks": [x.shortJson() for x in user.bookmark_set.all()]}

    return HttpResponse(json.dumps(result), content_type="application/json")


def handleDetailRequest(request, id):
    debug("detail request")
    token = getBearerToken(request)
    if token is None:
        print("invalid auth")
        return HttpResponseBadRequest("Invalid auth")

    if not token.isValid():
        print "token expired"
        return HttpResponseBadRequest("token is expired")

    debug("bookmark id = " + str(id))

    try:
        bms = models.Bookmark.objects.get(id=id)
        debug("scs")
    except:
        debug("bad")
        return HttpResponseBadRequest("none")
    return HttpResponse(json.dumps({"bookmark": bms.fullJson()}), content_type="application/json")


@csrf_exempt
def handleTokenRequest(request):
    if request.method == 'POST':

        post = request.POST

        if not httpBasicAuth(request):
            return errorInvalidClientJSON()

        type = post.get('grant_type')

        if type == 'refresh_token':
            return handleRefreshTokenRequest(request)

        if type == 'authorization_code':
            return handleAccessTokenRequest(request)

        return errorUnsupportedGrantJSON()

    return HttpResponseBadRequest("ONLY POST!")

