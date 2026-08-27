import requests
from io import BytesIO
import telebot
from datetime import datetime
import time
import logging
from html import escape
import json
import re
import urllib.parse

API_TOKEN = "8498478739:AAFwbdWmT7reWAdp5FZ2jAdOGgaojY1Sc0A"
bot = telebot.TeleBot(API_TOKEN)

# ============ CONFIGURATION ============
VALID_REGIONS = ["ind", "sg", "br", "ru", "id", "tw", "us", "vn", "th", "me", "pk", "cis", "bd", "na"]

# APIs
PLAYER_INFO_API = "https://info.killersharmabot.online/player-info?uid={uid}"

# NEW IMAGE APIs
OUTFIT_API_URL = "https://image.killersharmabot.online/outfit-image?avatar_id={avatar_id}&clothes={clothes}"
BANNER_API_URL = "https://image.killersharmabot.online/banner-image?headPic={headPic}&bannerId={bannerId}&name={name}&level={level}&guild={guild}&pinId={pinId}&celebrity={celebrity}&frame={frame}"
AVATAR_API_URL = "https://ffoutfitapis.vercel.app/avatar-image?uid={uid}&region={region}&key=99day"  # Keeping old API as fallback

# ============ LOGGING ============
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ HELPER FUNCTIONS ============

def is_valid_uid(uid):
    return uid.isdigit() and 8 <= len(uid) <= 11

def escape_markdown(text):
    """Escape special MarkdownV2 characters"""
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in str(text)])

def format_timestamp(ts):
    """Format timestamp to readable date"""
    try:
        if ts and ts != 'ɴ/ᴀ' and ts != '':
            return datetime.utcfromtimestamp(int(ts)).strftime('%d-%m-%Y %H:%M:%S')
        return 'ɴ/ᴀ'
    except:
        return 'ɴ/ᴀ'

def encode_for_url(text):
    """Encode text for URL"""
    if text and text != 'ɴ/ᴀ':
        return urllib.parse.quote(str(text))
    return ''

# ============ API FUNCTIONS ============

