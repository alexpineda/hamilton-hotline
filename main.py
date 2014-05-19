#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import random

import webapp2, os, logging

from google.appengine.ext.webapp import template


#from pytz import timezone

from urlparse import parse_qsl

import time, random
import oauth2 as oauth
from datetime import datetime,tzinfo,timedelta;
import urllib

import twitter

from hh_models import User, VoiceRecording, VoiceTranscription, Stream, TwilioRecordingManagement
from hh_models import Session, EmailConfirmation, PhoneVerification


#est_tz = timezone("US/Eastern")
record_date_fmt = '%Y-%m-%d %H:%M:%S:%f'

TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET=""

TWITTER_HAMILTON_HOTLINE_ACCESS_TOKEN = ""
TWITTER_HAMILTON_HOTLINE_TOKEN_SECRET = ""

TWEET_MAX = 140

TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""

HAMILTON_HOTLINE = '+19055810686'
signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
oauth_consumer = oauth.Consumer(key=TWITTER_CONSUMER_KEY, secret=TWITTER_CONSUMER_SECRET)

#recording_ancestor = db.Key.from_path("HamiltonHotlineRecording","recordings")

class TwitterHelper():
    @staticmethod
    def get_temporary_request_token_from_twitter():
        oauth_client = oauth.Client(oauth_consumer)
        #calling GET when twitter says use post
#        params = {
#            'oauth_callback':'http://www.hamiltonhotline.com'
#        }


#        oauth_consumer_key="",
#        oauth_nonce="",
#        oauth_signature="",
#        oauth_signature_method="HMAC-SHA1",
#        oauth_timestamp="1318467427",
#        oauth_version="1.0"
        #req = oauth.Request(url=twitter.REQUEST_TOKEN_URL, parameters=params)

        #resp, content = oauth_client.request(twitter.REQUEST_TOKEN_URL, method='GET')
        resp, content = oauth_client.request(twitter.REQUEST_TOKEN_URL, 'POST', body=urllib.urlencode({'oauth_callback':"http://www.hamiltonhotline.com/twitter-finalize"}).encode("utf-8"))

        if resp['status'] != '200':
            raise Exception('Invalid respond from Twitter requesting temp token: %s' % resp['status'])
        else:
            return dict(parse_qsl(content))

    @staticmethod
    def get_auth_for_user(request_token):
        return '%s?oauth_token=%s' % (twitter.AUTHORIZATION_URL, request_token['oauth_token'])

    @staticmethod
    def generate_and_sign_request(oauth_token, oauth_token_secret, pincode):

        token = oauth.Token(oauth_token, oauth_token_secret)
        #token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
        token.set_verifier(pincode)

        oauth_client = oauth.Client(oauth_consumer, token)
        resp, content = oauth_client.request(twitter.ACCESS_TOKEN_URL, method='POST', body='oauth_callback=oob&oauth_verifier=%s' % pincode)
        access_token  = dict(parse_qsl(content))

        if resp['status'] != '200':
            raise Exception('The request for a Token did not succeed: %s' % resp['status'])
        else:
            return access_token['oauth_token'], access_token['oauth_token_secret']

def template_render(template_name, template_values=None):
    path = os.path.join(os.path.dirname(__file__), template_name + '.tpl')
    #logging.info("rendering %s") % path
    return template.render(path, template_values)

class MainHandler(webapp2.RequestHandler):

    def get(self):
        #session = Session.load_session(self)
        db_recordings = VoiceRecording.gql("ORDER BY date DESC LIMIT 10").run()

        recordings = process_recordings_for_view(db_recordings)

        template_values = {
            'user' : None,#session.user,
            'recordings' : recordings,
            "allow_auto_play" : True
        }
        self.response.write(template_render('views/homepage',template_values))
#        if session.user and not session.user.beenSetup:
#            session.user.beenSetup = True
#            session.user.put()
        #session.save_session(self)
        return






class TwilioCallHandler(webapp2.RequestHandler):
    def post(self):
        data = template_render('twilio_responses/call')
        self.response.write(data)

