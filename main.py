from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
import pandas as pd
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import re
import logging


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


ABILITY, GTRUTH1, GTRUTH2, GTRUTH3 = range(4)
TAR, NEY, SETAR, SANTOUR, KAMANCHEH, END_ANNOT = range(6)

ability_mapping = {"Low": 0, "Moderate": 1, "High": 2}
instrument_mapping = {"tar": TAR, "ney": NEY, "setar": SETAR, "santour": SANTOUR, "kamancheh": KAMANCHEH}
basic_annotation = { instrument: -1 for instrument in instrument_mapping.keys()}

# Start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    reply_keyboard = [["Low", "Moderate", "High"]]
    

    await update.message.reply_text(
        "Hi! This is PersianMIR. "
        "Send /cancel to stop annotation.\n\n"
        "How would you rate your ear-training abilities (wriate a number between 1 and 4 with 1 being lowest and 4 being highest):",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Ear training ability"
        ),
    )

    return ABILITY


# Handle the ear-training question and send the first gtruth
async def gtruth1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text
    logger.info("ability of %s: %s", user.first_name, update.message.text)

    ability = ability_mapping[text]

    try:
        df = pd.read_excel('./dataframe/user.xlsx')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['chat_id', 'answer', 'correct', 'credit', 'level'])

    # Check if the user has already submitted an answer     
    if chat_id in df['chat_id'].values:
        df.loc[df['chat_id'] == chat_id, 'answer'] = ability
        df.loc[df['chat_id'] == chat_id, ['correct', 'credit', 'level']] = 0
        await update.message.reply_text('Your answer has been updated.')

    else:
        # Append the new answer
        new_entry = pd.DataFrame([[chat_id, ability]], columns=['chat_id', 'answer'])
        df = pd.concat([df, new_entry], ignore_index=True)
        await update.message.reply_text('Thank you! Your answer has been recorded.')

    # Save the updated data
    df.to_excel('./dataframe/user.xlsx', index=False)
            

    await update.message.reply_text(
        "For each of these ground-truth tests check the instrument you recognized!",
        reply_markup=ReplyKeyboardRemove(),
    )

    reply_keyboard = [["Tar", "Ney", "Kamancheh"], ["Setar", "Santour"]]
    
    audio_file = open("./dataset/truth/track 1.mp3", "rb")
    await context.bot.send_audio(chat_id=chat_id, audio=audio_file)
    audio_file.close()
    
    await update.message.reply_text(
        "What instrument did you heared?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Instrument"
        ),
    )
    
    return GTRUTH1
    

async def gtruth2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text
    logger.info("ability of %s: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "Your answer has been recorded!",
        reply_markup=ReplyKeyboardRemove(),
    )

    answer = text=="Ney"
    df = pd.read_excel('./dataframe/user.xlsx')
    df.loc[df['chat_id'] == chat_id, 'correct'] = df.loc[df['chat_id'] == chat_id, 'correct'] + answer
    df.to_excel('./dataframe/user.xlsx', index=False)
    
    reply_keyboard = [["Tar", "Ney", "Kamancheh"], ["Setar", "Santour"]]

    audio_file = open("./dataset/truth/track 2.mp3", "rb")
    await context.bot.send_audio(chat_id=chat_id, audio=audio_file)
    audio_file.close()

    await update.message.reply_text(
        "What instrument did you heared?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Instrument"
        ),
    )
    
    return GTRUTH2    

async def gtruth3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text
    logger.info("ability of %s: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "Your answer has been recorded!",
        reply_markup=ReplyKeyboardRemove(),
    )

    answer = text=="Kamancheh"
    df = pd.read_excel('./dataframe/user.xlsx')
    df.loc[df['chat_id'] == chat_id, 'correct'] = df.loc[df['chat_id'] == chat_id, 'correct']+answer
    df.to_excel('./dataframe/user.xlsx', index=False)

    reply_keyboard = [["Tar", "Ney", "Kamancheh"], ["Setar", "Santour"]]

    audio_file = open("./dataset/truth/track 3.mp3", "rb")
    await context.bot.send_audio(chat_id=chat_id, audio=audio_file)
    audio_file.close()

    await update.message.reply_text(
        "What instrument did you heared?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Instrument"
        ),
    )
    
    return GTRUTH3


