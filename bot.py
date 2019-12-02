import telegram
import login
import configparser

# option 1 : import login file and read TOKEN var
TOKEN = login.TOKEN

# option 2 : use configparser to read .ini files
config = configparser.ConfigParser()
config.read("telegram.ini")
TOKEN = config["Remindotron"]["TOKEN"]
