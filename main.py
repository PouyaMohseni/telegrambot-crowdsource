from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import pandas as pd
import logging
import random
import asyncio


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

USER_PATH = './dataframe/user.xlsx'
ANNOTATION_PATH, ANNOTATION_SAMPLES_PATH = './dataframe/annotation.xlsx', './dataframe/annotation_samples.xlsx'
EMOTION_PATH, EMOTION_SAMPLES_PATH = './dataframe/emotion.xlsx', './dataframe/emotion_samples.xlsx'
TRUTH1_PATH, TRUTH2_PATH, TRUTH3_PATH = './dataset/truth/track 1.mp3', './dataset/truth/track 2.mp3', './dataset/truth/track 3.mp3'

ABILITY, GTRUTH1, GTRUTH2, GTRUTH3 = range(4)
INSTRUMENT, AVAZ, END_ANNOT = range(3)
FAMILIAR, LIKE, QUALITY, Q_REASON, EMOTION, END_LABEL = range(6)

all_instruments = ["singer", "tar", "ney", "setar", "santour", "kamancheh", "tonbak", "oud", "daf"]

farsi_instruments = {"singer": "آواز", "tar": "تار", "ney": "نی", "setar": "سه تار", "santour": "سنتور", "kamancheh": "کمانچه", "tonbak": "تنبک", "oud": "عود", "daf": "دف"}
ability_mapping = {"کم: آشنایی کمی با سازهای موسیقی دارم": 0,
            "متوسط: با تفاوت صوتی برخی از سازهای موسیقی آشنا هستم": 1,
            "زیاد: گوش موسیقی من آموزش‌دیده است": 2
    }
avaz_mapping = {"شعر و چه‌چه":3, "چه‌چه": 2, "شعر": 1, "وجود نداشت": 0}
familiar_mapping = {"آشنا نیست": 0, "تا حدودی آشناست": 1, "بسیار آشناست": 2}

basic_annotation = {instrument: -1 for instrument in all_instruments}

quality_examples_p = ["شفاف بود", "صدا واضح بود", "صدا قوی بود", "صدا پر بود", "نرم و شفاف بود", "بلند بود", "قدرت",
                    "وضوح", "شفاف", "نرمی", "واضح", "بلندبودن"]
quality_examples_n = ["نویزی بود", "خش داشت", "صدا ناواضح بود", "صدای محیط زیاد بود", "خشن بود", "دیستوردد بود", "کدر بود",
                      "صدا کم بود", "وضوح کم بود", "خشن", "دیستورد", "کدر", "نویز"]
quality_examples_m = ["نازک بود", "نازک", "صدا ترد بود"]

quality_example_mapping = {
    1: quality_examples_n,
    2: quality_examples_m + quality_examples_n,
    3: quality_examples_p + quality_examples_m + quality_examples_n,
    4: quality_examples_p + quality_examples_m,
    5: quality_examples_p,
}

# Start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:


    reply_keyboard = [ #راز به راست
            ["کم: آشنایی کمی با سازهای موسیقی دارم"],
            ["متوسط: با تفاوت صوتی برخی از سازهای موسیقی آشنا هستم"],
            ["زیاد: گوش موسیقی من آموزش‌دیده است"]
        ]

    await update.message.reply_text(
        "متشکریم! ❤️ همکاری شما کمک شایانی در راستای تحقق اهداف ذکر شده است. \n\n"
        "برای اطلاعات بیشتر، کانال @PemLab را دنبال کنید.\n"
        "برای توقف دکمه /cancel را فشار دهید."
    )

    await update.message.reply_text(
        "در ابتدا مهارت شنیداری موسیقی (Ear-training) شما بررسی میشود. \n\n"
        "گوش موسیقی شما چقدر قوی است؟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="سطح گوش موسيقی"
        ),
    )

    return ABILITY


