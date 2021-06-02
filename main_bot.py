import logging

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
from tempfile import NamedTemporaryFile

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
CLEAR,
HELP) = map(chr, range(14))

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> str:
    text = ("Hai saya neuRoute! 🤖\n\n"
        "Selamat datang di Aplikasi Pencari Rute Destinasi Terpendek!\n"
        "Jika ada kesulitan silahkan pilih tombol HELP!")
    if not context.user_data.get(RESULT):
        context.user_data[RESULT] = TSP()

    buttons = [
        [
            InlineKeyboardButton(text='Add Your Location', callback_data=str(ADDING_SELF)),
            InlineKeyboardButton(text='Add Destination', callback_data=str(ADDING_OTHER)),
        ],
        [
            InlineKeyboardButton(text='Selected Destination', callback_data=str(SHOW)),
            InlineKeyboardButton(text='Reset Destination', callback_data=str(CHOOSE_CLEAR)),
        ],
        [
            InlineKeyboardButton(text='Show neuRoute!', callback_data=str(GENERATE)),
        ],
        [
            InlineKeyboardButton(text='Help', callback_data=str(HELP)),
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

def adding_again(update: Update, _: CallbackContext) -> str:
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
    text = (
        "Tambahkan lokasi kamu saat ini!\n"
        "(Attach > Location > Send My Current Location)"
    )

    context.user_data[ADDING_SELF] = True
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return ADDING_LOC

def adding_other(update: Update, context: CallbackContext) -> str:
    text = (
        "Tambahkan lokasi destinasi kamu!\n"
        "(Attach > Location > Pilih Destinasi Kamu)"
    )
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return ADDING_LOC

def add_location(update: Update, context: CallbackContext) -> str:
    cek_self = context.user_data.get(ADDING_SELF)
    res = update.message
    loc = res.location
    ltd, lng = loc.latitude, loc.longitude
    
    text = None

    if cek_self:
        context.user_data[RESULT].add_curr((ltd, lng))
        context.user_data[ADDING_SELF] = False
        text = "Sip, lokasi kamu berhasil ditambahkan! 👍"
    else:
        venue = res.venue
        if venue:
            title = venue.title
            addr = venue.address
            context.user_data[RESULT].add_node(title, (ltd, lng))
            text = f"{title}, {addr}\n\nMantab! Berhasil ditambahkan! 👍"
        else:
            text = "Kamu tidak dapat menambahkan lokasi kamu saat ini sebagai destinasi wisata"
    
    update.message.reply_text(text)

    if cek_self:    
        return start(update,context)
    else:
        return adding_again(update, context)

def show_selected(update: Update, context: CallbackContext) -> str:
    res = context.user_data.get(RESULT)
    daftar_lokasi = res.daftar_lokasi

    text = "====Destinasi Kamu===="

    if len(daftar_lokasi) == 1:
        if daftar_lokasi[0]:
            text = "Selamat... lokasi kamu saat ini sudah ditambahkan\nTapi belum ada destinasi yang dipilih nih!"
        else:
            text = "Oppsss... 🤭\nKamu belum menambahkan lokasi apapun!"
    else:
        for i, destinasi in enumerate(daftar_lokasi[1:], 1):
            text += f"\n{i}.{destinasi['nama']}"
        
        if daftar_lokasi[0]:
            text += "\n\nYeay.... Kamu juga sudah menambahkan lokasi kamu saat ini!"
        else:
            text += "\n\nYahhh... tapi kamu belum menambahkan lokasi kamu saat ini!"
    
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
    
    update.callback_query.answer()
    text = None
    if mincost:
        path = " --> ".join(mincost[0])
        jarak = round(mincost[1],2)

        text = (
            f"Jalur terpendek\n: {path}\n\n" + 
            f"Jarak yang harus ditempuh sekitar {jarak} meter")

        path = NamedTemporaryFile(dir="figure", suffix=".png").name
        
        with NamedTemporaryFile(dir="figure", suffix=".png") as tmpfile:
            result.show_result(tmpfile)
            # result.show_graf(tmpfile)
            tmpfile.seek(0)
            update.callback_query.delete_message()
            update.callback_query.bot.send_photo(chat_id=update.effective_chat.id, photo=tmpfile)
            
    else:
        text = "Kamu belum menambahkan lokasi kamu atau belum pernah menambahkan destinasi wisata.\n\nKamu dapat mengecek dengan tombol SELECTED DESTINATION"

    buttons = [
        [
            InlineKeyboardButton(text='Done', callback_data=str(DONE)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.bot.send_message(chat_id=update.effective_chat.id, text=text)

    update.callback_query.bot.send_message(chat_id=update.effective_chat.id, text="Back to Menu", reply_markup=keyboard)

    return SELECTING_ACTION

def validate_clear(update: Update, _: CallbackContext) -> str:
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
    del context.user_data[RESULT]
    context.user_data[RESULT] = TSP()
    text = "Seluruh pilihan kamu berhasil dihapus!"
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return start(update, context)

def stop(update: Update, context: CallbackContext) -> str:
    """End Conversation by command."""
    text = "Terima kasih sudah menggunakan neuRoute! 😁"
    
    if update.callback_query:
        update.callback_query.answer()

        update.callback_query.edit_message_text(text=text)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return END

def helper(update: Update, context: CallbackContext) -> str:

    text = (
        "1. Add Your Location : menambahkan lokasi kamu saat ini.\n\n"
        "2. Add Destination : menambahkan destinasi yang akan dituju.\n\n"
        "3. Selected Destination : melihat destinasi yang sudah ditambahkan.\n\n"
        "4. Reset Destination : menghapus semua lokasi yang sudah ditambahkan.\n\n"
        "5. Show neuRoute! : menampilkan rute destinasi terpendek.\n\n"
        "6. Help : menampilkan menu bantuan.\n\n"
        "7. Exit : keluar dari bot neuRoute."
    )

    buttons = [
        [
            InlineKeyboardButton(text='Done', callback_data=str(DONE)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_ACTION

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("1744180713:AAHDm1MzCQ5pqAmp4a6EpzdL_9Apie7dt48")

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
        CallbackQueryHandler(stop, pattern='^' + str(EXIT) + '$'),
        CallbackQueryHandler(helper, pattern='^' + str(HELP) + '$')
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION : selection_handler,
            ADDING_LOC: [MessageHandler(Filters.location, add_location)],
            END: [CommandHandler('start', start)]
        },
        fallbacks=[
            CommandHandler('stop', stop)
        ],
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