import os
import logging
import pickle

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

admin_users = dict()
cache_filename = os.path.join(os.environ["BOT_CACHE"], "admin_users")

def save_cache():
    logging.info("Writing admins cache file '%s'" % (cache_filename, ))
    cache_file = open(cache_filename, "wb")
    pickle.dump(admin_users, cache_file)
    cache_file.close()

def read_cache():
    global admin_users
    if os.path.exists(cache_filename):
        logging.info("Reading admins cache file '%s'" % (cache_filename, ))
        cache_file = open(cache_filename, "rb")
        admin_users = pickle.load(cache_file)
        cache_file.close()

def check_admin(update):
    if update.effective_user.id not in admin_users:
        update.message.reply_text("You are not an admin")
        return False
    return True

def start(update, context):
    update.message.reply_text("type /password <your_password> to enable the bot")

def help_command(update, context):
    if not check_admin(update): return
    update.message.reply_text("""
/list  Shows the list of scamminator users
/add <name>  Adds <name> to the list of scamminator users
/remove <name>  Removes <name> from the list of scamminator users
""")


def password_command(update, context):
    if context.args[0] == os.environ["BOT_PASSWORD"]:
        admin_users[update.effective_user.id] = "%s %s" % (update.effective_user.first_name, update.effective_user.last_name)
        save_cache()
        update.message.reply_text("Enabled type /help for the command list")
    else:
        update.message.reply_text("Wrong password")

def main():
    read_cache()

    updater = Updater(os.environ["BOT_TOKEN"])

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("password", password_command, pass_args=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
