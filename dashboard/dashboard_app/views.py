# -*- coding: utf-8 -*-

'''
Defines the views of the dashboard.
This defines the interaction points, but the actual logic is treated
by the :mod:`controller`.
'''

from flask import current_app, Blueprint, render_template, request
from flask import jsonify
#from lxml import objectify
import dateutil.parser
import json
from flask_api import status

from requests import RequestException, ConnectionError

from dashboard_app import controller
from dashboard_app import util



#Logging
from logging import getLogger
from simplejson.scanner import JSONDecodeError
LOG = getLogger(__name__)

#Blueprint
dashboard = Blueprint('dashboard', __name__, url_prefix='')

#Declaration of object responsible for controller of events
events_controller = False

@dashboard.route('/error')
def error():
    return render_template("error.html",
                           title='Error')


@dashboard.route('/')
@dashboard.route('/index')
@dashboard.route('/events/', methods = ['GET'])
@dashboard.route('/events', methods = ['GET'])
def index():
    '''
    Lists gaming sessions available to be followed.
    '''
    return render_template("index.html", title='Dashboard')


@dashboard.route('/dashboard/', methods = ['POST'])
def menu():
    '''
    Lists gaming sessions available to be followed.
    '''
    username_clientid = ""
    password_apikey = ""

    try:

        username_clientid = request.form.get('username')
        password_apikey = request.form.get('password')

        #This is a ajust for save information username_clientid and password_apikey, because the implementation about session for avoid input again this information yet no finish.
        data = {"username_clientid": username_clientid, "password_apikey": password_apikey}
        with open('tmp/data.json', 'w') as outfile:
            json.dump(data, outfile)

    except RequestException as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error', error=str(e))    

    session_list = []
    try:
        events_controller = controller.EventsController(username_clientid, password_apikey)
        
        result = events_controller.get_sessions()
        
        items = result['items']
        count = result['count']
        
        LOG.debug(items)
        
        items_sorted = sorted(items, key=lambda d: dateutil.parser.parse(d['created']), reverse = True)
        print(items_sorted)

        return render_template("menu.html", session_list = items_sorted, 
                               count = count, title='Dashboard Home')
    except RequestException as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error', error=str(e))    
    except Exception as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error', error='Unknown error. The developer has been notified.')        
    

@dashboard.route('/events/<sessionid>', methods = ['GET'])
def events(sessionid):
    '''
    Lists game events related to a given *sessionid*.
    :param sessionid:
    '''
    events_list = []

    try:

        #Read username_clientid and password_apikey
        with open('tmp/data.json') as json_file:
            data = json.load(json_file)

        events_controller = controller.EventsController(data["username_clientid"], data["password_apikey"])
        result = events_controller.get_events(sessionid)
        if result:
            try:
                for event in result["events"]:
                    #LOG.debug(event)
                    formatted_event = _format_event(event)
                    #LOG.debug(formatted_event)
                    events_list.append(formatted_event)
            except (AttributeError,KeyError,JSONDecodeError):
                return render_template("error.html",
                       title='Error',
                       error='Error reading the list of events from service.')

    except ConnectionError as e:
        return render_template("error.html",
                           title='Error',
                           error='Connection error. Is the game events service up?')

    except Exception as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error',
                           error=e.args)

    #get conceitos
    aux_controller = get_controller()
    dic_conceito = aux_controller.get_list_conceitos()

    #Sort by timestamp desc
    events_list_sorted = sorted(events_list, key=lambda d: d['timestamp'], reverse = True)  

    return render_template('events.html', events = events_list_sorted, sessionid=sessionid, dic_conceito=dic_conceito)


@dashboard.route('/metrica-acc/<sessionid>')
def metrica_acc(sessionid):
    '''
    Calcula a metrica ACC.
    '''

    try:
        controller = get_controller()
        username = controller.get_user_from_sessionid(sessionid)

        #get conceitos
        lista_conceitos = []
        for dic_conceito in controller.get_list_conceitos():
            print(dic_conceito)
            lista_conceitos.append(dic_conceito['nome'])

        #genereted metrica ACC
        tabela_acc = controller.calcular_metrica_acc(username, lista_conceitos)['metrica_acc']
        for dic_conceito in controller.get_list_conceitos():
            tabela_acc[str(dic_conceito['nome'])] = tabela_acc[str(dic_conceito['id'])]
            del tabela_acc[str(dic_conceito['id'])]

        LOG.debug(tabela_acc)

        return render_template("metrica-acc.html", aluno=username, tabela_acc = tabela_acc, lista_conceitos=lista_conceitos, title='Métrica de Aquisição de Conceitos-Chaves (ACC)')

    except Exception as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error',
                           error=e.args)

@dashboard.route('/vsr/<sessionid>', methods = ['POST'])
def vsr(sessionid):
    '''
    Escala de Verificação de Similaridade de Respostas (VSR).
    '''

    # Check if request is json and contains all the required fields
    required_fields = ["conceitos"]

    error = {}

    if not request.form or not (set(required_fields).issubset(request.form)):
        LOG.error("Erro request, field conceitos is not present.", exc_info=True)
        return render_template("error.html",
                           title='Error',
                           error="Erro request, field conceitos is not present.")

    try:
        controller = get_controller()
        username = controller.get_user_from_sessionid(sessionid)

        #get list from atividades
        lista_atividades = controller.get_list_all_atividades()[:-2]

        #get conceito
        nome_conceito = request.form['conceitos']
        LOG.debug(nome_conceito)

        #genereted metrica ACC
        vsr = controller.gerar_vsr(username, lista_atividades, nome_conceito)['message']['vsr']

        # altering the first column of last raw from number where value is number for one string 'TC', because this is correct presentation according VSR.
        vsr[-1][0] = "TC"
        LOG.debug(vsr[-1][0])

        #getting length raw from table vsr, because it's necessary inform the number of questões
        length = len(vsr[1]) - 2

        return render_template("vsr.html", aluno=username, vsr=vsr, length=length,
                               title='Escala de Verificação de Similaridade de Respostas (VSR)')

    except Exception as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error',
                           error=e.args)



def _format_event(event):
    '''
    Internal helper function to clean up fields in the event before sending to template.
    :param event:
    '''
    
    
    if not ("level" in event):
        event["level"] = "==Not in a level=="
    else:
        if (event["level"] == ""):
            event["level"] = "==Not in a level=="
    
    if not ("timestamp" in event):
        event["timestamp"] = "==No timestamp=="
    else:
        if (event["timestamp"] == ""):
            event["timestamp"] = "==No timestamp=="        
        
    if not ("action" in event):
        event["action"] = "==No action=="
    else:
        if event["action"] =="":
            event["action"] = "==No action=="
    
    if not ("update" in event):
        event["update_string"] = ""
    else:
        event["update_string"] = event["update"]
        event.pop("update", None)
        
    if not ("result" in event):
        event["result"] = {}
    else:
        #LOG.debug(event["result"])
        if len(event["result"])>0:
            event["result"] = event["result"][0]
        else:
            event["result"] = {}

    return(event)


def get_controller():
    # Read username_clientid and password_apikey
    with open('tmp/data.json') as json_file:
        data = json.load(json_file)

    events_controller = controller.EventsController(data["username_clientid"], data["password_apikey"])
    return events_controller
