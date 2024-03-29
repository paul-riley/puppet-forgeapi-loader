#!/usr/bin/env python3

###############################
# node Group controller
###############################

import sys, os, json, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from types import SimpleNamespace
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

class Forgecontroller:

    def __init__(self):
        self.headers = {}
        self.module_list = ["forge 'https://forge.puppet.com'"]
        self.__connection = None
        self.__token = None


    #returns dictionary {}
    def set_connection(self, connection = None, token = None):

        if connection is None:
            self.__connection = 'https://forgeapi-cdn.puppet.com'
        if token is None:
            try:
                current_dir = os.getcwd()
                #os.chdir('/Users/paulriley/projects/puppet-forgeapi-loader/forgeapikey')
                fh = open(os.path.abspath('forgeapikey/token'))
                token = fh.readline().strip()
            except IOError:
                token = 'Error Reading Token!'
                print('Error Reading Token')
            else:
                fh.close()
                os.chdir(current_dir)
            self.__token = token

        self.headers = {'Accept': '*/*',
                        'Accept-Encoding': 'gzip,deflate,br',
                        'Connection': 'keep-alive',
                        'Authorization': 'Bearer ' + self.__token,
                        'Content-Type': 'application/json' }

        return {
          'connection': self.__connection,
          'token': self.__token
        }


    #loads data in to node_obj_list
    def get_modules(self, number) :
        uri = '/v3/modules?hide_deprecated=true&limit=100'
        #print('connection: ' + self.__connection + uri)
        #print('token:' + self.__token )
        resp = requests.get(self.__connection + uri, verify=False, headers=self.headers)

        paginate_list = []

        if resp.status_code == 200 :
            # This worked the first time. Let's paginate and get data.

            #build the list of pages to get based on the modules we want.
            pages = int(number/100) + (number % 100 > 0)
            for i in list(range(pages)) :
                offset = i*100
                if offset > 0 :
                    #ignore the first offset. We already have that data.
                    paginate_list.append('/v3/modules?hide_deprecated=true&limit=100&offset=' + str(offset))


                # This turns the json automatically into a model without having to do that heavy lifting :)
                # Apparently... the .json method creates lists that "look" like json
                # This does not encode the json into strings correctly. Which is crap.
                # because the method is called .json() why not call it .to_dictionary()?
                # if you need to turn it in parseable json: json.loads(data.json()) :(
            first_ref = json.loads(json.dumps(resp.json()),object_hook=lambda d: SimpleNamespace(**d))

            #first time through. let's save some rest calls
            for single_mod in first_ref.results :
                self.module_list.append("mod '" + single_mod.slug + "',    '" + single_mod.current_release.version + "'")

            for next_uri in paginate_list:
                next_resp = requests.get(self.__connection + next_uri, verify=False, headers=self.headers)
                if next_resp.status_code == 200 :
                    next_ref = json.loads(json.dumps(next_resp.json()),object_hook=lambda d: SimpleNamespace(**d))
                    for single_mod in next_ref.results :
                        self.module_list.append("mod '" + single_mod.slug + "',    '" + single_mod.current_release.version + "'")

        return self.module_list

    #I should code a view, but I just want to get this done.
    def write_puppetfile(self):
        try:
            fh = open(os.path.abspath('Puppetfile'), "w")
            for item in self.module_list:
                fh.write(item + "\n")
        except IOError:
            print('Unable to Write to Puppetfile')
        else:
            fh.close()
