import telegram
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,CallbackQueryHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup
import logging
import sqlite3
from tabulate import tabulate

bot=telegram.Bot(token='Token')
updater = Updater(token='Token')
connection = sqlite3.connect('userDetails.db',check_same_thread=False)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

#Function to start the bot,initiated on /start command
def start(bot,update):
    bot.send_message(chat_id=update.message.chat_id, text='Hi, I am pizza order bot')

#Function to ask user its details to register,initiated on /register command
def register(bot,update):
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id,text='Enter your details in the following format : '
                                                         'Name, Address, Phone number')

def database(user_id,customer_name,address,phone_number):
    print(user_id,customer_name,address,phone_number)
    connection.execute('''CREATE TABLE IF NOT EXISTS userdetails(user_id int,customer_name text,address text,phone_number int )''')
    connection.execute("INSERT INTO userdetails VALUES (?,?,?,?)",(user_id,customer_name,address,phone_number))
    connection.commit()

#Function to save user details in the database
def saveuserDetails(bot,update):
    user_id=update.message.from_user.id
    customer_name,address,phone_number=update.message.text.split(',')
    database(user_id,customer_name,address,phone_number)

 #Function to ask user about type of pizza he wants to order
def pizzatype(bot,update):
    reply_markup = telegram.ReplyKeyboardRemove()

    print("message sent by user",update.message.text)
    if update.message.text == 'Veg':
        vegpizzaoptions(bot,update)
    elif update.message.text =='Non Veg':
        nonvegpizzaoptions(bot,update)

def vegpizzaoptions(bot,update):
    print("inside vegpizaa method")
    #button_labels = connection.execute("SELECT name from pizza_details where type=='VEG'")
    for row in connection.execute("SELECT name from pizza_details where type=='VEG'"):
     print(row)
    #print("Button labesl ",button_labels)
    #button_list=[InlineKeyboardButton(button_labels,callback_data=1)]
    #reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=len(button_labels)))
    #update.message.reply_text("Please choose from the following : ",reply_markup=reply_markup)
    #bot.send_message(chat_id=update.message.chat_id, text='Choose from the following',reply_markup=reply_markup)

def nonvegpizzaoptions(bot,update):
    for row in connection.execute("SELECT name from pizza_details where type=='NonVeg'"):
     button_labels = row
    print("Button Labels", button_labels)
    button_list=[
            InlineKeyboardButton('Cheese Chicken ',callback_data=1),
            InlineKeyboardButton('Mushroom Chicken ',callback_data=2)]
    reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=2))
    #update.message.reply_text("Please choose from the following : ",reply_markup=reply_markup)
    bot.send_message(chat_id=update.message.chat_id, text='Choose from the following',reply_markup=reply_markup)

#Function to cancel the order by text
def cancelorder(bot,update):
    cancel_order_list=['Cancel my order','I dont want this order','Cancel it','Don\'t feel hungry now' ]
    for text in cancel_order_list:
     if update.message.text.lower()==text.lower():
      bot.send_message(chat_id=update.message.chat_id, text='Your order has been cancelled')

# Function to check the userdetails initiated by user on /checkdetails command
def checkDetails(bot,update):
    value = update.message.from_user.id
    print("VALUE : ", value)
    for row in connection.execute("SELECT *from userdetails WHERE user_id=?", (value,)):
        print(row)
        user_id, customer_name, address, phone_number = row
    labels=["Customer Name : ","Address : ","Phone Number : "]
    data=[customer_name, address, phone_number]
    table=zip(labels,data)
    list=tabulate(table,tablefmt="fancy_grid")
    bot.send_message(chat_id=update.message.chat_id,text=list)

#FUNCTION FOR ORDERING PIZZA
def orderpizza(bot,update):
    button_labels = [['Veg'], ['Non Veg']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id,text='Which type of pizza you want',reply_markup=reply_keyboard)

def button(bot,update):
    query=update.callback_query
    bot.send_chat_action(chat_id=update.effective_user.id,action=telegram.ChatAction.TYPING)
    bot.edit_message_text(text="Your order is received and will be delivered within 30 mins",chat_id=query.message.chat_id,message_id=query.message.message_id)

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def offers():
    connection.execute('SELECT offers from offerTable')

def main():
    updater.dispatcher.add_handler(CommandHandler('start',start))
    updater.dispatcher.add_handler(CommandHandler('register',register))
    updater.dispatcher.add_handler(CommandHandler('checkdetails',checkDetails))
    updater.dispatcher.add_handler(CommandHandler('order',orderpizza))
    updater.dispatcher.add_handler(CommandHandler('offers',offers))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, saveuserDetails),group=0)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, pizzatype),group=1)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, cancelorder),group=2)
    updater.dispatcher.add_handler((CallbackQueryHandler(button)))
    updater.start_polling()

main()

