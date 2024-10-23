import json
import time


def wrapper_audit_service(main_file, trigger_word):

    # Чтение основного JSON файла
    with open(main_file, 'r', encoding='utf-8') as main_file:
        main_data = json.load(main_file)

    main_data['message']['timestamp'] = int(time.time() * 1000)

    # Чтение JSON файла с изменениями
    with open("testdata/audit/changes_for_test.json", 'r') as changes_file:
        changes_data = json.load(changes_file)


    # Проверяем, есть ли в данных изменения для переданного триггерного слова
    if trigger_word in changes_data:
        changes = changes_data[trigger_word]  # Изменения для конкретного триггера

        # Применение изменений к основному JSON
        for key, value in changes.items():
            # Проверяем, если поле есть в основном JSON, то изменяем его
            if key in main_data['message']:
                main_data['message'][key] = value
            else:
                print(f"Поле '{key}' не найдено в основном JSON.")
    else:
        print(f"Изменений для триггерного слова '{trigger_word}' не найдено.")

    return main_data


def wrapper_nlu_proxy_service(main_file, trigger_word):

    # Чтение основного JSON файла
    with open(main_file, 'r', encoding='utf-8') as main_file:
        main_data = json.load(main_file)

    # Чтение JSON файла с изменениями
    with open("testdata/nlu_proxy/changes_for_test.json", 'r') as changes_file:
        changes_data = json.load(changes_file)


    # Проверяем, есть ли в данных изменения для переданного триггерного слова
    if trigger_word in changes_data:
        changes = changes_data[trigger_word]  # Изменения для конкретного триггера

        # Применение изменений к основному JSON
        for key, value in changes.items():
            # Проверяем, если поле есть в основном JSON, то изменяем его
            if key in main_data['message']:
                main_data['message'][key] = value
            else:
                print(f"Поле '{key}' не найдено в основном JSON.")
    else:
        print(f"Изменений для триггерного слова '{trigger_word}' не найдено.")

    return main_data
