===========
rbc-tools
===========

rbc-tools provides commandline tools for accessing `RedBridge Cloud <https://cloud.redbridge.se>`_.

After signing up, create a config file for rbc-tools in ~/.rbc/rbc.cfg.

A sample config file looks like:

[main]
apikey = <your api key as found in portal.redbridge.se>
secretkey = <your secret key as found in portal.redbridge.se>
endpoint = api.rbcloud.net
objekt_auth_url = https://objekt.rbcloud.net/v1.0

Make sure that the keys are written within quotation marks or any kind of
punctuation ie. XXXXX not "XXXXX".

Apikey and secretkey may be overridden by environment variables:
export RBC_APIKEY=XXXXX; export RBC_SECRETKEY=XXXX
rbc-instances deploy ...
