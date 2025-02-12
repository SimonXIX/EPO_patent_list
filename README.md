# Python script to query the European Patent Office's Open Patent Services (OPS) API

## configuration variables

Start by copying config_template.py to a file called config.py. Fill in the configuration variables using your own details. 

consumer_key and consumer_secret can be obtained following EPO OPS' API documentation at https://www.epo.org/en/searching-for-patents/data/web-services/ops.

## running the script

The script has several functions which can be run by changing the parameter in the command:

`python3 epo_api.py [license|help|date_query]`

'license' prints the MIT License.

'help' prints a simple help file (saved here as help.md).

'date_query' runs the main date query. This retrieves a range of patent titles and abstracts from patents registered today (or close to today)