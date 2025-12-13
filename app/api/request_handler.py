import os
import re

from dotenv import load_dotenv, find_dotenv
from yandexgptlite import YandexGPTLite

load_dotenv(find_dotenv())
account = YandexGPTLite(os.getenv('YANDEX_FOLDER_ID'), os.getenv('YANDEX_API_KEY'))

text = account.create_completion('скажи мне что-нибудь хорошее', '0.1', system_prompt = 'отвечай на английском')
print(text) #Sounds good!
