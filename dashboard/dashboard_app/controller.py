'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

#Make REST calls
import requests 
from requests import RequestException

from config import GAMEEVENTS_SERVICE_ENDPOINT, CLIENTID, APIKEY

#Logging
from logging import getLogger
LOG = getLogger(__name__)

class EventsController:
    
    def __init__ (self):
        #start with empty token
        self.token = False

    def get_events(self, sessionid):
        try:
            token = self.get_token(sessionid)
            if token:
                LOG.debug("Sending request for events...")
                payload = {"token": token}
                url = GAMEEVENTS_SERVICE_ENDPOINT + '/events'
                response = requests.post(url, json=payload)
                myresponse = response.json()
                return(myresponse)
            else:
                return False
        except RequestException as e:
            LOG.error(e.args, exc_info=False)
            raise e
            #return render_template('error.html', error="Could not process your request, sorry! Reason: %s " % str(e.args))
    
    def get_token(self, sessionid):
        if self.token:
            return self.token
        else:
            payload = {"clientid": CLIENTID, "apikey": APIKEY, "sessionid": sessionid}
            url = GAMEEVENTS_SERVICE_ENDPOINT + '/token'
            LOG.debug("sending request for token...")
            
            try:
                response = requests.post(url, json=payload)
                myresponse = response.json()
                
                if (response.status_code==200):        
                    if "token" in myresponse:
                        token = myresponse["token"]
                        return token
                    else:
                        LOG.debug("Server response: %s " % myresponse["message"])
                        raise Exception("Unknown error when trying to get token.")
                else:
                    if "message" in myresponse:
                        LOG.debug("Server response: %s " % myresponse["message"])
                        #response.raise_for_status()
            except RequestException as e:
                LOG.error("Request exception when trying to get a token. returning false")
                LOG.error(e.args, exc_info=False)
                return False
            except Exception as e:
                LOG.error("Unknown exception when trying to get a token")
                LOG.error(e.args, exc_info=False)
                raise e
    
    def get_sessions(self):
        try:
            payload = {"clientid": CLIENTID, "apikey": APIKEY}
            url = GAMEEVENTS_SERVICE_ENDPOINT + '/sessions'
            LOG.debug("requesting existing sessions...")
            response = requests.post(url, json=payload)
            myresponse = response.json()
            #LOG.debug(myresponse)
            
            if (response.status_code==200): 
                #LOG.debug("Response 200.")       
                if "results" in myresponse:
                    #sessions_list = myresponse["results"]
                    #LOG.debug(sessions_list)
                    return myresponse
                else:
                    LOG.debug("Server response: %s " % myresponse["message"])
                    raise Exception("Unknown error when trying to get sessions.")
            else:
                if "message" in myresponse:
                    LOG.debug("Server response: code %s, message: %s " % (response.status_code, myresponse["message"]))
                    raise Exception("Unknown error when trying to get sessions.")            

        except RequestException as e:
            LOG.error(e.args, exc_info=False)
            raise e
        