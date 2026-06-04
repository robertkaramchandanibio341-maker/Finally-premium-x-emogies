from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging
import re
import json
import os
import threading
import random
import asyncio
from datetime import datetime, timedelta
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== CONFIG ==========
BOT_TOKEN = "8639960336:AAG1gmd4DPETqiiYmTdnt_9WudmLmc-8oRY"
OWNER_ID = 8586849798
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
EMOJI_FILE = "emojis.json"
STATS_FILE = "stats.json"
GIVEAWAY_FILE = "giveaway.json"

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
giveaway_data = {"active": False, "participants": [], "prize": "", "end_time": None}

# ========== STATS FUNCTIONS ==========
def load_stats():
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"emoji_usage": {}, "user_activity": {}}

def save_stats(stats):
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except:
        pass

def update_emoji_stats(emoji_name):
    stats = load_stats()
    if "emoji_usage" not in stats:
        stats["emoji_usage"] = {}
    stats["emoji_usage"][emoji_name] = stats["emoji_usage"].get(emoji_name, 0) + 1
    save_stats(stats)

def update_user_activity(user_id):
    stats = load_stats()
    if "user_activity" not in stats:
        stats["user_activity"] = {}
    today = datetime.now().strftime("%Y-%m-%d")
    if str(user_id) not in stats["user_activity"]:
        stats["user_activity"][str(user_id)] = {}
    stats["user_activity"][str(user_id)][today] = stats["user_activity"][str(user_id)].get(today, 0) + 1
    save_stats(stats)

# ========== GIVEAWAY FUNCTIONS ==========
def load_giveaway():
    global giveaway_data
    try:
        if os.path.exists(GIVEAWAY_FILE):
            with open(GIVEAWAY_FILE, 'r', encoding='utf-8') as f:
                giveaway_data = json.load(f)
    except:
        pass

def save_giveaway():
    try:
        with open(GIVEAWAY_FILE, 'w', encoding='utf-8') as f:
            json.dump(giveaway_data, f, ensure_ascii=False, indent=2)
    except:
        pass

# ========== EMOJI FUNCTIONS ==========
def save_emojis():
    try:
        with open(EMOJI_FILE, 'w', encoding='utf-8') as f:
            json.dump(PREMIUM_EMOJIS, f, ensure_ascii=False, indent=2)
    except:
        pass

