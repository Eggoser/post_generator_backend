import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import pickle
import random as rd
import re


class GPT:
    """This class is the GPT interface"""

    def __init__(self, model='sberbank-ai/rugpt3small_based_on_gpt2',
                 file='bad_words.pkl', num_seq=1, addition=20, num_beams=1):
        with open(file, 'rb') as f:
            self.bad_words = pickle.load(f)
        self.model = GPT2LMHeadModel.from_pretrained(
            model).cuda()
        self.tokenizer = GPT2Tokenizer.from_pretrained(model)
        self.addition = addition
        self.num_seq = num_seq
        self.num_beams = num_beams

    def filter(self, text, return_words=False, ex=[]):
        """Returns True if there are bad words, else False """
        res = []
        keys = [',', '.', '?', '!', '-', ';', ':', '''"''', "'", '(', ')']
        for i in keys:
            text = text.replace(i, '')
        text = text.lower().split()
        for i in text:
            if i in self.bad_words and i not in ex:
                res.append(i)
        if len(res) == 0:
            return False
        if return_words:
            return True, res
        return True

    def detect_adv(self, text):
        """Returns True if there are advert, else False"""
        adv = ['https://', 'http://', 'www', '.com', '.ru', '.org', '#',
               '@', '+7']
        rex = re.compile(r'(\+7|8|7).*?(\d{3}).*?(\d{3}).*?(\d{2}).*?(\d{2})')
        if rex.findall(text):
            return True
        for i in adv:
            if i in text:
                return True
        return False

    def generate(self,
                 text,
                 do_sample=True, max_length=50, repetition_penalty=5.0,
                 top_k=5, top_p=0.95, temperature=1,
                 num_beams=1,
                 no_repeat_ngram_size=3,
                 num_return_sequences=1,
                 censormode=True
                 ):
        """Returns the text made by the gpt"""
        input_ids = self.tokenizer.encode(text, return_tensors="pt").cuda()
        bad_words = []
        for i in self.bad_words:
            bad_words.append(self.tokenizer(i, add_prefix_space=True).input_ids)
        out = self.model.generate(
            input_ids.cuda(),
            max_length=max_length,
            repetition_penalty=repetition_penalty,
            do_sample=do_sample,
            top_k=top_k, top_p=top_p, temperature=temperature,
            num_beams=num_beams, no_repeat_ngram_size=no_repeat_ngram_size,
            num_return_sequences=num_return_sequences,
            bad_words_ids=bad_words if censormode else None
        )
        return list(map(self.tokenizer.decode, out))

    def stabilizer(self, text):
        '''Clear text from unfinished sentences'''
        sym = ['.', '?', '!', ';']
        if text[-1] in sym:
            return text
        pos = []
        for i in sym:
            pos.append(text.rfind(i))
        if max(pos) == -1:
            return text
        return text[:max(pos) + 1]

    def clear(self, text):
        '''Clear text from special characters'''
        text = text.replace('\nA', '')
        text = text.replace('&quot', '''"''')
        text = text.replace('&amp', '''"''')
        text = text.replace('&laquo', '''"''')
        text = text.replace('&raquo', '''"''')
        text = text.replace('&ndash', 'â€”')
        text = text.replace('&mdash', 'â€”')
        text = text.replace('&nbsp', ' ')
        text = text.replace('&lt', '<')
        text = text.replace('&gt', '>')
        text = text.replace('&hellip', '...')
        # text = text.replace('&rahellip', '')
        text = text.replace('''";''', '''"''')
        text = text.replace('&rave;', '''"''')
        text = text.replace('&raqip;', '''"''')
        text = text.replace('&raacute;', '''"''')
        # text = text.replace('&hellash;', '')
        text = text.replace('&raqicacute;', '''"''')
        text = text.replace('&rdquo;', '''"''')
        text = text.replace('&ldquo;', '''"''')
        text = text.replace('&rdsdash;', '''"''')
        text = text.replace('&ra;', '''"''')
        text = text.replace(';&rdquot;', '''"''')
        text = text.replace('&rdquot;', '''"''')
        # text = text.replace('&la;', '')
        for i in re.compile('[;]?&[a-z]+[;]?').findall(text):
            text = text.replace(i, '')
        return text

    def auto(self, text, max_length=50):
        """Automatically generates text of a given length"""
        while True:
            ans = self.generate(text, max_length=max_length + self.addition,
                                num_return_sequences=self.num_seq, num_beams=self.num_beams)
            for i, d in enumerate(ans):
                d = self.clear(d)
                d = self.stabilizer(d)
                ans[i] = d
                if self.detect_adv(d):
                    ans.remove(d)
            if len(ans) == 0:
                continue
            if self.num_seq == 1:
                return ans[0]
            return rd.choice(ans)
