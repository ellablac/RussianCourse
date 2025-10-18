import asyncio, re
import string
import edge_tts

# Activate venv and run:
# source .venv/bin/activate
# python utilities/word2mp3.py

# edge_tts is a free undocumented Microsoft service that provides
# text-to-speech synthesis. Works in all browsers, including Chrome.

# Choose a natural Russian neural voice
# VOICE = "ru-RU-SvetlanaNeural"
# GENDER = "female"
VOICE = "ru-RU-DmitryNeural" 
GENDER = "male"

# WORDS = [
#     "щща"
# ]

# WORDS = [
#     "а́а", "бэ", "вэ", "гэ", "дэ", "е", "ё", "жэ", "зэ", "и", "й",
#     "ка", "эл", "эм", "эн", "о́", "пэ", "эр", "эс", "тэ", "у", "эф",
#     "ха", "цэ", "чэ", "ша", "щща", "твёрдый знак", "ы", "мягкий знак", "э", "ю", "я"
# ]

WORDS = [
   #  "рoбат", "р-р-р"
   # "комета", "космос"
#    "мама", "томат", "кот", "атом"
    # "текст", "маска"
    # "метро", "карта", "банк", "Москва",
    # "мотор", "ракета", "театр", "секрет"
    # "ресторан", "нота", "тур", "курс", "ресурс", "структура", "хор", "хаос"
    # "зона", "журнал", "пижама", "массаж", "борщ", "зоопарк", "чек", "центр", "цирк", "шок", "шеф"
    # "конь", "есть", "есть", "сесть" , "съесть", "счастье",
    # "подъезд", "объект", "субъект", "адъютант", "инъекция"
    # "ест", "мель", "шесть", "пьеса", "жить", "тень", "мой", "йогурт", "йода", "жесть", "восемь"
    # "ёгурт"
    # "здравствуйте", "привет", "как дела?", "как вас зовут?", "меня зовут Элла", "очень приятно"
    # "здравствуйте!", "как дела?", "как дела", "как вас зовут?", "как вас зовут"
    # "меня зовут Яков", "приятно познакомиться", "до свидания", "до скорой встречи", "спасибо", "пожалуйста", "пока"
    # "с праздником!", "спасибо, хорошо" , "как ваши дела?"
    # "приятно познакомиться", "добрый день", "добрый вечер", "спокойной ночи"
    # "шофёр", "дирижёр", "интернет", "идея", "импорт", "индекс", "инженер", "сын", "мышь", "экзамен", 
    # "экономика", "электрон", "энергия", "эффект", "юмор", "юпитер", "яхта", "ягуар"
    # "ум", "енот", "экзамен", "люк", "лук", "бить", "быть", "генезис", "гамма", "дом", "песнь", "пасха", "фильм", "миф", "декан"  
    # "евангелие", "дьякон"
    # "края", "яблоко", "мясо", "мост", "поёт", "ёлка", "лёд", "суп", "люди", "пою", "нэп", "поёт", "пе́ние", "мы", "мир", "игла", "мои",
    # "море", "кино", "радио", "пицца", "жилье", "небо", "окно", "музей", 
    # "девочка",  "мальчик", "машина", "цветок" 
    "это", "он", "она", "оно",  "большой", "большая", "большое", "маленький", "маленькая", "маленькое"
]

# azbuka = \
#     "а́, бэ, вэ, гэ, дэ, е, ё, жэ, зэ, и, й, \
#     ка, эл, эм, эн, о́, пэ, эр, эс, тэ, у, эф, \
#     ха, цэ, чэ, ша, щща, твёрдый знак, ы, мягкий знак, э, ю, я"
    


async def main():

    # # Read words from a file (supports commas and/or newlines)
    # with open("words.txt", "r", encoding="utf-8") as f:
    #     content = f.read()
    # # supports a file with the words separated by either commas or newlines
    # WORDS = [word.strip() for word in re.split(r"[,\n]", content) if word.strip()]

    for input_text in WORDS:
        safe_name = safe_filename(input_text)
        filename = f"../assets/sound/{GENDER}/words/{safe_name}.mp3"
        communicate = edge_tts.Communicate(
            text=input_text,
            voice=VOICE,
            rate="+0%",
            volume="+0%",
            pitch="+0Hz"
        )
        await communicate.save(filename)
        print(f"Saved {filename}")

    # filename = f"../assets/sound/{GENDER}/azbuka.mp3"
    # communicate = edge_tts.Communicate(
    #         text=azbuka,
    #         voice=VOICE,
    #         rate="-50%",
    #         volume="+0%",
    #         pitch="+0Hz"
    #     )
    # await communicate.save(filename)
    # print(f"Saved {filename}")

def safe_filename(text: str, max_length: int = 50) -> str:
    """
    Convert text into a safe filename:
    - Keep letters, numbers, spaces, underscores, dashes
    - Replace other characters with '_'
    - Trim to max_length
    """
    # Replace invalid characters with underscore
    safe = re.sub(r'[?]', '_q', text)
    safe = re.sub(r'[!]', '_ex', safe)
    safe = re.sub(r'[^0-9A-Za-zА-Яа-яЁё _-]', '_', safe)

    # Strip leading/trailing spaces/underscores
    safe = safe.strip(" _-")

    # Collapse multiple underscores/spaces into one
    safe = re.sub(r'[\s_]+', '_', safe)

    # Cut to a safe length
    return safe[:max_length]

asyncio.run(main())

# а́ е́ и́ о́ у́ ы́ э́ ю́ я́