async def credit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text
    logger.info("ability of %s: %s", user.first_name, update.message.text)

    answer = text=="Tar"
    df = pd.read_excel('./dataframe/user.xlsx')
    df.loc[df['chat_id'] == chat_id, 'correct'] += answer

    # Updating the credit
    credit = (df[df['chat_id'] == chat_id]['correct'] + df[df['chat_id'] == chat_id]['answer']).values[0]
    df.loc[df['chat_id'] == chat_id, 'credit'] = credit

    if credit == 5: level = 3
    elif credit > 2: level = 2
    else: level = 1
    
    df.loc[df['chat_id'] == chat_id, 'level'] = level

    df.to_excel('./dataframe/user.xlsx', index=False)

           
    await update.message.reply_text(
        "Ground Truth tests are finished! \n\n"
        f"Your level is: {level}.\n\n"
        "To annotate a sample click on /annotate.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("ability of %s: %s", user.first_name, update.message.text)
    
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def annotate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    df = pd.read_excel('./dataframe/user.xlsx')

    if chat_id not in df['chat_id'].values:
        await update.message.reply_text(
            "You have not yet complited the Ground Truth tests.\n\n"
            "To do so please press /start."
        )
        return True

    level = df.loc[df['chat_id'] == chat_id, 'level'].values[0]

    # Load samples dataframe
    samples = pd.read_excel('./dataframe/samples.xlsx')

    # Filter on level
    filtered_samples = samples[samples['level'] <= level]

    # Filter on num_annotation
    filtered_samples = filtered_samples[filtered_samples['num_annotation'] == filtered_samples['num_annotation'].min()]

    # Return if there are no samples
    if filtered_samples.empty:
        await update.message.reply_text(
            "Sorry, currently there are no samples at this level.\n\n"
            "Please press /annotate later.",
            reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END
        
    # Choose a random sample from the filtered samples
    random_sample = filtered_samples.sample(n=1)
    sample_id = random_sample['sample_id'].values[0]

    # Send this sample
    audio_file = open(f"./dataset/samples/{sample_id}.mp3", "rb")
    await context.bot.send_audio(chat_id=chat_id, audio=audio_file)
    audio_file.close()

    reply_keyboard = [["No", "Yes"]]
    await update.message.reply_text(
        "Did you heared a *singer*?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Singer?"
        ),
        parse_mode='Markdown',
    )

    # Construct the list of instruments
    sample_instruments = random_sample.drop(columns=["sample_id", "level", "num_annotation", "singer"])
    instruments = sample_instruments.columns[sample_instruments.eq(1).any()].tolist()
    
    # Make the context
    context.user_data["sample_id"] = sample_id
    context.user_data["instruments"] = instruments
    context.user_data["annotations"] = basic_annotation
    context.user_data["last_instrument"] = "singer"

    if len(context.user_data["instruments"]) > 0:
        next_instrument = context.user_data["instruments"].pop(0)
        return instrument_mapping[next_instrument]
        
    
    return END_ANNOT



async def tar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Save the annotation in the context
    text = update.message.text
    context.user_data["annotations"][context.user_data["last_instrument"]] = text

    # Ask the tar annotation
    reply_keyboard = [["0", "1", "2"]]
    await update.message.reply_text(
        "How strong does the *tar* sound?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Tar?"
        ),
        parse_mode='Markdown',
    )

    # Update the last instruent
    context.user_data["last_instrument"] = "tar"

    # Continue the conversation to the next instrument
    if len(context.user_data["instruments"]) > 0:
        next_instrument = context.user_data["instruments"].pop(0)
        return instrument_mapping[next_instrument]
        
    return END_ANNOT



async def ney(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Save the annotation in the context
    text = update.message.text
    context.user_data["annotations"][context.user_data["last_instrument"]] = text

    # Ask the ney annotation
    reply_keyboard = [["0", "1", "2"]]
    await update.message.reply_text(
        "How strong does the *ney* sound?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Ney?"
        ),
        parse_mode='Markdown',
    )

    # Update the last instruent
    context.user_data["last_instrument"] = "ney"

    # Continue the conversation to the next instrument
    if len(context.user_data["instruments"]) > 0:
        next_instrument = context.user_data["instruments"].pop(0)
        return instrument_mapping[next_instrument]
        
    return END_ANNOT


async def setar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Save the annotation in the context
    text = update.message.text
    context.user_data["annotations"][context.user_data["last_instrument"]] = text

    # Ask the setar annotation
    reply_keyboard = [["0", "1", "2"]]
    await update.message.reply_text(
        "How strong does the *setar* sound?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Setar?"
        ),
        parse_mode='Markdown',
    )

    # Update the last instruent
    context.user_data["last_instrument"] = "Setar"

    # Continue the conversation to the next instrument
    if len(context.user_data["instruments"]) > 0:
        next_instrument = context.user_data["instruments"].pop(0)
        return instrument_mapping[next_instrument]
        
    return END_ANNOT