def get_player_info(uid):
    """Get player info from API"""
    try:
        url = PLAYER_INFO_API.format(uid=uid)
        logger.info(f"Fetching player info from: {url}")
        
        response = requests.get(url, timeout=15)
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Format 1: Direct basicInfo structure
                if 'basicInfo' in data:
                    basic = data['basicInfo']
                    captain = data.get('captainBasicInfo', {})
                    clan = data.get('clanBasicInfo', {})
                    credit = data.get('creditScoreInfo', {})
                    pet = data.get('petInfo', {})
                    profile = data.get('profileInfo', {})
                    social = data.get('socialInfo', {})
                    
                    # Extract clothes IDs and character ID
                    clothes_ids = profile.get('clothes', [])
                    avatar_id = profile.get('avatarId', '')
                    
                    return {
                        "success": True,
                        # Basic Info
                        "nickname": basic.get('nickname', 'ɴ/ᴀ'),
                        "region": basic.get('region', 'ɴ/ᴀ'),
                        "level": basic.get('level', 'ɴ/ᴀ'),
                        "likes": basic.get('liked', 'ɴ/ᴀ'),
                        "uid": basic.get('accountId', uid),
                        "rank": basic.get('rankingName', 'ɴ/ᴀ'),
                        "rank_points": basic.get('rankingPoints', 'ɴ/ᴀ'),
                        "ban_status": basic.get('banStatus', 'Not Banned'),
                        "title": basic.get('titleName', 'ɴ/ᴀ'),
                        "headpic": basic.get('headPic', 'ɴ/ᴀ'),
                        "headpic_name": basic.get('headPicName', 'ɴ/ᴀ'),
                        "banner": basic.get('bannerName', 'ɴ/ᴀ'),
                        "banner_id": basic.get('bannerId', 'ɴ/ᴀ'),
                        "last_login": basic.get('lastLoginAt', 'ɴ/ᴀ'),
                        "create_at": basic.get('createAt', 'ɴ/ᴀ'),
                        "exp": basic.get('exp', 'ɴ/ᴀ'),
                        "exp_needed": basic.get('expNeeded', 'ɴ/ᴀ'),
                        "level_progress": basic.get('levelProgress', 'ɴ/ᴀ'),
                        "badge_cnt": basic.get('badgeCnt', 'ɴ/ᴀ'),
                        "badge_id": basic.get('badgeId', 'ɴ/ᴀ'),
                        "pin_name": basic.get('pinName', 'ɴ/ᴀ'),
                        "pin_id": basic.get('pinId', 'ɴ/ᴀ'),
                        "equipped_gun": basic.get('equippedGunName', 'ɴ/ᴀ'),
                        "equipped_animation": basic.get('equippedAnimationName', 'ɴ/ᴀ'),
                        "release_version": basic.get('releaseVersion', 'ɴ/ᴀ'),
                        "season_id": basic.get('seasonId', 'ɴ/ᴀ'),
                        "cs_rank": basic.get('csRankingName', 'ɴ/ᴀ'),
                        "max_rank": basic.get('maxRank', 'ɴ/ᴀ'),
                        "prime_level": basic.get('primeLevel', {}).get('level', 'ɴ/ᴀ'),
                        
                        # Profile Info (for outfit)
                        "avatar_id": avatar_id,
                        "clothes_ids": clothes_ids,
                        "clothes_names": profile.get('clothesNames', []),
                        
                        # Captain Info
                        "captain_nickname": captain.get('nickname', 'ɴ/ᴀ'),
                        "captain_uid": captain.get('accountId', 'ɴ/ᴀ'),
                        "captain_level": captain.get('level', 'ɴ/ᴀ'),
                        "captain_likes": captain.get('liked', 'ɴ/ᴀ'),
                        "captain_rank": captain.get('rankingName', 'ɴ/ᴀ'),
                        "captain_banner": captain.get('bannerName', 'ɴ/ᴀ'),
                        "captain_headpic": captain.get('headPicName', 'ɴ/ᴀ'),
                        
                        # Clan Info
                        "clan_name": clan.get('clanName', 'ɴ/ᴀ'),
                        "clan_id": clan.get('clanId', 'ɴ/ᴀ'),
                        "clan_level": clan.get('clanLevel', 'ɴ/ᴀ'),
                        "clan_members": clan.get('memberNum', 'ɴ/ᴀ'),
                        "clan_captain": clan.get('captainId', 'ɴ/ᴀ'),
                        
                        # Credit Score
                        "credit_score": credit.get('creditScore', 'ɴ/ᴀ'),
                        "credit_status": credit.get('rewardState', 'ɴ/ᴀ'),
                        
                        # Pet Info
                        "pet_name": pet.get('petName', 'ɴ/ᴀ'),
                        "pet_level": pet.get('level', 'ɴ/ᴀ'),
                        "pet_skin": pet.get('skinName', 'ɴ/ᴀ'),
                        "pet_skill": pet.get('skillName', 'ɴ/ᴀ'),
                        
                        # Profile Info
                        "avatar_name": profile.get('avatarName', 'ɴ/ᴀ'),
                        "skills": profile.get('equippedSkillsNames', 'ɴ/ᴀ'),
                        
                        # Social Info
                        "language": social.get('language', 'ɴ/ᴀ'),
                        "signature": social.get('signature', 'ɴ/ᴀ'),
                        "time_online": social.get('timeOnline', 'ɴ/ᴀ'),
                        
                        "data": data
                    }
                
                # Format 2: Player wrapper
                elif 'player' in data:
                    player_data = data['player']
                    return {
                        "success": True,
                        "nickname": player_data.get('name', 'ɴ/ᴀ'),
                        "region": player_data.get('region', 'ɴ/ᴀ'),
                        "uid": player_data.get('uid', uid),
                        "data": data
                    }
                
                else:
                    return {"success": False, "error": "Unknown response format"}
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return {"success": False, "error": "Invalid JSON response"}
        else:
            return {"success": False, "error": f"API returned {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Player info error: {e}")
        return {"success": False, "error": str(e)}