def load_emojis():
    global PREMIUM_EMOJIS
    try:
        if os.path.exists(EMOJI_FILE):
            with open(EMOJI_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                for key, value in loaded.items():
                    if key not in PREMIUM_EMOJIS:
                        PREMIUM_EMOJIS[key] = value
    except:
        pass

def get_emoji_html(name):
    if name in PREMIUM_EMOJIS:
        data = PREMIUM_EMOJIS[name]
        return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>'
    return ""

def get_random_emoji():
    names = list(PREMIUM_EMOJIS.keys())
    if not names:
        return ""
    random_name = random.choice(names)
    return get_emoji_html(random_name)

def format_with_double_emojis(text):
    """Har line ke aage aur piche random premium emoji lagao"""
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        if line.strip():
            left_emoji = get_random_emoji()
            right_emoji = get_random_emoji()
            formatted_lines.append(f"{left_emoji} {line} {right_emoji}")
        else:
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
        return True  # New user
    return False  # Existing user

def is_banned(user_id):
    banned = load_banned()
    return str(user_id) in banned

# ========== SEND NEW USER NOTIFICATION TO OWNER ==========
async def send_new_user_notification(context, user_id, username, first_name, last_name=None):
    """Jab koi naya user bot start karega toh owner ko notification bhejo"""
    full_name = first_name
    if last_name:
        full_name += f" {last_name}"
    
    mention = f"<a href='tg://user?id={user_id}'>{full_name}</a>"
    
    notification = f"""👤 **NEW USER JOINED** 👤

━━━━━━━━━━━━━━━━━━
📛 **Name:** {mention}
🆔 **User ID:** <code>{user_id}</code>
📝 **Username:** @{username if username else 'No username'}
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━

📊 **Total Users:** {len(load_users())}

👑 Developer: @iflexvenom"""
    
    try:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=notification,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send new user notification: {e}")

# ========== FORWARD USER MESSAGE TO OWNER ==========
async def forward_to_owner(context, user_id, username, message_text, first_name):
    """Har user ka message owner ko forward karo"""
    mention = f"<a href='tg://user?id={user_id}'>{first_name}</a>"
    
    forward_msg = f"""📨 **NEW MESSAGE FROM USER** 📨

━━━━━━━━━━━━━━━━━━
👤 **User:** {mention}
🆔 **ID:** <code>{user_id}</code>
📛 **Username:** @{username if username else 'No username'}
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **Message:**
<code>{message_text[:500]}</code>
━━━━━━━━━━━━━━━━━━

💡 **Reply:** /reply {user_id} your message"""
    
    try:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=forward_msg,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error forwarding to owner: {e}")

# ========== REPLY TO USER ==========
async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /reply USER_ID your message\n\nExample: /reply 123456789 Hello there!")
        return
    
    try:
        target_id = int(context.args[0])
        reply_msg = " ".join(context.args[1:])
        
        # Format with emoji for the reply
        formatted_reply = format_with_double_emojis(f"📩 **Reply from Owner:**\n\n{reply_msg}\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom")
        
        await context.bot.send_message(
            chat_id=target_id,
            text=formatted_reply,
            parse_mode="HTML"
        )
        await update.message.reply_text(f"✅ Reply sent to user {target_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ========== /emojify COMMAND ==========
async def emojify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    update_user_activity(user_id)
    
    if not context.args:
        msg = format_with_double_emojis("❌ Usage: /emojify (emoji_name) your text\n\nExample: /emojify (verified) how are you")
        await update.message.reply_text(msg, parse_mode="HTML")
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
                update_emoji_stats(emoji_name)
                return emoji_html
            return match.group(0)
        
        processed_line = re.sub(r'\(([^)]+)\)', replace_emoji, line)
        processed_lines.append(processed_line)
    
    result = '\n'.join(processed_lines)
    
    if not result.strip():
        await update.message.reply_text("❌ No valid emoji found. Use /ads to see available emojis")
        return
    
    await update.message.reply_text(result, parse_mode="HTML")

# ========== /analytics COMMAND ==========
async def analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied! Only owner can view analytics.")
        return
    
    stats = load_stats()
    emoji_usage = stats.get("emoji_usage", {})
    
    if not emoji_usage:
        msg = format_with_double_emojis("📊 No analytics data yet.\n\nUsers haven't used any emojis.")
        await update.message.reply_text(msg, parse_mode="HTML")
        return
    
    sorted_emojis = sorted(emoji_usage.items(), key=lambda x: x[1], reverse=True)[:10]
    
    msg = "📊 **EMOJI ANALYTICS** 📊\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += "🏆 **Top 10 Most Used Emojis:**\n\n"
    
    for i, (name, count) in enumerate(sorted_emojis, 1):
        emoji_html = get_emoji_html(name)
        msg += f"{i}. {emoji_html} **{name}** - {count} times\n"
    
    total_usage = sum(emoji_usage.values())
    msg += f"\n━━━━━━━━━━━━━━━━━━\n"
    msg += f"📈 **Total Emoji Usage:** {total_usage}\n"
    msg += f"🎨 **Unique Emojis Used:** {len(emoji_usage)}\n"
    msg += f"\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
    
    formatted_msg = format_with_double_emojis(msg)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

# ========== /topusers COMMAND ==========
async def topusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied! Only owner can view top users.")
        return
    
    stats = load_stats()
    user_activity = stats.get("user_activity", {})
    
    if not user_activity:
        await update.message.reply_text("📊 No user activity data yet.")
        return
    
    user_total = {}
    for uid, days in user_activity.items():
        user_total[uid] = sum(days.values())
    
    sorted_users = sorted(user_total.items(), key=lambda x: x[1], reverse=True)[:15]
    
    msg = "🏆 **TOP USERS** 🏆\n━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, (uid, count) in enumerate(sorted_users, 1):
        msg += f"{i}. **ID:** <code>{uid}</code> - {count} uses\n"
    
    msg += f"\n━━━━━━━━━━━━━━━━━━\n📊 **Total Active Users:** {len(user_total)}\n"
    msg += f"\n👑 Developer: @iflexvenom"
    
    formatted_msg = format_with_double_emojis(msg)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

# ========== /giveaway COMMANDS ==========
async def giveaway_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    global giveaway_data
    load_giveaway()
    
    if not context.args:
        if user_id == OWNER_ID:
            msg = """🎁 **Giveaway Commands** 🎁
━━━━━━━━━━━━━━━━━━

• `/giveaway start PRIZE` - Start new giveaway
• `/giveaway end` - End giveaway & pick winner
• `/giveaway status` - Check giveaway status
• `/giveaway join` - Join active giveaway

👑 Developer: @iflexvenom"""
            formatted_msg = format_with_double_emojis(msg)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
        else:
            msg = """🎁 **Giveaway Commands** 🎁
━━━━━━━━━━━━━━━━━━

• `/giveaway join` - Join active giveaway
• `/giveaway status` - Check giveaway status

👑 Developer: @iflexvenom"""
            formatted_msg = format_with_double_emojis(msg)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
        return
    
    subcommand = context.args[0].lower()
    
    if subcommand == "start" and user_id == OWNER_ID:
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /giveaway start PRIZE_NAME")
            return
        
        prize = " ".join(context.args[1:])
        giveaway_data = {
            "active": True,
            "participants": [],
            "prize": prize,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        }
        save_giveaway()
        
        msg = f"🎁 **NEW GIVEAWAY STARTED!** 🎁\n━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"🏆 **Prize:** {prize}\n"
        msg += f"⏰ **Ends:** {giveaway_data['end_time']}\n\n"
        msg += f"📝 **To join:** Send `/giveaway join`\n\n"
        msg += f"👑 Developer: @iflexvenom"
        
        formatted_msg = format_with_double_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        
        users = load_users()
        for uid_str in users:
            try:
                await context.bot.send_message(
                    chat_id=int(uid_str),
                    text=f"🎁 **New Giveaway!** 🎁\n\nPrize: {prize}\nSend /giveaway join to participate!",
                    parse_mode="Markdown"
                )
                await asyncio.sleep(0.05)
            except:
                pass
    
    elif subcommand == "end" and user_id == OWNER_ID:
        if not giveaway_data.get("active", False):
            await update.message.reply_text("❌ No active giveaway!")
            return
        
        participants = giveaway_data.get("participants", [])
        
        if len(participants) < 1:
            msg = f"❌ **Giveaway Ended!**\n━━━━━━━━━━━━━━━━━━\n\nNo one participated!\nPrize: {giveaway_data['prize']}\n\n👑 Developer: @iflexvenom"
            formatted_msg = format_with_double_emojis(msg)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            giveaway_data["active"] = False
            save_giveaway()
            return
        
        winner = random.choice(participants)
        
        msg = f"🏆 **GIVEAWAY WINNER!** 🏆\n━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"🎁 **Prize:** {giveaway_data['prize']}\n"
        msg += f"👑 **Winner:** <code>{winner}</code>\n"
        msg += f"📊 **Total Participants:** {len(participants)}\n\n"
        msg += f"🎉 Congratulations! 🎉\n\n"
        msg += f"👑 Developer: @iflexvenom"
        
        formatted_msg = format_with_double_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        
        try:
            await context.bot.send_message(
                chat_id=int(winner),
                text=f"🎉 **CONGRATULATIONS!** 🎉\n\nYou won the giveaway!\nPrize: {giveaway_data['prize']}\n\nContact @iflexvenom to claim your prize!",
                parse_mode="Markdown"
            )
        except:
            pass
        
        giveaway_data["active"] = False
        save_giveaway()
    
    elif subcommand == "join":
        if not giveaway_data.get("active", False):
            await update.message.reply_text("❌ No active giveaway right now!")
            return
        
        participants = giveaway_data.get("participants", [])
        user_id_str = str(user_id)
        
        if user_id_str in participants:
            await update.message.reply_text("❌ You already joined this giveaway!")
            return
        
        participants.append(user_id_str)
        giveaway_data["participants"] = participants
        save_giveaway()
        
        msg = f"✅ **You joined the giveaway!** 🎁\n━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"🏆 **Prize:** {giveaway_data['prize']}\n"
        msg += f"📊 **Total Participants:** {len(participants)}\n"
        msg += f"⏰ **Ends:** {giveaway_data['end_time']}\n\n"
        msg += f"Good luck! 🍀\n\n"
        msg += f"👑 Developer: @iflexvenom"
        
        formatted_msg = format_with_double_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
    
    elif subcommand == "status":
        if not giveaway_data.get("active", False):
            await update.message.reply_text("❌ No active giveaway right now!")
            return
        
        participants = giveaway_data.get("participants", [])
        user_id_str = str(user_id)
        has_joined = user_id_str in participants
        
        msg = f"🎁 **Giveaway Status** 🎁\n━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"🏆 **Prize:** {giveaway_data['prize']}\n"
        msg += f"📊 **Participants:** {len(participants)}\n"
        msg += f"⏰ **Ends:** {giveaway_data['end_time']}\n"
        msg += f"📝 **Your Status:** {'✅ Joined' if has_joined else '❌ Not joined'}\n\n"
        
        if not has_joined:
            msg += f"Send `/giveaway join` to participate!\n\n"
        
        msg += f"👑 Developer: @iflexvenom"
        
        formatted_msg = format_with_double_emojis(msg)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")

# ========== /notify COMMAND ==========
async def notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied! Only owner can send notifications.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /notify your notification message\n\nExample: /notify New emoji added! Check /ads")
        return
    
    notification = " ".join(context.args)
    users = load_users()
    banned = load_banned()
    
    status_msg = await update.message.reply_text(f"📤 Sending notification to {len(users)} users...")
    
    success = 0
    for uid_str in users:
        if uid_str in banned:
            continue
        try:
            formatted_notify = format_with_double_emojis(f"🔔 **NOTIFICATION** 🔔\n\n{notification}\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom")
            await context.bot.send_message(
                chat_id=int(uid_str),
                text=formatted_notify,
                parse_mode="HTML"
            )
            success += 1
            await asyncio.sleep(0.05)
        except:
            pass
    
    await status_msg.edit_text(f"✅ Notification sent to {success} users!")

# ========== /broadcast COMMAND ==========
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied! Only owner can broadcast.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📢 Broadcast Command\n\n"
            "Usage: /broadcast your message here\n\n"
            "Example: /broadcast Hello everyone!\n\n"
            "⚠️ This will send message to ALL users."
        )
        return
    
    message_text = " ".join(context.args)
    users = load_users()
    
    if not users:
        await update.message.reply_text("❌ No users found in database.")
        return
    
    status_msg = await update.message.reply_text(f"📤 Broadcasting to {len(users)} users...")
    
    success_count = 0
    fail_count = 0
    banned = load_banned()
    
    for uid_str, user_data in users.items():
        try:
            uid = int(uid_str)
            if str(uid) in banned:
                continue
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 Announcement:\n\n{message_text}\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
            )
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            fail_count += 1
    
    result_msg = f"✅ Broadcast Complete!\n\n📨 Sent: {success_count} users\n❌ Failed: {fail_count}\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
    
    formatted_result = format_with_double_emojis(result_msg)
    await status_msg.edit_text(formatted_result, parse_mode="HTML")

