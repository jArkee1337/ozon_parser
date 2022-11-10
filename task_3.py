import time
from collections import Counter
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from datetime import datetime

URL = 'https://www.ozon.ru/category/smartfony-15502/?sorting=rating'


def get_chrome_driver():
    service = ChromeService(executable_path=ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0')
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def get_html_from_start_page(url):
    driver = get_chrome_driver()
    driver.get(url)
    print('Start getting html of pages')
    time.sleep(3)
    list_of_htmls = []
    for _ in range(3):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(3)
        result = driver.page_source
        list_of_htmls.append(result)
        if len(list_of_htmls) == 3:
            break
        driver.quit()
        driver = next_page_link(result)
        print('link next page')
        time.sleep(3)
    driver.quit()
    print('list of html was created')
    return list_of_htmls


def next_page_link(html):
    soup = BeautifulSoup(html, 'lxml')
    url = 'https://ozon.ru' + soup.find('a', class_='_4-a1').get('href')
    driver = get_chrome_driver()
    driver.get(url)
    return driver


def get_all_links(html_list):
    links = []
    print('Start taking all links from html_list')
    for html in html_list:
        soup = BeautifulSoup(html, 'lxml')
        soup_divs = soup.find_all('div', class_='k4r')

        for div in soup_divs:
            link_part = div.find('a', class_='tile-hover-target').get('href')
            link = 'https://ozon.ru' + link_part
            links.append(link)
            if len(links) == 100:
                print('One hundred links were creaated')
                break
    print(f'The len of links list is: {len(links)}')
    return links


def get_html_from_phone_page(url):
    driver = get_chrome_driver()
    try:
        driver.get(url)
    except:
        print('Some exception')

    time.sleep(2)
    # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    try:
        smartphone_link = driver.find_element(By.CLASS_NAME, 'xl2')
        smartphone_name = driver.find_element(By.CLASS_NAME, 'vn0').text
        smartphone_link.click()
    except:
        print('Can not find description button')
        smartphone_name = 'Nonephone'

    time.sleep(3)
    result = driver.page_source
    driver.quit()
    print(f'html from phone: {smartphone_name} was received')
    return result


def get_data_from_page(html):
    soup = BeautifulSoup(html, 'lxml')
    print('Start finding os_version')
    try:
        os_version = soup.find('dd', string=[re.compile("Android "), re.compile("iOS ")]).string.strip()
    except:
        os_version = 'Could not find OS version'

    print(f'OS version: {os_version}')

    return os_version


# def make_all_for_pool(url):
#     phone_html = get_html_from_phone_page(url)
#     os_version = get_data_from_page(phone_html)


def main():
    while True:
        start = datetime.now()
        base_html = get_html_from_start_page(URL)
        all_urls = get_all_links(base_html)
        if len(all_urls) < 100:
            print('I could not to scrape enough links :( I am trying again')
            continue
        # with Pool() as pool:
        #     pool.map(make_all_for_pool, all_urls)
        result_list = []
        counter = 1
        for url in all_urls:
            print(counter)
            phone_html = get_html_from_phone_page(url)
            os_version = get_data_from_page(phone_html)
            result_list.append(os_version)
            counter += 1
        end = datetime.now()
        working_time = end - start
        result = Counter(result_list)
        print(f'The script has worked: {working_time}')
        print(result)
        return result


if __name__ == '__main__':
    main()
