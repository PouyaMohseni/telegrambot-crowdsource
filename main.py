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
INSTRUMENT, END_ANNOT = range(2)

all_instruments = ["tar", "ney", "setar", "santour", "kamancheh"]

ability_mapping = {
            "کم: آشنایی کمی با سازهای موسیقی دارم": 0,
            "متوسط: با تفاوت های بعضی از سازهای موسیقی آشنا هستم": 1,
            "زیاد: گوش موسیقی من آموزش دیده است": 2
    }
basic_annotation = {instrument: -1 for instrument in all_instruments}


# Start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    reply_keyboard = [
            ["کم: آشنایی کمی با سازهای موسیقی دارم"],
            ["متوسط: با تفاوت های بعضی از سازهای موسیقی آشنا هستم"],
            ["زیاد: گوش موسیقی من آموزش دیده است"]
        ]

    await update.message.reply_text(
        "به آزمايشگاه موسيثي سنتي ايراني خوش آمديد. "
        "برای توقف دکمه /cancel را فشار دهید \n\n"
        "در ابتدا مهارت شنیداری موسیقی (Ear-training) شما بررسی میشود. \n\n"
        "چقدر گوش موسیقی شما آموزش دیده است؟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="سطح گوش موسيقي"
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
        await update.message.reply_text('متشکرم! پاسخ قبلي شما به روز رساني شد.')

    else:
        # Append the new answer
        new_entry = pd.DataFrame([[chat_id, ability]], columns=['chat_id', 'answer'])
        df = pd.concat([df, new_entry], ignore_index=True)
        await update.message.reply_text('متشکرم! پاسخ شما ذخيره شد.')

    # Save the updated data
    df.to_excel('./dataframe/user.xlsx', index=False)
            

    await update.message.reply_text(       
        "حال، در ادامه بررسی مهارت های شنیداری شما سه قطعه موسیقی برای شما پخش میشود. شما باید برای هر قطعه، از بین پنج ساز آورده شده در منوی پایینی، سازی که میشنوید را انتخاب کنید.",
        reply_markup=ReplyKeyboardRemove(),
    )

    reply_keyboard = [["Tar", "Ney", "Kamancheh"], ["Setar", "Santour"]]
    
    audio_file = open("./dataset/truth/track 1.mp3", "rb")
    await context.bot.send_audio(chat_id=chat_id, audio=audio_file)
    audio_file.close()
    
    await update.message.reply_text(
        "صداي چه سازي را شنيديد؟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="ساز؟"
        ),
    )
    
    return GTRUTH1
    

async def gtruth2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text
    logger.info("ability of %s: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "پاسخ شما ذخيره شد.",
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
        "صداي چه سازي را شنيديد؟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="ساز؟"
        ),
    )
    
    return GTRUTH2    

async def gtruth3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text
    logger.info("ability of %s: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "پاسخ شما ذخيره شد.",
        reply_markup=ReplyKeyboardRemove(),
    )

    answer = text=="Kamancheh"
    df = pd.read_excel('./dataframe/user.xlsx')
    df.loc[df['chat_id'] == chat_id, 'correct'] = df.loc[df['chat_id'] == chat_id, 'correct'] + answer
    df.to_excel('./dataframe/user.xlsx', index=False)

    reply_keyboard = [["Tar", "Ney", "Kamancheh"], ["Setar", "Santour"]]

    audio_file = open("./dataset/truth/track 3.mp3", "rb")
    await context.bot.send_audio(chat_id=chat_id, audio=audio_file)
    audio_file.close()

    await update.message.reply_text(
        "صداي چه سازي را شنيديد؟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="ساز؟"
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

           
    await update.message.reply_text("بررسی مهارت های شنیداری شما پایان یافت. \n\n"
        f"سطح شما {level} مي باشد. \n\n"
        "برای برچسب زدن قطعات /annotate را فشار دهید",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("ability of %s: %s", user.first_name, update.message.text)
    
    await update.message.reply_text(
        "از مشاکرت شما متشکريم.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def annotate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    df = pd.read_excel('./dataframe/user.xlsx')

    if chat_id not in df['chat_id'].values:
        await update.message.reply_text(
            "مهارت شنیداری شما بررسی نشده. برای ادامه /start را فشار دهید."
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
            "متاسفانه هیچ قطعه ای در این سطح وجود ندارد. \n\n"
            "لطفا، بعدا با فشردن /annotate دوباره امتحان کنید.",
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
        "آيا قطعه *خواننده* داشت؟",
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
        context.user_data["next_instrument"] = next_instrument
        return INSTRUMENT
        
    
    return END_ANNOT


async def instrument(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Save the annotation in the context
    instrument = context.user_data["next_instrument"]
    text = update.message.text
    context.user_data["annotations"][context.user_data["last_instrument"]] = text

    # Ask the kamancheh annotation
    reply_keyboard = [["0", "1", "2"]]
    await update.message.reply_text(
        f"صدای *{instrument}* در قطعه چقدر قوی بود؟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=f"{instrument}?"
        ),
        parse_mode='Markdown',
    )

    # Update the last instruent
    context.user_data["last_instrument"] = instrument

    # Continue the conversation to the next instrument
    if len(context.user_data["instruments"]) > 0:
        next_instrument = context.user_data["instruments"].pop(0)
        context.user_data["next_instrument"] = next_instrument
        return INSTRUMENT
        
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
        "برچسب زني اين قطعه پايان يافت. بسيار متشکريم!"
        "براي برچسب زني يک قطعه ديگر /annotate را فشار دهيد.",
        reply_markup=ReplyKeyboardRemove(),
    )
        
    return ConversationHandler.END



async def cancel_annotation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        "با فشردن /annotate یک قطعه دیگر را برچسب زنی کنید.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END



# Main function
def main()-> None:

    app = ApplicationBuilder().token("6900009914:AAGomuchkUQ-hFQcVQLtK7E8gJXrRU4AwN0").build()

    conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                ABILITY: [MessageHandler(filters.Regex("^(کم: آشنایی کمی با سازهای موسیقی دارم|متوسط: با تفاوت های بعضی از سازهای موسیقی آشنا هستم|زیاد: گوش موسیقی من آموزش دیده است)$"), gtruth1)],
                GTRUTH1: [MessageHandler(filters.Regex("^(Tar|Ney|Setar|Santour|Kamancheh)$"), gtruth2)],
                GTRUTH2: [MessageHandler(filters.Regex("^(Tar|Ney|Setar|Santour|Kamancheh)$"), gtruth3)],
                GTRUTH3: [MessageHandler(filters.Regex("^(Tar|Ney|Setar|Santour|Kamancheh)$"), credit)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )


    annotation_handler = ConversationHandler(
            entry_points=[CommandHandler("annotate", annotate)],
            states={
                INSTRUMENT: [MessageHandler(filters.Regex("^(0|1|2|Yes|No)$"), instrument)],
                END_ANNOT: [MessageHandler(filters.Regex("^(0|1|2|Yes|No)$"), end_annotation)],
            },
            fallbacks=[CommandHandler("cancel_annotation", cancel_annotation)],
        )

    app.add_handler(conv_handler)
    app.add_handler(annotation_handler)

    app.run_polling()
    updater.idle()




if __name__ == "__main__":
    main()

