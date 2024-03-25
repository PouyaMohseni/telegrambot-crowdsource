from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler #, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes



# Define a function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text("Welcome to the bot!")
    keyboard = [[InlineKeyboardButton("Not Proficient", callback_data='st_1'),
                 InlineKeyboardButton("Moderate", callback_data='st_2'),
                 InlineKeyboardButton("Perfect", callback_data='st_3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('How would you rate your ear-training abilities:', reply_markup=reply_markup)

async def buttonstart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    response = query.data
    
    ####
    # Handeling the start response
    ####
    if response[:2] == 'st':
        response_code = int(response[3])
        # Check if the user already exists in the DataFrame
        if user_id not in user["ID"].values:
            # If the user is new, append their response to the DataFrame
            user.loc[len(user)] = [user_id, response, 0, 0]
            # Update Excel file
            user.to_excel(user_db, index=False)
            await query.edit_message_text(text="Your answer has been recorded. Thank you!")
        else:
            await query.edit_message_text(text="Your answer has been updated!")

        await query.edit_message_text(text="For each of these ground-truth tests check the instrument you recognized!")

        
        audio_file = open("./dataset/truth/track 1.mp3", "rb")
        await context.bot.send_audio(chat_id=user_id, audio=audio_file)
        audio_file.close()

        instruments_q1 = [[InlineKeyboardButton("Tar", callback_data='q1_01'),
                     InlineKeyboardButton("Ney", callback_data='q1_1'),
                     InlineKeyboardButton("Setar", callback_data='q1_02'),
                     InlineKeyboardButton("Santour", callback_data='q1_03')]]
        instrument_markup_q1 = InlineKeyboardMarkup(instruments_q1)
            
        await query.message.reply_text('What instrument did you heared?', reply_markup=instrument_markup_q1)

    ####
    # Handeling the question 1 response
    ####
    elif response[:2] == 'q1':
        await query.edit_message_text(text="Your answer has been recorded!")
        # Adding to the dataset


        # Asking the next question
        audio_file = open("./dataset/truth/track 1.mp3", "rb")
        await context.bot.send_audio(chat_id=user_id, audio=audio_file)
        audio_file.close()

        instruments_q2 = [[InlineKeyboardButton("Tar", callback_data='q2_1'),
                     InlineKeyboardButton("Ney", callback_data='q2_01'),
                     InlineKeyboardButton("Setar", callback_data='q2_02'),
                     InlineKeyboardButton("Santour", callback_data='q2_03')]]
        instrument_markup_q2 = InlineKeyboardMarkup(instruments_q2)


        await query.message.reply_text('What instrument did you heared?', reply_markup=instrument_markup_q2)


    ####
    # Handeling the question 2 response
    ####
    elif response[:2] == 'q2':
        await query.edit_message_text(text="Your answer has been recorded!")
        # Adding to the dataset


        # Asking the next question
        audio_file = open("./dataset/truth/track 1.mp3", "rb")
        await context.bot.send_audio(chat_id=user_id, audio=audio_file)
        audio_file.close()

        instruments_q3 = [[InlineKeyboardButton("Tar", callback_data='q3_01'),
                     InlineKeyboardButton("Ney", callback_data='q3_02'),
                     InlineKeyboardButton("Setar", callback_data='q3_13'),
                     InlineKeyboardButton("Santour", callback_data='q3_04')]]
        instrument_markup_q3 = InlineKeyboardMarkup(instruments_q3)


        await query.message.reply_text('What instrument did you heared?', reply_markup=instrument_markup_q3)
        

    ####
    # Handeling the question 3 response
    ####
    elif response[:2] == 'q3':
        await query.edit_message_text(text="Your answer has been recorded!")
        # Adding to the dataset


        # Updating the credit

        #Stating the credit
        #if full
            #await query.message.reply_text('What instrument yo', reply_markup=instrument_markup_q3)

        #elif 3-5
            #await query.message.reply_text('What instrument yo', reply_markup=instrument_markup_q3)

        #else
            #await query.message.reply_text('What instrument yo', reply_markup=instrument_markup_q3)




# Main function
def main():

    app = ApplicationBuilder().token("6900009914:AAGomuchkUQ-hFQcVQLtK7E8gJXrRU4AwN0").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttonstart, pattern='^1$'))

    app.run_polling()

#if __name__ == "__main__":
#    main()


user_db = "user.xlsx"
user = pd.read_excel(user_db)

app = ApplicationBuilder().token("6900009914:AAGomuchkUQ-hFQcVQLtK7E8gJXrRU4AwN0").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttonstart))


app.run_polling()