# ========== /ads COMMAND (Sirf Premium Emoji - Bina Extra Normal Emoji Ke) ==========
async def ads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("You have been banned.")
        return
    
    update_user_activity(user_id)
    
    # Sirf premium emoji - koi extra character nahi, koi normal emoji nahi
    emoji_list = []
    for name, data in PREMIUM_EMOJIS.items():
        emoji_html = get_emoji_html(name)
        added_by = data.get("added_by", "system")
        emoji_list.append(f"{emoji_html} {name} (by {added_by})")
    
    content = f"PREMIUM EMOJIS ({len(PREMIUM_EMOJIS)})\n\n" + "\n".join(emoji_list) + f"\n\nUsage: /emojify (verified) your text\n\nDeveloper: @iflexvenom"
    
    # WITHOUT any extra emoji - direct send
    await update.message.reply_text(content, parse_mode="HTML")

# ========== OTHER COMMANDS ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    first_name = update.effective_user.first_name or "User"
    last_name = update.effective_user.last_name
    
    is_new = register_user(user_id, username, first_name)
    
    # Agar naya user hai toh owner ko notification bhejo
    if is_new:
        await send_new_user_notification(context, user_id, username, first_name, last_name)
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned from using this bot.")
        return
    
    msg = """🎉 Welcome to Premium Emoji Bot!

Commands:
• /emojify (emoji) text - Add premium emoji to text
• /ads - Show all premium emojis
• /myemojis - Your added emojis
• /addemoji - Add new custom emoji
• /help - Help menu

Examples:
/emojify (verified) how are you
/emojify (flex) I'm the best

━━━━━━━━━━━━━━━━━━
👑 Developer: @iflexvenom"""
    
    formatted_msg = format_with_double_emojis(msg)
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
        content = f"📌 Your Added Emojis ({len(user_emojis)})\n━━━━━━━━━━━━━━━━━━\n" + "\n".join(user_emojis) + f"\n━━━━━━━━━━━━━━━━━━\n💡 Use /addemoji to add more\n\n👑 Developer: @iflexvenom"
        formatted_msg = format_with_double_emojis(content)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")
    else:
        content = f"❌ You haven't added any emojis yet!\n\nUse /addemoji to add your first custom emoji\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
        formatted_msg = format_with_double_emojis(content)
        await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    content = """📚 HELP GUIDE

━━━━━━━━━━━━━━━━━━
🔹 USER COMMANDS:
━━━━━━━━━━━━━━━━━━

/start - Start the bot
/emojify (emoji) text - Add premium emoji around your text
/ads - Show ALL available premium emojis
/myemojis - Show emojis YOU added
/addemoji - Add new custom emoji
/help - Show this help

━━━━━━━━━━━━━━━━━━
🔸 OWNER COMMANDS:
━━━━━━━━━━━━━━━━━━

/owner - Owner panel
/users - List all users
/tousers - List all users
/ban USER_ID - Ban user
/unban USER_ID - Unban user
/stats - Bot statistics
/broadcast msg - Send to all users
/notify msg - Send notification
/analytics - Emoji usage analytics
/topusers - Most active users
/giveaway - Manage giveaways
/reply id msg - Reply to user

━━━━━━━━━━━━━━━━━━
💡 EXAMPLES:
━━━━━━━━━━━━━━━━━━

/emojify (verified) Welcome to my channel
/emojify (flex) I'm the best
/emojify (heart) I love this

━━━━━━━━━━━━━━━━━━
👑 Developer: @iflexvenom"""
    
    formatted_msg = format_with_double_emojis(content)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def addemoji_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    user_data_store[user_id] = {"step": "waiting_emoji_name", "user_name": update.effective_user.username or update.effective_user.first_name}
    
    content = f"➕ ADD CUSTOM EMOJI\n━━━━━━━━━━━━━━━━━━\n\nStep 1: Send the emoji name (no spaces, use underscore)\n\nExample: fire_emoji or cool_badge\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
    formatted_msg = format_with_double_emojis(content)
    await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    users = load_users()
    banned = load_banned()
    stats = load_stats()
    emoji_usage = stats.get("emoji_usage", {})
    total_usage = sum(emoji_usage.values())
    
    msg = f"""👑 **OWNER PANEL** 👑
━━━━━━━━━━━━━━━━━━

📊 **Statistics**
• Total Users: {len(users)}
• Banned Users: {len(banned)}
• Active Users: {len(users) - len(banned)}
• Premium Emojis: {len(PREMIUM_EMOJIS)}
• Total Emoji Usage: {total_usage}

━━━━━━━━━━━━━━━━━━
👑 **Owner Commands**
• /users - List all users
• /tousers - List all users
• /ban <id> - Ban user
• /unban <id> - Unban user
• /stats - Bot statistics
• /broadcast <msg> - Send to all
• /notify <msg> - Send notification
• /analytics - Emoji analytics
• /topusers - Top active users
• /giveaway - Manage giveaways
• /reply <id> <msg> - Reply to user

━━━━━━━━━━━━━━━━━━
👑 Developer: @iflexvenom"""
    
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
    msg = "📋 **USER LIST**\n━━━━━━━━━━━━━━━━━━\n"
    
    for uid_str, data in users.items():
        status = "🚫 Banned" if uid_str in banned else "✅ Active"
        username = data.get("username", "No username")
        name = data.get("name", "Unknown")
        msg += f"🆔 ID: <code>{uid_str}</code> | @{username} | {name} | {status}\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
    
    formatted_msg = format_with_double_emojis(msg)
    
    if len(formatted_msg) > 4000:
        await update.message.reply_text(f"Total users: {len(users)}\nUse /stats for details\n\nDeveloper: @iflexvenom")
    else:
        await update.message.reply_text(formatted_msg, parse_mode="HTML")

