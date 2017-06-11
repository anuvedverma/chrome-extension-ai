import json
from wit import Wit


class ChromeExtensionAI:
    """
    The logic/AI object for translating natural language commands
    into an actionable response
    """

    # Define command entities
    CMD_NEW_WINDOW = 'command_new_window'
    CMD_NEW_TAB = 'command_new_tab'
    CMD_GO_TO_WEBSITE = 'command_go_to_website'
    CMD_SEARCH = 'command_search'
    CMD_BOOKMARK_PAGE = 'command_bookmark_page'
    CMD_OPEN_DOWNLOADS = 'command_open_downloads'
    CMD_CLEAR_BROWSING_DATA = 'command_clear_browsing_data'
    CMD_CHECK_EMAIL = 'command_check_email'

    # Define infer-able param entities
    BOOKMARK_NAME = 'bookmark_name'
    BROWSING_DATA_TYPE = 'browsing_data_type'
    URL = 'url'

    # Define remaining param entities
    NUMBER = 'number'
    MESSAGE_BODY = 'message_body'
    DURATION = 'duration'

    entities_list = [
        CMD_NEW_WINDOW,
        CMD_NEW_TAB,
        CMD_GO_TO_WEBSITE,
        CMD_SEARCH,
        CMD_BOOKMARK_PAGE,
        CMD_OPEN_DOWNLOADS,
        CMD_CLEAR_BROWSING_DATA,
        CMD_CHECK_EMAIL,
        BOOKMARK_NAME,
        BROWSING_DATA_TYPE,
        URL
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

    def __init__(self):
        # Connect to Wit API
        self.wit_client = Wit(access_token=self.__get_access_token())

        # Initialize list of actions to execute
        self.actions = []

    def get_response(self, input_text):
        return self.__get_response(input_text, self.wit_client)

    @staticmethod
    def __get_access_token():
        f = open("ai/.config", "r")
        token = f.readline()
        return token

    def __get_response(self, input_text, wit_client):
        self.__extract_commands(wit_client, input_text)
        json_data = json.dumps(self.actions)
        self.actions = []
        return json_data

    def __extract_commands(self, client, message):
        wit_resp = client.message(message)

        entities = list(wit_resp['entities'])

        # Execute according to command entities
        if ChromeExtensionAI.CMD_NEW_TAB in entities:
            self.__extract_new_tab(wit_resp)

        if ChromeExtensionAI.CMD_NEW_WINDOW in entities:
            self.__extract_new_window(wit_resp)

        if ChromeExtensionAI.CMD_GO_TO_WEBSITE in entities or ChromeExtensionAI.URL in entities:
            self.__extract_go_to_website(wit_resp)

        if ChromeExtensionAI.CMD_CHECK_EMAIL in entities:
            self.__extract_check_email(wit_resp)

        if ChromeExtensionAI.CMD_OPEN_DOWNLOADS in entities:
            self.__extract_open_downloads(wit_resp)

        if ChromeExtensionAI.CMD_SEARCH in entities:
            self.__extract_search(wit_resp)

        if ChromeExtensionAI.CMD_BOOKMARK_PAGE in entities or ChromeExtensionAI.BOOKMARK_NAME in entities:
            self.__extract_bookmark_page(wit_resp)

        if ChromeExtensionAI.CMD_CLEAR_BROWSING_DATA in entities or ChromeExtensionAI.BROWSING_DATA_TYPE in entities:
            self.__extract_clear_browsing_data(wit_resp)

        return self.actions

    def __extract_new_tab(self, wit_resp):
        new_tab_entities = wit_resp['entities'][ChromeExtensionAI.CMD_NEW_TAB]

        for entity in new_tab_entities:
            data = {'action': 'new_tab'}
            try:
                data['num_tabs'] = entity['entities'][ChromeExtensionAI.NUMBER][0]['value']
            except:
                data['num_tabs'] = 1

            self.actions.append(data)

    def __extract_new_window(self, wit_resp):
        sentence = wit_resp['_text']
        print(sentence)
        incognito = ['incognito', 'private', 'hidden', 'anonymous']

        new_window_entities = wit_resp['entities'][ChromeExtensionAI.CMD_NEW_WINDOW]

        for entity in new_window_entities:
            data = {'action': 'new_window'}
            try:
                data['num_windows'] = entity['entities'][ChromeExtensionAI.NUMBER][0]['value']
            except:
                data['num_windows'] = 1

            if set(incognito).isdisjoint(sentence.lower().split(' ')):
                data['incognito'] = False
            else:
                data['incognito'] = True

            self.actions.append(data)

    def __extract_go_to_website(self, wit_resp):
        # if command-go-to-website...
        go_to_website_entities = None
        url_entities = None
        bookmark_entities = None

        try:
            go_to_website_entities = wit_resp['entities'][ChromeExtensionAI.CMD_GO_TO_WEBSITE]
        except:
            pass

        try:
            url_entities = wit_resp['entities'][ChromeExtensionAI.URL]
        except:
            pass

        try:
            bookmark_entities = wit_resp['entities'][ChromeExtensionAI.CMD_BOOKMARK_PAGE]
        except:
            pass

        try:
            bookmark_entities += wit_resp['entities'][ChromeExtensionAI.BOOKMARK_NAME]
        except:
            pass

        if go_to_website_entities is not None:
            sentence = wit_resp['_text']
            for entity in go_to_website_entities:
                data = {'action': 'go_to_website'}
                try:
                    sub_url = entity['entities'][ChromeExtensionAI.URL][0]['value']
                    data['url'] = sub_url
                except:
                    if url_entities is not None:
                        sub_url = url_entities['entities'][ChromeExtensionAI.URL][0]['value']
                        data['url'] = sub_url
                    elif not set(sentence.lower().split(' ')).isdisjoint(set(ChromeExtensionAI.pop_sites_map.keys())):
                        site_name = set(sentence.lower().split(' ')).intersection(set(ChromeExtensionAI.pop_sites_map.keys())).pop()
                        data['url'] = ChromeExtensionAI.pop_sites_map[site_name]
                    else:
                        data['missing_param'] = True
                        data['error_message'] = 'Please include a valid website you would like to visit'
                self.actions.append(data)

        # if url but no bookmark...
        elif url_entities is not None and bookmark_entities is None:
            for entity in url_entities:
                data = {'action': 'go_to_website',
                        'url': entity['value']
                        }
                self.actions.append(data)

        # if url and bookmark... (save processing for bookmark)
        else:
            pass

    def __extract_check_email(self, wit_resp):
        sentence = wit_resp['_text']
        data = {'action': 'go_to_website'}
        sites = set(sentence.lower().split(' ')).intersection(ChromeExtensionAI.pop_sites_map.keys())
        if len(sites) != 0:
            data['url'] = ChromeExtensionAI.pop_sites_map[sites.pop()]
        else:
            data['url'] = 'www.gmail.com'

        self.actions.append(data)

    def __extract_open_downloads(self, wit_resp):
        data = {'action': 'open_downloads'}
        self.actions.append(data)

    def __extract_search(self, wit_resp):
        search_entities = wit_resp['entities'][ChromeExtensionAI.CMD_SEARCH]
        search_query = None

        for entity in search_entities:
            data = {'action': 'search'}
            try:
                search_query = entity['entities'][ChromeExtensionAI.MESSAGE_BODY][0]['value']
            except:
                try:
                    search_query = wit_resp['entities'][ChromeExtensionAI.MESSAGE_BODY][0]['value']
                except:
                    pass

            if search_query is not None:
                data['query'] = search_query
            else:
                data['query'] = ''

            self.actions.append(data)

    def __extract_bookmark_page(self, wit_resp):
        bookmark_entities = None
        bookmark_name_entities = None

        try:
            bookmark_entities = wit_resp['entities'][ChromeExtensionAI.CMD_BOOKMARK_PAGE]
        except:
            pass

        try:
            bookmark_name_entities = wit_resp['entities'][ChromeExtensionAI.BOOKMARK_NAME]
        except:
            try:
                bookmark_name_entities = wit_resp['entities'][ChromeExtensionAI.MESSAGE_BODY]
            except:
                pass

        # if bookmark-entities is not None
        if bookmark_entities is not None:
            for entity in bookmark_entities:
                data = {'action': 'bookmark'}

                # handle bookmark name
                try:
                    name_bookmark = entity['entities'][ChromeExtensionAI.BOOKMARK_NAME][0]['value']
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
                    bookmark_url = entity['entities'][ChromeExtensionAI.URL][0]['value']
                except:
                    try:
                        bookmark_url = wit_resp['entities'][ChromeExtensionAI.URL][0]['value']
                    except:
                        bookmark_url = 'CURRENT PAGE'
                data['url'] = bookmark_url
                self.actions.append(data)

        elif bookmark_name_entities is not None:
            for entity in bookmark_name_entities:
                data = {'action': 'bookmark'}

                # handle bookmark name
                try:
                    name_bookmark = entity['entities'][ChromeExtensionAI.BOOKMARK_NAME][0]['value']
                except:
                    name_bookmark = ''
                data['bookmark_name'] = name_bookmark

                # handle bookmark url
                try:
                    bookmark_url = entity['entities'][ChromeExtensionAI.URL][0]['value']
                except:
                    try:
                        bookmark_url = wit_resp['entities'][ChromeExtensionAI.URL][0]['value']
                    except:
                        bookmark_url = 'CURRENT PAGE'

                data['url'] = bookmark_url
                self.actions.append(data)

    def __extract_clear_browsing_data(self, wit_resp):
        clear_browsing_entities = None
        browsing_data_entities = None

        try:
            clear_browsing_entities = wit_resp['entities'][ChromeExtensionAI.CMD_CLEAR_BROWSING_DATA]
        except:
            pass

        try:
            browsing_data_entities = wit_resp['entities'][ChromeExtensionAI.BROWSING_DATA_TYPE]
        except:
            pass

        # if clear-browsing-entities is not None
        if clear_browsing_entities is not None:
            for entity in clear_browsing_entities:
                data = {'action': 'clear_browsing_data'}

                # handle browsing data type
                try:
                    data_type = entity['entities'][ChromeExtensionAI.BROWSING_DATA_TYPE][0]['value']
                except:
                    try:
                        data_type = wit_resp['entities'][ChromeExtensionAI.BROWSING_DATA_TYPE][0]['value']
                    except:
                        data_type = 'all'
                data['browsing_data_type'] = data_type

                # handle time duration
                try:
                    duration = entity['entities'][ChromeExtensionAI.DURATION][0]['value']
                    unit = entity['entities'][ChromeExtensionAI.DURATION][0]['unit']
                except:
                    try:
                        duration = wit_resp['entities'][ChromeExtensionAI.DURATION][0]['value']
                        unit = wit_resp['entities'][ChromeExtensionAI.DURATION][0]['unit']
                    except:
                        duration = 'all'
                        unit = 'None'
                data['duration'] = duration
                data['unit'] = unit
                self.actions.append(data)

        elif browsing_data_entities is not None:
            data = {'action': 'clear_browsing_data'}

            # handle browsing data type
            try:
                data_type = wit_resp['entities'][ChromeExtensionAI.BROWSING_DATA_TYPE][0]['value']
            except:
                data_type = 'all'
            data['browsing_data_type'] = data_type

            # handle time duration
            try:
                duration = wit_resp['entities'][ChromeExtensionAI.DURATION][0]['value']
                unit = wit_resp['entities'][ChromeExtensionAI.DURATION][0]['unit']
            except:
                duration = 'all'
                unit = 'None'

            data['duration'] = duration
            data['unit'] = unit
            self.actions.append(data)