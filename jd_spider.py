import requests
from fake_useragent import UserAgent
from urllib.parse import quote
import logging
from pyquery import PyQuery as pq
import csv

FIRST_URL = 'https://search.jd.com/Search?keyword={keyword}&page={page}'
SECOND_URL = 'https://search.jd.com/s_new.php?keyword={keyword}&page={page}'

UA = UserAgent()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
TOTAL_PAGE = 10
KEYWORD = FILENAME = ''


def scrape_page(url, referer=None):
    logging.info('scraping %s', url)
    headers = {'User-Agent': UA.random, 'referer': referer}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        logging.error('get invalid status code %s while scraping %s', response.status_code, url)
    except Exception:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_first_half(page):
    first_url = FIRST_URL.format(keyword=KEYWORD, page=page * 2 - 1)
    return first_url, scrape_page(first_url)


def scrape_second_half(page, referer):
    second_url = SECOND_URL.format(keyword=KEYWORD, page=page * 2)
    return scrape_page(second_url, referer)


def parse_page(html):
    doc = pq(html)
    goods = doc('#J_goodsList li')
    data = []
    for item in goods.items():
        name = item('.p-name>a:first-child>em').text()
        name = name.replace('\n', '').replace(' ', '') if name else None
        price = item('.p-price i').text()
        shop_name = item('.hd-shopname').text()
        link = item('.p-img a').attr('href')
        link = 'https:' + link if link else None
        not (name and price and shop_name and link) or data.append((name, price, shop_name, link))
    return data


def save_data(data):
    with open(FILENAME, 'a') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def main():
    global KEYWORD, FILENAME
    input_keyword = input('请输入关键词：')
    KEYWORD = quote(input_keyword)
    FILENAME = f'{input_keyword}.csv'
    for page in range(1, TOTAL_PAGE + 1):
        first_url, first_html = scrape_first_half(page)
        if not first_html:
            continue
        first_data = parse_page(first_html)
        logging.info('saving page %s data', page)
        save_data(first_data)
        second_html = scrape_second_half(page, first_url)
        if not second_html:
            continue
        second_data = parse_page(second_html)
        logging.info('saving page %s data', page)
        save_data(second_data)


if __name__ == '__main__':
    main()
