import os
import pickle
import pyAesCrypt
from decouple import config
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from Authentication.models import UserAccount
from Teams.models import Team, Game, Contingent
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

bufferSize = 64 * 1024
password = config('SERVICE_ACCOUNT_DECRYPT_KEY')
spreadsheet_id = config('SPREADSHEET_ID')

def decrypt_file(filename):
    with open(os.path.join(BASE_DIR, f"{filename}.aes"), "rb") as encrypted_file:
        with open(os.path.join(BASE_DIR, filename), "wb") as decrypted_file:
            encFileSize = os.stat(os.path.join(BASE_DIR, f"{filename}.aes")).st_size
            # decrypt file stream
            pyAesCrypt.decryptStream(
                encrypted_file,
                decrypted_file,
                password,
                bufferSize,
                encFileSize
            )

def encrypt_file(filename):
    with open(os.path.join(BASE_DIR, filename), "rb") as decrypted_file:
        with open(os.path.join(BASE_DIR, f"{filename}.aes"), "wb") as encrypted_file:
            pyAesCrypt.encryptStream(decrypted_file, encrypted_file, password, bufferSize)


class UsersSheet:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    RANGE_NAME = 'Registration'
    value_input_option = 'USER_ENTERED'

    creds = None
    if os.path.exists(os.path.join(BASE_DIR, 'token.pickle.aes')):
        decrypt_file('token.pickle')
        with open(os.path.join(BASE_DIR, 'token.pickle'), 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(BASE_DIR, 'client_secret.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(os.path.join(BASE_DIR, 'token.pickle'), 'wb') as token:
            pickle.dump(creds, token)
        encrypt_file('token.pickle')
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    @classmethod
    def get_user_row(cls, user):
        result = cls.sheet.values().get(spreadsheetId=spreadsheet_id, range=cls.RANGE_NAME).execute()
        rows = result.get('values', [])
        for i in  range(len(rows)):
            if rows[i][1] == user.email:
                return i+1
        return len(rows)+1

    @classmethod
    def get_user_data(cls,user):
        row=[user.username, user.email, user.name, user.institution_name, user.designation, user.phone_no]
        try:
            conti=Contingent.objects.get(college_rep=user)
            row.append(conti.leader_name)
            row.append(conti.leader_contact_num)
            row.append(conti.num_of_boys)
            row.append(conti.num_of_girls)
            row.append(conti.num_of_officials)
        except:
            for i in range(5): row.append("")
        row.append("Yes" if user.is_active else "No")
        row.append("Yes" if user.is_deleted else "No")
        row.append("Yes" if user.is_admin else "No")
        row.append("Yes" if user.is_staff else "No")
        return row

    @classmethod
    def initialize_spreadsheet(cls):
        values = []
        for user in UserAccount.objects.all().order_by('id'):
            values.append(cls.get_user_data(user))

        body = {
            'values': values
        }
        result = cls.service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=cls.RANGE_NAME+"!A2:O10000").execute()
        result = cls.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=cls.RANGE_NAME, valueInputOption=cls.value_input_option, body=body).execute()

    @classmethod
    def update_user(cls, email):
        user=UserAccount.objects.get(email=email)
        row = cls.get_user_row(user)
        values = [cls.get_user_data(user)]
        body = {
            'values': values
        }
        result = cls.service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=cls.RANGE_NAME+f"!A{row}", valueInputOption=cls.value_input_option, body=body).execute()

    @classmethod
    def new_user(cls, user):
        values = [cls.get_user_data(user)]
        body = {
            'values': values
        }
        result = cls.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=cls.RANGE_NAME, valueInputOption=cls.value_input_option, body=body).execute()