def download_image(url):
    """Download image from URL"""
    try:
        logger.info(f"Downloading image from: {url}")
        response = requests.get(url, timeout=15)
        logger.info(f"Image response status: {response.status_code}")
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        logger.error(f"Image download error: {e}")
        return None

# ============ BOT COMMANDS ============

@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    try:
        start_msg = """👋 ʜᴇʟʟᴏ! ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ғʀᴇᴇ ғɪʀᴇ ɪɴғᴏ ʙᴏᴛ.

📝 ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs:

• /info <ᴜɪᴅ> - ɢᴇᴛ ᴄᴏᴍᴘʟᴇᴛᴇ ᴘʟᴀʏᴇʀ ɪɴғᴏ ᴡɪᴛʜ ᴀᴠᴀᴛᴀʀ, ᴏᴜᴛғɪᴛ & ʙᴀɴɴᴇʀ

🔰 ᴄʀᴇᴅɪᴛ: @KILLERSHARMABOT
🔰 ᴅᴇᴠᴇʟᴏᴘᴇʀ: @BugSpyBots

ᴇɴᴊᴏʏ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ !!"""
        
        bot.reply_to(message, start_msg)
    except Exception as e:
        logger.error(f"Start command error: {str(e)}")
        bot.reply_to(message, "❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")

@bot.message_handler(commands=['info'])
def info_command(message):
    """Get complete player info with avatar, outfit & banner"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /info <uid>\nExample: /info 12345678")
            return
            
        uid = parts[1]
        if not is_valid_uid(uid):
            bot.reply_to(message, "ɪɴᴠᴀʟɪᴅ ᴜɪᴅ! ᴜɪᴅ ᴍᴜsᴛ ʙᴇ 8-11 ᴅɪɢɪᴛs.")
            return
            
        processing_msg = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ᴘʟᴀʏᴇʀ ɪɴғᴏ...")
        
        # Get player info
        info = get_player_info(uid)
        
        if not info['success']:
            bot.edit_message_text(
                f"❌ ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴘʟᴀʏᴇʀ ɪɴғᴏ\nError: {info.get('error', 'Unknown error')}",
                processing_msg.chat.id,
                processing_msg.message_id
            )
            return
        
        region = info['region']
        nickname = info['nickname']
        
        # Format timestamps
        last_login = format_timestamp(info.get('last_login'))
        create_at = format_timestamp(info.get('create_at'))
        
        # Build player info text - ALL DATA FROM API
        ban_status = "✅ ɴᴏᴛ ʙᴀɴɴᴇᴅ" if info.get('ban_status') == 'Not Banned' else "❌ ʙᴀɴɴᴇᴅ"
        
        # Build clothes string for outfit URL
        clothes_ids = info.get('clothes_ids', [])
        clothes_str = ','.join(str(c) for c in clothes_ids) if clothes_ids else ''
        avatar_id = info.get('avatar_id', '')
        
        info_text = f"""🎮 ᴘʟᴀʏᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
