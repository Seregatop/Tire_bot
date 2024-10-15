import pygsheets

from config import SPREADSHEET_ID

gs = pygsheets.authorize(service_file=r"client_secret.json")

sh = gs.open_by_key(SPREADSHEET_ID)


async def send_gs_car(*args):
    wks = sh.worksheet_by_title("Import1")
    wks.append_table(values=args, dimension="ROWS", overwrite=False)


async def send_gs_pay(*args):

    wks = sh.worksheet_by_title("Pay")
    wks.append_table(values=args, dimension="ROWS", overwrite=False)


async def get_day():
    wks = sh.worksheet_by_title("Svod")
    result = wks.get_value("L3")
    return result


async def get_season():
    wks = sh.worksheet_by_title("Svod")
    result = wks.get_value("O7")
    return result
