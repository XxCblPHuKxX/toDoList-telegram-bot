import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

DB_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tasks():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

tasks = load_tasks()
user_state = {}

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Add task", callback_data="add")],
        [InlineKeyboardButton("Show list", callback_data="list")],
        [InlineKeyboardButton("Delete task", callback_data="delete")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I`m the toDo list bot", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if query.data == "add":
        user_state[user_id] = "adding"
        await query.message.reply_text("Write a task which you want to add:")

    elif query.data == "list":
        task_list = tasks.get(user_id, [])
        if not task_list:
            await query.message.reply_text("Task list is empty.")
        else:
            response = "\n".join(f"{i+1}. {t}" for i, t in enumerate(task_list))
            await query.message.reply_text(response)

    elif query.data == "delete":
        task_list = tasks.get(user_id, [])
        if not task_list:
            await query.message.reply_text("Task list is empty.")
        else:
            user_state[user_id] = "deleting"
            await query.message.reply_text("Send the number of a task you want to delete:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    state = user_state.get(user_id)

    if state == "adding":
        tasks.setdefault(user_id, []).append(update.message.text)
        save_tasks()
        user_state[user_id] = None
        await update.message.reply_text("Task successfuly added!", reply_markup=get_main_menu())

    elif state == "deleting":
        try:
            index = int(update.message.text) - 1
            removed = tasks[user_id].pop(index)
            save_tasks()
            user_state[user_id] = None
            await update.message.reply_text(f"Deleted: {removed}", reply_markup=get_main_menu())
        except:
            await update.message.reply_text("Error. Please write the number of task you want to delete correctly.")
    else:
        await update.message.reply_text("Choose an action in the menu:", reply_markup=get_main_menu())

app = ApplicationBuilder().token("here is a bot token from the @BotFather in telegram").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()
