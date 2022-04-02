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
password = config("SERVICE_ACCOUNT_DECRYPT_KEY")
spreadsheet_id = config("SPREADSHEET_ID")


def decrypt_file(filename):
    with open(os.path.join(BASE_DIR, f"{filename}.aes"), "rb") as encrypted_file:
        with open(os.path.join(BASE_DIR, filename), "wb") as decrypted_file:
            encFileSize = os.stat(os.path.join(BASE_DIR, f"{filename}.aes")).st_size
            # decrypt file stream
            pyAesCrypt.decryptStream(
                encrypted_file, decrypted_file, password, bufferSize, encFileSize
            )


def encrypt_file(filename):
    with open(os.path.join(BASE_DIR, filename), "rb") as decrypted_file:
        with open(os.path.join(BASE_DIR, f"{filename}.aes"), "wb") as encrypted_file:
            pyAesCrypt.encryptStream(
                decrypted_file, encrypted_file, password, bufferSize
            )


class TeamsSheet:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    RANGE_NAME = None
    value_input_option = "USER_ENTERED"

    creds = None
    if os.path.exists(os.path.join(BASE_DIR, "token.pickle.aes")):
        decrypt_file("token.pickle")
        with open(os.path.join(BASE_DIR, "token.pickle"), "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(BASE_DIR, "client_secret.json"), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(os.path.join(BASE_DIR, "token.pickle"), "wb") as token:
            pickle.dump(creds, token)
        encrypt_file("token.pickle")

    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    @classmethod
    def get_team_row(cls, user):
        result = (
            cls.sheet.values()
            .get(spreadsheetId=spreadsheet_id, range=cls.RANGE_NAME)
            .execute()
        )
        rows = result.get("values", [])
        for i in range(len(rows)):
            if rows[i][0] == user.email:
                return i + 1
        return len(rows) + 1

    @classmethod
    def get_team_data(cls, team):
        row = [
            team.user.email,
            team.user.institution_name,
            team.captain_name,
            team.captain_phone,
        ]
        for player in team.players:
            row.append(player)
        return row

    @classmethod
    def get_sheet_id(cls):
        spreadsheet = (
            cls.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        )
        sheet_id = None
        for _sheet in spreadsheet["sheets"]:
            if _sheet["properties"]["title"] == cls.RANGE_NAME:
                sheet_id = _sheet["properties"]["sheetId"]
        return sheet_id

    @classmethod
    def create_sheet(cls, game):
        body = {
            "values": [["Email", "Institution Name", "Captain Name", "Captain Phone"]],
        }
        for i in range(game.max_players):
            body["values"][0].append(f"Player {i+1}")
        
        l=len(cls.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()["sheets"]) + 1
        spreadsheet_data = [
            {
                "addSheet": {
                    "properties": {
                        "title": cls.RANGE_NAME,
                    }
                }
            }
        ]
        result = (
            cls.service.spreadsheets()
            .batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": spreadsheet_data}
            )
            .execute()
        )
        result = (
            cls.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=cls.RANGE_NAME,
                valueInputOption=cls.value_input_option,
                body=body,
            )
            .execute()
        )

    @classmethod
    def initialize_spreadsheet(cls):
        for game in Game.objects.all().order_by('name', 'game_type'):
            values = []
            cls.RANGE_NAME = game.name + "_" + game.game_type
            if cls.get_sheet_id() is None:
                cls.create_sheet(game)
            for team in Team.objects.filter(game=game).order_by('id'):
                values.append(cls.get_team_data(team))
            body = {"values": values}
            result = (
                cls.service.spreadsheets()
                .values()
                .clear(
                    spreadsheetId=spreadsheet_id, range=cls.RANGE_NAME + "!A2:O10000"
                )
                .execute()
            )
            result = (
                cls.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=cls.RANGE_NAME,
                    valueInputOption=cls.value_input_option,
                    body=body,
                )
                .execute()
            )

    @classmethod
    def update_team(cls, team):
        cls.RANGE_NAME = team.game.name + "_" + team.game.game_type
        if cls.get_sheet_id() is None:
            cls.create_sheet(team.game)
        row = cls.get_team_row(team.user)
        values = [cls.get_team_data(team)]
        body = {"values": values}
        result = (
            cls.service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=cls.RANGE_NAME + f"!A{row}",
                valueInputOption=cls.value_input_option,
                body=body,
            )
            .execute()
        )

    @classmethod
    def new_team(cls, team):
        cls.RANGE_NAME = team.game.name + "_" + team.game.game_type
        if cls.get_sheet_id() is None:
            cls.create_sheet(team.game)
        values = [cls.get_team_data(team)]
        body = {"values": values}
        result = (
            cls.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=cls.RANGE_NAME,
                valueInputOption=cls.value_input_option,
                body=body,
            )
            .execute()
        )

    @classmethod
    def delete_team(cls, team):
        cls.RANGE_NAME = team.game.name + "_" + team.game.game_type
        if cls.get_sheet_id() is None:
                cls.create_sheet(team.game)
        row = cls.get_team_row(team.user)
        spreadsheet_data = [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": int(cls.get_sheet_id()),
                        "dimension": "ROWS",
                        "startIndex": int(row)-1,
                        "endIndex": int(row),
                    }
                }
            }
        ]
        result = (
            cls.service.spreadsheets()
            .batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": spreadsheet_data}
            )
            .execute()
        )
