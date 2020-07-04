import requests
import feedparser

def read_article_feed(feed):
    mass = []
    feed = feedparser.parse(feed)
    for article in feed['entries']:
        mass.append({article.title: article.link})
    print(mass[1])
read_article_feed("https://habr.com/ru/rss/all/all/?fl=ru")