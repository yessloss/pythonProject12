import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.constants import ParseMode

TELEGRAM_BOT_TOKEN = "5990142121:AAE7DpkJWUapD1zgjJWgPuP-RAxI5RP5ZkE"


TELEGRAM_CHANNEL_ID = "@tesmanian_parser"

TESMANIAN_EMAIL = "andrey.loosev@gmail.com"
TESMANIAN_PASSWORD = "1234560"


def tesmanian_login():
    session = requests.Session()

    login_url = "https://www.tesmanian.com/login"
    login_data = {"email": TESMANIAN_EMAIL, "password": TESMANIAN_PASSWORD}
    session.post(login_url, data=login_data)

    return session


def scrape_tesmanian(session):
    url = "https://www.tesmanian.com/"
    response = session.get(url)

    if response.status_code == 401:
        session = tesmanian_login()
        response = session.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("div", class_="blog-post-card")

    results = []
    for article in articles:
        title = article.find("h2", class_="blog-post-card--title").text.strip()
        link = article.find("a")["href"]
        results.append({"title": title, "link": link})

    return results


def send_new_articles(bot, new_articles):
    for article in new_articles:
        message = f"<b>{article['title']}</b>\n{article['link']}"
        bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode=ParseMode.HTML)


def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    session = tesmanian_login()

    last_articles = scrape_tesmanian(session)

    while True:
        time.sleep(15)
        current_articles = scrape_tesmanian(session)

        new_articles = [article for article in current_articles if article not in last_articles]
        if new_articles:
            send_new_articles(bot, new_articles)
            last_articles = current_articles


if __name__ == "__main__":
    main()