────────────────────
👤 ɴɪᴄᴋɴᴀᴍᴇ: <code>{escape(info.get('nickname', 'ɴ/ᴀ'))}</code>
🆔 ᴜɪᴅ: <code>{uid}</code>
🌍 ʀᴇɢɪᴏɴ: <code>{info.get('region', 'ɴ/ᴀ')}</code>
📊 ʟᴇᴠᴇʟ: <code>{info.get('level', 'ɴ/ᴀ')}</code>
📈 ʟᴇᴠᴇʟ ᴘʀᴏɢʀᴇss: <code>{info.get('level_progress', 'ɴ/ᴀ')}</code>
⭐ ᴇxᴘ: <code>{info.get('exp', 'ɴ/ᴀ')}</code>
📌 ᴇxᴘ ɴᴇᴇᴅᴇᴅ: <code>{info.get('exp_needed', 'ɴ/ᴀ')}</code>
👍 ʟɪᴋᴇs: <code>{info.get('likes', 'ɴ/ᴀ')}</code>
🏅 ʀᴀɴᴋ: <code>{info.get('rank', 'ɴ/ᴀ')}</code>
⭐ ʀᴀɴᴋ ᴘᴏɪɴᴛs: <code>{info.get('rank_points', 'ɴ/ᴀ')}</code>
🔰 ᴍᴀx ʀᴀɴᴋ: <code>{info.get('max_rank', 'ɴ/ᴀ')}</code>
🏆 ᴄs ʀᴀɴᴋ: <code>{info.get('cs_rank', 'ɴ/ᴀ')}</code>
🔒 ʙᴀɴ sᴛᴀᴛᴜs: <code>{ban_status}</code>
📌 ᴛɪᴛʟᴇ: <code>{info.get('title', 'ɴ/ᴀ')}</code>
🖼️ ʜᴇᴀᴅᴘɪᴄ: <code>{info.get('headpic_name', 'ɴ/ᴀ')}</code>
🎨 ʙᴀɴɴᴇʀ: <code>{info.get('banner', 'ɴ/ᴀ')}</code>
📛 ʙᴀɴɴᴇʀ ɪᴅ: <code>{info.get('banner_id', 'ɴ/ᴀ')}</code>
🎯 ᴘɪɴ: <code>{info.get('pin_name', 'ɴ/ᴀ')}</code>
🔫 ᴇǫᴜɪᴘᴘᴇᴅ ɢᴜɴ: <code>{info.get('equipped_gun', 'ɴ/ᴀ')}</code>
💫 ᴇǫᴜɪᴘᴘᴇᴅ ᴀɴɪᴍᴀᴛɪᴏɴ: <code>{info.get('equipped_animation', 'ɴ/ᴀ')}</code>
🏅 ʙᴀᴅɢᴇ ᴄᴏᴜɴᴛ: <code>{info.get('badge_cnt', 'ɴ/ᴀ')}</code>
📦 ᴘʀɪᴍᴇ ʟᴇᴠᴇʟ: <code>{info.get('prime_level', 'ɴ/ᴀ')}</code>
📱 ʀᴇʟᴇᴀsᴇ ᴠᴇʀsɪᴏɴ: <code>{info.get('release_version', 'ɴ/ᴀ')}</code>
📅 sᴇᴀsᴏɴ: <code>{info.get('season_id', 'ɴ/ᴀ')}</code>
📅 ʟᴀsᴛ ʟᴏɢɪɴ: <code>{last_login}</code>
📆 ᴀᴄᴄᴏᴜɴᴛ ᴄʀᴇᴀᴛᴇᴅ: <code>{create_at}</code>

────────────────────
👑 ᴄʟᴀɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
🏠 ᴄʟᴀɴ ɴᴀᴍᴇ: <code>{escape(info.get('clan_name', 'ɴ/ᴀ'))}</code>
🆔 ᴄʟᴀɴ ɪᴅ: <code>{info.get('clan_id', 'ɴ/ᴀ')}</code>
📊 ᴄʟᴀɴ ʟᴇᴠᴇʟ: <code>{info.get('clan_level', 'ɴ/ᴀ')}</code>
👥 ᴍᴇᴍʙᴇʀs: <code>{info.get('clan_members', 'ɴ/ᴀ')}</code>

────────────────────
💳 ᴄʀᴇᴅɪᴛ sᴄᴏʀᴇ
⭐ ᴄʀᴇᴅɪᴛ sᴄᴏʀᴇ: <code>{info.get('credit_score', 'ɴ/ᴀ')}</code>
📌 sᴛᴀᴛᴜs: <code>{info.get('credit_status', 'ɴ/ᴀ')}</code>