# Handle the ear-training question and send the first gtruth
async def gtruth1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text
    ability = ability_mapping[text]

    try:
        df = pd.read_excel(USER_PATH)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['chat_id', 'name', 'answer', 'correct', 'credit', 'level', 'num_annotation'])

    # Check if the user has already submitted an answer     
    if chat_id in df['chat_id'].values:
        df.loc[df['chat_id'] == chat_id, 'answer'] = ability
        df.loc[df['chat_id'] == chat_id, ['correct', 'credit', 'level', 'num_annotation']] = 0
        await update.message.reply_text("متشکرم! پاسخ قبلی شما به روز رسانی شد.")

    else:
        # Append the new answer
        new_entry = pd.DataFrame([[chat_id, user.first_name, ability, 0, 0, 0, 0]], columns=['chat_id', 'name', 'answer', 'correct', 'credit', 'level', 'num_annotation'])
        df = pd.concat([df, new_entry], ignore_index=True)
        await update.message.reply_text('متشکرم!')

    # Save the updated data
    df.to_excel(USER_PATH, index=False)
            

    await update.message.reply_text(       
        "حال، برای بررسی مهارت‌های شنیداری شما، سه قطعه موسیقی پخش می‌شود. برای هر قطعه، از بین پنج ساز آورده‌شده در منوی پایین، سازی را که می‌شنوید، انتخاب نمایید.",

        reply_markup=ReplyKeyboardRemove(),
    )

    reply_keyboard = [["تار", "نی", "کمانچه", "عود"], ["سه تار", "سنتور", "تنبک", "دف"]]
    
    audio_file = open(TRUTH1_PATH, "rb")
    await context.bot.send_voice(chat_id=chat_id, voice=audio_file, caption="track 1")
    audio_file.close()
    
    await update.message.reply_text(
        "چه سازی شنیده شد؟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="ساز؟"
        ),
    )
    
    return GTRUTH1
    

async def gtruth2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text


    answer = 2*(text=="نی")
    df = pd.read_excel(USER_PATH)
    df.loc[df['chat_id'] == chat_id, 'correct'] = df.loc[df['chat_id'] == chat_id, 'correct'] + answer
    df.to_excel(USER_PATH, index=False)
    
    reply_keyboard = [["تار", "نی", "کمانچه", "عود"], ["سه تار", "سنتور", "تنبک", "دف"]]

    audio_file = open(TRUTH2_PATH, "rb")
    await context.bot.send_voice(chat_id=chat_id, voice=audio_file, caption="track 2")
    audio_file.close()

    await update.message.reply_text(
        "چه سازی شنیده شد؟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="ساز؟"
        ),
    )
    
    return GTRUTH2    

async def gtruth3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text


    answer = 2*(text=="کمانچه")
    df = pd.read_excel(USER_PATH)
    df.loc[df['chat_id'] == chat_id, 'correct'] = df.loc[df['chat_id'] == chat_id, 'correct'] + answer
    df.to_excel(USER_PATH, index=False)

    reply_keyboard = [["تار", "نی", "کمانچه", "عود"], ["سه تار", "سنتور", "تنبک", "دف"]]

    audio_file = open(TRUTH3_PATH, "rb")
    await context.bot.send_voice(chat_id=chat_id, voice=audio_file, caption="track 3")
    audio_file.close()

    await update.message.reply_text(
        "چه سازی شنیده شد؟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="ساز؟"
        ),
    )
    
    return GTRUTH3


