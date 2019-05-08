import json


def get_user_and_password():
    user_and_password = {}
    with open('tmp/data.json') as json_file:
        data = json.load(json_file)
        user_and_password["username"] = data["username_clientid"]
        user_and_password["password"] = data["password_apikey"]

    return user_and_password

