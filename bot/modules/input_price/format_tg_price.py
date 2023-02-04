import re


def format_inputprice(textinput):
    # разделяем сплошной текст на строки (каждая строка - один товар), заполняем им массив
    text_lines_li = textinput.split('\n')
    # если в строке будут эти эмодзи, значит эта строка содержит товар
    emojiflag_li = ['🇮🇳', '🇪🇺', '🇬🇧', '🇺🇸', '🇯🇵', '🇷🇺', '🇦🇪', '🇭🇰', '🇰🇿', '🇰🇷', '📺', '🎮', '🔌', '🔋', '🖱']
    name_spc_dict = {}

    for line in text_lines_li:
        for emoji_flag in emojiflag_li:
            if emoji_flag in line:
                try:
                    price = re.search('\d{4,6}', line)[0]
                    name = line.split()
                    name = ''.join(name)

                    # при помощи проверки находим, как в строке поставщик разделил название и цену, чтобы правильно её
                    # сформировать
                    if name[0:name.index('-')]:
                        name_spc = name[0:name.index('-')].upper()
                    elif name[0:name.index('.')]:
                        name_spc = name[0:name.index('.')].upper()
                    else:
                        continue

                    if name_spc in name_spc_dict:
                        if price < name_spc_dict[name_spc]:
                            name_spc_dict[name_spc] = price
                    else:
                        name_spc_dict[name_spc] = price

                except AttributeError:
                    print("AttributeError in try statement, format_tg_price.py line 15", line)
                except TypeError:
                    print("TypeError in try statement, format_tg_price.py line 15", line)

    return name_spc_dict
