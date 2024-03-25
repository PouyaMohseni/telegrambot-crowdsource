from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler #, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
#import logging
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


# Define a function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text("Welcome to the bot!")
    keyboard = [[InlineKeyboardButton("Not Proficient", callback_data='1'),
                 InlineKeyboardButton("Moderate", callback_data='2'),
                 InlineKeyboardButton("Perfect", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('How would you rate your ear-training abilities:', reply_markup=reply_markup)

# Define a button for start function
async def buttonstart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    response = int(query.data)
    
    # Check if the user already exists in the DataFrame
    if user_id not in user["ID"].values:
        # If the user is new, append their response to the DataFrame
        user.loc[len(user)] = [user_id, response, 0, 0]
        # Update Excel file
        user.to_excel(user_db, index=False)
        await query.edit_message_text(text="Your answer has been recorded. Thank you!")
    else:
        await query.edit_message_text(text="Your answer has been updated!")


# Define groundtruth functions
# Function one
async def question_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("For each of these ground-truth tests check the instrument you recognized!")
    audio_file = open("./dataset/truth/track 1.mp3", "rb")
    await context.bot.send_audio(audio=audio_file)
    audio_file.close()

    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
            InlineKeyboardButton("Option 3", callback_data='3'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text="Question 1: Choose an option", reply_markup=reply_markup)

# Function to handle the first question response
def answer_1(update, context):
    query = update.callback_query
    user_responses[query.message.chat_id].append(query.data)

    # Ask the second question
    question_2(query.message.chat_id, context)

# Function to ask the second question
def question_2(chat_id, context):
    audio_file = open("path_to_your_audio_file.mp3", "rb")  # Replace with the path to your audio file
    context.bot.send_audio(chat_id=chat_id, audio=audio_file)
    audio_file.close()

    keyboard = [
        [
            InlineKeyboardButton("Option A", callback_data='A'),
            InlineKeyboardButton("Option B", callback_data='B'),
            InlineKeyboardButton("Option C", callback_data='C'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="Question 2: Choose an option", reply_markup=reply_markup)

# Function to handle the second question response
def answer_2(update, context):
    query = update.callback_query
    user_responses[query.message.chat_id].append(query.data)

    # Ask the third question
    question_3(query.message.chat_id, context)

# Function to ask the third question
def question_3(chat_id, context):
    audio_file = open("path_to_your_audio_file.mp3", "rb")  # Replace with the path to your audio file
    context.bot.send_audio(chat_id=chat_id, audio=audio_file)
    audio_file.close()

    context.bot.send_message(chat_id=chat_id, text="Question 3: What is your favorite color?")

# Function to handle the third question response
def answer_3(update, context):
    user_responses[update.message.chat_id].append(update.message.text)

    # Display the collected responses
    context.bot.send_message(chat_id=update.message.chat_id, text="Thank you for your responses!")
    context.bot.send_message(chat_id=update.message.chat_id, text="Here are your responses:")
    context.bot.send_message(chat_id=update.message.chat_id, text=str(user_responses[update.message.chat_id]))

#gtruth
async def gtruth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text("For each of these ground-truth tests check the instrument you recognized!")

    await update.message.reply_text('How would you rate your ear-training abilities:', reply_markup=reply_markup)



# Main function
def main():
    # Define the Excel file name
    user_db = "user.xlsx"
    user = pd.read_excel(user_db)

    # Define markup for ground truth questions
    instruments = [[InlineKeyboardButton("Tar", callback_data='1'),
                 InlineKeyboardButton("Ney", callback_data='2'),
                 InlineKeyboardButton("Setar", callback_data='3'),
                 InlineKeyboardButton("Santour", callback_data='4')]]
    instrument_markup = InlineKeyboardMarkup(instruments)

    app = ApplicationBuilder().token("6900009914:AAGomuchkUQ-hFQcVQLtK7E8gJXrRU4AwN0").build()

    app.add_handler(CommandHandler("hello", hello))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttonstart, pattern='^1$'))

    #app.add_handler(CommandHandler("test", test))
    #app.add_handler(CallbackQueryHandler(buttontest))

    app.run_polling()


user_db = "user.xlsx"
user = pd.read_excel(user_db)

    # Define markup for ground truth questions
instruments = [[InlineKeyboardButton("Tar", callback_data='1'),
                 InlineKeyboardButton("Ney", callback_data='2'),
                 InlineKeyboardButton("Setar", callback_data='3'),
                 InlineKeyboardButton("Santour", callback_data='4')]]
instrument_markup = InlineKeyboardMarkup(instruments)

app = ApplicationBuilder().token("6900009914:AAGomuchkUQ-hFQcVQLtK7E8gJXrRU4AwN0").build()

app.add_handler(CommandHandler("hello", hello))

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttonstart))

app.add_handler(CommandHandler("question_1", question_1))

    #app.add_handler(CommandHandler("test", test))
    #app.add_handler(CallbackQueryHandler(buttontest))

app.run_polling()
