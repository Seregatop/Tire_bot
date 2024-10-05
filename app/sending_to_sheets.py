import pygsheets

gs = pygsheets.authorize(service_file=r"client_secret.json")

sheet = gs.open_by_key('1cElu0aCG2bi6ocoK3GCKVwRY_ze8S7d3M8XfJQPfF24')


async def write_row(*args):
    wks = sheet.worksheet_by_title('Import1')
    wks.append_table(values=args, dimension='ROWS', overwrite=False)







"""
import httplib2
import apiclient

from oauth2client.service_account import ServiceAccountCredentials
from config import SPREADSHEET_ID

CREDENTIALS_FILE = 'client_secret.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

range_ = 'Import!A:A'
value_input_option = 'RAW'
insert_data_option = 'INSERT_ROWS'

user_data = await state.get_data()
# дата
now = datetime.now()
new_years = datetime(day=30, month=12, year=1899)
countdown = now - new_years
value_range_body = {
    "range": "Import!A:A",
    "majorDimension": "ROWS",
    "values":
        [[int(countdown.days), int(countdown.days), str(call.message.date.time()), str(call.message.chat.full_name),
          call.message.from_user, call.message.chat.username, user_data["chosen_radius"],
          str(user_data["chosen_usluga"]), user_data["chosen_dopusluga"],
          "", user_data["chosen_oplata"], int(user_data["chosen_skidka"]), int(user_data["chosen_czena"])]]

}
await call.answer(text="Отправлено")
await call.message.edit_reply_markup(reply_markup=keybord_inline_new)
request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                 valueInputOption=value_input_option,
                                                 insertDataOption=insert_data_option, body=value_range_body)
response = request.execute()
"""