async def santour(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Save the annotation in the context
    text = update.message.text
    context.user_data["annotations"][context.user_data["last_instrument"]] = text

    # Ask the santour annotation
    reply_keyboard = [["0", "1", "2"]]
    await update.message.reply_text(
        "How strong does the *santour* sound?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Santour?"
        ),
        parse_mode='Markdown',
    )

    # Update the last instruent
    context.user_data["last_instrument"] = "santour"

    # Continue the conversation to the next instrument
    if len(context.user_data["instruments"]) > 0:
        next_instrument = context.user_data["instruments"].pop(0)
        return instrument_mapping[next_instrument]
        
    return END_ANNOT


async def kamancheh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Save the annotation in the context
    text = update.message.text
    context.user_data["annotations"][context.user_data["last_instrument"]] = text

    # Ask the kamancheh annotation
    reply_keyboard = [["0", "1", "2"]]
    await update.message.reply_text(
        "How strong does the *kamancheh* sound?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="kamancheh?"
        ),
        parse_mode='Markdown',
    )

    # Update the last instruent
    context.user_data["last_instrument"] = "kamancheh"

    # Continue the conversation to the next instrument
    if len(context.user_data["instruments"]) > 0:
        next_instrument = context.user_data["instruments"].pop(0)
        return instrument_mapping[next_instrument]
        
    return END_ANNOT


async def end_annotation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Save the annotation in the context
    text = update.message.text
    context.user_data["annotations"][context.user_data["last_instrument"]] = text

    # Add to the dataframe
    sample_id = context.user_data["sample_id"]
    chat_id = update.message.chat_id
    row = context.user_data["annotations"]
    
    # Convert every item to int
    row = {key: int(value) if key != 'singer' else value for key, value in row.items()}
    
    row.update({"sample_id": sample_id, "chat_id": chat_id})
    
    df = pd.read_excel('./dataframe/annotation.xlsx')
    df_row = pd.DataFrame([row])
    output = pd.concat([df, df_row], ignore_index=True)
    output.to_excel('./dataframe/annotation.xlsx', index=False)

    # Iterate an annotation
    samples = pd.read_excel('./dataframe/samples.xlsx')
    samples.loc[samples['sample_id'] == sample_id, 'num_annotation'] += 1
    samples.to_excel('./dataframe/samples.xlsx', index=False)
    
    
    # Finish replay
    await update.message.reply_text(
        "Thank  you for annotating this piece.",
        reply_markup=ReplyKeyboardRemove(),
    )

        
    return ConversationHandler.END


async def cancel_annotation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        "Bye! I hope we can talk again some day. Start another annotation by /annotate", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


# Main function
def main()-> None:

    app = ApplicationBuilder().token("6900009914:AAGomuchkUQ-hFQcVQLtK7E8gJXrRU4AwN0").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttonstart, pattern='^1$'))

    app.run_polling()

#if __name__ == "__main__":
#    main()



app = ApplicationBuilder().token("6900009914:AAGomuchkUQ-hFQcVQLtK7E8gJXrRU4AwN0").build()

conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ABILITY: [MessageHandler(filters.Regex("^(Low|Moderate|High)$"), gtruth1)],
            GTRUTH1: [MessageHandler(filters.Regex("^(Tar|Ney|Setar|Santour|Kamancheh)$"), gtruth2)],
            GTRUTH2: [MessageHandler(filters.Regex("^(Tar|Ney|Setar|Santour|Kamancheh)$"), gtruth3)],
            GTRUTH3: [MessageHandler(filters.Regex("^(Tar|Ney|Setar|Santour|Kamancheh)$"), credit)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


annotation_handler = ConversationHandler(
        entry_points=[CommandHandler("annotate", annotate)],
        states={
            TAR: [MessageHandler(filters.Regex("^(0|1|2|Yes|No)$"), tar)],
            NEY: [MessageHandler(filters.Regex("^(0|1|2|Yes|No)$"), ney)],
            SETAR: [MessageHandler(filters.Regex("^(0|1|2|Yes|No)$"), setar)],
            SANTOUR: [MessageHandler(filters.Regex("^(0|1|2|Yes|No)$"), santour)],
            KAMANCHEH: [MessageHandler(filters.Regex("^(0|1|2|Yes|No)$"), kamancheh)],
            END_ANNOT: [MessageHandler(filters.Regex("^(0|1|2|Yes|No)$"), end_annotation)],
        },
        fallbacks=[CommandHandler("cancel_annotation", cancel_annotation)],
    )

app.add_handler(conv_handler)
#app.add_handler(CommandHandler("annotate", annotate))
app.add_handler(annotation_handler)

app.run_polling()
updater.idle()
