import re
import json
import aiomax
import os
from gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

os.environ["GIGACHAT_VERIFY_SSL_CERTS"] = "False"

MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN")
GIGACHAT_API = os.getenv("GIGACHAT_API")

giga = GigaChat(
    base_url="https://api.giga.chat/v1",
    credentials=GIGACHAT_API,
    model="GigaChat-3-Ultra",
    verify_ssl_certs=False,
    temperature=0.3,
    top_p=0.9,
    repetition_penalty=1.05
)

bot = aiomax.Bot(MAX_BOT_TOKEN, use_certificate=True)

verified_users = {}

try:
    with open("contacts.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        authorized_phones = set(data["authorized_phones"])
        questions = data["questions"]
except Exception as e:
    print(f"ошибка загрузки json файла: {e}")
    authorized_phones = set()
    questions = []

promt = """Ты бот-помщник для распознования типа вопроса и их параметров, который задал пользователь из списка типов возможных вопросов.
Правила:
1.Не додумывай лишнего, опирайся только на информацию, данную пользователем
2.В ответе выдавай список, где первый элемент - номер вопроса из списка от 0, а второй - вложенный список с параметрами для определенного типа запроса в таком же порядке, котором он дан в списке типов. Если пользователь не написал какой-то из параметров, на его месте напиши None.
3.Если не удалось сопоставить вопрос пользователя со списком ответь:None
Пример: [2, ["9 класс", "город Якутск"]]
Помни, что пользователь может заменять слова на синонимы, использовать сокращения или совершать ошибки. Вот сообщение пользователя:"""

def get_phone_from_max(vcf_text: str):
    if not vcf_text:
        return None
    match = re.search(r'TEL[^:]*?:([\d+]+)', vcf_text)
    return match.group(1) if match else None


@bot.on_bot_start()
async def on_bot_start(payload: aiomax.BotStartPayload):
    kb = aiomax.buttons.KeyboardBuilder()
    kb.add(aiomax.buttons.ContactButton(text="Поделиться номером телефона"))
    await payload.send("Нажмите кнопку, чтобы поделиться номером", keyboard=kb)

@bot.on_message()
async def on_message(message: aiomax.Message):
    user_id = message.sender.user_id

    if hasattr(message, "body") and hasattr(message.body, "attachments") and message.body.attachments:
        for i in message.body.attachments:
            if getattr(i, 'type', None) == 'contact':
                vcf = getattr(i, 'vcf_info', '')
                phone = get_phone_from_max(vcf)
                if phone and phone in authorized_phones:
                    verified_users[user_id] = phone
                    await message.reply(f"Номер {phone} подтверждён! {questions}")
                else:
                    await message.reply("Доступ запрещён")
                return

    if message.content == "/start":
        kb = aiomax.buttons.KeyboardBuilder()
        kb.add(aiomax.buttons.ContactButton(text="Поделиться номером телефона"))
        await message.reply("Нажмите кнопку, чтобы поделиться номером", keyboard=kb)
        return

    if hasattr(message, 'content') and message.content:
        if user_id in verified_users:
            last_message = message.content
            response = giga.chat(f"{promt} '{last_message}'. Возможные типы вопросов и их параметры: {questions}.")
            res = response.choices[0].message.content
            if res == "None":
                await message.reply("Не возможно выполнить этот запрос")
            else:
                await message.reply(res)
        else:
            await message.reply("Напишите /start для того, чтоб поделится номером для проверки")
        return

if __name__ == "__main__":
    print("бот запущен")
    bot.run()



