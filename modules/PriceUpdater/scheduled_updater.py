from modules.TelegramAlerts import send_notification
import modules.PriceUpdater.prices_parser as prices_parser
import schedule
import time
import datetime


# запускает парсинг цен с сайтов конкурентов и их загрузку в таблицу
def upload_all_prices():
    for site_type in prices_parser.sites_typeData:
        flagSuccesUpdate = True
        try:
            prices_parser.update_prices(site_type)
        except Exception as _ex:
            print([f'[UPLOAD ALL PRICES {site_type.upper()}] Ошибка! ({_ex})'])
            send_notification(f"[PIKPRICE {site_type.upper()}] Ошибка во время обновления товаров! ({_ex}).")
            flagSuccesUpdate = False
        finally:
            if flagSuccesUpdate:
                send_notification(f"[PIKPRICE {site_type.upper()}] Цены успешно обновлены ({datetime.datetime.now()}).")


# запускает процесс обновления цен с сайтов конкурентов по расписанию
def run_scheduled_update():
    # расписание для 9, 11, 14, 17 и 20 часов по Московскому времени
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