────────────────────
🐾 ᴘᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
🐕 ɴᴀᴍᴇ: <code>{escape(info.get('pet_name', 'ɴ/ᴀ'))}</code>
📊 ʟᴇᴠᴇʟ: <code>{info.get('pet_level', 'ɴ/ᴀ')}</code>
🎨 sᴋɪɴ: <code>{escape(info.get('pet_skin', 'ɴ/ᴀ'))}</code>
⚡ sᴋɪʟʟ: <code>{escape(info.get('pet_skill', 'ɴ/ᴀ'))}</code>

────────────────────
🎭 ᴘʀᴏғɪʟᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
👤 ᴀᴠᴀᴛᴀʀ: <code>{escape(info.get('avatar_name', 'ɴ/ᴀ'))}</code>
🆔 ᴀᴠᴀᴛᴀʀ ɪᴅ: <code>{info.get('avatar_id', 'ɴ/ᴀ')}</code>
👕 ᴄʟᴏᴛʜᴇs: <code>{', '.join(info.get('clothes_names', [])) if info.get('clothes_names') else 'ɴ/ᴀ'}</code>
⚡ sᴋɪʟʟs: <code>{escape(info.get('skills', 'ɴ/ᴀ'))}</code>

────────────────────
👤 ᴄᴀᴘᴛᴀɪɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
👤 ɴᴀᴍᴇ: <code>{escape(info.get('captain_nickname', 'ɴ/ᴀ'))}</code>
🆔 ᴜɪᴅ: <code>{info.get('captain_uid', 'ɴ/ᴀ')}</code>
📊 ʟᴇᴠᴇʟ: <code>{info.get('captain_level', 'ɴ/ᴀ')}</code>
👍 ʟɪᴋᴇs: <code>{info.get('captain_likes', 'ɴ/ᴀ')}</code>
🏅 ʀᴀɴᴋ: <code>{info.get('captain_rank', 'ɴ/ᴀ')}</code>

────────────────────
🌐 sᴏᴄɪᴀʟ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
💬 ʟᴀɴɢᴜᴀɢᴇ: <code>{info.get('language', 'ɴ/ᴀ')}</code>
✍️ sɪɢɴᴀᴛᴜʀᴇ: <code>{escape(info.get('signature', 'ɴ/ᴀ'))}</code>
⏰ ᴛɪᴍᴇ ᴏɴʟɪɴᴇ: <code>{info.get('time_online', 'ɴ/ᴀ')}</code>

