from .neuroengine import GPT
gpt = GPT()
text = gpt.auto('Мы играли в ролевую игру', max_length=100)
print(text)
