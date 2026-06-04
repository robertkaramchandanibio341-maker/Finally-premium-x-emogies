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
import asyncio

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
ACTIVITY_FILE = "activity.json"
BROADCAST_FILE = "broadcasts.json"

# ========== PREMIUM EMOJIS (ONLY) ==========
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

# ========== EXTRA PREMIUM EMOJIS (additional) ==========
EXTRA_PREMIUM_EMOJIS = {
    "fire": {"id": "6147524086768604985", "fallback": "🔥", "added_by": "system", "date": "2024-01-01"},
    "crown": {"id": "6147565374289220368", "fallback": "👑", "added_by": "system", "date": "2024-01-01"},
    "rocket": {"id": "6147464060305676048", "fallback": "🚀", "added_by": "system", "date": "2024-01-01"},
    "lightning": {"id": "5971944878815317190", "fallback": "⚡", "added_by": "system", "date": "2024-01-01"},
    "cross": {"id": "6273840152980755328", "fallback": "❌", "added_by": "system", "date": "2024-01-01"},
    "check": {"id": "6274007313107915274", "fallback": "✔️", "added_by": "system", "date": "2024-01-01"},
    "warning": {"id": "5852873584912896283", "fallback": "⚠️", "added_by": "system", "date": "2024-01-01"},
    "info": {"id": "5978776771623914876", "fallback": "ℹ️", "added_by": "system", "date": "2024-01-01"},
    "question": {"id": "6276057176444246654", "fallback": "❓", "added_by": "system", "date": "2024-01-01"},
    "target": {"id": "6273997026661241933", "fallback": "🎯", "added_by": "system", "date": "2024-01-01"},
    "trophy": {"id": "6235620067942341623", "fallback": "🏆", "added_by": "system", "date": "2024-01-01"},
    "gem": {"id": "6147524086768604985", "fallback": "💎", "added_by": "system", "date": "2024-01-01"},
    "shield": {"id": "5449449325434266744", "fallback": "🛡️", "added_by": "system", "date": "2024-01-01"},
    "music": {"id": "5895735846698487922", "fallback": "🎵", "added_by": "system", "date": "2024-01-01"},
    "game": {"id": "5895297528106061174", "fallback": "🎮", "added_by": "system", "date": "2024-01-01"},
    "money": {"id": "5197434882321567830", "fallback": "💰", "added_by": "system", "date": "2024-01-01"},
    "gift": {"id": "6147617184479711380", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "bell": {"id": "6235403472741603087", "fallback": "🔔", "added_by": "system", "date": "2024-01-01"},
    "lock_open": {"id": "5465443379917629504", "fallback": "🔓", "added_by": "system", "date": "2024-01-01"},
    "lock_closed": {"id": "5465443379917629504", "fallback": "🔒", "added_by": "system", "date": "2024-01-01"},
}

# Merge extra emojis into PREMIUM_EMOJIS
for key, value in EXTRA_PREMIUM_EMOJIS.items():
    if key not in PREMIUM_EMOJIS:
        PREMIUM_EMOJIS[key] = value

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
    """Random premium emoji - ONLY premium <tg-emoji> tags"""
    names = list(PREMIUM_EMOJIS.keys())
    if not names:
        return '<tg-emoji emoji-id="6147464060305676048">😎</tg-emoji>'
    random_name = random.choice(names)
    return get_emoji_html(random_name)

def format_with_premium_emojis(text):
    """
    Har line ke AAGE aur PICCHE sirf premium emoji <tg-emoji> tags lagao
    Koi bhi normal Unicode emoji nahi dikhega
    """
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():
            # Aage aur piche - sirf premium emoji tags
            left_emoji = get_random_emoji()
            right_emoji = get_random_emoji()
            formatted_lines.append(f"{left_emoji} {line} {right_emoji}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

# ========== ACTIVITY TRACKING ==========
def load_activity():
    try:
        if os.path.exists(ACTIVITY_FILE):
            with open(ACTIVITY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_activity(activity):
    try:
        with open(ACTIVITY_FILE, 'w', encoding='utf-8') as f:
            json.dump(activity, f, ensure_ascii=False, indent=2)
    except:
        pass

def log_user_activity(user_id, username, action, text_preview=""):
    """Track what each user does"""
    activity = load_activity()
    uid = str(user_id)
    
    if uid not in activity:
        activity[uid] = {
            "user_id": user_id,
            "username": username,
            "total_actions": 0,
            "commands_used": {},
            "last_text_tried": "",
            "last_seen": "",
            "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    activity[uid]["total_actions"] = activity[uid].get("total_actions", 0) + 1
    activity[uid]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activity[uid]["username"] = username
    
    if action:
        commands = activity[uid].get("commands_used", {})
        commands[action] = commands.get(action, 0) + 1
        activity[uid]["commands_used"] = commands
    
    if text_preview:
        activity[uid]["last_text_tried"] = text_preview[:200]
    
    save_activity(activity)

# ========== BROADCAST LOGGING ==========
def save_broadcast_log(sender_id, sender_name, channel, text):
    try:
        broadcasts = []
        if os.path.exists(BROADCAST_FILE):
            with open(BROADCAST_FILE, 'r', encoding='utf-8') as f:
                broadcasts = json.load(f)
        
        broadcasts.append({
            "sender_id": sender_id,
            "sender_name": sender_name,
            "channel": channel,
            "text": text[:200],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        with open(BROADCAST_FILE, 'w', encoding='utf-8') as f:
            json.dump(broadcasts[-100:], f, ensure_ascii=False, indent=2)
    except:
        pass

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
    username = update.effective_user.username or "NoUsername"
    
    log_user_activity(user_id, username, "/emojify")
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    if not context.args:
        msg = "❌ Usage: /emojify (emoji_name) your text\n\nExample: /emojify (verified) how are you"
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        return
    
    full_text = update.message.text
    if full_text.startswith('/emojify'):
        full_text = full_text[8:].strip()
    
    if not full_text:
        msg = "❌ Please provide text"
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
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
        msg = "❌ No valid emoji found. Use /ads"
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        return
    
    # Owner ko notify about what text user tried
    if user_id != OWNER_ID:
        try:
            owner_notify = f"👤 User @{username} ({user_id}) used /emojify with text:\n{full_text[:300]}"
            await context.bot.send_message(chat_id=OWNER_ID, text=owner_notify)
        except:
            pass
    
    await update.message.reply_text(result, parse_mode="HTML")

# ========== OWNER PANEL COMMANDS ==========
async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied! Only bot owner can use this panel.")
        return
    
    users = load_users()
    banned = load_banned()
    activity = load_activity()
    total_users = len(users)
    banned_count = len(banned)
    active_today = sum(1 for v in activity.values() if v.get("last_seen", "").startswith(datetime.now().strftime("%Y-%m-%d")))
    
    msg = f"""OWNER PANEL

📊 Statistics
• Total Users: {total_users}
• Banned Users: {banned_count}
• Active Users: {total_users - banned_count}
• Active Today: {active_today}

👑 Owner Commands
• /users - List all users
• /tousers - Top users by activity
• /ban <user_id> - Ban a user
• /unban <user_id> - Unban a user
• /stats - Show statistics
• /msg <user_id> <text> - DM a user via bot
• /owner - Show this panel
• /activity - View all user activity logs

━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_premium_emojis(msg)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    users = load_users()
    if not users:
        msg = "📭 No users found."
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        return
    
    banned = load_banned()
    msg = "📋 ALL USERS LIST\n━━━━━━━━━━━━━━━━━━\n"
    for uid, data in users.items():
        status = "🚫 Banned" if uid in banned else "✅ Active"
        username = data.get("username", "No username")
        name = data.get("name", "Unknown")
        msg += f"🆔 {uid} | @{username} | {name} | {status}\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
    
    formatted_msg = format_with_premium_emojis(msg)
    
    if len(formatted_msg) > 4000:
        # Send in chunks if too long
        chunk = ""
        for uid, data in users.items():
            status = "🚫" if uid in banned else "✅"
            line = f"🆔 {uid} @{data.get('username', 'N/A')} {status}\n"
            if len(chunk) + len(line) > 3500:
                await update.message.reply_text(chunk, parse_mode="HTML")
                chunk = line
            else:
                chunk += line
        if chunk:
            await update.message.reply_text(chunk, parse_mode="HTML")
    else:
        await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def top_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/tousers - Top users by activity"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    activity = load_activity()
    if not activity:
        msg = "📭 No activity data found."
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        return
    
    # Sort by total_actions descending
    sorted_users = sorted(activity.values(), key=lambda x: x.get("total_actions", 0), reverse=True)
    
    msg = "🏆 TOP USERS BY ACTIVITY\n━━━━━━━━━━━━━━━━━━\n"
    for i, data in enumerate(sorted_users[:50], 1):
        uid = data.get("user_id", "?")
        username = data.get("username", "NoUsername")
        actions = data.get("total_actions", 0)
        last_seen = data.get("last_seen", "Unknown")
        msg += f"{i}. 🆔 {uid} | @{username} | {actions} actions | Last: {last_seen[:10]}\n"
    
    msg += f"\nTotal active users: {len(activity)}"
    msg += "\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
    
    formatted_msg = format_with_premium_emojis(msg)
    
    if len(formatted_msg) > 4000:
        await update.message.reply_text(f"Total active users: {len(activity)}\nUse /activity for details\n\nDeveloper: @iflexvenom")
    else:
        await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def activity_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/activity - Detailed activity log"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    activity = load_activity()
    if not activity:
        msg = "📭 No activity data found."
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        return
    
    msg = "📊 DETAILED ACTIVITY LOG\n━━━━━━━━━━━━━━━━━━\n"
    for uid, data in activity.items():
        username = data.get("username", "NoUsername")
        actions = data.get("total_actions", 0)
        last_seen = data.get("last_seen", "Unknown")
        first_seen = data.get("first_seen", "Unknown")
        last_text = data.get("last_text_tried", "None")
        commands = data.get("commands_used", {})
        
        msg += f"🆔 {uid} (@{username})\n"
        msg += f"   📈 Total: {actions} | First: {first_seen[:10]} | Last: {last_seen[:10]}\n"
        msg += f"   💬 Last Text: {last_text[:100]}\n"
        if commands:
            top_cmd = max(commands, key=commands.get)
            msg += f"   ⌨️ Top Cmd: {top_cmd} ({commands[top_cmd]}x)\n"
        msg += "\n"
    
    msg += "━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
    
    formatted_msg = format_with_premium_emojis(msg)
    
    if len(formatted_msg) > 4000:
        # Short version
        short_msg = "📊 ACTIVITY SUMMARY\n"
        for uid, data in activity.items():
            short_msg += f"🆔 {uid} @{data.get('username','?')} - {data.get('total_actions',0)} actions\n"
        short_msg += "\nUse /tousers for sorted list\nDeveloper: @iflexvenom"
        await update.message.reply_text(short_msg)
    else:
        await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    if not context.args:
        msg = "Usage: /ban USER_ID"
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        return
    
    try:
        target_id = str(context.args[0])
        if int(target_id) == OWNER_ID:
            await update.message.reply_text("❌ Cannot ban the owner!")
            return
        
        banned = load_banned()
        banned.add(target_id)
        save_banned(banned)
        msg = f"✅ User {target_id} has been banned."
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    if not context.args:
        msg = "Usage: /unban USER_ID"
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        return
    
    try:
        target_id = str(context.args[0])
        banned = load_banned()
        if target_id in banned:
            banned.remove(target_id)
            save_banned(banned)
            msg = f"✅ User {target_id} has been unbanned."
            formatted_msg = format_with_premium_emojis(msg)
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
    activity = load_activity()
    
    # Count commands usage
    total_actions = sum(v.get("total_actions", 0) for v in activity.values())
    active_today = sum(1 for v in activity.values() if v.get("last_seen", "").startswith(datetime.now().strftime("%Y-%m-%d")))
    
    msg = f"""📊 BOT STATISTICS
━━━━━━━━━━━━━━━━━━
• Total Users: {len(users)}
• Banned Users: {len(banned)}
• Active Users: {len(users) - len(banned)}
• Active Today: {active_today}
• Total Actions: {total_actions}
• Premium Emojis: {len(PREMIUM_EMOJIS)}
━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_premium_emojis(msg)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

# ========== /msg COMMAND - Reply to user ID ==========
async def msg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/msg <user_id> <text> - Send private message to user via bot"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    if len(context.args) < 2:
        msg = "Usage: /msg USER_ID your message here\n\nExample: /msg 123456789 Hello! This is a test message."
        formatted_msg = format_with_premium_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        return
    
    target_id = context.args[0]
    message_text = " ".join(context.args[1:])
    
    try:
        target_id_int = int(target_id)
        
        # Owner ko bhi notification aaye
        confirm_text = f"📨 Message sent to {target_id}\n\nContent: {message_text[:200]}"
        formatted_confirm = format_with_premium_emojis(confirm_text)
        await update.message.reply_text(formatted_confirm, parse_mode="HTML")
        
        # User ko message bhejo
        user_msg = f"📩 Message from Admin:\n\n{message_text}"
        
        try:
            await context.bot.send_message(chat_id=target_id_int, text=user_msg)
            await update.message.reply_text(f"✅ Message delivered to {target_id}")
        except Exception as e:
            await update.message.reply_text(f"❌ Could not deliver to {target_id}: {str(e)}")
            
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID. Please provide a numeric ID.")

# ========== BROADCAST COMMAND ==========
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied! Only owner can broadcast.")
        return
    
    msg = f"""📢 Broadcast Setup

Step 1: Send the text you want to broadcast
Include emoji names in parentheses like (verified)

Example: Welcome to our channel (verified)

━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_premium_emojis(msg)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")
    
    user_data_store[user_id] = {"step": "waiting_text"}

# ========== REGULAR COMMANDS ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    name = update.effective_user.first_name or "User"
    
    register_user(user_id, username, name)
    log_user_activity(user_id, username, "/start")
    
    # Owner ko notify
    if user_id != OWNER_ID:
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"🆕 New user started bot: @{username} ({user_id}) - {name}"
            )
        except:
            pass
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned from using this bot.")
        return
    
    msg = """Premium Emoji Bot

Commands:
• /emojify (emoji) text - Add emoji around text
• /ads - See all premium emojis
• /myemojis - Your added emojis
• /addemoji - Add new emoji
• /help - Help

Example:
/emojify (verified) how are you

━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_premium_emojis(msg)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def ads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ads - Sirf premium emoji dikhao, koi normal emoji nahi"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    
    log_user_activity(user_id, username, "/ads")
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    # Sirf premium emoji list - sab <tg-emoji> tags ke saath
    emoji_list = []
    for name, data in PREMIUM_EMOJIS.items():
        emoji_html = get_emoji_html(name)
        added_by = data.get("added_by", "system")
        # Sirf premium emoji HTML tag, koi normal emoji nahi
        emoji_list.append(f"{emoji_html}  <b>{name}</b>  (by {added_by})")
    
    # Group by first letter for organization
    content = f"<b>Available Premium Emojis ({len(PREMIUM_EMOJIS)})</b>\n\n"
    content += "\n".join(emoji_list)
    content += "\n\nUsage: /emojify (verified) your text\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
    
    # Sirf premium emoji tags use karo, koi normal emoji nahi
    await update.message.reply_text(content, parse_mode="HTML")

async def myemojis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    log_user_activity(user_id, username, "/myemojis")
    
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
        await update.message.reply_text(content, parse_mode="HTML")
    else:
        content = f"❌ You haven't added any emojis yet!\n\nUse /addemoji to add your first emoji\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
        formatted_msg = format_with_premium_emojis(content)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    log_user_activity(user_id, username, "/help")
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    content = """Help Guide

Commands:
• /start - Start the bot
• /emojify (emoji) text - Add emoji around your text
• /ads - Show ALL available premium emojis
• /myemojis - Show emojis YOU added
• /addemoji - Add new custom emoji
• /help - Show this help

Owner Commands (Owner only):
• /owner - Owner panel
• /users - List all users
• /tousers - Top users by activity
• /ban USER_ID - Ban user
• /unban USER_ID - Unban user
• /stats - Bot statistics
• /activity - View activity logs
• /msg USER_ID text - DM a user
• /broadcast - Broadcast to channel

Examples:
/emojify (verified) how are you

━━━━━━━━━━━━━━━━━━
Developer: @iflexvenom"""
    
    formatted_msg = format_with_premium_emojis(content)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def addemoji_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    log_user_activity(user_id, username, "/addemoji")
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    user_data_store[user_id] = {"step": "waiting_emoji_name", "user_name": update.effective_user.username or update.effective_user.first_name}
    
    content = f"➕ Adding New Emoji\n\nStep 1: Send the emoji name (no spaces, use underscore)\nExample: fire_emoji or cool_badge\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
    formatted_msg = format_with_premium_emojis(content)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

# ========== MESSAGE HANDLER ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    
    # Track all non-command messages
    if update.message.text and not update.message.text.startswith('/'):
        log_user_activity(user_id, username, "text_message", update.message.text[:200])
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    if user_id not in user_data_store:
        return
    
    step = user_data_store[user_id].get("step")
    
    if step == "waiting_emoji_name":
        emoji_name = update.message.text.strip().lower()
        
        if ' ' in emoji_name:
            msg = "❌ Emoji name cannot contain spaces. Use underscore (_). Send again:"
            formatted_msg = format_with_premium_emojis(msg)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            return
        
        if emoji_name in PREMIUM_EMOJIS:
            await update.message.reply_text(f"❌ Emoji name '{emoji_name}' already exists! Choose a different name:")
            return
        
        user_data_store[user_id]["emoji_name"] = emoji_name
        user_data_store[user_id]["step"] = "waiting_emoji_data"
        
        content = f"✅ Emoji name: <b>{emoji_name}</b>\n\nStep 2: Now send the emoji ID (or forward a message with custom emoji)\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
        formatted_msg = format_with_premium_emojis(content)
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
                content = f"✅ Emoji ID: <code>{emoji_id}</code>\n\nPlease send the fallback emoji character:\nExample: 🔥 or ⭐\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
                formatted_msg = format_with_premium_emojis(content)
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
            
            content = f"✅ Emoji '<b>{emoji_name}</b>' added successfully!\n\nAdded to global emoji list!\nAdded by: {user_name}\nUse: /emojify ({emoji_name}) your text\n\nEveryone can now use '{emoji_name}' emoji!\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_premium_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
        else:
            content = "❌ Could not extract emoji ID!\nPlease send a valid emoji ID or forward a message with custom emoji.\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
            formatted_msg = format_with_premium_emojis(content)
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
        
        content = f"✅ Emoji '<b>{emoji_name}</b>' added successfully!\n\nAdded to global emoji list!\nAdded by: {user_name}\nUse: /emojify ({emoji_name}) your text\n\nEveryone can now use '{emoji_name}' emoji!\n\n━━━━━━━━━━━━━━━━━━\nDeveloper: @iflexvenom"
        formatted_msg = format_with_premium_emojis(content)
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
            formatted_msg = format_with_premium_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            
        except Exception as e:
            content = f"❌ Error: {str(e)}"
            formatted_msg = format_with_premium_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            del user_data_store[user_id]
    
    elif step == "waiting_channel":
        channel = update.message.text.strip()
        
        if not channel.startswith("@"):
            content = "❌ Please send channel username starting with @"
            formatted_msg = format_with_premium_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            return
        
        is_admin = await is_admin_in_channel(context, user_id, channel)
        
        if not is_admin:
            content = f"❌ Access Denied!\n\nYou are not an admin in {channel}"
            formatted_msg = format_with_premium_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            del user_data_store[user_id]
            return
        
        user_data_store[user_id]["channel"] = channel
        user_data_store[user_id]["step"] = "confirm"
        
        content = f"✅ Admin Verified!\n\n📢 Channel: {channel}\n✅ Send CONFIRM to broadcast\n❌ Send CANCEL to abort"
        formatted_msg = format_with_premium_emojis(content)
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
                
                # Log the broadcast
                save_broadcast_log(user_id, username, channel, user_data_store[user_id].get("text", ""))
                
                content = f"✅ Broadcast successful!\n\n📢 Sent to: {channel}"
                formatted_msg = format_with_premium_emojis(content)
                await update.message.reply_text(formatted_msg, parse_mode="HTML")
                
            except Exception as e:
                content = f"❌ Error: {str(e)}"
                formatted_msg = format_with_premium_emojis(content)
                await update.message.reply_text(formatted_msg, parse_mode="HTML")
            
            del user_data_store[user_id]
        
        elif response == "CANCEL":
            del user_data_store[user_id]
            content = "❌ Broadcast cancelled"
            formatted_msg = format_with_premium_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
        
        else:
            content = "Please send CONFIRM or CANCEL"
            formatted_msg = format_with_premium_emojis(content)
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
    application.add_handler(CommandHandler("tousers", top_users))
    application.add_handler(CommandHandler("activity", activity_command))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("msg", msg_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    
    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("emojify", emojify_command))
    application.add_handler(CommandHandler("ads", ads_command))
    application.add_handler(CommandHandler("myemojis", myemojis_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addemoji", addemoji_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("=" * 50)
    print("🤖 Premium Emoji Bot Starting...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print("✅ Sirf PREMIUM emoji <tg-emoji> tags dikhenge")
    print("✅ Koi normal Unicode emoji nahi dikhega")
    print("✅ Har line ke AAGE aur PICCHE sirf premium emoji lagega")
    print(f"✅ Total Premium Emojis: {len(PREMIUM_EMOJIS)}")
    print("=" * 50)
    
    # Start Flask in background (for Render)
    threading.Thread(target=run_flask, daemon=True).start()
    
    application.run_polling()

if __name__ == "__main__":
    main()
