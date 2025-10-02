import asyncio, re
import string
import edge_tts

# Activate venv and run:
# source .venv/bin/activate
# python utilities/word2mp3.py


# Choose a natural Russian neural voice
VOICE = "ru-RU-SvetlanaNeural"
GENDER = "female"
# VOICE = "ru-RU-DmitryNeural" 
# GENDER = "male"

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
]


    


async def main():

    # # Read words from a file (supports commas and/or newlines)
    # with open("words.txt", "r", encoding="utf-8") as f:
    #     content = f.read()
    # # supports a file with the words separated by either commas or newlines
    # WORDS = [word.strip() for word in re.split(r"[,\n]", content) if word.strip()]

    # for input_text in WORDS:
    #     safe_name = safe_filename(input_text)
    #     filename = f"../assets/sound/{GENDER}/words/{safe_name}.mp3"
    #     communicate = edge_tts.Communicate(
    #         text=input_text,
    #         voice=VOICE,
    #         rate="+0%",
    #         volume="+0%",
    #         pitch="+0Hz"
    #     )
    #     await communicate.save(filename)
    #     print(f"Saved {filename}")

    filename = f"../assets/sound/female/иии.mp3"
    communicate = kids_rollecoster("иииииии")
    await communicate.save(filename)
    print(f"Saved {filename}")

def kids_rollecoster(text: str):
    """
    returns sound as kids yelling on a rollecoaster
    """
    # SSML with a long vowel and falling pitch (glissando), a touch faster & louder
    SSML = """
    <speak version="1.0" xml:lang="ru-RU">
    <prosody rate="+15%" pitch="+8%">
        иииииииииииииииииииииии!
    </prosody>
    </speak>
    """
    return edge_tts.Communicate(SSML, "ru-RU-SvetlanaNeural")

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