import sys
from wit import Wit


def get_access_token():
    f = open(".config", "r")
    token = f.readline()
    return token


def test(client, message):
    resp = client.message(message)
    print(resp)

    # on_off = None
    # appliance = None
    # intensity = None
    #
    # try:
    #     on_off = resp['entities']['on_off'][0]['value']
    #     appliance = resp['entities']['appliance'][0]['value']
    #     intensity = resp['entities']['intensity'][0]['value']
    # except:
    #     pass
    #
    # print(on_off)
    # print(appliance)
    # print(intensity)


wit_client = Wit(access_token=get_access_token())
message = ""
while message != 'exit':
    message = raw_input('Enter command: ')
    # message = "increase the fan speed"
    test(wit_client, message)