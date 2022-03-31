import os
import pickle
import pyAesCrypt
from decouple import config
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

bufferSize = 64 * 1024
password = config('SERVICE_ACCOUNT_DECRYPT_KEY')
spreadsheet_id = config('SPREADSHEET_ID')

def decrypt_file(filename):
    with open(f"{filename}.aes", "rb") as encrypted_file:
        with open(filename, "wb") as decrypted_file:
            encFileSize = os.stat(f"{filename}.aes").st_size
            # decrypt file stream
            pyAesCrypt.decryptStream(
                encrypted_file,
                decrypted_file,
                password,
                bufferSize,
                encFileSize
            )

def encrypt_file(filename):
    with open(filename, "rb") as decrypted_file:
        with open(f"{filename}.aes", "wb") as encrypted_file:
            pyAesCrypt.encryptStream(decrypted_file, encrypted_file, password, bufferSize)


class EventsSheet:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    RANGE_NAME = 'Sheet1'
    value_input_option = 'USER_ENTERED'

    creds = None
    if os.path.exists('token.pickle.aes'):
        decrypt_file('token.pickle')
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        encrypt_file('token.pickle')
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    @classmethod
    def initialize_spreadsheet(cls):
        values = [
            ["Column 1", "Column 2", "Column 3"],
            ["."]
        ]
        body = {
            'values': values
        }
        result = cls.service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=cls.RANGE_NAME).execute()
        result = cls.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=cls.RANGE_NAME, valueInputOption=cls.value_input_option, body=body).execute()
