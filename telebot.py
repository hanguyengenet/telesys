import configparser
import os 
import re
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import subprocess

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'setting.ini'))
TOKEN = config['telegram']['TOKEN']
list_normal = config['telegram']['chat_id_normal'].split(',')
list_spec = config['telegram']['chat_id_special'].split(',')

# Remove backspace
list_normal = [x.strip(' ') for x in list_normal]
list_spec = [x.strip(' ') for x in list_spec]

help_msg="""/status <service> - Check Status Service 
/start <service> - Start service 
/stop <service> - Stop service 
/restart <service> - Restart service 
/help - Print help menu of bot
"""

def bash(string):
    """
    Define bash to call bash shell command return 
    """
    output = subprocess.run(string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return output.stdout

def inject_bash(string):
    """
    Remove inject in bash allow only a-z,A-Z,0-9,-_
    """
    if (1 <= len(string) <= 25 and re.match('^[0-9a-zA-Z\-\_]+$', string) and 
        not string.startswith("-") and not string.startswith("_") and
        not string.endswith("-") and not string.endswith("_")):
        return False
    else:
        return True

def check_status(string):
    """
    Check service running 
    """
    status = os.system('systemctl status '+string[0]+ ' > /dev/null')
    if (status == 0):
        return "Running"
    else:
        return "Stopped or Not-found"


# Telegram dispatcher ========================================
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

# /status command to all id
def status(bot, update, args):
    if not args:
        message="Missing service"
    elif inject_bash(args[0]):
        message="WARNING-Inject detect"
    else:
        message=bash('systemctl status '+args[0])
    bot.send_message(chat_id=update.message.chat_id, text='```\n'+ message +'```', parse_mode='MARKDOWN')

status_handler = CommandHandler('status', status, pass_args=True)
dispatcher.add_handler(status_handler)

# /start command to list id
def start(bot, update, args):
    if str(update.message.chat_id) not in list_normal:
        message="Permision deny"
    elif not args:
        message="Missing service"
    elif inject_bash(args[0]):
        message="WARNING-Inject detect"
    elif check_status(args) == "Running":
        message="Service still running..."
    else:
        message=bash('systemctl start '+args[0])
    bot.send_message(chat_id=update.message.chat_id, text='```\n'+ message +'```', parse_mode='MARKDOWN')

start_handler = CommandHandler('start', start, pass_args=True)
dispatcher.add_handler(start_handler)

# /stop command to list id
def stop(bot, update, args):
    if str(update.message.chat_id) not in list_normal:
        message="Permision deny"
    elif not args:
        message="Missing service"
    elif inject_bash(args[0]):
        message="WARNING-Inject detect"
    elif check_status(args) == "Stopped":
        message="Service stopped"
    else: 
        message=bash('systemctl stop '+args[0])
    bot.send_message(chat_id=update.message.chat_id, text='```\n'+ message +'```', parse_mode='MARKDOWN')

stop_handler = CommandHandler('stop', stop, pass_args=True)
dispatcher.add_handler(stop_handler)

# /restat command to list id
def restart(bot, update, args):
    if str(update.message.chat_id) not in list_normal:
        message="Permision deny"
    elif not args:
        message="Missing service"
    elif inject_bash(args[0]):
        message="WARNING-Inject detect"
    else:
        message=bash('systemctl restart '+args[0])
    bot.send_message(chat_id=update.message.chat_id, text='```\n'+ message +'```', parse_mode='MARKDOWN')

restart_handler = CommandHandler('restart', restart, pass_args=True)
dispatcher.add_handler(restart_handler)

# /help command to special id 
def command(bot, update, args):
    if str(update.message.chat_id) not in list_spec:
        message="Permision deny"
    elif not args:
        message="Missing command"
    else:
        command = " ".join(str(x) for x in args)
        message=bash(command)
    bot.send_message(chat_id=update.message.chat_id, text='```\n'+ message +'```', parse_mode='MARKDOWN')

command_handler = CommandHandler('command', command, pass_args=True)
dispatcher.add_handler(command_handler)



# /help command
def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='```\n' +help_msg+ '```',parse_mode= 'Markdown')

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

# except all text 
def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="```\nWrong syntax using this command bellow \n\n" +help_msg+ '```',parse_mode= 'Markdown')

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

# except all command not in handler
def unknown(bot, update):
    #bot.send_message(chat_id=update.message.chat_id, text="Wrong syntax using this command bellow \n"+help_msg)
    bot.send_message(chat_id=update.message.chat_id, text="```\nWrong syntax using this command bellow \n\n" +help_msg+ '```',parse_mode= 'Markdown')

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
updater.idle()