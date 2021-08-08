import argparse
import sys
import time
import random
from pytg.receiver import Receiver
from pytg.sender import Sender
from pytg.utils import coroutine

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--peers", type=str, default="")
    args = parser.parse_args()

    receiver = Receiver(host="localhost", port=4458)
    sender = Sender(host="localhost", port=4458)
    
    peer_ids = list()  
    founds = 0
    for user in sender.dialog_list():
        for peer in args.peers.split(","):
            if peer in user["print_name"]:
                print("Found name: %s\t id: %s\tadding it to peers list" % (user["print_name"], user["peer_id"]))
                peer_ids.append(user["peer_id"])

    if len(peer_ids) == 0:
        print("Cant find any peer matching '%s'" % (args.peers, ))
        sys.exit(0)

    print("Loading DialoGPT...")

    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

    print("Starting...")

    receiver.start()
    receiver.message(reply(sender, peer_ids, tokenizer, model))

    receiver.stop()

@coroutine
def reply(sender, peer_ids, tokenizer, model):
    quit = False
    gpt_hidden_states = dict()

    try:
        while not quit:
            msg = (yield)
            
            sender.status_online()
            if "sender" not in msg:
                continue
            if msg["sender"]["peer_id"] not in peer_ids:
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
            with torch.no_grad():
                new_user_input_ids = tokenizer.encode(received + tokenizer.eos_token, return_tensors="pt")
                bot_input_ids = torch.cat([gpt_hidden_states[msg["sender"]["peer_id"]], new_user_input_ids], dim=-1) if msg["sender"]["peer_id"] in gpt_hidden_states else new_user_input_ids
                gpt_hidden_states[msg["sender"]["peer_id"]] = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
                reply = tokenizer.decode(gpt_hidden_states[msg["sender"]["peer_id"]][:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
                if len(reply) == 0: reply = "sorry what?"

            time.sleep(random.randint(0, 10))
            
            sender.send_typing_abort(msg.peer.cmd)
            sender.send_msg(msg.peer.cmd, reply)
            print("Reply: %s" % (reply, ))


    except GeneratorExit:
        pass
    except KeyboardInterrupt:
        pass
    else:
        pass


if __name__ == "__main__":
    main()
