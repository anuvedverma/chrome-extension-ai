import sys
import json
from wit import Wit


# Workflow
# 1 - define "extract commands" function
# 2 - define function to extract relevant data for each command type (in order of execution)
# 3     - return dict object for just that command
# 4 - combine them into single object
# 5 - jsonify object and return

# Define command entities
command_new_window = 'command_new_window'
command_new_tab = 'command_new_tab'
command_go_to_website = 'command_go_to_website'
command_search = 'command_search'
command_bookmark_page = 'command_bookmark_page'
command_open_downloads = 'command_open_downloads'
command_clear_browsing_data = 'command_clear_browsing_data'
command_check_email = 'command_check_email'

# Define infer-able param entities
bookmark_name = 'bookmark_name'
browsing_data_type = 'browsing_data_type'
url = 'url'

# Define remaining param entities
number = 'number'
message_body = 'message_body'
duration = 'duration'

entities_list = [
    command_new_window,
    command_new_tab,
    command_go_to_website,
    command_search,
    command_bookmark_page,
    command_open_downloads,
    command_clear_browsing_data,
    command_check_email,
    bookmark_name,
    browsing_data_type,
    url
]

pop_sites_map = {
    'gmail': 'www.gmail.com',
    'facebook': 'www.facebook.com',
    'twitter': 'www.twitter.com',
    'linkedin': 'www.linkedin.com',
    'amazon': 'www.amazon.com',
    'wikipedia': 'www.wikipedia.com',
    'youtube': 'www.youtube.com',
    'google': 'www.google.com',
    'reddit': 'www.reddit.com',
    'yahoo': 'www.yahoo.com',
    'msn': 'www.msn.com',
    'hotmail': 'www.hotmail.com',
    'outlook': 'www.outlook.com'
}

# Map entities to actions
# action_map = {'command_new_window': 'new_window',
#               'command_new_tab': 'new_tab',
#               'command_go_to_website': 'go_to_website',
#               'bookmark_name': 'bookmark_page',
#               'command_search': 'search',
#               'command_bookmark_page': 'bookmark_page',
#               'command_open_downloads': 'open_downloads',
#               'browsing_data_type': 'clear_browsing_data',
#               'command_clear_browsing_data': 'clear_browsing_data',
#               'command_check_email': 'check_email',
#               'url': 'go_to_website'}
#
# action_map2 = {'new_tab': ['command_new_tab'],
#               'new_window': ['command_new_window'],
#               'go_to_website': ['command_go_to_website', 'url'],
#               'check_email': ['command_check_email'],
#               'open_downloads': ['command_open_downloads'],
#               'search': ['command_search'],
#               'bookmark_page': ['command_bookmark_page', 'bookmark_name'],
#               'clear_browsing_data': ['command_clear_browsing_data', 'browsing_data_type']
#               }

# Initialize list of actions to execute
actions = []


def get_access_token():
    f = open(".config", "r")
    token = f.readline()
    return token


def extract_commands(client, message):
    wit_resp = client.message(message)
    print(wit_resp)
    print('\n')

    entities = list(wit_resp['entities'])

    # Execute according to command entities
    if command_new_tab in entities:
        extract_new_tab(wit_resp)

    if command_new_window in entities:
        extract_new_window(wit_resp)

    if command_go_to_website in entities or url in entities:
        extract_go_to_website(wit_resp)

    if command_check_email in entities:
        extract_check_email(wit_resp)

    if command_open_downloads in entities:
        extract_open_downloads(wit_resp)

    if command_search in entities:
        extract_search(wit_resp)

    if command_bookmark_page in entities or bookmark_name in entities:
        extract_bookmark_page(wit_resp)

    if command_clear_browsing_data in entities or browsing_data_type in entities:
        extract_clear_browsing_data(wit_resp)


def extract_new_tab(wit_resp):
    new_tab_entities = wit_resp['entities'][command_new_tab]

    for entity in new_tab_entities:
        data = {'action': 'new_tab'}
        try:
            data['num_tabs'] = entity['entities']['number'][0]['value']
        except:
            data['num_tabs'] = 1
        actions.append(data)


def extract_new_window(wit_resp):
    sentence = wit_resp['_text']
    print(sentence)
    incognito = ['incognito', 'private', 'hidden', 'anonymous']

    new_window_entities = wit_resp['entities'][command_new_window]

    for entity in new_window_entities:
        data = {'action': 'new_window'}
        try:
            data['num_windows'] = entity['entities']['number'][0]['value']
        except:
            data['num_windows'] = 1

        if set(incognito).isdisjoint(sentence.lower().split(' ')):
            data['incognito'] = False
        else:
            data['incognito'] = True
        actions.append(data)


def extract_go_to_website(wit_resp):
    # if command-go-to-website...
    go_to_website_entities = None
    url_entities = None
    bookmark_entities = None

    try:
        go_to_website_entities = wit_resp['entities'][command_go_to_website]
    except:
        pass

    try:
        url_entities = wit_resp['entities'][url]
    except:
        pass

    try:
        bookmark_entities = wit_resp['entities'][command_bookmark_page]
    except:
        pass

    try:
        bookmark_entities += wit_resp['entities'][bookmark_name]
    except:
        pass

    if go_to_website_entities is not None:
        sentence = wit_resp['_text']
        for entity in go_to_website_entities:
            data = {'action': 'go_to_website'}
            try:
                sub_url = entity['entities'][url][0]['value']
                data['url'] = sub_url
            except:
                if url_entities is not None:
                    sub_url = url_entities['entities'][url][0]['value']
                    data['url'] = sub_url
                elif not set(sentence.lower().split(' ')).isdisjoint(set(pop_sites_map.keys())):
                    site_name = set(sentence.lower().split(' ')).intersection(set(pop_sites_map.keys())).pop()
                    data['url'] = pop_sites_map[site_name]
                else:
                    data['missing_param'] = True
                    data['error_message'] = 'Please include a valid website you would like to visit'
            actions.append(data)

    # if url but no bookmark...
    elif url_entities is not None and bookmark_entities is None:
        for entity in url_entities:
            data = {'action': 'go_to_website',
                    'url': entity['value']
                    }
            actions.append(data)

    # if url and bookmark... (save processing for bookmark)
    else:
        pass