async def credit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text

    answer = 2*(text=="تار")
    df = pd.read_excel(USER_PATH)
    df.loc[df['chat_id'] == chat_id, 'correct'] += answer

    # Updating the credit
    credit = df[df['chat_id'] == chat_id]['correct'].values[0] + df[df['chat_id'] == chat_id]['answer'].values[0]
    df.loc[df['chat_id'] == chat_id, 'credit'] = credit

    if credit == 8: level = 3
    elif credit >= 4: level = 2
    else: level = 1
    
    df.loc[df['chat_id'] == chat_id, 'level'] = level

    df.to_excel(USER_PATH, index=False)

    await update.message.reply_text(
            "بررسی مهارت های شنیداری شما پایان یافت\\. \n\n"
            f"سطح شما {level} می‌باشد\\.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='MarkdownV2',
            )
    
    if level>=2:
 
        await update.message.reply_text(
            "هر بار، یک قطعه پنج ثانیه‌ای ارسال می‌شود و احتمال حضور سازهای مختلف در این قطعه، پرسیده می‌شود\\. \n\n"
            "اگر صدای سازی را در قطعه نشنیدید، 0 را انتخاب کنید\\. \n"
            "در صورتیکه صدای ساز را شنیدید، بین 1، 2 و 3 بسته به پررنگی حضور صدای ساز، انتخاب کنید\\. \n\n"
            "در هنگامی که صدای خواننده در قطعه وجود داشته باشد، در مورد وجود یا عدم وجود چه‌چه نیز پرسیده می‌شود\\. \n\n"
            ">چه‌چه یا چَهچَهه \\(تحریر\\) نوعی زینت آوازی است که به وسیله آن خواننده، صدایی آهنگین و *بدون کلام* را تولید می‌ کند\\.\n"
            ">بنابر این تعریف، هر صوتی از خواننده که بدون کلام باشد *چه‌چه* است\\. \n\n"
            "اگر قسمت صوتی خواننده، حاوی کلام نبود و صرفا زینت آوازی بود، *چه‌چه* را انتخاب کرده\\. در غیر این صورت، *شعر* را انتخاب کنید\\. \n\n"
            "برای برچسب زدن قطعات /annotate را فشار دهید\\.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='MarkdownV2',
            )
    else:
        await update.message.reply_text(
            "هر بار، یک قطعه بیست ثانیه‌ای ارسال می‌شود و سوالاتی مانند آشنایی شما با قطعه، علاقه شما به آن، کیفیت صوتی‌اش و احساسات برانگیخته‌شده توسط قطعه، پرسیده می‌شود\\. \n\n"
            "برای برچسب زدن قطعات /label را فشار دهید\\.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='MarkdownV2',
        )


    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    
    await update.message.reply_text(
        "از مشارکت شما متشکریم!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def annotate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    df = pd.read_excel(USER_PATH)

    if chat_id not in df['chat_id'].values:
        await update.message.reply_text(
            "مهارت شنیداری شما بررسی نشده. برای ادامه /start را فشار دهید."
        )
        return True

    level = df.loc[df['chat_id'] == chat_id, 'level'].values[0]

    # Load samples dataframe
    samples = pd.read_excel(ANNOTATION_SAMPLES_PATH)

    # Filter on apply
    applied_samples = samples[samples['apply'] == 1]

    # Filter on level
    filtered_samples = applied_samples[applied_samples['level'] == level]

    # Filter on num_annotation
    filtered_samples = filtered_samples[filtered_samples['num_annotation'] == filtered_samples['num_annotation'].min()]

    # Return if there are no samples
    if filtered_samples.empty:
        if level >= 2:
            await update.message.reply_text(
                "متاسفانه هیچ قطعه ای در این سطح وجود ندارد. \n\n"
                "لطفا، بعدا با فشردن /annotate دوباره امتحان کنید.",
                reply_markup=ReplyKeyboardRemove()
            )
        
        else:
            await update.message.reply_text(
                "متاسفانه هیچ قطعه ای در این سطح وجود ندارد. \n\n"
                "لطفا، بعدا با فشردن /label دوباره امتحان کنید.",
                reply_markup=ReplyKeyboardRemove()
            )

        return ConversationHandler.END
        
    # Choose a random sample from the filtered samples
    random_sample = filtered_samples.sample(n=1)
    sample_id = random_sample['sample_id'].values[0]

    # Construct the list of instruments
    sample_instruments = random_sample.drop(columns=["sample_id", "apply", "level", "num_annotation"])
    instruments = sample_instruments.columns[sample_instruments.eq(1).any()].tolist()
    
    # Make the context
    context.user_data["sample_id"] = sample_id
    context.user_data["instruments"] = instruments
    context.user_data["annotations"] = basic_annotation.copy()

    mapped_instruments = [farsi_instruments[instrument] for instrument in instruments]
    instrument = context.user_data["instruments"].pop(0)
    context.user_data["last_instrument"] = instrument
    context.user_data['level'] = level

    # Send this sample
    audio_file = open(f"./dataset/annotation_samples/{sample_id}", "rb")
    await context.bot.send_voice(chat_id=chat_id, voice=audio_file)#, caption="#m"+sample_id.replace('-','_').replace('.mp3',''))
    audio_file.close()

    instrument_print =  "*" + "*، *".join(mapped_instruments[:-1]) + "* و *" + mapped_instruments[-1] + "*"
    await update.message.reply_text(
        f"در این قطعه حضور {instrument_print} محتمل است.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown',
    )

    if instrument=="singer":
        # Ask for singer annotation
        reply_keyboard = [["شعر"], ["چه‌چه"], ["شعر و چه‌چه"], ["وجود نداشت"]]
        await update.message.reply_text(
                "صدای *خواننده* چگونه بود؟",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, input_field_placeholder="خواننده؟"
                ),
                parse_mode='Markdown',
            )
        if len(context.user_data["instruments"]) > 0:
            next_instrument = context.user_data["instruments"].pop(0)
            context.user_data["next_instrument"] = next_instrument
            return INSTRUMENT
            
        
        return END_ANNOT 
    
            
    else:
        # Ask the instrument annotation
        reply_keyboard = [["0", "1", "2", "3"]]
        await update.message.reply_text(
            f"چقدر اطمینان دارید که ساز *{farsi_instruments[instrument]}* در قطعه حضور دارد؟\n"
            "(3=بیشترین اطمینان حضور/ 0=اطمینان از عدم حضور)",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=f"{farsi_instruments[instrument]}؟"
            ),
            parse_mode='Markdown',
        )

        if len(context.user_data["instruments"]) > 0:
            next_instrument = context.user_data["instruments"].pop(0)
            context.user_data["next_instrument"] = next_instrument
            return INSTRUMENT
            
        
        return END_ANNOT

