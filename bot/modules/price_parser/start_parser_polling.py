import datetime
import time

from bot.modules.tables.form_table import upload_sotohit_prices, upload_gsm_prices, upload_store77_prices

while True:
    try:
        upload_sotohit_prices()
        upload_store77_prices()
        upload_gsm_prices()

        print(f"Цены успешно обновлены: {datetime.datetime.now()}")
    except Exception as exc:
        print(exc, datetime.datetime.now())
    time.sleep(60 * 60 * 24)
