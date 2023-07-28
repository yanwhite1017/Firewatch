import aiogram
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
token = config["TELEGRAM"]["token"]