def extract_check_email(wit_resp):
    sentence = wit_resp['_text']
    data = {'action': 'go_to_website'}
    sites = set(sentence.lower().split(' ')).intersection(pop_sites_map.keys())
    if len(sites) != 0:
        data['url'] = pop_sites_map[sites.pop()]
    else:
        data['url'] = 'www.gmail.com'
    actions.append(data)


def extract_open_downloads(wit_resp):
    data = {'action': 'open_downloads'}
    actions.append(data)


def extract_search(wit_resp):
    search_entities = wit_resp['entities'][command_search]
    search_query = None

    for entity in search_entities:
        data = {'action': 'search'}
        try:
            search_query = entity['entities']['message_body'][0]['value']
        except:
            try:
                search_query = wit_resp['entities']['message_body'][0]['value']
            except:
                pass

        if search_query is not None:
            data['query'] = search_query
        else:
            data['query'] = ''
        actions.append(data)


def extract_bookmark_page(wit_resp):
    bookmark_entities = None
    bookmark_name_entities = None

    try:
        bookmark_entities = wit_resp['entities'][command_bookmark_page]
    except:
        pass

    try:
        bookmark_name_entities = wit_resp['entities'][bookmark_name]
    except:
        try:
            bookmark_name_entities = wit_resp['entities']['message_body']
        except:
            pass

    # if bookmark-entities is not None
    if bookmark_entities is not None:
        for entity in bookmark_entities:
            data = {'action': 'bookmark'}

            # handle bookmark name
            try:
                name_bookmark = entity['entities'][bookmark_name][0]['value']
            except:
                try:
                    name_bookmark = entity['entities']['message_body'][0]['value']
                except:
                    try:
                        name_bookmark = wit_resp['entities']['message_body'][0]['value']
                    except:
                        name_bookmark = ''
            data['bookmark_name'] = name_bookmark

            # handle bookmark url
            try:
                bookmark_url = entity['entities'][url][0]['value']
            except:
                try:
                    bookmark_url = wit_resp['entities'][url][0]['value']
                except:
                    bookmark_url = 'CURRENT PAGE'
            data['url'] = bookmark_url
            actions.append(data)
    elif bookmark_name_entities is not None:
        for entity in bookmark_name_entities:
            data = {'action': 'bookmark'}

            # handle bookmark name
            try:
                name_bookmark = entity['entities'][bookmark_name][0]['value']
            except:
                name_bookmark = ''
            data['bookmark_name'] = name_bookmark

            # handle bookmark url
            try:
                bookmark_url = entity['entities'][url][0]['value']
            except:
                try:
                    bookmark_url = wit_resp['entities'][url][0]['value']
                except:
                    bookmark_url = 'CURRENT PAGE'
            data['url'] = bookmark_url
            actions.append(data)


def extract_clear_browsing_data(wit_resp):
    clear_browsing_entities = None
    browsing_data_entities = None

    try:
        clear_browsing_entities = wit_resp['entities'][command_clear_browsing_data]
    except:
        pass

    try:
        browsing_data_entities = wit_resp['entities'][browsing_data_type]
    except:
        pass

    # if clear-browsing-entities is not None
    if clear_browsing_entities is not None:
        for entity in clear_browsing_entities:
            data = {'action': 'clear_browsing_data'}

            # handle browsing data type
            try:
                data_type = entity['entities'][browsing_data_type][0]['value']
            except:
                try:
                    data_type = wit_resp['entities'][browsing_data_type][0]['value']
                except:
                    data_type = 'all'
            data['browsing_data_type'] = data_type

            # handle time duration
            try:
                duration = entity['entities']['duration'][0]['value']
                unit = entity['entities']['duration'][0]['unit']
            except:
                try:
                    duration = wit_resp['entities']['duration'][0]['value']
                    unit = wit_resp['entities']['duration'][0]['unit']
                except:
                    duration = 'all'
                    unit = 'None'
            data['duration'] = duration
            data['unit'] = unit
            actions.append(data)
    elif browsing_data_entities is not None:
        data = {'action': 'clear_browsing_data'}

        # handle browsing data type
        try:
            data_type = wit_resp['entities'][browsing_data_type][0]['value']
        except:
            data_type = 'all'
        data['browsing_data_type'] = data_type

        # handle time duration
        try:
            duration = wit_resp['entities']['duration'][0]['value']
            unit = wit_resp['entities']['duration'][0]['unit']
        except:
            duration = 'all'
            unit = 'None'
        data['duration'] = duration
        data['unit'] = unit
        actions.append(data)


wit_client = Wit(access_token=get_access_token())
message = ""
while message != 'exit':
    message = raw_input('Enter command: ')
    # message = "increase the fan speed"
    extract_commands(wit_client, message)
    json_data = json.dumps(actions)
    actions = []
    print(json_data)
