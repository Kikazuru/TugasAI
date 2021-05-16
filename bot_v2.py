import logging
from typing import Text

from ShortDest import TSP

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

(ADDING_SELF,
ADDING_OTHER,
ADDING_LOC,
SHOW,
CHOOSE_CLEAR,
END,
DONE,
SELECTING_ACTION,
STOPPING,
RESULT,
EXIT,
GENERATE,
CLEAR) = map(chr, range(13))

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> str:
    text = "Selamat datang di Bot Kami! :)"
    if not context.user_data.get(RESULT):
        context.user_data[RESULT] = TSP()

    buttons = [
        [
            InlineKeyboardButton(text='Add Your Location', callback_data=str(ADDING_SELF)),
            InlineKeyboardButton(text='Add destination', callback_data=str(ADDING_OTHER)),
        ],
        [
            InlineKeyboardButton(text='Show destination', callback_data=str(SHOW)),
            InlineKeyboardButton(text='Clear All Destiation', callback_data=str(CHOOSE_CLEAR)),
        ],
        [
            InlineKeyboardButton(text='Generate', callback_data=str(GENERATE)),
            InlineKeyboardButton(text='Exit', callback_data=str(EXIT))
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    return SELECTING_ACTION

def adding_again(update: Update, context: CallbackContext) -> str:
    text = "Tambah destinasi lagi?"
    buttons = [
        [
            InlineKeyboardButton(text='Add again', callback_data=str(ADDING_OTHER)),
            InlineKeyboardButton(text='Done', callback_data=str(DONE)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text=text, reply_markup=keyboard)
    
    return SELECTING_ACTION

def adding_self(update: Update, context: CallbackContext) -> str:
    text = "Tambahkan lokasi anda saat ini"
    context.user_data[ADDING_SELF] = True
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return ADDING_LOC

def adding_other(update: Update, context: CallbackContext) -> str:
    text = "Tambahkan lokasi destinasi anda"
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return ADDING_LOC

def add_location(update: Update, context: CallbackContext) -> str:
    cek_self = context.user_data[ADDING_SELF]
    res = update.message
    loc = res.location
    ltd, lng = loc.latitude, loc.longitude
    
    text = None

    if cek_self:
        context.user_data[RESULT].add_curr((ltd, lng))
        context.user_data[ADDING_SELF] = False
        text = "Lokasi anda berhasil ditambahkan!"
    else:
        venue = res.venue
        title = venue.title
        addr = venue.address
        context.user_data[RESULT].add_node(title, (ltd, lng))
        text = f"{title}, {addr}\nBerhasil ditambahkan!"
    
    update.message.reply_text(text)

    if cek_self:    
        return start(update,context)
    else:
        return adding_again(update, context)

def show_selected(update: Update, context: CallbackContext) -> str:
    res = context.user_data.get(RESULT)
    daftar_lokasi = res.daftar_lokasi

    text = "====Destinasi Anda===="

    if len(daftar_lokasi) == 1:
        if daftar_lokasi[0]:
            text = "Anda sudah menambahkan lokasi anda.\nNamun belum ada destinasi yang dipilih!"
        else:
            text = "Anda belum menambahkan lokasi apapun!"
    else:
        for i, destinasi in enumerate(daftar_lokasi[1:], 1):
            text += f"\n{i}.{destinasi['nama']}"
        
        if daftar_lokasi[0]:
            text += "\n\nAnda sudah menambahkan lokasi anda saat ini :)"
        else:
            text += "\n\nAnda belum menambahkan lokasi anda saat ini!"
    
    buttons = [
        [
            InlineKeyboardButton(text='Done', callback_data=str(DONE)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_ACTION

def generate_result(update: Update, context: CallbackContext) -> str:
    result = context.user_data[RESULT]
    result.generate_graf()
    mincost = result.solve()
    
    text = None
    if mincost:
        path = " --> ".join(mincost[0])
        jarak = round(mincost[1],2)

        text = (
            f"Jalur terpendek\n: {path}\n\n" + 
            f"Jarak yang harus ditempuh sekitar {jarak} meter")
        result.show_graf()
    else:
        text = "Anda belum menambahkan lokasi anda atau belum pernah menambahkan destinasi wisata.\n\nAnda dapat mengecek dengan tombol SHOW DESTINATION :)"

    buttons = [
        [
            InlineKeyboardButton(text='Done', callback_data=str(DONE)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_ACTION

def validate_clear(update: Update, context: CallbackContext) -> str:
    text = "SELURUH PILIHAN LOKASI ANDA AKAN DIHAPUS!"

    buttons = [
        [
            InlineKeyboardButton(text='YES', callback_data=str(CLEAR)),
            InlineKeyboardButton(text='Cancel', callback_data=str(DONE)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_ACTION

def clear(update: Update, context: CallbackContext) -> str:
    context.user_data[RESULT] = TSP()
    text = "Seluruh pilihan anda berhasil dihapus!"
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return start(update, context)

def stop(update: Update, _: CallbackContext) -> str:
    """End Conversation by command."""
    update.callback_query.answer()

    update.callback_query.edit_message_text(text="Terima kasih :)")

    return END

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("1807137142:AAF0o7ZpqHhnP17b_AL-B5NLIYqbayAbVLM")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    selection_handler = [
        CallbackQueryHandler(adding_self, pattern='^' + str(ADDING_SELF) + '$'),
        CallbackQueryHandler(adding_other, pattern='^' + str(ADDING_OTHER) + '$'),
        CallbackQueryHandler(start, pattern='^' + str(DONE) + '$'),
        CallbackQueryHandler(show_selected, pattern='^' + str(SHOW) + '$'),
        CallbackQueryHandler(validate_clear, pattern='^' + str(CHOOSE_CLEAR) + '$'),
        CallbackQueryHandler(clear, pattern='^' + str(CLEAR) + '$'),
        CallbackQueryHandler(generate_result, pattern='^' + str(GENERATE) + '$'),
        CallbackQueryHandler(stop, pattern='^' + str(EXIT) + '$')
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION : selection_handler,
            ADDING_LOC: [MessageHandler(Filters.location, add_location)],
            END: [CommandHandler('start', start)]
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()