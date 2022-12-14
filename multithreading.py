import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains

URL = 'https://www.ozon.ru/category/smartfony-15502/?sorting=rating'
result_list = []


def get_chrome_driver():
    """Create instance of chrome driver
    """
    service = ChromeService(executable_path=ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; '
                         'rv:106.0) Gecko/20100101 Firefox/106.0')
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def get_html_from_start_page(url):
    """
    Takes html from required number of pages
    :param url: url of base page
    :return: list of html pages
    """
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
    """
    Make get request to next page and return driver instance
    :param html: html from base page
    :return: new driver instance
    """
    soup = BeautifulSoup(html, 'lxml')
    url = 'https://ozon.ru' + soup.find('a', class_='_4-a1').get('href')
    driver = get_chrome_driver()
    driver.get(url)
    return driver


def get_all_links(html_list):
    """
    Return all links that we will parse
    :param html_list: list of all html pages from which
           we will get the links
    :return: all links that we will parse
    """
    links = []
    print('Start taking all links from html_list')
    for html in html_list:
        soup = BeautifulSoup(html, 'lxml')
        soup_divs = soup.find_all('div', class_='kr7')

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
    """
    Takes html code from separate page
    :param url: url of separate phone
    :return: html code of separate page
    """
    print('start getting html from phone page')
    driver = get_chrome_driver()
    try:
        driver.get(url)
    except Exception:
        print('Some exception')
    time.sleep(2)
    try:
        smartphone_description_link = driver.find_element(By.CLASS_NAME, 'l5x')
        action = ActionChains(driver)
        action.move_to_element(smartphone_description_link)
        time.sleep(1)
        smartphone_description_link.click()
        time.sleep(3)
        smartphone_name = driver.find_element(By.CLASS_NAME, 'n3v').text
    except Exception:
        print('Can not find description button')
        smartphone_name = 'Nonephone'
        time.sleep(5)
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(3)
    result = driver.page_source
    driver.quit()
    print(f'html from phone: {smartphone_name} was received')
    return result


def get_data_from_page(html):
    """
    Takes OS version from page of separate phone
    :param html: html code of separate phone page
    :return: OS version of phone
    """
    soup = BeautifulSoup(html, 'lxml')
    print('Start finding os_version')
    try:
        os_version = soup.find('dd', string=[re.compile("Android "),
                                             re.compile("iOS ")]).string.strip()
    except Exception:
        os_version = 'Could not find OS version'
    print(f'OS version: {os_version}')
    return os_version


def run_process(url, result_list_for_run):
    """
    Auxiliary function for correct calling of ThreadPoolExecutor
    :param url: single phone's link
    :param result_list_for_run: list, where all OS version will be kept
    :return: None
    """
    phone_html = get_html_from_phone_page(url)
    os_version = get_data_from_page(phone_html)
    result_list_for_run.append(os_version)


def main(result_list_main):
    """ Main function
    """
    while True:
        start = datetime.now()
        base_html = get_html_from_start_page(URL)
        all_urls = get_all_links(base_html)
        if len(all_urls) < 100:
            print('I could not to scrape enough links :( I am trying again')
            continue
        futures = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            for url in all_urls:
                futures.append(
                    executor.submit(run_process, url, result_list)
                )
        wait(futures)
        end = datetime.now()
        working_time = end - start
        result = Counter(result_list_main)
        print(f'The script has worked: {working_time}')
        print(result)
        return result


if __name__ == '__main__':
    main(result_list)
