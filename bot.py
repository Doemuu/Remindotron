import telegram
import login
import configparser
import logging
import mysql.connector


from functools import wraps
from datetime import datetime
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import ChatAction
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import InlineQueryHandler
from telegram.ext import ConversationHandler

# option 1 : import login file and read TOKEN var
# TOKEN = login.TOKEN

# option 2 : use configparser to read .ini files
config = configparser.ConfigParser()
config.read("telegram.ini")
TOKEN = config["Remindotron"]["TOKEN"]

bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)



def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

# /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="remindotron"
)

# request Tasks
@send_typing_action
def request(update, context):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT Beschreibung, Datum, Wer FROM task")

    myresult = mycursor.fetchall()
    tasks = list()

    for x in myresult:
        print(x)
        tasks.append(x)
    task = "I'm a bot, these are your tasks! \n{}".format("\n".join(["\n {} \n Datum: {} \n Wer: {}".format(x[0], x[1], x[2]) for x in tasks]))
    context.bot.send_message(chat_id=update.effective_chat.id, text=task)

request_handler = CommandHandler('request', request)
dispatcher.add_handler(request_handler)

# clear old Tasks
@send_typing_action
def clear(update, context):
    mycursor = mydb.cursor()
    r = mycursor.execute("DELETE FROM `task` WHERE Datum < CURRENT_DATE")
    mydb.commit()
    result = mycursor.rowcount, "record(s) deleted"
    context.bot.send_message(chat_id=update.effective_chat.id, text=result)

clarity_handler = CommandHandler('clear', clear)
dispatcher.add_handler(clarity_handler)

# clear old Tasks
@send_typing_action
def today(update, context):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT Beschreibung, Wer FROM `task` WHERE Datum = CURRENT_DATE")

    myresult = mycursor.fetchall()
    tasks = list()

    for x in myresult:
        print(x)
        tasks.append(x)
    result = "Du musst heute: \n{}".format("\n".join(["\n Task: {} \n Wer: {}".format(x[0], x[1]) for x in tasks]))

    context.bot.send_message(chat_id=update.effective_chat.id, text=result)

today_handler = CommandHandler('today', today)
dispatcher.add_handler(today_handler)

# clear old Tasks
@send_typing_action
def week(update, context):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT Beschreibung, Datum, Wer FROM `task` WHERE WEEK(Datum) = WEEK(CURRENT_DATE)")

    myresult = mycursor.fetchall()
    tasks = [(x[0], x[1].strftime('%d/%m/%Y'), x[2]) for x in myresult]
    for x in tasks: print(x)
    result = "Du musst in dieser Woche: \n{}".format("\n".join(["\n Task: {} \n Datum: {} \n Wer: {}".format(x[0], x[1], x[2]) for x in tasks]))

    context.bot.send_message(chat_id=update.effective_chat.id, text=result)

week_handler = CommandHandler('week', week)
dispatcher.add_handler(week_handler)

@send_typing_action
def create(update, context):
    mycursor = mydb.cursor()
    questionTask = "Was soll getan werden?"
    context.bot.send_message(chat_id=update.effective_chat.id, text=questionTask)
    return "TASK_NAME"

def task_name(update, context):
    task = update.message.text
    context.user_data["task_name"] = task
    questionTask = "Wann soll es getan werden? \n Im Format 'dd/mm/yyyy'"
    context.bot.send_message(chat_id=update.effective_chat.id, text=questionTask)
    return "TASK_DATE"

def task_date(update, context):
    task = update.message.text
    print(task)
    day,month,year = task.split("/")
    try:
        datetime(int(year),int(month), int(day))
        task = "{}-{}-{}".format(year,month,day)
    except ValueError:
        task = "Falsche Eingabe"
        context.bot.send_message(chat_id=update.effective_chat.id, text=task)
        return ConversationHandler.END
    context.user_data["task_date"] = task
    questionTask = "Wer tut es?"
    context.bot.send_message(chat_id=update.effective_chat.id, text=questionTask)
    return "TASK_PERSON"

def task_person(update, context):
    task = update.message.text
    context.user_data["task_person"] = task
    task_name = context.user_data["task_name"]
    task_date = context.user_data["task_date"]
    task_person = context.user_data["task_person"]
    # add to database
    mycursor = mydb.cursor()
    sql_insertion = """INSERT INTO task (Task_ID, Beschreibung, Datum, Wer) VALUES (NULL, %s, %s, %s);"""
    sql_prepared = (task_name, task_date, task_person)
    mycursor.execute(sql_insertion, sql_prepared)
    mydb.commit()
    print(task_name, task_date, task_person)
    # save task with mysql
    context.user_data.clear()
    return ConversationHandler.END

def cancel(update, context):
    # handle cancel action
    return ConversationHandler.END

# create_handler = CommandHandler('create', create)
# dispatcher.add_handler(create_handler)

conv_handler = ConversationHandler(
        entry_points=[CommandHandler('create', create)],
        states={
            "TASK_NAME": [MessageHandler(None, task_name)],
            "TASK_DATE": [MessageHandler(None, task_date)],
            "TASK_PERSON": [MessageHandler(None, task_person)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

dispatcher.add_handler(conv_handler)

# starting the bot
updater.start_polling()
