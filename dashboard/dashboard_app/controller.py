'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

#Make REST calls
import requests
import json

# Exceptions and errors
from requests import RequestException
from simplejson.decoder import JSONDecodeError
import simplejson

# Configuration
from config_sample import GAMEEVENTS_SERVICE_ENDPOINT, USERPROFILE_SERVICE_ENDPOINT, LEARNINGANALYSIS_SERVICE_ENDPOINT

#Logging
from logging import getLogger

LOG = getLogger(__name__)


class EventsController:
    '''Class that manages the display of events in the dashboard.'''
    
    def __init__ (self, clientid, apikey):
        #start with empty token
        self.token = False
        self.clientid = clientid
        self.apikey = apikey
        
    def get_events(self, sessionid):
        '''
        Fetches the events from the gameevents service for a given sessionid.
        :param sessionid:
        '''
        
        try:
            token = self.get_token()
            if token:
                #LOG.debug("Sending request for events...")
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
                        raise RequestException("Unrecognized response from server")

                elif (response.status_code==400):
                    raise RequestException("Badly formed request.")
                elif (response.status_code==401):
                    raise RequestException("Not authorized.")
                else:
                    raise RequestException("Unknown error when trying to get token.")
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
            payload = {"clientid": self.clientid, "apikey": self.apikey}
            url = GAMEEVENTS_SERVICE_ENDPOINT + '/token'
            # LOG.debug("sending request for token..." + GAMEEVENTS_SERVICE_ENDPOINT)

            try:
                response = requests.post(url, json=payload)
                myresponse = response.json()
                
                # print(response.status_code)
                # print(myresponse)


                if (response.status_code==200):        
                    if "token" in myresponse:
                        token = myresponse["token"]
                        return token
                    else:
                        #LOG.debug("Server response: %s " % myresponse["message"])
                        raise RequestException("Unknown error when trying to get token.")
                elif (response.status_code==401):
                    LOG.debug("Server response: %s " % myresponse["message"])
                    raise RequestException("Not authorized.")
                elif (response.status_code==400):
                    #LOG.debug("Server response: %s " % myresponse["message"])
                    raise RequestException("Badly formed request. Change in the API?")
                else:
                    #LOG.debug("Server response: %s " % myresponse["message"])
                    response.raise_for_status()
            except RequestException as e:
                LOG.error("Request exception when trying to get a token. returning false")
                #LOG.error(e.args, exc_info=False)
                return False
            except Exception as e:
                #LOG.error("Unknown exception when trying to get a token")
                LOG.error(e.args, exc_info=True)
                raise RequestException('Unknown error when trying to get a token.')
    
    def get_sessions(self):
        '''
        Makes a request to gameevents service to fetch available game sessions.
        '''
        try:
            token = self.get_token()
            if not token:
                raise RequestException("Not able to get a valid token.")
            else:             
                headers = {}
                headers["X-AUTH-TOKEN"] = token
                url = GAMEEVENTS_SERVICE_ENDPOINT + '/sessions'
                #LOG.debug("requesting existing sessions...")
                response = requests.get(url, headers=headers)
                if (response.status_code==200): 
                    json_response = response.json()
                    formatted_response = {}
                    #LOG.debug("Response 200.") 
                    count = int(response.headers.get('X-Total-Count', None))
                    try:
                        for session in json_response:
                            username = self.get_user_from_sessionid(session["id"])
                            # print("oioioioio:::" + str(username))
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
                    LOG.debug("Server response: %s" % response.get_text() )
                    response.raise_for_status()            

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

        # LOG.debug(response.text)
        if response.status_code == 200:
            try:
                myresponse = response.json()
                # LOG.debug(myresponse)
                id_user = myresponse['_links'][1]['href'].split('/', 3)[-1]

                url_user = USERPROFILE_SERVICE_ENDPOINT + '/users/' + id_user
                response_user = requests.get(url_user)

                # LOG.debug(response_user.json()["message"]["username"])

                username = response_user.json()["message"]["username"]
                # LOG.debug(username)

            except JSONDecodeError:
                username="<unknown>"         
            except (KeyError, TypeError):
                username = "<unknown>"
        else:
            username = "<unknown>"       
        
        return(username)

    def set_notas_for_learning_analisys(self, sessionid, nome_aluno):
        eventos = self.get_events(sessionid)
        id_habilidade_mundo = sessionid
        for event in eventos:
            id_atividade = self.get_id_atividade(nome_aluno, str(id_habilidade_mundo))['id_atividade']
            LOG.debug(id_atividade)
            self.set_nota(int(id_atividade), int(event["id_questao"]), event["nota"])



    # #Def for test
    # def criar_questoes(self, quesito, tipo_questao):
    #     '''
    #     Def for test
    #     :param quesito:
    #     :param tipo_questao:
    #     :return:
    #     '''
    #     aux_conceitos_chave= ["alfa", "beta", "gama", "delta"]
    #     index = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1]
    #
    #     list_questoes = []
    #     for i in range(10):
    #         aux_dic = {}
    #         aux_dic['quesito'] = quesito + str(i)
    #         aux_dic['tipoDeQuestao'] = tipo_questao
    #         aux_dic['conceitoChave'] = aux_conceitos_chave[index[i]]
    #         list_questoes.append(aux_dic)
    #
    #     return list_questoes
    # #Def for test
    # def criar_e_enviar_atividade_para_service(self):
    #     '''
    #     Def for test
    #     :param quesito:
    #     :param tipo_questao:
    #     :return:
    #     '''
    #     url = LEARNINGANALYSIS_SERVICE_ENDPOINT + '/atividades'
    #     payload = {'some': 'data'}
    #     headers = {'content-type': 'application/json'}
    #
    #     # atividades = []
    #     aux_dic = {}
    #     peso = 1
    #
    #     for i in range(5):
    #         questoes = self.criar_questoes(str(i), 'ordenacao')
    #         aux_dic = {}
    #         aux_dic['nome'] = "Joao e maria"
    #         aux_dic['questoes'] = questoes
    #         aux_dic['peso'] = peso
    #         aux_dic['aluno'] = 'danilo'
    #         aux_dic['id_habilidade_mundo'] = peso
    #
    #         peso+=1
    #         print(requests.post(url, data=json.dumps(aux_dic), headers=headers).json())

    def get_id_atividade(self, aluno, id_habilidade_mundo):
        url = LEARNINGANALYSIS_SERVICE_ENDPOINT + '/' + aluno + '/atividades/' + id_habilidade_mundo
        # payload = {'nota': nota}
        headers = {'content-type': 'application/json'}

        r = requests.get(url)
        return r.json()['message']



    def set_nota(self, id_atividade, quesito, nota):
        url = LEARNINGANALYSIS_SERVICE_ENDPOINT + '/atividade/' + id_atividade + '/questao/' + quesito
        print(url)
        payload = {'nota': nota}
        headers = {'content-type': 'application/json'}

        return requests.post(url, data=json.dumps(payload), headers=headers).json()

    def calcular_metrica_acc(self, aluno, lista_conceitos):
        url = LEARNINGANALYSIS_SERVICE_ENDPOINT + '/' + aluno + '/calcular_metrica_acc'
        print(url)
        payload = {'lista_conceitos': lista_conceitos}
        headers = {'content-type': 'application/json'}

        r = requests.get(url, data=json.dumps(payload), headers=headers)
        return r.json()['message']


    def get_list_conceitos(self):
        url = LEARNINGANALYSIS_SERVICE_ENDPOINT + '/conceitos'
        headers = {'content-type': 'application/json'}

        r = requests.get(url)
        return r.json()

    def get_list_atividades(self, nome_aluno):
        url = LEARNINGANALYSIS_SERVICE_ENDPOINT + '/' + nome_aluno + '/atividades'
        headers = {'content-type': 'application/json'}

        r = requests.get(url)
        return r.json()

    def get_list_all_atividades(self):
        url = LEARNINGANALYSIS_SERVICE_ENDPOINT + '/atividades'
        headers = {'content-type': 'application/json'}

        r = requests.get(url)
        return r.json()


    def gerar_vsr(self, aluno, lista_atividades, conceito_chave):
        url = LEARNINGANALYSIS_SERVICE_ENDPOINT + '/' + aluno + '/verificar_similaridade_respostas'
        print(url)
        payload = {'lista_atividades': lista_atividades, "conceito_chave": conceito_chave}
        headers = {'content-type': 'application/json'}

        r = requests.get(url, data=json.dumps(payload), headers=headers)
        return r.json()
