import os
import telebot
from groq import Groq
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')
groq_key = os.getenv('GROQ_API_KEY')
bot_token = os.getenv('BOT_API_TOKEN')
bot = telebot.TeleBot(bot_token)

# Define global variable to keep track of user's choice
user_choice = {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id, "Hello! I'm your bot. You can use me to chat with Google's Gemini or Groq chat bot!\nTo start, just send me a textual message or use /alter to choose your chat bot.")


@bot.message_handler(commands=['alter'])
def handle_alter(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Chat with Gemini', 'Chat with Groq')
    msg = bot.send_message(
        message.chat.id, "Choose a chat bot:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_choice_step)


def process_choice_step(message):
    chat_id = message.chat.id
    choice = message.text

    if choice == 'Chat with Gemini':
        user_choice[chat_id] = 'gemini'
        bot.send_message(
            chat_id, "You chose to chat with Gemini. Send me a message to start!")
    elif choice == 'Chat with Groq':
        user_choice[chat_id] = 'groq'
        bot.send_message(
            chat_id, "You chose to chat with Groq. Send me a message to start!")
    else:
        bot.send_message(
            chat_id, "Invalid choice. Please type /alter to choose again.")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    if chat_id in user_choice:
        if user_choice[chat_id] == 'gemini':
            bot.send_message(chat_id, gemini(message.text))
        elif user_choice[chat_id] == 'groq':
            bot.send_message(chat_id, groq(message.text))
    else:
        bot.send_message(chat_id, "Please type /alter to choose a chat bot.")


def gemini(input):
    genai.configure(api_key=gemini_key)

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

    convo = model.start_chat(history=[])

    try:
        convo.send_message(input)
        return convo.last.text
    except Exception as e:
        print(e)
        return "Sorry, I encountered a problem. Please wait a bit and try again."


def groq(input):
    client = Groq(
        api_key=os.getenv("groq_api_key"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": input,
            }
        ],
        model="llama3-8b-8192",
        temperature=0,
    )

    return chat_completion.choices[0].message.content


if __name__ == "__main__":
    bot.polling(none_stop=True)
