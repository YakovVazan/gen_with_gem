import os
import telebot
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')
bot_token = os.getenv('BOT_API_TOKEN')
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id, "Hello! I'm your bot. You can use me to chat with Google's Gemini chat bot!\nTo start, just send me a textual message.")


@bot.message_handler()
def handle_text(message):
    bot.send_message(message.chat.id, gen(message.text))


def gen(input):
    genai.configure(api_key=gemini_key)

    # Set up the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[
    ])

    try:
        convo.send_message(input)
        return convo.last.text
    except Exception as e:
        print(e)
        return "Sorry, I couldn't understand that. Please try again."


if __name__ == "__main__":
    bot.polling(none_stop=True)