────────────────────
🔰 ᴄʀᴇᴅɪᴛ: @KILLERSHARMABOT
🔰 ᴅᴇᴠᴇʟᴏᴘᴇʀ: @SAM_GMR08"""

        # Delete processing message
        bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
        
        # Send player info text first
        bot.send_message(
            message.chat.id,
            info_text,
            parse_mode="HTML"
        )
        
        # Build and download images using NEW APIs
        images_to_send = []
        
        # 1. Outfit Image (NEW API)
        if avatar_id and clothes_str:
            outfit_url = OUTFIT_API_URL.format(
                avatar_id=avatar_id,
                clothes=clothes_str
            )
            outfit_img = download_image(outfit_url)
            if outfit_img:
                images_to_send.append(("👕 ᴏᴜᴛғɪᴛ", outfit_img))
        
        # 2. Banner Image (NEW API)
        headpic = info.get('headpic', '')
        banner_id = info.get('banner_id', '')
        name = encode_for_url(nickname)
        level = info.get('level', '')
        guild = encode_for_url(info.get('clan_name', ''))
        pin_id = info.get('pin_id', '')
        celebrity = ''  # Not available in API response
        frame = ''  # Not available in API response
        
        if headpic and banner_id:
            banner_url = BANNER_API_URL.format(
                headPic=headpic,
                bannerId=banner_id,
                name=name,
                level=level,
                guild=guild,
                pinId=pin_id,
                celebrity=celebrity,
                frame=frame
            )
            banner_img = download_image(banner_url)
            if banner_img:
                images_to_send.append(("🎨 ʙᴀɴɴᴇʀ", banner_img))
        
        # 3. Avatar Image (Old API as fallback)
        if not images_to_send:
            avatar_url = AVATAR_API_URL.format(uid=uid, region=region)
            avatar_img = download_image(avatar_url)
            if avatar_img:
                images_to_send.append(("🖼️ ᴀᴠᴀᴛᴀʀ", avatar_img))
        
        # Send all images
        for caption, img in images_to_send:
            try:
                bot.send_photo(
                    message.chat.id,
                    img,
                    caption=f"{caption}\n👤 {escape(nickname)}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Image send error: {e}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Handle regular text messages (UID only)"""
    try:
        text = message.text.strip()
        if is_valid_uid(text):
            uid = text
            processing_msg = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ᴘʟᴀʏᴇʀ ɪɴғᴏ...")
            
            info = get_player_info(uid)
            
            if info['success']:
                region = info['region']
                nickname = info['nickname']
                
                # Format timestamps
                last_login = format_timestamp(info.get('last_login'))
                create_at = format_timestamp(info.get('create_at'))
                
                # Build player info text
                ban_status = "✅ ɴᴏᴛ ʙᴀɴɴᴇᴅ" if info.get('ban_status') == 'Not Banned' else "❌ ʙᴀɴɴᴇᴅ"
                
                # Build clothes string for outfit URL
                clothes_ids = info.get('clothes_ids', [])
                clothes_str = ','.join(str(c) for c in clothes_ids) if clothes_ids else ''
                avatar_id = info.get('avatar_id', '')
                
                info_text = f"""🎮 ᴘʟᴀʏᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
────────────────────
👤 ɴɪᴄᴋɴᴀᴍᴇ: <code>{escape(info.get('nickname', 'ɴ/ᴀ'))}</code>
🆔 ᴜɪᴅ: <code>{uid}</code>
🌍 ʀᴇɢɪᴏɴ: <code>{info.get('region', 'ɴ/ᴀ')}</code>
📊 ʟᴇᴠᴇʟ: <code>{info.get('level', 'ɴ/ᴀ')}</code>
📈 ʟᴇᴠᴇʟ ᴘʀᴏɢʀᴇss: <code>{info.get('level_progress', 'ɴ/ᴀ')}</code>
⭐ ᴇxᴘ: <code>{info.get('exp', 'ɴ/ᴀ')}</code>
📌 ᴇxᴘ ɴᴇᴇᴅᴇᴅ: <code>{info.get('exp_needed', 'ɴ/ᴀ')}</code>
👍 ʟɪᴋᴇs: <code>{info.get('likes', 'ɴ/ᴀ')}</code>
🏅 ʀᴀɴᴋ: <code>{info.get('rank', 'ɴ/ᴀ')}</code>
⭐ ʀᴀɴᴋ ᴘᴏɪɴᴛs: <code>{info.get('rank_points', 'ɴ/ᴀ')}</code>
🔰 ᴍᴀx ʀᴀɴᴋ: <code>{info.get('max_rank', 'ɴ/ᴀ')}</code>
🏆 ᴄs ʀᴀɴᴋ: <code>{info.get('cs_rank', 'ɴ/ᴀ')}</code>
🔒 ʙᴀɴ sᴛᴀᴛᴜs: <code>{ban_status}</code>
📌 ᴛɪᴛʟᴇ: <code>{info.get('title', 'ɴ/ᴀ')}</code>
🖼️ ʜᴇᴀᴅᴘɪᴄ: <code>{info.get('headpic_name', 'ɴ/ᴀ')}</code>
🎨 ʙᴀɴɴᴇʀ: <code>{info.get('banner', 'ɴ/ᴀ')}</code>
📛 ʙᴀɴɴᴇʀ ɪᴅ: <code>{info.get('banner_id', 'ɴ/ᴀ')}</code>
🎯 ᴘɪɴ: <code>{info.get('pin_name', 'ɴ/ᴀ')}</code>
🔫 ᴇǫᴜɪᴘᴘᴇᴅ ɢᴜɴ: <code>{info.get('equipped_gun', 'ɴ/ᴀ')}</code>
💫 ᴇǫᴜɪᴘᴘᴇᴅ ᴀɴɪᴍᴀᴛɪᴏɴ: <code>{info.get('equipped_animation', 'ɴ/ᴀ')}</code>
🏅 ʙᴀᴅɢᴇ ᴄᴏᴜɴᴛ: <code>{info.get('badge_cnt', 'ɴ/ᴀ')}</code>
📦 ᴘʀɪᴍᴇ ʟᴇᴠᴇʟ: <code>{info.get('prime_level', 'ɴ/ᴀ')}</code>
📱 ʀᴇʟᴇᴀsᴇ ᴠᴇʀsɪᴏɴ: <code>{info.get('release_version', 'ɴ/ᴀ')}</code>
📅 sᴇᴀsᴏɴ: <code>{info.get('season_id', 'ɴ/ᴀ')}</code>
📅 ʟᴀsᴛ ʟᴏɢɪɴ: <code>{last_login}</code>
📆 ᴀᴄᴄᴏᴜɴᴛ ᴄʀᴇᴀᴛᴇᴅ: <code>{create_at}</code>

────────────────────
👑 ᴄʟᴀɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
🏠 ᴄʟᴀɴ ɴᴀᴍᴇ: <code>{escape(info.get('clan_name', 'ɴ/ᴀ'))}</code>
🆔 ᴄʟᴀɴ ɪᴅ: <code>{info.get('clan_id', 'ɴ/ᴀ')}</code>
📊 ᴄʟᴀɴ ʟᴇᴠᴇʟ: <code>{info.get('clan_level', 'ɴ/ᴀ')}</code>
👥 ᴍᴇᴍʙᴇʀs: <code>{info.get('clan_members', 'ɴ/ᴀ')}</code>

────────────────────
💳 ᴄʀᴇᴅɪᴛ sᴄᴏʀᴇ
⭐ ᴄʀᴇᴅɪᴛ sᴄᴏʀᴇ: <code>{info.get('credit_score', 'ɴ/ᴀ')}</code>
📌 sᴛᴀᴛᴜs: <code>{info.get('credit_status', 'ɴ/ᴀ')}</code>

────────────────────
🐾 ᴘᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
🐕 ɴᴀᴍᴇ: <code>{escape(info.get('pet_name', 'ɴ/ᴀ'))}</code>
📊 ʟᴇᴠᴇʟ: <code>{info.get('pet_level', 'ɴ/ᴀ')}</code>
🎨 sᴋɪɴ: <code>{escape(info.get('pet_skin', 'ɴ/ᴀ'))}</code>
⚡ sᴋɪʟʟ: <code>{escape(info.get('pet_skill', 'ɴ/ᴀ'))}</code>

────────────────────
🎭 ᴘʀᴏғɪʟᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
👤 ᴀᴠᴀᴛᴀʀ: <code>{escape(info.get('avatar_name', 'ɴ/ᴀ'))}</code>
🆔 ᴀᴠᴀᴛᴀʀ ɪᴅ: <code>{info.get('avatar_id', 'ɴ/ᴀ')}</code>
👕 ᴄʟᴏᴛʜᴇs: <code>{', '.join(info.get('clothes_names', [])) if info.get('clothes_names') else 'ɴ/ᴀ'}</code>
⚡ sᴋɪʟʟs: <code>{escape(info.get('skills', 'ɴ/ᴀ'))}</code>

────────────────────
👤 ᴄᴀᴘᴛᴀɪɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
👤 ɴᴀᴍᴇ: <code>{escape(info.get('captain_nickname', 'ɴ/ᴀ'))}</code>
🆔 ᴜɪᴅ: <code>{info.get('captain_uid', 'ɴ/ᴀ')}</code>
📊 ʟᴇᴠᴇʟ: <code>{info.get('captain_level', 'ɴ/ᴀ')}</code>
👍 ʟɪᴋᴇs: <code>{info.get('captain_likes', 'ɴ/ᴀ')}</code>
🏅 ʀᴀɴᴋ: <code>{info.get('captain_rank', 'ɴ/ᴀ')}</code>

────────────────────
🌐 sᴏᴄɪᴀʟ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
💬 ʟᴀɴɢᴜᴀɢᴇ: <code>{info.get('language', 'ɴ/ᴀ')}</code>
✍️ sɪɢɴᴀᴛᴜʀᴇ: <code>{escape(info.get('signature', 'ɴ/ᴀ'))}</code>
⏰ ᴛɪᴍᴇ ᴏɴʟɪɴᴇ: <code>{info.get('time_online', 'ɴ/ᴀ')}</code>

────────────────────
🔰 ᴄʀᴇᴅɪᴛ: @KILLERSHARMABOT
🔰 ᴅᴇᴠᴇʟᴏᴘᴇʀ: @BugSpyBots"""
                
                # Delete processing message
                bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                
                # Send player info text first
                bot.send_message(
                    message.chat.id,
                    info_text,
                    parse_mode="HTML"
                )
                
                # Build and download images using NEW APIs
                images_to_send = []
                
                # 1. Outfit Image (NEW API)
                if avatar_id and clothes_str:
                    outfit_url = OUTFIT_API_URL.format(
                        avatar_id=avatar_id,
                        clothes=clothes_str
                    )
                    outfit_img = download_image(outfit_url)
                    if outfit_img:
                        images_to_send.append(("👕 ᴏᴜᴛғɪᴛ", outfit_img))
                
                # 2. Banner Image (NEW API)
                headpic = info.get('headpic', '')
                banner_id = info.get('banner_id', '')
                name = encode_for_url(nickname)
                level = info.get('level', '')
                guild = encode_for_url(info.get('clan_name', ''))
                pin_id = info.get('pin_id', '')
                celebrity = ''
                frame = ''
                
                if headpic and banner_id:
                    banner_url = BANNER_API_URL.format(
                        headPic=headpic,
                        bannerId=banner_id,
                        name=name,
                        level=level,
                        guild=guild,
                        pinId=pin_id,
                        celebrity=celebrity,
                        frame=frame
                    )
                    banner_img = download_image(banner_url)
                    if banner_img:
                        images_to_send.append(("🎨 ʙᴀɴɴᴇʀ", banner_img))
                
                # 3. Avatar Image (Old API as fallback)
                if not images_to_send:
                    avatar_url = AVATAR_API_URL.format(uid=uid, region=region)
                    avatar_img = download_image(avatar_url)
                    if avatar_img:
                        images_to_send.append(("🖼️ ᴀᴠᴀᴛᴀʀ", avatar_img))
                
                # Send all images
                for caption, img in images_to_send:
                    try:
                        bot.send_photo(
                            message.chat.id,
                            img,
                            caption=f"{caption}\n👤 {escape(nickname)}",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.error(f"Image send error: {e}")
                
            else:
                bot.edit_message_text(
                    f"❌ ᴘʟᴀʏᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ ᴏʀ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ\nError: {info.get('error', 'Unknown error')}",
                    processing_msg.chat.id,
                    processing_msg.message_id
                )
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

# ============ START BOT ============
if __name__ == "__main__":
    print("🤖 Bot started successfully!")
    print("📡 Using APIs from @KILLERSHARMABOT")
    print("🔰 Developer: @BugSpyBots")
    print("📝 Command: /info <uid> or just send UID")
    print("📋 Shows ALL data from API response")
    print("🖼️ Using new image APIs from image.killersharmabot.online")
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Bot error: {e}")