import json
import logging
import re
from os import getenv

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError


def download_page(url: str, path: str):
    """
    Download page as `html` file.
    """

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    }
    try:
        req = requests.get(url, headers=headers)
    except ConnectionError:
        logging.error('We have lose the connection!')
        return
    with open(path, "w", encoding="utf-8") as file:
        file.write(req.text)


def parse_html(html_patn: str, json_path: str):
    """
    Parse `html` file with `search_dict` to news and append data into `json`.

    Return only fresh news.
    """

    with open(html_patn, encoding="utf-8") as file:
        src = file.read()
    with open(json_path, "r", encoding="utf-8") as file:
        articles_list = json.load(file)
    soup = BeautifulSoup(src, "lxml")
    fresh_articles = {}

    search_dict = [
        re.compile('[В,в]одоканал'),
        re.compile('[М,м]етеопопередження'),
        re.compile('Прикарпаттяобленерго'),
        re.compile('Прикарпатенерготрейд'),
        re.compile('[О,о]бмежений'),
        re.compile('[У,у]складнення'),
        re.compile('[У,у]вага'),
        re.compile('[П,п]овідомляє'),
        re.compile('[О,о]бережно'),
        re.compile('[Н,н]ебезпе'),
        re.compile('[П,п]ризупинен'),
        re.compile('[А,а]варі'),
        re.compile('[В,в]имкнення'),
        re.compile('[В,в]од'),
        re.compile('[Г,г]аз'),
        re.compile('[Л,л]іфт'),
        re.compile('[Р,р]емонт'),
        re.compile('[П,п]еревір'),
        re.compile('[З,з]он')
        ]

    exclude_dict = [
        re.compile('[П,п]осад'),
        re.compile('[К,к]онкурс'),
        re.compile('[Б,б]лагодій'),
        re.compile('[З,з]асідання'),
        re.compile('[К,к]омісі'),
        re.compile('[П,п]роект'),
        re.compile('[П,п]питан')
    ]
    articles = soup.find_all(string=search_dict)

    for items in articles:
        article = items.find_parent("article")
        post_title = article.find("a").text
        post_link = article.find("a").get("href")
        article_id = post_link.split('/')[-2]
        timestamp = article.find(class_="entry-date").text

        # Pass not interested articles
        if not article.find(string=exclude_dict):
            if article_id not in articles_list:
                fresh_articles[article_id] = {
                    "Title": post_title,
                    "Post_link": post_link,
                    "Timestamp": timestamp
                }
                # Append fresh news to all
                articles_list.update(fresh_articles)
                with open(json_path, "w", encoding="utf-8") as news:
                    json.dump(
                        articles_list, news, indent=4, ensure_ascii=False
                        )
                print(post_title)
            elif timestamp != articles_list[article_id]["Timestamp"]:
                fresh_articles[article_id] = {
                    "Title": post_title,
                    "Post_link": post_link,
                    "Timestamp": timestamp
                }
                # Append fresh news to all
                articles_list.update(fresh_articles)
                with open(json_path, "w", encoding="utf-8") as news:
                    json.dump(
                        articles_list, news, indent=4, ensure_ascii=False
                        )
                print(post_title)
    return fresh_articles


def check_news_update():
    """
    Check for new articles in site https://www.ukr.net/news/main.html

    Download a news page. Find fresh news in downloaded `html` file.
    Write all news into `json` file. Return `dict` with only fresh.
    """

    url = getenv("NEWS_URL")
    html_patn = "data/index.html"
    json_path = "data/articles_dict.json"

    download_page(url, html_patn)
    return parse_html(html_patn, json_path)


if __name__ == '__main__':
    check_news_update()
