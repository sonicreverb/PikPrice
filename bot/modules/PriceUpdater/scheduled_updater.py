from bot.modules.GoogleSheets.tables import upload_sotohit_prices, upload_gsm_prices, upload_store77_prices
import schedule
import time
import datetime


def upload_all_prices():
    upload_store77_prices()
    upload_sotohit_prices()
    upload_gsm_prices()

    print(f"Цены успешно обновлены: {datetime.datetime.now()}")


def run_scheduled_update():

    # Расписание для 9, 11, 14, 17 и 20 часов по Московскому времени
    schedule.every().day.at("09:00").do(upload_all_prices)
    schedule.every().day.at("11:00").do(upload_all_prices)
    schedule.every().day.at("14:00").do(upload_all_prices)
    schedule.every().day.at("17:00").do(upload_all_prices)
    schedule.every().day.at("20:00").do(upload_all_prices)

    while True:
        # Обновляем расписание и выполняем задачу, если время совпадает
        schedule.run_pending()
        time.sleep(1)
