# vi: ft=python
'''grab_xmltv: Grabs XMLTV data, and places it in S3'''

from __future__ import print_function

import base64
import tempfile

import boto3
import requests

# These could be cmd args, or from a config file or something...
# ... if it were to be more generic.
CHUNK_SIZE = 10240
XMLTV_FILE = 'xmltv/tvguide.xml'

# Crypto'd with KMS
S3_BUCKET = '''
CiDsnjoHljskbVBug+gWXfjPQPqIYmhm1P/n+kaFSUrEWRKOAQEBAgB47J46B5Y7JG1QboPoFl34
z0D6iGJoZtT/5/pGhUlKxFkAAABlMGMGCSqGSIb3DQEHBqBWMFQCAQAwTwYJKoZIhvcNAQcBMB4G
CWCGSAFlAwQBLjARBAwMRubCIUEPDVn7jlQCARCAIp4SPd04s39R+kqC7hJp/rY6AWxYx15EGu+m
9kUobPhi0Qs=
'''

XMLTV_URL = '''
CiDsnjoHljskbVBug+gWXfjPQPqIYmhm1P/n+kaFSUrEWRLMAQEBAgB47J46B5Y7JG1QboPoFl34
z0D6iGJoZtT/5/pGhUlKxFkAAACjMIGgBgkqhkiG9w0BBwaggZIwgY8CAQAwgYkGCSqGSIb3DQEH
ATAeBglghkgBZQMEAS4wEQQMX4zDCH/Ly933v50kAgEQgFyRDXncpxaeooDQxu764801h4Xi7O+F
C2vv2p1cnkcXJrj2pI6x10cGybEKgqEStMKcg/c9MGAaVTPGXyjTaKC1bAZQfvP68U7VmLhCb7Zb
tlKIEJ0rlI8FyOgJuw==
'''

XMLTV_USER = '''
CiDsnjoHljskbVBug+gWXfjPQPqIYmhm1P/n+kaFSUrEWRKOAQEBAgB47J46B5Y7JG1QboPoFl34
z0D6iGJoZtT/5/pGhUlKxFkAAABlMGMGCSqGSIb3DQEHBqBWMFQCAQAwTwYJKoZIhvcNAQcBMB4G
CWCGSAFlAwQBLjARBAwFrmiNpSu98ndidj4CARCAIpZokFi2+nr9AdXp43ZHh1VoQcx2ap76VvHV
9Kc4Ts2NgyE=
'''
XMLTV_PASS = '''
CiDsnjoHljskbVBug+gWXfjPQPqIYmhm1P/n+kaFSUrEWRKTAQEBAgB47J46B5Y7JG1QboPoFl34
z0D6iGJoZtT/5/pGhUlKxFkAAABqMGgGCSqGSIb3DQEHBqBbMFkCAQAwVAYJKoZIhvcNAQcBMB4G
CWCGSAFlAwQBLjARBAxj6fTJGAOp9/dtIlUCARCAJx4HHlOv3GOmUGjX2ePZ9IkMfXAzBhipPHRE
l2niDucNJYxWAqyh7A==
'''

class GrabXMLTV(object): # pylint: disable=too-few-public-methods
    '''Main Class'''

    @classmethod
    def grab(cls):
        '''Main Method'''
        kms = boto3.client('kms')
        bucket = kms.decrypt(CiphertextBlob=base64.b64decode(S3_BUCKET))['Plaintext']
        username = kms.decrypt(CiphertextBlob=base64.b64decode(XMLTV_USER))['Plaintext']
        password = kms.decrypt(CiphertextBlob=base64.b64decode(XMLTV_PASS))['Plaintext']
        url = kms.decrypt(CiphertextBlob=base64.b64decode(XMLTV_URL))['Plaintext']
        print("DEBUG: Decrypted secrets")

        with tempfile.NamedTemporaryFile() as xmltv:
            response = requests.get(
                url,
                stream=True,
                auth=requests.auth.HTTPBasicAuth(username, password),
            )

            if not response.ok:
                raise RuntimeError("Response not ok: %s" % response.status_code)

            print("DEBUG: Starting http download")
            for chunk in response.iter_content(CHUNK_SIZE):
                xmltv.write(chunk)
            print("DEBUG: Finished http download (bytes: %d)" % xmltv.tell())

            print("DEBUG: Starting s3 upload")
            s3 = boto3.client('s3')
            s3.upload_file(xmltv.name, bucket, XMLTV_FILE)
            print("DEBUG: Finished s3 upload")


def run(json_input=None, context=None): # pylint: disable=unused-argument
    '''Main entry pointi (AWS Lambda compatible)'''
    grabber = GrabXMLTV()
    grabber.grab()


if __name__ == "__main__":
    run()
