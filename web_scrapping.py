import requests
import re
from bs4 import BeautifulSoup


def get_titles(soup_element):
    title_list = []
    titles = soup_element.find_all(class_='tm-article-snippet__title-link')
    name = titles[0].text.strip()
    title_list.append(name)
    return title_list


def get_hubs(soup_element):
    hubs_list = []
    hubs = soup_element.find_all(class_='tm-article-snippet__hubs-item')
    for hub in hubs:
        section = hub.text.strip()
        hubs_list.append(section)
    return hubs_list


def get_hub_text(soup_element):
    text_list = []
    hub_text = soup_element.find_all(class_=['article-formatted-body article-formatted-body_version-2',
                                             'article-formatted-body article-formatted-body_version-1'])
    for paragraph in hub_text:
        text = paragraph.text.strip()
        text_list.append(text)
    return text_list


def get_link(soup_element):
    title = soup_element.find_all(class_='tm-article-snippet__title-link')
    href = title[0].get('href')
    full_link = 'https://habr.com' + href
    return full_link


def info_from_opened_link(link):
    """Opening link from get_link() for getting parsed text on the page"""

    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'}
    ret = requests.get(link, headers=HEADERS)
    ret.raise_for_status()
    page = ret.text
    new_soup = BeautifulSoup(page, 'html.parser')
    page = new_soup.find_all(class_='tm-article-presenter__content tm-article-presenter__content_narrow')
    text = page[0].text
    return text


def get_publish_time(soup_element):
    pattern = r'(\d{4})[ -]?(\d{2})[ -]?(\d{2})[A-Za-z]?(\d{2})[:]?(\d{2})[:](\d{2})[.](\w+)'
    sub = r'\1-\2-\3 \4:\5:\6'
    publish_class = soup_element.find_all(class_='tm-article-snippet__datetime-published')
    time = publish_class[0].find('time').get('datetime')
    objective = re.sub(pattern, sub, time)
    return objective


def find_overlap(soup_element, init_list, titles, hubs, text):
    """Getting pages with keywords that we wanted. Parsing post preview and full text from opened page"""

    overlap_list = []
    for i in init_list:
        link = get_link(soup_element)
        time = get_publish_time(soup_element)
        title = get_titles(soup_element)[0]
        text_from_link = info_from_opened_link(link)
        if any([i.lower() in desired.lower() for desired in titles]) and (link not in overlap_list):
            overlap_list.append(link)
            print(time, title, link, sep=' --- ')
        elif any([i.lower() in desired.lower() for desired in hubs]) and (link not in overlap_list):
            overlap_list.append(link)
            print(time, title, link, sep=' --- ')
        elif any([i.lower() in desired.lower() for desired in text]) and (link not in overlap_list):
            overlap_list.append(link)
            print(time, title, link, sep=' --- ')
        elif any([i.lower() in desired.lower() for desired in [text_from_link]]) and (link not in overlap_list):
            overlap_list.append(link)
            print(time, title, link, sep=' --- ')


def get_soup_articles():
    """Making soup"""

    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'}
    url = 'https://habr.com/ru/'
    ret = requests.get(url, headers=HEADERS)
    ret.raise_for_status()
    page = ret.text
    soup = BeautifulSoup(page, 'html.parser')
    articles = soup.find_all('article')
    return articles


if __name__ == '__main__':
    KEYWORDS = ['дизайн', 'web', 'python', 'Лейбниц', 'Искусственный интеллект', 'redux']
    soup = get_soup_articles()
    for article in soup:
        titles = get_titles(article)
        hubs = get_hubs(article)
        text = get_hub_text(article)
        find_overlap(article, KEYWORDS, titles, hubs, text)

