============
Usage
============

Example
----------------------

::

    '''Get rop.io Delegation Signer'''

    from rrda import RRDAAPI

    API = RRDAAPI('http://api.statdns.com/rop.io') # api url + domain
    RESPONSE = API.DS.get()
    ANSWER = RESPONSE.data['answer'][0]['rdata']

    print ANSWER

