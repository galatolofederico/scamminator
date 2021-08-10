import os
import logging
import pickle
import xmlrpc.client

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


admin_users = dict()
cache_filename = os.path.join(os.environ["BOT_CACHE"], "admin_users")
client = None

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

def start_command(update, context):
    update.message.reply_text("type /password <your_password> to enable the bot")

def help_command(update, context):
    if not check_admin(update): return
    update.message.reply_text("""
/list  Shows the list of scamminator users
/search <name> Search <name> in your chats list
/add <id> <name>  Adds <id> with the name <name> to the list of scamminator users
/remove <id>  Removes <id> from the list of scamminator users
/reset <id> Resets the AI for <id>
""")

def search_command(update, context):
    if not check_admin(update): return
    results = client.search("".join(context.args))
    if len(results) > 0:
        reply = "Search results:\n"
        for result in results:
            reply += "name: %s  id: %s\n" % (result["name"], result["peer_id"])
        update.message.reply_text(reply)
    else:
        update.message.reply_text("No results for '%s'" % ("".join(context.args)))
    
def add_command(update, context):
    if not check_admin(update): return
    if len(context.args) != 2:
        update.message.reply_text("Error: use /add <id> <name> (name is just a mnemonic name)")
        return
    if client.add(context.args[0], context.args[1]):
        update.message.reply_text("id '%s' added to scamminator" % (context.args[0]))
    else:
        update.message.reply_text("cant add '%s'" % (context.args[0]))

def remove_command(update, context):
    if not check_admin(update): return
    if len(context.args) != 1:
        update.message.reply_text("Error: use /remove <id>")
        return
    if client.remove(context.args[0]):
        update.message.reply_text("id '%s' removed from scamminator" % (context.args[0]))
    else:
        update.message.reply_text("cant remove '%s'" % (context.args[0]))

def list_command(update, context):
    if not check_admin(update): return
    active_users = client.list()
    if len(active_users) > 0:
        reply = "Scamminator active users:\n"
        for id, name in active_users.items():
            reply += "name: %s  id: %s\n" % (name, id)
        update.message.reply_text(reply)
    else:
        update.message.reply_text("Scamminator is not active /add a user to activate it")

def reset_command(update, context):
    if not check_admin(update): return
    if len(context.args) != 1:
        update.message.reply_text("Error: use /reset <id>")
        return
    if client.reset(context.args[0]):
        update.message.reply_text("Conversation id '%s' reset" % (context.args[0]))
    else:
        update.message.reply_text("Cant reset '%s'" % (context.args[0]))

def password_command(update, context):
    if len(context.args) != 1:
        update.message.reply_text("Error: use /password <your_password>")
        return
    if context.args[0] == os.environ["BOT_PASSWORD"]:
        admin_users[update.effective_user.id] = "%s %s" % (update.effective_user.first_name, update.effective_user.last_name)
        save_cache()
        update.message.reply_text("Enabled type /help for the command list")
    else:
        update.message.reply_text("Wrong password")

def start():
    global client
    read_cache()

    updater = Updater(os.environ["BOT_TOKEN"])

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("password", password_command, pass_args=True))
    dispatcher.add_handler(CommandHandler("search", search_command, pass_args=True))
    dispatcher.add_handler(CommandHandler("add", add_command, pass_args=True))
    dispatcher.add_handler(CommandHandler("remove", remove_command, pass_args=True))
    dispatcher.add_handler(CommandHandler("reset", reset_command, pass_args=True))
    dispatcher.add_handler(CommandHandler("list", list_command))
    

    logging.info("Starting telegram bot")

    client = xmlrpc.client.ServerProxy("http://%s:%s/" % (os.environ["RPC_HOST"], os.environ["RPC_PORT"]))
    updater.start_polling()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start()