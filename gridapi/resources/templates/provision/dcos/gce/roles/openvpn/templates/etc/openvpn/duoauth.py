#!/usr/bin/python2
#
import duo_client
import pam
import os
import sys

enable_duo = {{ enable_duo }}
duo_ikey = '{{ duo_ikey }}'
duo_skey = '{{ duo_skey }}'
duo_host = '{{ duo_host }}'

pam_authenticator = pam.pam()

remote_ip = os.environ.get('untrusted_ip')
remote_login = os.environ.get('username')
remote_password = os.environ.get('password')

local_login = remote_login
if enable_duo:
    duo_authenticator = duo_client.Auth(ikey=duo_ikey, skey=duo_skey, host=duo_host)
    try:
        local_password = remote_password.split(',')[0]
        duo_passcode = remote_password.split(',')[1]
    except:
        raise Exception('ivalid password format')
else:
    local_password = remote_password

if pam_authenticator.authenticate(local_login, local_password):
    print('local auth OK')
    if enable_duo:
        if duo_authenticator.auth('passcode', username=local_login, ipaddr=remote_ip, passcode=duo_passcode)['result'] != 'allow':
            print('duo auth FAILED')
            sys.exit(1)
        else:
            print('duo auth OK')
    print('auth OK')
    sys.exit(0)

print('auth FAILED')
sys.exit(1)
