'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

#Make REST calls
import requests 

# Exceptions and errors
from requests import RequestException
from simplejson.decoder import JSONDecodeError
import simplejson

# Configuration
from config import GAMEEVENTS_SERVICE_ENDPOINT, CLIENTID, APIKEY, USERPROFILE_SERVICE_ENDPOINT

#Logging
from logging import getLogger

LOG = getLogger(__name__)


class EventsController:
    '''Class that manages the display of events in the dashboard.'''
    
    def __init__ (self):
        #start with empty token
        self.token = False
        
    def get_events(self, sessionid):
        '''
        Fetches the events from the gameevents service for a given sessionid.
        :param sessionid:
        '''
        
        try:
            token = self.get_token()
            if token:
                LOG.debug("Sending request for events...")
                #payload = {"token": token, "sessionid": sessionid}
                headers = {}
                headers["X-AUTH-TOKEN"] = token
                url = GAMEEVENTS_SERVICE_ENDPOINT + '/sessions/%s/events' % sessionid
                response = requests.get(url, headers=headers)
                if (response.status_code==200): 
                    clean_response = {}
                    try:    
                        count = int(response.headers.get('X-Total-Count', None))                    
                        
                        #Load the list of responses
                        json_response = response.json()
                        LOG.debug(json_response)
                        
                        #Iterate over the responses and extract the interesting bit (gameevent key)
                        clean_response = {}
                        events = []
                        
                        for item in json_response:
                            events.append(item["gameevent"])                        
                        
                        clean_response["events"]=events
                        clean_response["count"]=count
                        
                        return clean_response
                    
                    except KeyError:
                        #LOG.debug("Server response: %s " % myresponse["message"])
                        raise Exception("Unrecognized response from server")

                elif (response.status_code==400):
                    raise RequestException("Badly formed request.")
                elif (response.status_code==401):
                    raise RequestException("Not authorized.")
                else:
                    raise Exception("Unknown error when trying to get token.")
            else:
                raise RequestException("Could not get a token.")
        except RequestException as e:
            LOG.error(e.args, exc_info=True)
            raise e
        except ValueError as e:
            LOG.error(e.args, exc_info=False)
            return False
        except Exception as e:
            LOG.error(e.args, exc_info=True)
            raise e
            #return render_template('error.html', error="Could not process your request, sorry! Reason: %s " % str(e.args))
    
    def get_token(self):
        '''
        Makes the request to gameevents service for an authentication token.
        '''
        if self.token:
            return self.token
        else:
            payload = {"clientid": CLIENTID, "apikey": APIKEY}
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
                elif (response.status_code==401):
                    LOG.debug("Server response: %s " % myresponse["message"])
                    raise RequestException("Not authorized.")
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
        '''
        Makes a request to gameevents service to fetch available game sessions.
        '''
        try:
            token = self.get_token()
            if not token:
                raise Exception("Not able to get a valid token.")
            else:             
                headers = {}
                headers["X-AUTH-TOKEN"] = token
                url = GAMEEVENTS_SERVICE_ENDPOINT + '/sessions'
                LOG.debug("requesting existing sessions...")
                response = requests.get(url, headers=headers)
                if (response.status_code==200): 
                    json_response = response.json()
                    formatted_response = {}
                    #LOG.debug("Response 200.") 
                    count = int(response.headers.get('X-Total-Count', None))
                    try:
                        for session in json_response:
                            username = self.get_user_from_sessionid(session["id"])
                            session["username"] = username
                        formatted_response["items"]=json_response
                        formatted_response["count"]=count
                        return formatted_response
                    except KeyError:
                        #LOG.debug("Server response: %s " % myresponse["message"])
                        raise Exception("Unrecognized response from server")
                elif (response.status_code==404):
                        #LOG.debug("Server response: %s " % myresponse["message"])
                        raise RequestException("Session does not exist.")
                elif (response.status_code==401):
                        #LOG.debug("Server response: %s " % myresponse["message"])
                        raise RequestException("Not authorized.")
                else:
                    if "errors" in json_response:
                        #LOG.debug("Server response: code %s, message: %s " % (response.status_code, myresponse["message"]))
                        raise Exception("Unknown error when trying to get sessions.")            

        except RequestException as e:
            LOG.error(e.args, exc_info=False)
            raise e
        
    def get_user_from_sessionid(self, sessionid):
        '''
        Fetches from the user profile service the username associated to a given sessionid. It also 
        searches in inactive game sessions.
        :param sessionid:
        '''
        url = USERPROFILE_SERVICE_ENDPOINT + '/sessions/' + sessionid + '?inactive=true'
        response = requests.get(url)
        #LOG.debug(response.text)
        if response.status_code == 200:
            try:
                myresponse = response.json()
                #LOG.debug(myresponse)
                username = myresponse["user"][0]["username"]    
            except JSONDecodeError:
                username="<unknown>"         
            except (KeyError, TypeError):
                username = "<unknown>"
        else:
            username = "<unknown>"       
        
        return(username)
        