'''
Defines the views of the dashboard.
This defines the interaction points, but the actual logic is treated
by the :mod:`controller`.
'''

from flask import current_app, Blueprint, render_template
from flask import jsonify
from lxml import objectify
import dateutil.parser
import json

from requests import ConnectionError

from dashboard_app import controller

#Logging
from logging import getLogger
LOG = getLogger(__name__)

#Blueprint
dashboard = Blueprint('dashboard', __name__, url_prefix='')

@dashboard.route('/')
@dashboard.route('/index')
@dashboard.route('/events/', methods = ['GET'])
@dashboard.route('/events', methods = ['GET'])
def index():
    session_list = []
    try:
        events_controller = controller.EventsController()
        
        result = events_controller.get_sessions()  
        
        sessions_list_sorted = sorted(result["items"], key=lambda d: dateutil.parser.parse(d['timestamp']), reverse = True)
        
        count = 0
        session_list = []
        
        if "count" in result:
            count = result["count"]
        if "items" in result:
            session_list = sessions_list_sorted

        return render_template("index.html", session_list = session_list, 
                               count = count, title='Dashboard Home')
    except Exception as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error', error=e.args)        
    
    
@dashboard.route('/error')
def error():
    return render_template("error.html",
                           title='Error')


# @dashboard.route('/events/', methods = ['GET'])
# @dashboard.route('/events', methods = ['GET'])
# def eventswrapper():
#     return render_template('eventswrapper.html')

@dashboard.route('/events/<sessionid>', methods = ['GET'])
def events(sessionid):
    #ajax_response = {}
    list_events_as_dict = []
    #list_events_as_xml = []
    try:
        events_controller = controller.EventsController()
        result = events_controller.get_events(sessionid)
        #LOG.debug(events_result) 
        if result:
#             if "items" in result:
#                 list_events_as_xml = result["items"]
#             for event_as_xml in list_events_as_xml:
#                 formatted_event = {}
#                 myevent = objectify.fromstring(event_as_xml["gameevent"])
            if "events" in result:
                events = result["events"]
            
            for event in events:
                formatted_event = {}
                myevent = json.loads(event)
               
                try:
                    formatted_event["level"] = '%s' % myevent.level
                except AttributeError:
                    formatted_event["level"] = "==Not in a level=="
            
                try:
                    #timestamp = datetime.datetime.fromtimestamp(myevent.timestamp)
                    #formatted_event["timestamp"] = '%s' % timestamp.strftime( "%Y-%m-%d %H:%M:%S %Z")
                    #formatted_event["timestamp"] = '%s' % myevent.timestamp
                    formatted_event["timestamp"] = myevent.timestamp
                except AttributeError:
                    formatted_event["timestamp"] = "==No timestamp=="
                    
                try:
                    formatted_event["action"] = '%s' % myevent.action
                except AttributeError:
                    formatted_event["action"] = "==No action=="

                list_events_as_dict.append(formatted_event)
            
            #app.logger.debug(events)
            #events.reverse()

            #Sort by timestamp desc
            events_list_sorted = sorted(list_events_as_dict, key=lambda d: d['timestamp'], reverse = True)

        
        else:
            events_list_sorted = []

    except ConnectionError as e:
        return render_template("error.html",
                           title='Error',
                           error='Connection error. Is the game events service up?')
        #events_list["status"] = "error"
    except Exception as e:
        return render_template("error.html",
                           title='Error',
                           error=e.args)
        #events_list["status"] = "error"

    #return jsonify(ajax_response) 
    return render_template('events.html', events = events_list_sorted, sessionid=sessionid)


# @dashboard.route('/events/<sessionid>', methods = ['GET'])
# def get_events(sessionid):
#     """The index page makes a request to the gameevents service and
#     provides a live feed of the game events for a determined session      
#     """
#     events_xml = False
#     ajax_response = {}
#     try:
#         events_controller = controller.EventsController()
#         events_result = events_controller.get_events(sessionid)   
#         if events_result:
#             current_app.logger.debug(events_result)
# #             if "count" in events_result:
# #                 count = events_result["count"]
#             if "results" in events_result:
#                 events_xml = events_result["results"]
#             events = []
#             for event_xml in events_xml:
#                 formatted_event = {}
#                 
#                 #LOG.debug(event_xml["gameevent"])
#                 myevent = objectify.fromstring(event_xml["gameevent"])
#                 
#                 #current_app.logger.debug(myevent)
#                 
#                 try:
#                     formatted_event["level"] = '%s' % myevent.level
#                 except AttributeError:
#                     formatted_event["level"] = "==Not in a level=="
#             
#                 try:
#                     #timestamp = datetime.datetime.fromtimestamp(myevent.timestamp)
#                     #formatted_event["timestamp"] = '%s' % timestamp.strftime( "%Y-%m-%d %H:%M:%S %Z")
#                     formatted_event["timestamp"] = '%s' % myevent.timestamp
#                 except AttributeError:
#                     formatted_event["timestamp"] = "==No timestamp=="
#                     
#                 try:
#                     formatted_event["action"] = '%s' % myevent.action
#                 except AttributeError:
#                     formatted_event["action"] = "==No action=="
#                 
#                 current_app.logger.debug(formatted_event)
#                 events.append(formatted_event)
#             
#             #app.logger.debug(events)
#             #Invert the response
#             events.reverse()
#             #app.logger.debug(events)
#             ajax_response["status"] = "success"
#             ajax_response["data"] = events
# 
#         
#         else:
#             ajax_response["status"] = "error"
# 
#     except ConnectionError as e:
#         #return render_template("error.html",
#         #                   title='Error',
#         #                   error='Connection error. Is the game events service up?')
#         ajax_response["status"] = "error: %s" % e.args
# 
#     return jsonify(ajax_response)    
    