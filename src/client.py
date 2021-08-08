import time
import random
from pytg.receiver import Receiver
from pytg.sender import Sender
from pytg.utils import coroutine


class Client:
    def __init__(self):
        self.receiver = Receiver(host="localhost", port=4458)
        self.sender = Sender(host="localhost", port=4458)

        self.cache_filename = os.path.join(os.environ["BOT_CACHE"], "active_users")
        self.active_users = dict()
        self.read_cache()

    @coroutine
    def reply(self, sender):
        try:
            while True:
                msg = (yield)
                
                sender.status_online()
                if "sender" not in msg:
                    continue
                if msg["sender"]["peer_id"] not in self.active_users:
                    continue
                if msg.event != "message":
                    continue
                if msg.own:
                    continue
                if "text" not in msg:
                    continue
                if msg.text is None:
                    continue
                
                received = msg.text
                print("Received: %s from: %s" % (received, msg["sender"]["name"]))

                sender.send_typing(msg.peer.cmd, 1)
                
                reply = "hellooo"
                sender.send_typing_abort(msg.peer.cmd)
                sender.send_msg(msg.peer.cmd, reply)

        except GeneratorExit:
            pass
        except KeyboardInterrupt:
            pass
        else:
            pass

    def save_cache(self):
        logging.info("Writing users cache file '%s'" % (self.cache_filename, ))
        cache_file = open(self.cache_filename, "wb")
        pickle.dump(self.active_users, cache_file)
        cache_file.close()

    def read_cache(self):
        if os.path.exists(self.cache_filename):
            logging.info("Reading users cache file '%s'" % (self.cache_filename, ))
            cache_file = open(self.cache_filename, "rb")
            self.active_users = pickle.load(cache_file)
            cache_file.close()

    def start(self):
        self.receiver.start()
        self.receiver.message(self.reply(self.sender))

        self.receiver.stop()

if __name__ == "__main__":
    client = Client()
    client.start()
