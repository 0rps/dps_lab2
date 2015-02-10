from django.db import models
from django.db.models.signals import post_init

from datetime import datetime, timedelta
import pytz

import json
import hashlib

import pprint

def dump(v):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(v)

def debug(msg):
    print "DEBUG: " + str(msg)

def exact(str):
    return r'\b' + str + r'\b'

class User(models.Model):
    name = models.CharField(max_length=32)
    phone = models.CharField(max_length=16)
    email = models.EmailField()
    password = models.CharField(max_length=32)

    def json(self):
        dict = {}
        dict["name"] = self.name
        dict["phone"] = self.phone
        dict["email"] = self.email

        return json.dumps(dict)


class Bookmark(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=256)
    user = models.ForeignKey(User)

    def shortJson(self):
        return {"id": self.id, "url": self.url}

    def fullJson(self):
        return {"id": self.id, "url": self.url, "title": self.title}


class Authcode(models.Model):
    client_id = models.CharField(max_length=64)
    user = models.ForeignKey(User)
    code = models.CharField(max_length=64)
    creationTime = models.DateTimeField()

    def generateCode(self):
        self.code = hashlib.md5(self.user.email + self.client_id + str(datetime.now().microsecond)).hexdigest()

    def isValid(self):
        dif = datetime.now() - self.creationTime
        dump(self.creationTime)
        debug(str(dif))
        delta = timedelta(minutes=20)
        debug(str(delta))
        return dif <= delta


def authcodePostInit(**kwargs):
    instance = kwargs.get('instance')
    instance.creationTime = datetime.now()


post_init.connect(authcodePostInit, Authcode)


class Token(models.Model):
    user = models.ForeignKey(User)
    accessToken = models.CharField(max_length=64)
    refreshToken = models.CharField(max_length=64)
    expirationDate = models.DateTimeField()

    def generateAccessToken(self):
        debug("generate access token")
        source = self.user.email + str(datetime.now().microsecond)
        code = hashlib.md5(source).hexdigest()

        if len(Token.objects.filter(accessToken__iregex=exact(code))) > 0:
            self.generateAccessToken()
        self.accessToken = code

    def generateRefreshToken(self):
        debug("generate refresh token")
        source = str(self.accessToken) + str(datetime.now().microsecond)
        code = hashlib.md5(source).hexdigest()

        if len(Token.objects.filter(refreshToken__iregex=exact(code))) > 0:
            self.generateRefreshToken()
        self.refreshToken = code


    def isValid(self):
        debug("is valid date function")
        expDate = self.expirationDate
        now = datetime.now(tz=pytz.utc)
        now = now + timedelta(minutes=20)
        result = (now >= expDate)
        return result

    def init(self):
        debug("token init")
        self.generateAccessToken()
        self.generateRefreshToken()
        self.expirationDate = datetime.now() + timedelta(minutes=20)
        debug("token init finish")

    def json(self):
        result = { }
        result['access_token'] = self.accessToken
        result['refresh_token'] = self.refreshToken
        result['expires_in'] = str(20*60)
        return json.dumps(result)


def getAuthcode(code):
    debug("getAuthcode: " + code)
    authcodes = Authcode.objects.filter(code__iregex=exact(code))
    if len(authcodes) > 0:
        code = authcodes[0]
        if code.isValid():
            debug("valid auth")
            return authcodes[0]
        debug("invalid auth")
        code.delete()
    return None


def getAccessToken(accessToken):
    debug("getToken")
    try:
        return list(Token.objects.filter(accessToken__iregex=exact(accessToken)))[0]
    except IndexError:
        debug("none")
        return None

def getToken(refreshToken):
    debug("getToken")
    try:
        return list(Token.objects.filter(refreshToken__iregex=exact(refreshToken)))[0]
    except IndexError:
        debug("none")
        return None

def getUser(email):
    debug("getUser: " + email)
    users = list(User.objects.filter(email__iregex=exact(email)))
    if len(users) > 0:
        return users[0]
    debug("none")
    return None


def authorizeUser(email, password):
    debug("authorizeuser")
    user = getUser(email)
    if user is None:
        return False

    return user.password == password