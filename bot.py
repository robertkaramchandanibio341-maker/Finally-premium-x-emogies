from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging
import re
import json
import os
import threading
import random
from datetime import datetime
from flask import Flask

# ========== FLASK APP (Render Health Check) ==========
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "✅ Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ========== LOGGING ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== CONFIG ==========
BOT_TOKEN = "8977192256:AAF2K-fbWOtJYCKHlmw40LojIZyKnVsRPcg"
OWNER_ID = 8586849798
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
EMOJI_FILE = "emojis.json"

# ========== PREMIUM EMOJIS ==========
PREMIUM_EMOJIS = {
    "verified": {"id": "6147565374289220368", "fallback": "✅", "added_by": "system", "date": "2024-01-01"},
    "flex": {"id": "6147464060305676048", "fallback": "😎", "added_by": "system", "date": "2024-01-01"},
    "blue_verification": {"id": "6147524086768604985", "fallback": "💎", "added_by": "system", "date": "2024-01-01"},
    "frozen": {"id": "5449449325434266744", "fallback": "❄️", "added_by": "system", "date": "2024-01-01"},
    "crying": {"id": "6273840152980755328", "fallback": "😭", "added_by": "system", "date": "2024-01-01"},
    "smiling": {"id": "6276057176444246654", "fallback": "🙂", "added_by": "system", "date": "2024-01-01"},
    "seeing_up": {"id": "6273997026661241933", "fallback": "😋", "added_by": "system", "date": "2024-01-01"},
    "teeth": {"id": "6273726078649372769", "fallback": "😁", "added_by": "system", "date": "2024-01-01"},
    "done": {"id": "6274007313107915274", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "blue_badge": {"id": "5978776771623914876", "fallback": "🟫", "added_by": "system", "date": "2024-01-01"},
    "black_badge": {"id": "5978686323907628843", "fallback": "🔸", "added_by": "system", "date": "2024-01-01"},
    "busy_tag": {"id": "5852873584912896283", "fallback": "🟧", "added_by": "system", "date": "2024-01-01"},
    "instagram": {"id": "5895297528106061174", "fallback": "🌐", "added_by": "system", "date": "2024-01-01"},
    "telegram": {"id": "5895735846698487922", "fallback": "🌐", "added_by": "system", "date": "2024-01-01"},
    "whatsapp": {"id": "5895343514320899727", "fallback": "🌐", "added_by": "system", "date": "2024-01-01"},
    "india": {"id": "5913754823643107921", "fallback": "🇮🇳", "added_by": "system", "date": "2024-01-01"},
    "dollar": {"id": "5197434882321567830", "fallback": "💵", "added_by": "system", "date": "2024-01-01"},
    "top": {"id": "5463071033256848094", "fallback": "🔝", "added_by": "system", "date": "2024-01-01"},
    "bro": {"id": "5463256910851546817", "fallback": "🤝", "added_by": "system", "date": "2024-01-01"},
    "yes": {"id": "5463423955014529788", "fallback": "👌", "added_by": "system", "date": "2024-01-01"},
    "lock": {"id": "5465443379917629504", "fallback": "🔓", "added_by": "system", "date": "2024-01-01"},
    "good": {"id": "5465465194056525619", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "sigma": {"id": "6235620067942341623", "fallback": "🥃", "added_by": "system", "date": "2024-01-01"},
    "don": {"id": "6235717714023814969", "fallback": "🍂", "added_by": "system", "date": "2024-01-01"},
    "skills": {"id": "6235593671073339928", "fallback": "💀", "added_by": "system", "date": "2024-01-01"},
    "heart": {"id": "6147617184479711380", "fallback": "❤️‍🔥", "added_by": "system", "date": "2024-01-01"},
    "stars": {"id": "6235403472741603087", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "github": {"id": "5346181118884331907", "fallback": "📱", "added_by": "system", "date": "2024-01-01"},
    "motion": {"id": "5971944878815317190", "fallback": "💠", "added_by": "system", "date": "2024-01-01"},
}

user_data_store = {}

# ========== EMOJI HELPER FUNCTIONS ==========
def save_emojis():
    try:
        with open(EMOJI_FILE, 'w', encoding='utf-8') as f:
            json.dump(PREMIUM_EMOJIS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving emojis: {e}")

def load_emojis():
    global PREMIUM_EMOJIS
    try:
        if os.path.exists(EMOJI_FILE):
            with open(EMOJI_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                for key, value in loaded.items():
                    if key not in PREMIUM_EMOJIS:
                        PREMIUM_EMOJIS[key] = value
                logger.info(f"Loaded {len(loaded)} emojis")
    except Exception as e:
        logger.error(f"Error loading emojis: {e}")

def get_emoji_html(name):
    if name in PREMIUM_EMOJIS:
        data = PREMIUM_EMOJIS[name]
        return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>'
    return ""

def get_random_emoji():
    """Random premium emoji do (left aur right ke liye alag alag)"""
    names = list(PREMIUM_EMOJIS.keys())
    if not names:
        return "😎"
    random_name = random.choice(names)
    return get_emoji_html(random_name)

def format_with_double_emojis(text):
    """
    Har line ke AAGE ek random premium emoji lagayega
    Har line ke PICCHE ek alag random premium emoji lagayega
    """
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():
            # Aage wala emoji - random
            left_emoji = get_random_emoji()
            # Piche wala emoji - alag random
            right_emoji = get_random_emoji()
            # Line ke aage aur piche emoji daal diye
            formatted_lines.append(f"{left_emoji} {line} {right_emoji}")
        else:
            # Empty line ko same rakho
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

# ========== USER MANAGEMENT ==========
def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    return {}
    except:
        pass
    return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except:
        pass

def load_banned():
    try:
        if os.path.exists(BANNED_FILE):
            with open(BANNED_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    return set(data.keys())
                else:
                    return set()
    except:
        pass
    return set()

def save_banned(banned_set):
    try:
        with open(BANNED_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(banned_set), f, ensure_ascii=False, indent=2)
    except:
        pass

def register_user(user_id, username, name):
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {
            "id": user_id,
            "username": username,
            "name": name,
            "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(users)
        logger.info(f"New user: {user_id} (@{username})")

def is_banned(user_id):
    banned = load_banned()
    return str(user_id) in banned

# ========== /emojify COMMAND ==========
async def emojify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /emojify (emoji_name) your text\n\nExample: /emojify (verified) how are you")
        return
    
    full_text = update.message.text
    if full_text.startswith('/emojify'):
        full_text = full_text[8:].strip()
    
    if not full_text:
        await update.message.reply_text("❌ Please provide text")
        return
    
    lines = full_text.split('\n')
    processed_lines = []
    
    for line in lines:
        if not line.strip():
            processed_lines.append('')
            continue
        
        def replace_emoji(match):
            emoji_name = match.group(1).lower().strip()
            emoji_html = get_emoji_html(emoji_name)
            if emoji_html:
                return emoji_html
            return match.group(0)
        
        processed_line = re.sub(r'\(([^)]+)\)', replace_emoji, line)
        processed_lines.append(processed_line)
    
    result = '\n'.join(processed_lines)
    
    if not result.strip():
        await update.message.reply_text("❌ No valid emoji found. Use /ads")
        return
    
    await update.message.reply_text(result, parse_mode="HTML")

# ========== OWNER PANEL COMMANDS ==========
async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied! Only bot owner can use this panel.")
        return
    
    users = load_users()
    banned = load_banned()
    total_users = len(users)
    banned_count = len(banned)
    
    msg = f"""OWNER PANEL

📊 Statistics
━━━━━━━━━━━━━━━━━━
• Total Users: {total_users}
• Banned Users: {banned_count}
• Active Users: {total_users - banned_count}
━━━━━━━━━━━━━━━━━━

👑 Owner Commands
• /users - List all users
• /ban <user_id> - Ban a user
• /unban <user_id> - Unban a user
• /stats - Show statistics
• /owner - Show this panel

━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_double_emojis(msg)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    users = load_users()
    if not users:
        await update.message.reply_text("📭 No users found.")
        return
    
    banned = load_banned()
    msg = "📋 USER LIST\n━━━━━━━━━━━━━━━━━━\n"
    for uid, data in users.items():
        status = "🚫 Banned" if uid in banned else "✅ Active"
        username = data.get("username", "No username")
        name = data.get("name", "Unknown")
        msg += f"🆔 {uid} | @{username} | {name} | {status}\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
    
    formatted_msg = format_with_double_emojis(msg)
    
    if len(formatted_msg) > 4000:
        await update.message.reply_text(f"Total users: {len(users)}\nUse /stats for details\n\nDeveloper: @iflexvenom")
    else:
        await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban USER_ID")
        return
    
    try:
        target_id = str(context.args[0])
        if int(target_id) == OWNER_ID:
            await update.message.reply_text("❌ Cannot ban the owner!")
            return
        
        banned = load_banned()
        banned.add(target_id)
        save_banned(banned)
        msg = f"✅ User {target_id} has been banned.\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
        formatted_msg = format_with_double_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban USER_ID")
        return
    
    try:
        target_id = str(context.args[0])
        banned = load_banned()
        if target_id in banned:
            banned.remove(target_id)
            save_banned(banned)
            msg = f"✅ User {target_id} has been unbanned.\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_double_emojis(msg)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
        else:
            await update.message.reply_text(f"❌ User {target_id} is not banned.")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    users = load_users()
    banned = load_banned()
    msg = f"""📊 BOT STATISTICS
━━━━━━━━━━━━━━━━━━
• Total Users: {len(users)}
• Banned Users: {len(banned)}
• Active Users: {len(users) - len(banned)}
━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_double_emojis(msg)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

# ========== REGULAR COMMANDS ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    name = update.effective_user.first_name or "User"
    
    register_user(user_id, username, name)
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned from using this bot.")
        return
    
    msg = """Premium Emoji Bot

Commands:
• /emojify (emoji) text - Add emoji around text
• /ads - See all emojis
• /myemojis - Your added emojis
• /addemoji - Add new emoji
• /help - Help

Examples:
/emojify (verified) how are you

━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_double_emojis(msg)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def ads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    emoji_list = []
    for name, data in PREMIUM_EMOJIS.items():
        emoji_html = get_emoji_html(name)
        added_by = data.get("added_by", "system")
        emoji_list.append(f"{emoji_html} {name} (by {added_by})")
    
    content = f"Available Premium Emojis ({len(PREMIUM_EMOJIS)})\n\n" + "\n".join(emoji_list) + f"\n\nUsage: /emojify (verified) your text\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
    
    formatted_msg = format_with_double_emojis(content)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def myemojis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    user_name = update.effective_user.username or update.effective_user.first_name
    
    user_emojis = []
    for name, data in PREMIUM_EMOJIS.items():
        if data.get("added_by", "").lower() == str(user_id).lower() or data.get("added_by", "") == user_name:
            emoji_html = get_emoji_html(name)
            date = data.get("date", "Unknown")
            user_emojis.append(f"{emoji_html} {name} (added: {date})")
    
    if user_emojis:
        content = f"Your Added Emojis ({len(user_emojis)})\n\n" + "\n".join(user_emojis) + f"\n\nUse /addemoji to add more emojis\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
        formatted_msg = format_with_double_emojis(content)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
    else:
        content = f"❌ You haven't added any emojis yet!\n\nUse /addemoji to add your first emoji\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
        formatted_msg = format_with_double_emojis(content)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    content = """Help Guide

Commands:
• /start - Start the bot
• /emojify (emoji) text - Add emoji around your text
• /ads - Show ALL available emojis
• /myemojis - Show emojis YOU added
• /addemoji - Add new custom emoji
• /help - Show this help

Owner Commands (Owner only):
• /owner - Owner panel
• /users - List all users
• /ban USER_ID - Ban user
• /unban USER_ID - Unban user
• /stats - Bot statistics

Examples:
/emojify (verified) how are you

━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_double_emojis(content)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def addemoji_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    user_data_store[user_id] = {"step": "waiting_emoji_name", "user_name": update.effective_user.username or update.effective_user.first_name}
    
    content = f"➕ Adding New Emoji\n\nStep 1: Send the emoji name (no spaces, use underscore)\nExample: fire_emoji or cool_badge\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
    formatted_msg = format_with_double_emojis(content)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied! Only owner can broadcast.")
        return
    
    content = f"""📢 Broadcast Setup

Step 1: Send the text you want to broadcast
Include emoji names in parentheses like (verified)

Example: Welcome to our channel (verified)

━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_double_emojis(content)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")
    
    user_data_store[user_id] = {"step": "waiting_text"}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    if user_id not in user_data_store:
        return
    
    step = user_data_store[user_id].get("step")
    
    if step == "waiting_emoji_name":
        emoji_name = update.message.text.strip().lower()
        
        if ' ' in emoji_name:
            await update.message.reply_text("❌ Emoji name cannot contain spaces. Use underscore (_). Send again:")
            return
        
        if emoji_name in PREMIUM_EMOJIS:
            await update.message.reply_text(f"❌ Emoji name '{emoji_name}' already exists! Choose a different name:")
            return
        
        user_data_store[user_id]["emoji_name"] = emoji_name
        user_data_store[user_id]["step"] = "waiting_emoji_data"
        
        content = f"✅ Emoji name: {emoji_name}\n\nStep 2: Now send the emoji ID (or forward a message with custom emoji)\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
        formatted_msg = format_with_double_emojis(content)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
    
    elif step == "waiting_emoji_data":
        emoji_name = user_data_store[user_id]["emoji_name"]
        message_text = update.message.text or ""
        
        emoji_id = None
        fallback_text = None
        
        if update.message.forward_from_message_id:
            lines = message_text.split('\n')
            for line in lines:
                if "Custom Emoji ID:" in line:
                    parts = line.split("Custom Emoji ID:")
                    if len(parts) > 1:
                        emoji_id = parts[1].strip()
                        break
        
        if not emoji_id:
            if message_text.isdigit():
                emoji_id = message_text
                fallback_text = "?"
            else:
                match = re.search(r'(\d{10,})', message_text)
                if match:
                    emoji_id = match.group(1)
                    fallback_text = "?"
        
        if emoji_id:
            if not fallback_text or fallback_text == "?":
                content = f"✅ Emoji ID: {emoji_id}\n\nPlease send the fallback emoji character:\nExample: 🔥 or ⭐\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
                formatted_msg = format_with_double_emojis(content)
                await update.message.reply_text(formatted_msg, parse_mode="HTML")
                user_data_store[user_id]["emoji_id"] = emoji_id
                user_data_store[user_id]["step"] = "waiting_fallback"
                return
            
            user_name = user_data_store[user_id].get("user_name", str(user_id))
            
            PREMIUM_EMOJIS[emoji_name] = {
                "id": emoji_id,
                "fallback": fallback_text,
                "added_by": user_name,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            save_emojis()
            
            del user_data_store[user_id]
            
            content = f"✅ Emoji '{emoji_name}' added successfully!\n\nAdded to global emoji list!\nAdded by: {user_name}\nUse: /emojify ({emoji_name}) your text\n\nEveryone can now use '{emoji_name}' emoji!\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
        else:
            content = f"❌ Could not extract emoji ID!\nPlease send a valid emoji ID or forward a message with custom emoji.\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
    
    elif step == "waiting_fallback":
        fallback_text = update.message.text.strip()
        emoji_name = user_data_store[user_id]["emoji_name"]
        emoji_id = user_data_store[user_id]["emoji_id"]
        user_name = user_data_store[user_id].get("user_name", str(user_id))
        
        PREMIUM_EMOJIS[emoji_name] = {
            "id": emoji_id,
            "fallback": fallback_text,
            "added_by": user_name,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        save_emojis()
        
        del user_data_store[user_id]
        
        content = f"✅ Emoji '{emoji_name}' added successfully!\n\nAdded to global emoji list!\nAdded by: {user_name}\nUse: /emojify ({emoji_name}) your text\n\nEveryone can now use '{emoji_name}' emoji!\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
        formatted_msg = format_with_double_emojis(content)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
    
    elif step == "waiting_text":
        text = update.message.text
        user_data_store[user_id]["text"] = text
        user_data_store[user_id]["step"] = "waiting_channel"
        
        def preview_replace(match):
            emoji_name = match.group(1).lower().strip()
            emoji_html = get_emoji_html(emoji_name)
            if emoji_html:
                return emoji_html
            return match.group(0)
        
        preview_text = re.sub(r'\(([^)]+)\)', preview_replace, text)
        
        try:
            preview_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=preview_text,
                parse_mode="HTML"
            )
            
            user_data_store[user_id]["preview_msg_id"] = preview_msg.message_id
            
            content = f"✅ Text received!\n\nAbove is how it will look ↑\n\nStep 2: Now send the channel username (with @)\nExample: @yourchannel\n\n⚠️ You must be admin in that channel\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            
        except Exception as e:
            content = f"❌ Error: {str(e)}\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            del user_data_store[user_id]
    
    elif step == "waiting_channel":
        channel = update.message.text.strip()
        
        if not channel.startswith("@"):
            content = f"❌ Please send channel username starting with @\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            return
        
        is_admin = await is_admin_in_channel(context, user_id, channel)
        
        if not is_admin:
            content = f"❌ Access Denied!\n\nYou are not an admin in {channel}\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            del user_data_store[user_id]
            return
        
        user_data_store[user_id]["channel"] = channel
        user_data_store[user_id]["step"] = "confirm"
        
        content = f"✅ Admin Verified!\n\n📢 Channel: {channel}\n✅ Send CONFIRM to broadcast\n❌ Send CANCEL to abort\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
        formatted_msg = format_with_double_emojis(content)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
    
    elif step == "confirm":
        response = update.message.text.upper()
        
        if response == "CONFIRM":
            try:
                channel = user_data_store[user_id]["channel"]
                preview_msg_id = user_data_store[user_id].get("preview_msg_id")
                chat_id = update.effective_chat.id
                
                await context.bot.forward_message(
                    chat_id=channel,
                    from_chat_id=chat_id,
                    message_id=preview_msg_id,
                    disable_notification=True
                )
                
                content = f"✅ Broadcast successful!\n\n📢 Sent to: {channel}\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
                formatted_msg = format_with_double_emojis(content)
                await update.message.reply_text(formatted_msg, parse_mode="HTML")
                
            except Exception as e:
                content = f"❌ Error: {str(e)}\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
                formatted_msg = format_with_double_emojis(content)
                await update.message.reply_text(formatted_msg, parse_mode="HTML")
            
            del user_data_store[user_id]
        
        elif response == "CANCEL":
            del user_data_store[user_id]
            content = f"❌ Broadcast cancelled\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
        
        else:
            content = f"Please send CONFIRM or CANCEL\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def is_admin_in_channel(context, user_id, channel_username):
    try:
        chat = await context.bot.get_chat(chat_id=channel_username)
        chat_member = await context.bot.get_chat_member(chat_id=chat.id, user_id=user_id)
        return chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception as e:
        logger.error(f"Error checking admin: {e}")
        return False

# ========== MAIN ==========
def main():
    # Delete corrupted users file if exists
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    os.remove(USERS_FILE)
                    print("Removed corrupted users.json file")
        except:
            pass
    
    load_emojis()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Owner commands
    application.add_handler(CommandHandler("owner", owner_panel))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("emojify", emojify_command))
    application.add_handler(CommandHandler("ads", ads_command))
    application.add_handler(CommandHandler("myemojis", myemojis_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("addemoji", addemoji_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("=" * 50)
    print("🤖 Premium Emoji Bot Starting...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print("✅ Har line ke AAGE aur PICCHE random premium emoji lagega")
    print("=" * 50)
    
    # Start Flask in background (for Render)
    threading.Thread(target=run_flask, daemon=True).start()
    
    application.run_polling()

if __name__ == "__main__":
    main()
