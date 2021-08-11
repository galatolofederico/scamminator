import os
import logging
import time
import random
import pickle
from pytg.receiver import Receiver
from pytg.sender import Sender
from pytg.utils import coroutine

import threading
from xmlrpc.server import SimpleXMLRPCServer

from src.model import ChatModel

class Client:
    def __init__(self):
        self.receiver = Receiver(host=os.environ["TELEGRAM_CLI_HOST"], port=int(os.environ["TELEGRAM_CLI_PORT"]))
        self.sender = Sender(host=os.environ["TELEGRAM_CLI_HOST"], port=int(os.environ["TELEGRAM_CLI_PORT"]))
        self.model = ChatModel()

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
                if str(msg["sender"]["peer_id"]) not in self.active_users:
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
                logging.info("Received: %s from: %s" % (received, msg["sender"]["name"]))

                sender.send_typing(msg.peer.cmd, 1)
                reply = self.model.chat(msg["sender"]["peer_id"], received)
                sender.send_typing_abort(msg.peer.cmd)

                time.sleep(random.randint(0, 7))
                logging.info("Replying: %s to: %s" % (reply, msg["sender"]["name"]))
                sender.send_msg(msg.peer.cmd, reply)
                sender.status_offline()

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
        logging.info("Starting telegram client")
        self.receiver.start()
        self.receiver.message(self.reply(self.sender))

        self.receiver.stop()

    def dialog_list(self):
        return self.sender.dialog_list()
    
    def add(self, peer_id, name):
        if peer_id not in self.active_users:
            self.active_users[peer_id] = name
            self.save_cache()
            return True
        return False

    def force_reply(self, peer_id):
        try:
            peer_id = int(peer_id)
        except:
            return False
        peer = None
        for user in self.dialog_list():
            if peer_id == user["peer_id"]:
                peer = user["print_name"]
                break
        if peer is None: return False

        last_msg = None
        for event in self.sender.history(peer):
            if event["event"] == "message" and not event["out"] and "text" in event:
                last_msg = event["text"]
        
        if last_msg is None:
            return False
        
        logging.info("Force Reply using: %s from: %s" % (last_msg, peer))

        self.sender.send_typing(peer, 1)
        reply = self.model.chat(peer, last_msg)
        self.sender.send_typing_abort(peer)

        logging.info("Replying: %s to : %s" % (reply, peer))
        self.sender.send_msg(peer, reply)
        self.sender.status_offline()

        return True

    def remove(self, peer_id):
        if peer_id not in self.active_users:
            return False
        else:
            del self.active_users[peer_id]
            self.save_cache()
            return True
    
    def reset(self, peer_id):
        if peer_id not in self.active_users:
            return False
        else:
            return self.model.reset(peer_id)

    def list(self):
        return self.active_users

class RPCWrapper:
    def __init__(self, client):
        self.client = client

    def search(self, name):
        ret = []
        for user in self.client.dialog_list():
            if name in user["print_name"]:
                ret.append(dict(name=user["print_name"], peer_id=user["peer_id"]))
        return ret
    
    def add(self, peer_id, name):
        return self.client.add(peer_id, name)
    
    def reply(self, peer_id):
        return self.client.force_reply(peer_id)

    def remove(self, peer_id):
        return self.client.remove(peer_id)

    def reset(self, peer_id):
        return self.client.reset(peer_id)

    def list(self):
        return self.client.list()

def start_client(client):
    logging.info("Starting client")
    client.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = Client()
    server = SimpleXMLRPCServer((os.environ["RPC_HOST"], int(os.environ["RPC_PORT"])))

    threading.Thread(target=start_client, args=(client, )).start()

    wrapper = RPCWrapper(client)
    server.register_instance(wrapper)
    
    logging.info("Starting RPC Server")
    server.serve_forever()
    
    
