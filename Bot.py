import telegram
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,CallbackQueryHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup
import logging
import sqlite3
from tabulate import tabulate

bot=telegram.Bot(token='597548004:AAHRnEhZ8nuFUnxCBV9XKcPHBaHcU-lbOW4')
print(bot.get_me())
updater = Updater(token='597548004:AAHRnEhZ8nuFUnxCBV9XKcPHBaHcU-lbOW4')

connection = sqlite3.connect('userDetails.db',check_same_thread=False)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

#Function to start the bot,initiated on /start command
def start(bot,update):
    bot.send_message(chat_id=update.message.chat_id, text='Hi, I am pizza order bot')

#Function to ask user its details to register,initiated on /register command
def register(bot,update):
    bot.send_message(chat_id=update.message.chat_id,text='Enter your details in the following format : '
                                                         'Name, Address, Phone number, Credit Card number')


def database(update,user_id,customer_name,address,phone_number,creditcard_number):
    print(user_id,customer_name,address,phone_number,creditcard_number)
    connection.execute('''CREATE TABLE IF NOT EXISTS userdetails(user_id int,customer_name text,address text,phone_number int,creditcard_details int )''')
    connection.execute("INSERT INTO userdetails VALUES (?,?,?,?,?)",(user_id,customer_name,address,phone_number,creditcard_number))
    connection.commit()
    
#Function to save user details in the database
def saveuserDetails(bot,update):
    print("INSIDE GETUSER ID FUNCTION")
    user_id=update.message.from_user.id
    customer_name,address,phone_number,creditcard_number=update.message.text.split(',')
    database(update,user_id,customer_name,address,phone_number,creditcard_number)

#Function to check the userdetails initiated by user on /checkdetails command
def checkDetails(bot,update):
    value = update.message.from_user.id
    print("VALUE : ", value)
    for row in connection.execute("SELECT *from userdetails WHERE user_id=?", (value,)):
        print(row)
        user_id, customer_name, address, phone_number, creditcard_number = row
    labels=["Customer Name : ","Address : ","Phone Number : ","Credit Card Details : "]
    data=[customer_name, address, phone_number, creditcard_number]
    table=zip(labels,data)
    list=tabulate(table,tablefmt="fancy_grid")
    bot.send_message(chat_id=update.message.chat_id,text=list)

'''
def showuserDetails(bot,update):
    value=update.message.from_user.id
    for row in connection.execute("SELECT *from userdetails WHERE user_id=?",(value,)):
        print(row)
        user_id, customer_name, address, phone_number, creditcard_number=row
    bot.send_message(chat_id=update.message.chat_id,text=["Customer Name : ",customer_name,"Address : ",address,"PhoneNumber : ",phone_number,
                                                          "Credit Card Details : ",creditcard_number])
'''

#FUNCTION FOR ORDERING PIZZA
def pizza(bot,update):
    button_list=[
        InlineKeyboardButton('Cheese Pizza',callback_data=1),
        InlineKeyboardButton('Mushroom Pizza',callback_data=2)
    ]
    reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=2))
    #update.message.reply_text("Please choose from the following : ",reply_markup=reply_markup)
    bot.send_message(chat_id=update.message.chat_id, text='Choose from the following',reply_markup=reply_markup)


def button(bot,update):
    query=update.callback_query
    bot.edit_message_text(text="Your order is recieved and will be delivered within 30 mins",chat_id=query.message.chat_id,message_id=query.message.message_id)

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def main():
    updater.dispatcher.add_handler(CommandHandler('start',start))
    updater.dispatcher.add_handler(CommandHandler('register',register))
    updater.dispatcher.add_handler((MessageHandler(Filters.text, saveuserDetails)))
    updater.dispatcher.add_handler(CommandHandler('checkdetails',checkDetails))
    updater.dispatcher.add_handler(CommandHandler('order',pizza))
   #updater.dispatcher.add_handler(CommandHandler('userdetails',showuserDetails))
    updater.dispatcher.add_handler((CallbackQueryHandler(button)))
    updater.start_polling()

main()

