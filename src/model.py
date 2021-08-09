import os
import logging
import pickle
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ChatModel:
    def __init__(self):
        logging.info("Loading Chat Model")
        self.tokenizer = AutoTokenizer.from_pretrained(os.environ["MODEL"])
        self.model = AutoModelForCausalLM.from_pretrained(os.environ["TOKENIZER"])
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

            self.hidden_states[conversation] = self.model.generate(
                bot_input_ids,
                min_length = 1,
                max_length=1000,
                do_sample = True,
                early_stopping = False,
                num_beams = 1,
                num_beam_groups = 1,
                diversity_penalty = 0.0,
                temperature = 1,
                top_k = 40,
                top_p = 0.9,
                repetition_penalty = 1,
                length_penalty = 1,
                no_repeat_ngram_size = 0,
                num_return_sequences = 1,
                pad_token_id=self.tokenizer.eos_token_id
            )
    
            cache_file = open(cache_filename, "wb")
            pickle.dump(self.hidden_states[conversation], cache_file)
            cache_file.close()
            reply = self.tokenizer.decode(self.hidden_states[conversation][:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
            if len(reply) == 0: reply = "sorry what?"

            return reply


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    model = ChatModel()

    while True:
        print("Bot>> ", model.chat(2, input("Human>> ")))
    
