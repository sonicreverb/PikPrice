from bot.modules.tables.form_table import upload_sotohit_prices, upload_gsm_prices, upload_store77_prices
import schedule
import time
import datetime
import pytz


def upload_all_prices():
    upload_store77_prices()
    upload_sotohit_prices()
    upload_gsm_prices()

    print(f"Цены успешно обновлены: {datetime.datetime.now()}")


def run_scheduled_task():
    # Создаем объект timezone для Московского времени
    moscow_tz = pytz.timezone('Europe/Moscow')

    # Расписание для 9, 11, 14, 17 и 20 часов по Московскому времени
    schedule.every().day.at("01:20").do(upload_all_prices)
    schedule.every().day.at("11:00").do(upload_all_prices)
    schedule.every().day.at("14:00").do(upload_all_prices)
    schedule.every().day.at("17:00").do(upload_all_prices)
    schedule.every().day.at("20:00").do(upload_all_prices)

    while True:
        # Получаем текущее время в Московском часовом поясе
        current_time = datetime.datetime.now(moscow_tz).strftime('%H:%M:%S')
        # Обновляем расписание и выполняем задачу, если время совпадает
        schedule.run_pending()
        time.sleep(1)


run_scheduled_task()

