import os
import logging
import pickle
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ChatModel:
    def __init__(self, model="microsoft/DialoGPT-medium", tokenizer="microsoft/DialoGPT-medium"):
        logging.info("Loading Chat Model")
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(tokenizer)
        logging.info("Model loaded")
        
        self.cache = os.environ["BOT_CACHE"]
        self.hidden_states = dict()

    def chat(self, conversation, message):
        conversation = str(conversation)
        cache_filename = os.path.join(self.cache, conversation)
        if conversation not in self.hidden_states and os.path.exists(cache_filename):
            logging.info("Loading cache file for conversation '%s'" % (conversation, ))
            cache_file = open(cache_filename, "rb")
            self.hidden_states[conversation] = pickle.load(cache_file)
            cache_file.close()
        
        with torch.no_grad():
            input_ids = self.tokenizer.encode(message + self.tokenizer.eos_token, return_tensors="pt")

            if conversation in self.hidden_states:
                bot_input_ids = torch.cat([self.hidden_states[conversation], input_ids], dim=-1)
            else:
                bot_input_ids = input_ids

            hidden_state =  self.model.generate(bot_input_ids, max_length=1000, pad_token_id=self.tokenizer.eos_token_id)
    
            cache_file = open(cache_filename, "wb")
            pickle.dump(hidden_state, cache_file)
            cache_file.close()

            reply = self.tokenizer.decode(hidden_state[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
            if len(reply) == 0: reply = "sorry what?"

            return reply


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    model = ChatModel()

    print(model.chat(1, "hi my name is federico"))
    print(model.chat(2, "hi my name is marco"))

    print(model.chat(1, "what is my name?"))
    print(model.chat(2, "what is my name?"))
    