'''
async def avaz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    context.user_data["annotations"][context.user_data["last_instrument"]] = text

    if text == "بله":
        reply_keyboard = [["چه‌چه", "شعر", "غیرقابل تشخیص"]]
        await update.message.reply_text(
            "آواز به صورت چه‌چه بود یا شعر؟",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="نوع آواز?"
            ),
            parse_mode='Markdown',
        )

    # context.user_data["last_instrument"] = instrument last instrument doesnt change

    # Save the annotation in the context
    if len(context.user_data["instruments"]) > 0:
        next_instrument = context.user_data["instruments"].pop(0)
        context.user_data["next_instrument"] = next_instrument
        return INSTRUMENT
        
    
    return END_ANNOT
'''



async def instrument(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Save the annotation in the context
    instrument = context.user_data["next_instrument"]
    text = update.message.text
    if context.user_data["last_instrument"] == "singer": text = avaz_mapping[text] # Map if the text is from avaz
    context.user_data["annotations"][context.user_data["last_instrument"]] = text

    # Ask the kamancheh annotation 
    reply_keyboard = [["0", "1", "2", "3"]]
    await update.message.reply_text(
        f"چقدر اطمینان دارید که ساز *{farsi_instruments[instrument]}* در قطعه حضور دارد؟\n"
        "(3=بیشترین اطمینان حضور/ 0=اطمینان از عدم حضور)",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=f"{farsi_instruments[instrument]}؟"
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
    level = context.user_data["level"] 

    # Convert every item to int
    row = {key: int(value) if key != 'singer' else value for key, value in row.items()}
    row_new = {"sample_id": sample_id, "chat_id": chat_id, "level": level}
    row_new.update(row)
    
    df = pd.read_excel(ANNOTATION_PATH)
    df.loc[len(df)] = row_new
    df.to_excel(ANNOTATION_PATH, index=False)

    # Itelabel an annotation
    samples = pd.read_excel(ANNOTATION_SAMPLES_PATH)
    samples.loc[samples['sample_id'] == sample_id, 'num_annotation'] += 1
    samples.to_excel(ANNOTATION_SAMPLES_PATH, index=False)
    

    df = pd.read_excel(USER_PATH)
    df.loc[df['chat_id'] == chat_id, 'num_annotation'] += 1
    df.to_excel(USER_PATH, index=False)

    # Finish replay
    await update.message.reply_text(
        "✅ برچسب زنی این قطعه پایان یافت. بسیار متشکریم!\n\n"
        "اگر در برچسب‌زنی این قطعه اشتباه کردید و می‌خواهید نظرتان را حذف کنید،\n" 
        f"`#m{sample_id.replace('-','_').replace('.mp3','')}`"
        "\n"
        "را ارسال کنید.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown',
    )
    await update.message.reply_text(
        "برای برچسب‌زنی يک قطعه ديگر /annotate را فشار دهيد.",
        reply_markup=ReplyKeyboardRemove(),
    )
        
    return ConversationHandler.END



async def cancel_annotation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        "با فشردن /annotate یک قطعه دیگر را برچسب‌زنی کنید.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END





async def label(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    df = pd.read_excel(USER_PATH)

    if chat_id not in df['chat_id'].values:
        await update.message.reply_text(
            "مهارت شنیداری شما بررسی نشده. برای ادامه /start را فشار دهید."
        )
        return True

    level = df.loc[df['chat_id'] == chat_id, 'level'].values[0]

    # Load samples dataframe
    samples = pd.read_excel(EMOTION_SAMPLES_PATH)

    # Filter on apply
    applied_samples = samples[samples['apply'] == 1]
    
    # Filter on level
    filtered_samples = applied_samples[applied_samples['level'] <= level]

    # Filter on num_annotation
    filtered_samples = filtered_samples[filtered_samples['num_annotation'] == filtered_samples['num_annotation'].min()]

    # Return if there are no samples
    if filtered_samples.empty:
        if level >= 2:
            await update.message.reply_text(
                "متاسفانه هیچ قطعه ای در این سطح وجود ندارد. \n\n"
                "لطفا، بعدا با فشردن /annotate دوباره امتحان کنید.",
                reply_markup=ReplyKeyboardRemove()
            )

            return ConversationHandler.END
        
        else:
            await update.message.reply_text(
                "متاسفانه هیچ قطعه ای در این سطح وجود ندارد. \n\n"
                "لطفا، بعدا با فشردن /label دوباره امتحان کنید.",
                reply_markup=ReplyKeyboardRemove()
            )

            return ConversationHandler.END
        
    # Choose a random sample from the filtered samples
    random_sample = filtered_samples.sample(n=1)
    sample_id = random_sample['sample_id'].values[0]

    # Send this sample
    audio_file = open(f"./dataset/emotion_samples/{sample_id}", "rb")
    await context.bot.send_voice(chat_id=chat_id, voice=audio_file)#, caption="#e"+sample_id.replace('-','_').replace('.mp3',''))
    audio_file.close()
    
    # Make a user context
    context.user_data["label"] = {"familiar": -1, "like": -1, "quality": -1, "q_reason": -1, "Q1": -1, "Q2": -1, "Q3": -1, "Q4": -1}
    context.user_data["Q"] = ["Q1", "Q2", "Q3", "Q4"]
    context.user_data["emotion_text"] = ["شادی، قدرت یا شگفتی", "تنش، خشم یا ترس", "غم یا تلخی", "آرامش، لطافت یا تعالی"]
    context.user_data["sample_id"] = sample_id
    context.user_data["level"] = level

    # Ask for 'familiar' annotation
    reply_keyboard = [["آشنا نیست"], ["تا حدودی آشناست"], ["بسیار آشناست"]]
    await update.message.reply_text(
            "این قطعه برای شما چقدر آشناست؟",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="آشنایی؟"
            ),
            parse_mode='Markdown',
        )
    
    
    return FAMILIAR


async def familiar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Recieve familiar label
    text = update.message.text
    mapped_text = familiar_mapping[text]

    # Add to the context
    context.user_data["label"]["familiar"] = mapped_text

    # Ask for 'like' annotation
    reply_keyboard = [["1", "2", "3", "4", "5"]]
    await update.message.reply_text(
            "چقدر این قطعه را دوست دارید؟ (5=بیشترین)",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="علاقه؟"
            ),
            parse_mode='Markdown',
        )
    
    return LIKE


async def like(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Recieve familiar label
    text = update.message.text
    mapped_text = int(text)

    # Add to the context
    context.user_data["label"]["like"] = mapped_text

    # Ask for 'quality' annotation
    reply_keyboard = [["1", "2", "3", "4", "5"]]
    await update.message.reply_text(
            "به کیفیت این قطعه چه امتیازی می دهید؟ (5=بیشترین)",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="کیفیت؟"
            ),
            parse_mode='Markdown',
        )
    
    return QUALITY


async def quality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Recieve familiar label
    text = update.message.text
    mapped_text = int(text)

    # Add to the context
    context.user_data["label"]["quality"] = mapped_text

    # Make quality space and random reply 
    random_reply = random.sample(quality_example_mapping[mapped_text], 3)
    
    # Ask for 'q_reason' annotation
    await update.message.reply_text(
            f"در یک کلمه، عبارت یا جمله، دلیلتان را برای انتخاب {text} از 5 برای *کیفیت قطعه* بنویسید. (تایپ کنید) ",
            reply_markup=ForceReply(
                input_field_placeholder=f"مثال: {random_reply[0]}، {random_reply[1]}، {random_reply[2]} یا ..."[:64]
            ),
            parse_mode='Markdown',
        )
    
    return Q_REASON


async def q_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Recieve familiar label
    text = update.message.text
    mapped_text = text

    # Add to the context
    context.user_data["label"]["q_reason"] = mapped_text

    # Ask for 'emotion' annotation
    emotion_text_out = context.user_data["emotion_text"].pop(0)
    reply_keyboard = [["0%", "20%", "40%", "60%", "80%", "100%"]]
    await update.message.reply_text(
            f"شدت احساسات *{emotion_text_out}* در این قطعه چقدر بود؟\n (100%=بیشترین / 0%=عدم برانگیختگی این احساس)",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=f"{emotion_text_out}؟"
            ),
            parse_mode='Markdown',
        )
    
    return EMOTION


