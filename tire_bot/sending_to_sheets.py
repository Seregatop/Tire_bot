import pygsheets


# Добавляет новую строку с продажей в конец гугл таблиц со значениями из args
class SheetHandler:
    def __init__(self, service_file: str, spreadsheet_id: str):
        self.gs = pygsheets.authorize(service_file=service_file)
        self.sh = self.gs.open_by_key(spreadsheet_id)

    async def send_gs_car(self, *args):
        wks = self.sh.worksheet_by_title("Import1")
        wks.append_table(values=args, dimension="ROWS", overwrite=False)

    # Добавляет новую строку с расходом
    async def send_gs_pay(self, *args):
        wks = self.sh.worksheet_by_title("Pay")
        wks.append_table(values=args, dimension="ROWS", overwrite=False)

    # Возвращает оборот за день
    async def get_day(self) -> str:
        wks = self.sh.worksheet_by_title("Svod")
        result = wks.get_value("L3")
        return result

    # Возвращает оборот за все время
    async def get_season(self) -> str:
        wks = self.sh.worksheet_by_title("Svod")
        result = wks.get_value("O7")
        return result
