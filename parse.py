import telebot
import requests
import feedparser
import psycopg2

token = "1341285703:AAEYOAX5dFKK2Wfep5dJLgFzVri7E_oK4oQ"
bot = telebot.TeleBot(token)

con = psycopg2.connect(
    database="bot_parser",
    user="postgres",
    password="12345",
    host="127.0.0.1",
    port="5432"
)


@bot.message_handler(commands=['start'])
def hello(message):
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = '%s'" % message.chat.username)
    tmp = cur.fetchall()
    if len(tmp) == 0:
        con.rollback()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (fname, lname, username) VALUES ('{}', '{}', '{}')".format(message.chat.first_name,
                                                                                          message.chat.last_name,
                                                                                          message.chat.username))
        con.commit()

    rows = cur.fetchall()
    bot.send_message(message.chat.id, "Hello " + message.chat.username)
    con.close()


@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, "Bot was stopped. You can activate him by command \'run\'")


@bot.message_handler(content_types=['text'])
# функция пересылки новостей, которые юзер еще не получал
def parse(message):
    cur = con.cursor()
    cur.execute("select fname, title, users.id from(select * from posts) as post left join users on users.id = user_id where users.username = '{}'".format(message.chat.username))
    posts = cur.fetchall()
    cur.execute("SELECT id FROM users where username = '{}'".format(message.chat.username))
    tmp = cur.fetchone()
    user_id = tmp[0]
    rss = message.text + "rss/all/all"
    query = []
    feed = feedparser.parse(rss)
    for article in feed['entries']:
        count = 0
        for post in posts:
            if article.title == post[1]:
                count += 1
        if count == 0:
            query.append({article.title + ": " + article.link})
            cur.execute(
                "INSERT INTO posts(title, urls, user_id) VALUES('{}', '{}', {})".format(article.title, article.link, user_id))
            con.commit()
    for i in query:
        bot.send_message(message.chat.id, i)


bot.polling()