async def tousers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_users(update, context)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    users = load_users()
    banned = load_banned()
    stats = load_stats()
    emoji_usage = stats.get("emoji_usage", {})
    total_usage = sum(emoji_usage.values())
    
    msg = f"📊 **BOT STATISTICS**\n━━━━━━━━━━━━━━━━━━\n"
    msg += f"• Total Users: {len(users)}\n"
    msg += f"• Banned Users: {len(banned)}\n"
    msg += f"• Active Users: {len(users) - len(banned)}\n"
    msg += f"• Premium Emojis: {len(PREMIUM_EMOJIS)}\n"
    msg += f"• Total Emoji Usage: {total_usage}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"👑 Developer: @iflexvenom"
    
    formatted_msg = format_with_double_emojis(msg)
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

# ========== MESSAGE HANDLER - Forward User Messages to Owner ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_banned(str(user_id)) and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You have been banned.")
        return
    
    # Handle addemoji flow
    if user_id in user_data_store:
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
            user_data_store[user_id]["step"] = "waiting_emoji_id"
            
            content = f"✅ Emoji name: {emoji_name}\n\nStep 2: Send the emoji ID\n\nHow to get emoji ID:\n1. Forward a message with the custom emoji\n2. Copy the emoji ID from forwarded message\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            return
        
        elif step == "waiting_emoji_id":
            emoji_name = user_data_store[user_id]["emoji_name"]
            message_text = update.message.text or ""
            
            emoji_id = None
            
            if update.message.forward_from_message_id:
                lines = message_text.split('\n')
                for line in lines:
                    if "Custom Emoji ID:" in line:
                        parts = line.split("Custom Emoji ID:")
                        if len(parts) > 1:
                            emoji_id = parts[1].strip()
                            break
            
            if not emoji_id and message_text.isdigit():
                emoji_id = message_text
            
            if not emoji_id:
                match = re.search(r'(\d{10,})', message_text)
                if match:
                    emoji_id = match.group(1)
            
            if emoji_id:
                user_data_store[user_id]["emoji_id"] = emoji_id
                user_data_store[user_id]["step"] = "waiting_fallback"
                
                content = f"✅ Emoji ID: {emoji_id}\n\nStep 3: Send the fallback emoji character\n\nExample: 🔥 or ⭐ or ✅\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
                formatted_msg = format_with_double_emojis(content)
                await update.message.reply_text(formatted_msg, parse_mode="HTML")
            else:
                content = f"❌ Could not extract emoji ID!\n\nPlease forward a message with custom emoji or send emoji ID directly.\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
                formatted_msg = format_with_double_emojis(content)
                await update.message.reply_text(formatted_msg, parse_mode="HTML")
            return
        
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
            
            content = f"✅ Emoji '{emoji_name}' added successfully! 🎉\n━━━━━━━━━━━━━━━━━━\n\nAdded by: @{user_name}\nDate: {datetime.now().strftime('%Y-%m-%d')}\n\nUse: /emojify ({emoji_name}) your text\n\nEveryone can now use this emoji!\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: @iflexvenom"
            formatted_msg = format_with_double_emojis(content)
            await update.message.reply_text(formatted_msg, parse_mode="HTML")
            return
    
    # Forward any message to owner (except command and owner's own messages)
    if user_id != OWNER_ID and not update.message.text.startswith('/'):
        await forward_to_owner(
            context, 
            user_id, 
            update.effective_user.username or "NoUsername", 
            update.message.text,
            update.effective_user.first_name or "User"
        )
        await update.message.reply_text("✅ Your message has been forwarded to the owner. You will get a reply soon!")

# ========== MAIN ==========
def main():
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
    load_giveaway()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Owner commands
    application.add_handler(CommandHandler("owner", owner_panel))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("tousers", tousers_command))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("notify", notify_command))
    application.add_handler(CommandHandler("analytics", analytics_command))
    application.add_handler(CommandHandler("topusers", topusers_command))
    application.add_handler(CommandHandler("giveaway", giveaway_command))
    application.add_handler(CommandHandler("reply", reply_command))
    
    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("emojify", emojify_command))
    application.add_handler(CommandHandler("ads", ads_command))
    application.add_handler(CommandHandler("myemojis", myemojis_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addemoji", addemoji_command))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("=" * 50)
    print("🤖 Premium Emoji Bot Starting...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📋 Premium Emojis: {len(PREMIUM_EMOJIS)}")
    print("✅ New user notifications will be sent to owner")
    print("✅ User messages will be forwarded to owner")
    print("✅ /ads mein sirf premium emojis (bina extra normal emoji ke)")
    print("=" * 50)
    
    threading.Thread(target=run_flask, daemon=True).start()
    
    application.run_polling()

if __name__ == "__main__":
    main()
