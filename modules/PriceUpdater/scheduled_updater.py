from modules.GoogleSheets.tables import upload_sotohit_prices, upload_gsm_prices, upload_store77_prices
from modules.TelegramAlerts.notifier import send_notification
import schedule
import time
import datetime


# запускает парсинг цен с сайтов конкурентов и их загрузку в таблицу
def upload_all_prices():
    upload_store77_prices()
    upload_sotohit_prices()
    upload_gsm_prices()

    send_notification(f"[PIKPRICE] Цены успешно обновлены ({datetime.datetime.now()}).")


# запускает процесс обновления цен с сайтов конкурентов по расписанию
def run_scheduled_update():

    # Расписание для 9, 11, 14, 17 и 20 часов по Московскому времени
    schedule.every().day.at("09:00").do(upload_all_prices)
    schedule.every().day.at("11:00").do(upload_all_prices)
    schedule.every().day.at("14:00").do(upload_all_prices)
    schedule.every().day.at("17:00").do(upload_all_prices)
    schedule.every().day.at("20:00").do(upload_all_prices)

    while True:
        # обновляем расписание и выполняем задачу, если время совпадает
        try:
            schedule.run_pending()
            time.sleep(30)
        except Exception as _exception:
            send_notification(f"[PIKPRICE] При попытке обновления цен возникла ошибка ({datetime.datetime.now()}).\n"
                              f"{_exception}")
