__author__ = 'Alex Pineda'

import webapp2
import re
from hh_models import User, EmailConfirmation
from google.appengine.api import mail
import datetime

import logging

#confirmation key gen
import hashlib, random

class UserAccountEmailSignupHandler(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        screenName = self.request.get("screenName")
        user = User.gql("WHERE email = :email",email=email).get()
        #todo add application/json content header
        if user:
            if user.emailIsVerified:
                self.response.write('{"response":"verified"}')
            else:
                self.response.write('{"response":"not-verified"}')
            return

        #todo, validate email
        if not re.match(r'@',email):
            self.response.write('{"response":"invalid-email"}')
            return

        user = User()
        user.screenName = screenName
        user.put()

        emailConfirmation = EmailConfirmation(parent = user)
        emailConfirmation.email = email
        salt, conf_key = self.generate_email_confirmation_key(email)
        emailConfirmation.confirmationKey = conf_key
        emailConfirmation.salt = salt
        emailConfirmation.put()

        logging.info("sending confirmation to email %s" % email)
        mail.send_mail( sender="Hamilton Hotline <support@hamiltonhotline.com>",
                        to=email,
                        subject="Welcome to Hamilton Hotline!",
                        body="""
                        <html>
                            <body>
                            <h1>Welcome to Hamilton Hotline!</h1>
                            <p>Call or listen in! WOOHOO!</p>
                            <a href="http://www.hamiltonhotline.com/confirm-email?key=%s">Click here to choose your password and finish your signup</a>
                            <p>WE LOVE YOU!</p>
                            </body>
                        </html>
                        """ % "lol"
                        )
        self.response.write('{"response":"confirmation-sent"}')


    def generate_email_confirmation_key(self, email):
        salt = hashlib.sha256(str(random.random())).hexdigest()[:5]
        confirmation_key = hashlib.sha256(salt + email).hexdigest()
        return salt, confirmation_key

class UserAccountEmailConfirmationHandler(webapp2.RequestHandler):
    def post(self):
        password = self.request.get("password")
        if password is None:
            #todo push password entry form
            return
        #todo validate password

        key = self.request.get("key")
        emailConf = EmailConfirmation.gql("WHERE confirmationKey = :key", key = key).get()
        logging.info("confirming email %s", emailConf.email)

        #todo check expiry
        if not emailConf:
            return        #todo respond about invalid email conf

        user = emailConf.parent()
        if user is None:
            logging.error("The email confirmation %s has no parent", str(emailConf.key()))#todo, user message
            return
        user.emailIsConfirmed = datetime.datetime.now()
        user.email = emailConf.email
        user.password_salt, user.password = self.generate_password_hash(password)
        user.put()
        emailConf.delete()
        logging.info("user %s is confirmed", user.email)

    def generate_password_hash(self, password):
        salt = hashlib.sha256(str(random.random())).hexdigest()[:5]
        hashed_password = hashlib.sha256(salt + password).hexdigest()
        return salt,hashed_password

