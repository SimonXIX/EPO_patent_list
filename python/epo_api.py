# @name: epo_api.py
# @creation_date: 2025-02-11
# @license: The MIT License <https://opensource.org/licenses/MIT>
# @author: Simon Bowie <simon.bowie.19@gmail.com>
# @purpose: Performs functions against the European Patent Office's Open Patent Services (OPS) API
# @acknowledgements:
# OPS documented at https://www.epo.org/searching-for-patents/data/web-services/ops.html
# OPS RESTful API specification at http://documents.epo.org/projects/babylon/eponet.nsf/0/F3ECDCC915C9BCD8C1258060003AA712/$File/ops_v3.2_documentation_-_version_1.3.18_en.pdf
# OPS API functions list at https://developers.epo.org/ops-v3-2/apis

import os
import sys
import requests
import base64
from config import *
from datetime import date

# SUBROUTINES

# function to fetch help text
def get_help():
    f = open('help.md', 'r')
    help_text = f.read()
    print(help_text)

# function to fetch license text
def get_license():
    f = open('LICENSE', 'r')
    license_text = f.read()
    print(license_text)

def get_todays_date():
    today = date.today()
    today = today.strftime("%Y%m%d")
    return today

def get_access_token():

    # OPS API credentials (details at http://documents.epo.org/projects/babylon/eponet.nsf/0/F3ECDCC915C9BCD8C1258060003AA712/$File/ops_v3.2_documentation_-_version_1.3.18_en.pdf)
    endpoint_url = ops_url + '3.2/auth/accesstoken'
    auth = consumer_key + ":" + consumer_secret
    auth_bytes = auth.encode("ascii")
    base64_bytes = base64.b64encode(auth_bytes)
    base64_string = base64_bytes.decode("ascii")

    # set up API call
    headers = {"Authorization": "Basic " + base64_string, "Content-Type": "application/x-www-form-urlencoded"}
    data = "grant_type=client_credentials"

    # give back result
    response = requests.post(endpoint_url, headers=headers, data=data)

    if response.status_code == 200:
        # turn the API response into useful Json
        json = response.json()
        access_token = json['access_token']

    return access_token

def run_date_query():

    access_token = get_access_token()

    date = get_todays_date()

    # OPS API credentials (details at http://documents.epo.org/projects/babylon/eponet.nsf/0/F3ECDCC915C9BCD8C1258060003AA712/$File/ops_v3.2_documentation_-_version_1.3.16_en.pdf)
    endpoint_url = ops_url + 'rest-services/published-data/search/biblio?q=pd="' + date + '"&Range=1-' + range_limit

    # set up API call
    headers = {"Authorization": "Bearer " + access_token, "Accept": "application/json"}

    # get result
    response = requests.get(endpoint_url, headers=headers)

    output = []

    if response.status_code == 200:

        # turn the API response into useful Json
        json = response.json()

        for document in json['ops:world-patent-data']['ops:biblio-search']['ops:search-result']['exchange-documents']:

            patent = {}

            # for each invention title, check if it's in the original language
            try:
                document['exchange-document']['bibliographic-data']['invention-title']
                invention_titles = document['exchange-document']['bibliographic-data']['invention-title']
                try:
                    invention_titles[1]
                    for invention_title in invention_titles:
                        if invention_title['@lang'] is not None and invention_title['@lang'] == 'en':
                            patent['title'] = invention_title['$']
                        # if invention_title['@lang'] is not None and invention_title['@lang'] != 'en':
                        #     patent['original_title'] = invention_title['$']
                except KeyError:
                    if invention_titles['@lang'] is not None and invention_titles['@lang'] == 'en':
                            patent['title'] = invention_titles['$']
                    # if invention_title['@lang'] is not None and invention_title['@lang'] != 'en':
                    #     patent['original_title'] = invention_title['$']
            except KeyError:
                pass

            # for each abstract, check if it's in the original language
            try:
                document['exchange-document']['abstract']
                abstracts = document['exchange-document']['abstract']
                try:
                    abstracts[1]
                    for abstract in abstracts:
                        if abstract['@lang'] is not None and abstract['@lang'] == 'en':
                            patent['abstract'] = abstract['p']['$']
                        # if abstract['@lang'] is not None and abstract['@lang'] != 'en':
                        #     patent['original_abstract'] = abstract['p']['$']
                except KeyError:
                    if abstracts['@lang'] is not None and abstracts['@lang'] == 'en':
                            patent['abstract'] = abstracts['p']['$']
                    # if abstract['@lang'] is not None and abstract['@lang'] != 'en':
                    #     patent['original_abstract'] = abstract['p']['$']
            except KeyError:
                pass

            output.append(patent)

    print(output)

# MAIN PROGRAM

if len(sys.argv) == 1:
    get_help()
else:
    if sys.argv[1] == 'help':
        get_help()
    elif sys.argv[1] == 'license':
        get_license()
    elif sys.argv[1] == 'date_query':
        run_date_query()
    else:
        get_help()