async def emotion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Recieve Q label
    text = update.message.text
    mapped_text = int(text[:-1])/100

    # Add to the context
    context.user_data["label"][context.user_data["Q"].pop(0)] = mapped_text
    
    # Ask for 'emotion' annotation
    emotion_text_out = context.user_data["emotion_text"].pop(0)
    reply_keyboard = [["0%", "20%", "40%", "60%", "80%", "100%"]]
    await update.message.reply_text(
            f"شدت احساسات *{emotion_text_out}* در این قطعه چقدر بود؟\n (100%=بیشترین / 0%=عدم برانگیختگی این احساس)",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=f"{emotion_text_out}؟"
            ),
            parse_mode='Markdown',
        )

    if len(context.user_data["emotion_text"]) > 0:
        return EMOTION
    
    return END_LABEL
    

async def end_label(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Recieve Q label
    text = update.message.text
    mapped_text = int(text[:-1])/100


    # Add to the context
    context.user_data["label"][context.user_data["Q"].pop(0)] = mapped_text

    # Add to the dataframe
    sample_id = context.user_data["sample_id"]
    level = context.user_data["level"] 
    chat_id = update.message.chat_id

    row = context.user_data["label"]
    row_new = {"sample_id": sample_id, "chat_id": chat_id, "level": level}
    row_new.update(row)


    df = pd.read_excel(EMOTION_PATH)
    df.loc[len(df)] = row_new
    df.to_excel(EMOTION_PATH, index=False)
    
    
    # Iterate an annotation
    samples = pd.read_excel(EMOTION_SAMPLES_PATH)
    samples.loc[samples['sample_id'] == sample_id, 'num_annotation'] += 1
    samples.to_excel(EMOTION_SAMPLES_PATH, index=False)
    

    df = pd.read_excel(USER_PATH)
    df.loc[df['chat_id'] == chat_id, 'num_annotation'] += 1
    df.to_excel(USER_PATH, index=False)

    # Finish replay
    await update.message.reply_text(
        "✅ برچسب زنی این قطعه پایان یافت. بسیار متشکریم!\n\n"
        "اگر در برچسب‌زنی این قطعه اشتباه کردید و می‌خواهید نظرتان را حذف کنید،\n" 
        f"`#e{sample_id.replace('-','_').replace('.mp3','')}`"
        "\n"
        "را ارسال کنید.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown',
    )
    await update.message.reply_text(
        "برای برچسب‌زنی يک قطعه ديگر /label را فشار دهيد.",
        reply_markup=ReplyKeyboardRemove(),
    )
        
    return ConversationHandler.END


async def cancel_label(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        "با فشردن /label یک قطعه دیگر را برچسب زنی کنید.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message_text = update.message.text
    chat_id = update.message.chat_id

    # Process hashtag messages
    if '#' in message_text[0]:
        sample_id = message_text[2:].replace('_', '-')+".mp3"
        if message_text[1]=="m": dataframe_path, samples_path = ANNOTATION_PATH, ANNOTATION_SAMPLES_PATH 
        else: dataframe_path, samples_path = EMOTION_PATH, EMOTION_SAMPLES_PATH
        
        # Read the dataframe
        df = pd.read_excel(dataframe_path)
  
        # Find the first row with the matching sample_id and chat_id
        row_to_delete = df[(df['sample_id'] == sample_id) & (df['chat_id'] == chat_id)].index

        if not row_to_delete.empty:
            # Drop the first matching row from the DataFrame
            df.drop(row_to_delete[0], inplace=True)

            # Save the updated DataFrame back to the Excel file
            df.to_excel(dataframe_path, index=False)

            # Re-iterate an annotation
            samples = pd.read_excel(samples_path)
            samples.loc[samples['sample_id'] == sample_id, 'num_annotation'] -= 1
            samples.to_excel(samples_path, index=False)
            
            await update.message.reply_text(
                "برچسب این قطعه حذف شد.",
                reply_markup=ReplyKeyboardRemove(),
            )
            
        else:
            await update.message.reply_text(
                    "برچسبی از طرف شما برای این قطعه وجود ندارد.",
                    reply_markup=ReplyKeyboardRemove(),
                )
            
    # Preserved output
    df = pd.read_excel(USER_PATH)

    if chat_id not in df['chat_id'].values:
        await update.message.reply_text(
            "مهارت شنیداری شما بررسی نشده. برای ادامه /start را فشار دهید."
        )
        return True

    level = df.loc[df['chat_id'] == chat_id, 'level'].values[0]

    if level >= 2:
        await update.message.reply_text(
            "با فشردن /annotate یک قطعه دیگر را برچسب‌زنی کنید.",
            reply_markup=ReplyKeyboardRemove()
        )
            
    else:
        await update.message.reply_text(
            "با فشردن /label یک قطعه دیگر را برچسب‌زنی کنید.",
            reply_markup=ReplyKeyboardRemove()
        )

    return True

# Main function
def main()-> None:

    app = ApplicationBuilder().token("#TOKEN").build()

    conv_handler = ConversationHandler(
            entry_points = [CommandHandler("start", start)],
            states={
                ABILITY: [MessageHandler(filters.Regex("^(کم: آشنایی کمی با سازهای موسیقی دارم|متوسط: با تفاوت صوتی برخی از سازهای موسیقی آشنا هستم|زیاد: گوش موسیقی من آموزش‌دیده است)$"), gtruth1)],
                GTRUTH1: [MessageHandler(filters.Regex("^(تار|نی|سه تار|کمانچه|سنتور|تنبک|عود|دف)$"), gtruth2)],
                GTRUTH2: [MessageHandler(filters.Regex("^(تار|نی|سه تار|کمانچه|سنتور|تنبک|عود|دف)$"), gtruth3)],
                GTRUTH3: [MessageHandler(filters.Regex("^(تار|نی|سه تار|کمانچه|سنتور|تنبک|عود|دف)$"), credit)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
    

    annotation_handler = ConversationHandler(
            entry_points=[CommandHandler("annotate", annotate)],
            states={
                INSTRUMENT: [MessageHandler(filters.Regex("^(0|1|2|3|شعر و چه‌چه|وجود نداشت|شعر|چه‌چه)$"), instrument)],
                END_ANNOT: [MessageHandler(filters.Regex("^(0|1|2|3|وجود نداشت|شعر و چه‌چه|شعر|چه‌چه)$"), end_annotation)],
            },
            fallbacks=[CommandHandler("cancel_annotation", cancel_annotation)],
        )
    
    label_handler = ConversationHandler(
            entry_points=[CommandHandler("label", label)],
            states={
                FAMILIAR: [MessageHandler(filters.Regex("^(آشنا نیست|تا حدودی آشناست|بسیار آشناست)$"), familiar)],
                LIKE: [MessageHandler(filters.Regex("^(1|2|3|4|5)$"), like)],
                QUALITY: [MessageHandler(filters.Regex("^(1|2|3|4|5)$"), quality)],
                Q_REASON: [MessageHandler(filters.ALL, q_reason)],
                EMOTION: [MessageHandler(filters.Regex("^(0%|20%|40%|60%|80%|100%)$"), emotion)],
                END_LABEL: [MessageHandler(filters.Regex("^(0%|20%|40%|60%|80%|100%)$"), end_label)],
            },
            fallbacks=[CommandHandler("cancel_label", cancel_label)],
        )
    
    app.add_handler(conv_handler)
    app.add_handler(annotation_handler)
    app.add_handler(label_handler)
    app.add_handler(MessageHandler(filters.Regex(r"^(?!\/).*"), handle_message))

    app.run_polling()




if __name__ == "__main__":
    asyncio.run(main())



