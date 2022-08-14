from time import sleep
import json
import re

import requests
from bs4 import BeautifulSoup as bs, Tag

BASE_URL: str = 'https://www.rts-tender.ru/'
URL: str = f'{BASE_URL}poisk?page='
NUMBER_OF_PAGES: int = 3

DATA_SELECTOR: str = 'div.card-item'
TITLE_SELECTOR: str = 'div.card-item__title'
NAME_CUSTOMER_SELECTOR: str = 'div.card-item__organization-main:first-child span.text--bold'
INN_KPP_SELECTOR: str = 'div.card-item__organization-main:nth-child(2)'

NUMBER_TEXT: str = 'Закупка №'

HEADERS: dict[str, str] = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/104.0.0.0 Safari/537.36',
}


def get_html(url: str, num_of_pages: int = 1, headers: dict | None = None, sleep_sec: int | None = None) -> list:
    """
    Returns a list of lines with html, each line is one page
    """
    responses: list[str] = []

    for number_page in range(1, num_of_pages + 1):
        response = requests.get(url=f'{url}{number_page}', headers=headers)
        responses.append(response.text)
        if sleep:
            sleep(sleep_sec)

    return responses


def get_text_of_tag(tag: Tag) -> str | None:
    if text := tag.getText():
        return text.strip()


def get_number_of_tag(tag: Tag, length: int = None) -> int | None:
    text = get_text_of_tag(tag)
    if text:
        pattern = r'\b\d{n}\b'.replace('n', str(length), 1) if length else r'\d+'
        return int(resp.group(0)) if (resp := re.search(pattern, text)) else None


def get_data(tags_with_data: list[Tag]) -> list[dict]:
    data: list[dict] = []

    for tag in tags_with_data:
        title = get_text_of_tag(tag.select(TITLE_SELECTOR)[0])
        name_customer = get_text_of_tag(tag.select(NAME_CUSTOMER_SELECTOR)[0])

        inn_and_kpp_tag: Tag = tag.select(INN_KPP_SELECTOR)[0]
        inn: int = get_number_of_tag(inn_and_kpp_tag, 10)
        kpp: int = get_number_of_tag(inn_and_kpp_tag, 9)

        number_tag_a = tag.find(lambda tag: tag.string and re.search(NUMBER_TEXT, tag.string.text))
        number = get_number_of_tag(number_tag_a)
        href = number_tag_a['href']

        data.append(
            {'название': title,
             'наименование заказчика': name_customer,
             'ИНН': inn,
             'КПП': kpp,
             'номер': number,
             'ссылка': href, }
        )

    return data


def write_as_json(data: list | dict, name_file: str = 'result') -> None:
    with open(f'{name_file}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    try:
        htmls: list = get_html(url=URL, num_of_pages=3, headers=HEADERS, sleep_sec=1)
    except requests.ConnectionError:
        print('Соединение с сервером не удалось, попробуйте позже.')
    except requests.Timeout:
        print('Время ожидания ответа от сервера вышло, попробуйте еще.')
    else:
        html_response: str = ''.join(htmls)
        dom = bs(html_response, 'html.parser')
        tags_with_data: list[Tag] = dom.select(DATA_SELECTOR)
        data_for_write = get_data(tags_with_data=tags_with_data)
        write_as_json(data_for_write)


if __name__ == '__main__':
    main()