class TwilioTranscriptionHandler(webapp2.RequestHandler):
    def post(self):
    #sanity check
        completed = self.request.get("TranscriptionStatus") == "completed"
        if not completed:
            return
        trans_id = self.request.get("TranscriptionSid")
        text = self.request.get("TranscriptionText")
        status = self.request.get("TranscriptionStatus")
        url = self.request.get("TranscriptionUrl")
        recordingSid = self.request.get("RecordingSid")
        recordingUrl = self.request.get("RecordingUrl")

        #needs update if transcription callback was processed first
        recording =  VoiceRecording.gql("WHERE sid = :recordingSid", recordingSid=recordingSid).get()
        if recording is None:
            logging.error("Recording %s was not found in order to update transcription %s" % (recordingSid, trans_id))
            return

        recording.transcriptionText = text
        key = recording.put()
        #update queue or some shit

        transcription = VoiceTranscription(parent=key)#if key None, have cron clean up later
        transcription.status=status
        transcription.sid=trans_id
        transcription.text=text
        transcription.url=url
        transcription.recordingSid=recordingSid
        transcription.recordingUrl=recordingUrl
        key = transcription.put()
        logging.info("Saved new transcription with key %s" % str(key))

        status = post_status(text)
        recording.twitterStatusId = status.id
        recording.twitterStatusText = status.text
        recording.put()
        logging.info("Tweeted with status id %s" % str(status.id))

def post_status(msg):
    democamp = ' #democamp'
    tweet_max = TWEET_MAX - len(democamp)
    status = (msg[:tweet_max-2] + '..'+democamp) if len(msg) > tweet_max else msg + democamp
    api = twitter.Api(consumer_key= TWITTER_CONSUMER_KEY,
                      consumer_secret=TWITTER_CONSUMER_SECRET,
                      access_token_key=TWITTER_HAMILTON_HOTLINE_ACCESS_TOKEN,
                      access_token_secret=TWITTER_HAMILTON_HOTLINE_TOKEN_SECRET,
                      cache=None)

    return api.PostUpdate(status)

class TwilioRecordingThankyouHandler(webapp2.RequestHandler):
    def post(self):
        self.response.write(template_render("twilio_responses/call_complete_response"))

def generate_punchcode():
    code = ''
    random.seed()
    for i in range(6):
        code = code + str(random.randint(0,9))
    return code

def get_recording_from_sid_or_create(callSid, fromPhoneNumber):
    recording = VoiceRecording.gql("WHERE callSid = :callSid",callSid=callSid).get()
    if recording is None:
        #recognize user by phone number
        user = User.gql("WHERE phoneNumber = :phoneNumber AND phoneNumberIsVerified = TRUE", phoneNumber=fromPhoneNumber).get()
        #needs update if transcription callback was processed first
        recording = VoiceRecording(parent=user)
        #no parent recordings are anonymous, permanently
    else:
        user = recording.parent()
    return recording, user

class TwilioAnonRecordingHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("incoming anon call with status %s" % self.request.get("CallStatus"))
        callSid = self.request.get("CallSid")
        fromPhoneNumber = self.request.get("From")
        recording, user = get_recording_from_sid_or_create(callSid, fromPhoneNumber)

        digitsEntered = self.request.get("Digits")
        logging.info("digits " + digitsEntered)

        if digitsEntered != "2":
            logging.info("Invalid anon code entered: " + digitsEntered)
            data = template_render('twilio_responses/invalid_anon_code')
            self.response.write(data)
            return

        logging.info("now calling anonymously for recording id: " + str(recording.callSid))
        recording.anonymousCall = True
        recording.callSid = callSid
        recording.put()
        data = template_render('twilio_responses/anon_record')
        self.response.write(data)



