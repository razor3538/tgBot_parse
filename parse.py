import telebot
import requests
import feedparser
import psycopg2

token = "1341285703:AAEYOAX5dFKK2Wfep5dJLgFzVri7E_oK4oQ"
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def hello(message):
    con = psycopg2.connect(
      database="bot_parser",
      user="postgres",
      password="12345",
      host="127.0.0.1",
      port="5432"
    )
    cur = con.cursor()
    try:
        temp = cur.execute("SELECT * FROM users WHERE username = '%s'" % message.chat.username)
        rows = cur.fetchall()
        bot.send_message(message.chat.id, "Hello " + message.chat.first_name)
        con.close()
    except psycopg2.errors.UndefinedColumn:
        con.rollback()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (fname, lname, username) VALUES ('{}', '{}', '{}')".format(message.chat.first_name, message.chat.last_name, message.chat.username)
        )
        con.commit()
        con.close()
@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, "Bot was stopped. You can activate him by command \'run\'")

@bot.message_handler(content_types=['text'])
def parse(message):
    rss = message.text + "rss/all/all"
    mass = []
    feed = feedparser.parse(rss)
    for article in feed['entries']:
        mass.append({article.title + ": " + article.link})

    bot.send_message(message.chat.id, mass[0])

bot.polling()
