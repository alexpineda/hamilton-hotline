__author__ = 'Alex Pineda'

from google.appengine.ext import db
import logging

#session id generation
import base64, os

#a voice transcription associated with a recording
class VoiceTranscription(db.Model):
    date = db.DateTimeProperty(auto_now_add=True)
    text = db.StringProperty()
    sid = db.StringProperty()
    status = db.StringProperty()
    url = db.StringProperty()
    recordingSid = db.StringProperty()
    recordingUrl = db.StringProperty()

class EmailConfirmation(db.Model):
    email = db.EmailProperty()
    confirmationKey = db.StringProperty()
    salt = db.StringProperty()
    date = db.DateTimeProperty(auto_now=True)
    amtSent = db.IntegerProperty()#keep adding for robots

#a user containing email, password hash, and other information
class User(db.Model):
    twitterAccessToken = db.StringProperty()
    twitterAccessTokenSecret = db.StringProperty()
    twitterId = db.IntegerProperty()
    phoneNumber = db.PhoneNumberProperty()
    phoneNumberIsVerified = db.BooleanProperty()
    screenName = db.StringProperty()
    useTwitterScreenName = db.StringProperty()
    beenSetup = db.BooleanProperty()
    callAnonymously = db.BooleanProperty()
    #getHamiltonDeals

    email = db.EmailProperty()
    emailIsConfirmed = db.DateTimeProperty()
    recordings = db.ListProperty(long)

class Organization(db.Model):
    title = db.StringProperty()

#a categorical stream
class Stream(db.Model):
    organization = db.ReferenceProperty(Organization)
    creator = db.ReferenceProperty(User)
    title = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    punchcode = db.StringProperty()#5 digits
    lastCalled = db.DateTimeProperty()#determines inactive state


class TwilioRecordingManagement(db.Model):
    action = db.StringProperty()
    callSid = db.StringProperty()
    recordingSid = db.StringProperty()
    recordingUrl = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class VoiceRecording(db.Model): #key() for id
    date = db.DateTimeProperty(auto_now_add=True)
    #recording data
    sid = db.StringProperty()
    punchcode = db.StringProperty()#allows responding, 6 digits
    stream = db.ReferenceProperty(Stream)
    mp3Url = db.StringProperty()
    url = db.StringProperty()
    duration = db.IntegerProperty()
    fromPhoneNumber = db.StringProperty()
    callSid = db.StringProperty()
    fromCity = db.StringProperty()
    fromState = db.StringProperty()
    fromCountry = db.StringProperty()
    fromZip = db.StringProperty()
    lastCallStatus = db.StringProperty()

    forOrganization = db.ReferenceProperty(Organization)

    anonymousCall = db.BooleanProperty()
    callerName = db.StringProperty()

    transcriptionText = db.StringProperty()

    twitterStatusId = db.IntegerProperty()
    twitterStatusText = db.StringProperty()

    responseTo = db.SelfReferenceProperty()

class PhoneVerification(db.Model):
    phoneNumber = db.PhoneNumberProperty()
    verificationCode = db.StringProperty()
    twilioSMSStatus = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class Session(db.Model):
    user = db.ReferenceProperty(User)
    id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    oauth_token = db.StringProperty()
    oauth_token_secret = db.StringProperty()

    @staticmethod
    def load_session(webapp2):
        sess_id =  webapp2.request.cookies.get('hh_sess_id', None)
        if sess_id is None:
            logging.debug('no session cookie found, creating new session')
            return Session()

        #session = db.GqlQuery("SELECT * FROM Session WHERE sessid = ")
        session = Session.gql("WHERE id = :id", id=sess_id).get()
        if session is None:
            logging.debug('session not found in db, creating new session')
            return Session()
        else:
            logging.debug('session %s found in db' % sess_id)
            return session

    def save_session(self, webapp2):
        self.id = Session.generate_session_id()
        logging.debug('saving session.__key__ %s with id %s' % (str(self.put()), self.id))
        webapp2.response.headers.add_header('Set-Cookie','hh_sess_id=%s' % self.id)
        #webapp2.response.set_cookie('hh_sess_id', self.id)

    @staticmethod
    def destroy(webapp2):
        webapp2.response.delete_cookie('hh_sess_id')
        #webapp2.response.headers.add_header('Set-Cookie', 'hh_sess_id=;expires=Thu, 01 Jan 1970 00:00:01 GMT"')

    @staticmethod
    def generate_session_id(num_bytes = 16):
        return base64.b64encode(os.urandom(16))#todo replace with PyCrypto implementation
        #return base64.b64encode(M2Crypto.m2.rand_bytes(num_bytes))

    def is_logged_out(self):
        return self.user is None