class TwilioRecordingHandler(webapp2.RequestHandler):
    def post(self):
        #sanity check
        callstatus =  self.request.get("CallStatus")
        logging.info("incoming call with status %s" % self.request.get("CallStatus"))

        url = self.request.get("RecordingUrl")
        callSid = self.request.get("CallSid")

        #All phone numbers in requests from Twilio are in E.164 format if possible.
        # For example, (415) 555-4345 would come through as '+14155554345'.
        # However, there are occasionally cases where Twilio cannot normalize an incoming caller ID to E.164.
        # In these situations Twilio will report the raw caller ID string.
        #todo regex for e.164, if raw id found, display Unknown
        fromPhoneNumber = self.request.get("From")

        #TRY TO FIND EXISTING RECORDING
        recording, user = get_recording_from_sid_or_create(callSid, fromPhoneNumber)

        duration = int(self.request.get("RecordingDuration"))
        fromCity = self.request.get("FromCity")
        fromState = self.request.get("FromState")
        fromZip = self.request.get("FromZip")
        fromCountry = self.request.get("FromCountry")
        recordingSid = self.request.get("RecordingSid")
        punchcode = generate_punchcode()

        if recording.anonymousCall:
            callerName = None
        else:
            if user is None:
                callerName = self.request.get("CallerName")
            else:
                callerName = user.screenName

        recording.lastCallStatus=callstatus
        recording.url = url
        recording.mp3Url = url + ".mp3"
        recording.sid = recordingSid
        recording.duration = duration
        recording.callSid=callSid
        recording.fromPhoneNumber=fromPhoneNumber
        recording.fromCity = fromCity
        recording.fromState = fromState
        recording.fromZip = fromZip
        recording.fromCountry = fromCountry
        recording.punchcode = punchcode
        recording.callerName = callerName

        if duration < 10:
            twilioRecording = TwilioRecordingManagement()
            twilioRecording.callSid = callSid
            twilioRecording.action="delete"
            twilioRecording.recordingSid = recordingSid
            twilioRecording.recordingUrl = url
            twilioRecording.put()
            if recording.anonymousCall:
                recording.delete()#record already exists due to prev. processing
            self.response.write(template_render("twilio_responses/call_too_short"))
            return


        key =recording.put()
        logging.info("Saved new recording with key %s" % str(key))
        self.response.write(template_render("twilio_responses/call_complete_response"))

class TwilioRespondHandler(webapp2.RequestHandler):
    def post(self):
        return


class GetLatestRecordingsHandler(webapp2.RequestHandler):
    def get(self):
        lastUpdate = self.request.get("timestamp")
        if (lastUpdate is None):
            return
        date = datetime.strptime(lastUpdate,record_date_fmt)
        #date = est_tz.delocalize(date)
        db_recordings = VoiceRecording.gql('WHERE date > :date AND mp3Url != None ORDER BY date DESC LIMIT 1', date = date).run()
        recordings = process_recordings_for_view(db_recordings)

        view = {
            "recordings" : recordings,
            "allow_auto_play" : True
        }
        self.response.write(template_render('views/recordings',view))


class GetMoreRecordingsHandler(webapp2.RequestHandler):
    def get(self):
        timestamp = self.request.get("timestamp")
        if (timestamp is None):
            return
        date = datetime.strptime(timestamp,record_date_fmt);
        #date = est_tz.delocalize(date)
        db_recordings = VoiceRecording.gql("WHERE date < :date LIMIT 5", date = date).run()
        recordings = process_recordings_for_view(db_recordings)

        view = {
            "recordings" : recordings,
            "allow_auto_play" : False
        }
        self.response.write(template_render('views/recordings',view))

#uses local time??
#
def unix_time_from_datetime(datetime_instance):
    return time.mktime(datetime_instance.timetuple())

def process_recordings_for_view(db_recordings):
    recordings = []
    for r in db_recordings:
        #est_date = est_tz.localize(r.date)
        recording = {
            "id" : r.key(),
            "screenName" : (r.parent() and r.parent().screenName) or r.callerName,
            "anonymous" : r.anonymousCall,
            "date" : r.date.replace(tzinfo=EST),
            "unix_time" : r.date.strftime(record_date_fmt),
            "twitter" : {
                "id" : r.twitterStatusId,
                "text" : r.twitterStatusText
            },
            "transcription" : r.transcriptionText,
            "mp3":r.mp3Url,
            "punchcode" : r.punchcode
        }
        recordings.append(recording)
    return recordings

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name

    def utcoffset(self,dt):
        return timedelta(hours=self.offset)+self.dst(dt)

    def dst(self, dt):
        return timedelta(hours=1) if self.isdst else timedelta(0)

    def tzname(self,dt):
        return self.name

EST = Zone(-5,False,'EST');



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    #('/twitter-login', TwitterLoginHandler),
    #('/logout', LogoutHandler),
    ('/get-latest', GetLatestRecordingsHandler),
    ('/get-more', GetMoreRecordingsHandler),
    #('/req-verify-phone', RequestVerifyPhoneHandler),
#    webapp2.Route(r'/products', handler='main.MainHandler', name='products-list', methods=['GET']),
    ('/call', TwilioCallHandler),
    ('/record', TwilioRecordingHandler),
    ('/anonrecord', TwilioAnonRecordingHandler),
    #('/respond', TwilioRecordingHandler),
    #('/record_thankyou', TwilioRecordingHandler),
    #(r'/reply_start(/\d+)?', TwilioReplyStartHandler),
    ('/transcribe', TwilioTranscriptionHandler)
], debug=True)

