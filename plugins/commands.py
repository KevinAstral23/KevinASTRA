import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, CHNL_LNK, GRP_LNK, REQST_CHANNEL, SUPPORT_CHAT_ID, MAX_B_TN, IS_VERIFY, HOW_TO_VERIFY
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, send_all
from database.connections_mdb import active_connection
import re
import json
import base64
logger = logging.getLogger(__name__)

BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[
                    InlineKeyboardButton('🧸 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('🕴️ 𝖬𝗒 𝖮𝗐𝗇𝖾𝗋', callback_data="owner_info"),
                    InlineKeyboardButton('🔔 𝖡𝖮𝖳 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url=GRP_LNK)
                ],[
                    InlineKeyboardButton('🖇️ 𝖧𝖾𝗅𝗉', callback_data='help'),
                    InlineKeyboardButton('📜 𝖠𝖻𝗈𝗎𝗍', callback_data='about'),
                    InlineKeyboardButton('🔍 𝖨𝗇 𝗅𝗂𝗇𝖾 𝖲𝖾𝖺𝗋𝖼𝗁', switch_inline_query_current_chat='')
                ],[
                    InlineKeyboardButton('🔔 𝖡𝖮𝖳 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url=CHNL_LNK)
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
                    InlineKeyboardButton('🧸 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('🕴️ 𝖬𝗒 𝖮𝗐𝗇𝖾𝗋', callback_data="owner_info"),
                    InlineKeyboardButton('🔔 𝖡𝖮𝖳 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url=GRP_LNK)
                ],[
                    InlineKeyboardButton('🖇️ 𝖧𝖾𝗅𝗉', callback_data='help'),
                    InlineKeyboardButton('📜 𝖠𝖻𝗈𝗎𝗍', callback_data='about'),
                    InlineKeyboardButton('🔍 𝖨𝗇 𝗅𝗂𝗇𝖾 𝖲𝖾𝖺𝗋𝖼𝗁', switch_inline_query_current_chat='')
                ],[
                    InlineKeyboardButton('🔔 𝖡𝖮𝖳 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url=CHNL_LNK)
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("𝖬𝖺𝗌𝗍𝖾𝗋 𝖬𝖺𝗄𝖾 𝖲𝗎𝗋𝖾 𝖨𝗆 𝖠𝖽𝗆𝗂𝗇 𝖮𝗇 𝖥𝗈𝗋𝖼𝖾𝖲𝗎𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅")
            return
        btn = [
            [
                InlineKeyboardButton(
                    "‼️ 𝖩𝗈𝗂𝗇 𝖮𝗎𝗋 𝖬𝗈𝗏𝗂𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 ‼️", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton("↻ 𝖳𝗋𝗒 𝖠𝗀𝖺𝗂𝗇", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("↻ 𝖳𝗋𝗒 𝖠𝗀𝖺𝗂𝗇", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**𝖨'𝗆 𝗌𝗈𝗋𝗋𝗒, 𝖻𝗎𝗍 𝗒𝗈𝗎 𝖽𝗈 𝗇𝗈𝗍 𝗁𝖺𝗏𝖾 𝖺𝖼𝖼𝖾𝗌𝗌 𝗍𝗈 𝗍𝗁𝖾 𝗆𝗈𝗏𝗂𝖾 𝖿𝗂𝗅𝖾 𝖺𝗌 𝗒𝗈𝗎 𝖺𝗋𝖾 𝗇𝗈𝗍 𝗂𝗇 𝗈𝗎𝗋 𝖬𝗈𝗏𝗂𝖾 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗉𝗋𝗈𝗏𝗂𝖽𝖾𝖽 𝖻𝖾𝗅𝗈𝗐...\n\nIғ 𝗅𝖾𝖺𝗌𝖾 𝖾𝗇𝗌𝗎𝗋𝖾 𝗍𝗁𝖺𝗍 𝗒𝗈𝗎 𝗃𝗈𝗂𝗇 𝗍𝗁𝖾 𝖻𝖺𝖼𝗄𝗎𝗉 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗍𝗈 𝗋𝖾𝖼𝖾𝗂𝗏𝖾 𝗍𝗁𝖾 𝗆𝗈𝗏𝗂𝖾 𝖿𝗂𝗅𝖾...\n\n. 𝖳𝗁𝖺𝗇𝗄 𝗒𝗈𝗎 𝖿𝗈𝗋 𝗒𝗈𝗎𝗋 𝗎𝗇𝖽𝖾𝗋𝗌𝗍𝖺𝗇𝖽𝗂𝗇𝗀...**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
                    InlineKeyboardButton('🧸 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('🕴️ 𝖬𝗒 𝖮𝗐𝗇𝖾𝗋', callback_data="owner_info"),
                    InlineKeyboardButton('🔔 𝖡𝖮𝖳 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url=GRP_LNK)
                ],[
                    InlineKeyboardButton('🖇️ 𝖧𝖾𝗅𝗉', callback_data='help'),
                    InlineKeyboardButton('📜 𝖠𝖻𝗈𝗎𝗍', callback_data='about'),
                    InlineKeyboardButton('🔍 𝖨𝗇 𝗅𝗂𝗇𝖾 𝖲𝖾𝖺𝗋𝖼𝗁', switch_inline_query_current_chat='')
                ],[
                    InlineKeyboardButton('🔔 𝖡𝖮𝖳 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url=CHNL_LNK)
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("<b>𝖧𝗈𝗅𝖽 𝖴𝗉 𝖠 𝖡𝖨𝖳...</b>")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("Fᴀɪʟᴇᴅ")
                return await client.send_message(LOG_CHANNEL, "𝖢𝖺𝗇𝗍 𝖮𝗉𝖾𝗇 𝗍𝗁𝗂𝗌.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton('𝖡𝖮𝖳 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url=GRP_LNK),
                          InlineKeyboardButton('𝖬𝗈𝗏𝗂𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅', url=CHNL_LNK)
                       ],[
                          InlineKeyboardButton("𝖬𝖺𝗌𝗍𝖾𝗋𝖪𝖤𝖵", url="t.me/k_ASTRA1")
                         ]
                        ]
                    )
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton('𝖡𝖮𝖳 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url=GRP_LNK),
                          InlineKeyboardButton('𝖬𝗈𝗏𝗂𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅', url=CHNL_LNK)
                       ],[
                          InlineKeyboardButton("𝖬𝖺𝗌𝗍𝖾𝗋𝖪𝖤𝖵", url="t.me/k_ASTRA1")
                         ]
                        ]
                    )
                )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("<b>𝖧𝗈𝗅𝖽 𝖴𝗉 𝖠 𝖡𝖨𝖳...</b>")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()

    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        fileid = data.split("-", 3)[3]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>𝖨𝗍𝗌 𝖾𝗂𝗍𝗁𝖾𝗋 𝗂𝗇𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝖾𝗑𝗉𝗂𝗋𝖾𝖽</b>",
                protect_content=True if PROTECT_CONTENT else False
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            if fileid == "send_all":
                btn = [[
                    InlineKeyboardButton("𝖦𝖾𝗍 𝖥𝗂𝗅𝖾", callback_data=f"checksub#send_all")
                ]]
                await verify_user(client, userid, token)
                await message.reply_text(
                    text=f"<b>𝖧𝖾𝗒 {message.from_user.mention}, 𝖸𝗈𝗎𝗋𝖾 𝖭𝗈𝗐 𝖵𝖤𝖱𝖨𝖥𝖨𝖤𝖣!!!\n𝖭𝗈𝗐 𝖸𝗈𝗎 𝖧𝖺𝗏𝖾 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 𝖠𝖼𝖼𝖾𝗌𝗌 𝖥𝗈𝗋 𝖺𝗅𝗅 𝖿𝗂𝗅𝖾𝗌 𝖳𝗂𝗅𝗅 𝗍𝗁𝖾 𝗇𝖾𝗑𝗍 𝗏𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝗐𝗁𝗂𝖼𝗁 𝗂𝗌 𝖺𝖿𝗍𝖾𝗋 𝗁𝖺𝗅𝖿 𝖺 𝖽𝖺𝗒.</b>",
                    protect_content=True if PROTECT_CONTENT else False,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            btn = [[
                InlineKeyboardButton("Get File", url=f"https://telegram.me/{temp.U_NAME}?start=files_{fileid}")
            ]]
            await message.reply_text(
                text=f"<b>𝖧𝖾𝗒 {message.from_user.mention}, 𝖸𝗈𝗎𝗋𝖾 𝖭𝗈𝗐 𝖵𝖤𝖱𝖨𝖥𝖨𝖤𝖣!!!\n𝖭𝗈𝗐 𝖸𝗈𝗎 𝖧𝖺𝗏𝖾 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 𝖠𝖼𝖼𝖾𝗌𝗌 𝖥𝗈𝗋 𝖺𝗅𝗅 𝖿𝗂𝗅𝖾𝗌 𝖳𝗂𝗅𝗅 𝗍𝗁𝖾 𝗇𝖾𝗑𝗍 𝗏𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝗐𝗁𝗂𝖼𝗁 𝗂𝗌 𝖺𝖿𝗍𝖾𝗋 𝗁𝖺𝗅𝖿 𝖺 𝖽𝖺𝗒</b>",
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await verify_user(client, userid, token)
            return
        else:
            return await message.reply_text(
                text="<b>𝖨𝗍𝗌 𝖾𝗂𝗍𝗁𝖾𝗋 𝗂𝗇𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝖾𝗑𝗉𝗂𝗋𝖾𝖽</b>",
                protect_content=True if PROTECT_CONTENT else False
            )

    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            if IS_VERIFY and not await check_verification(client, message.from_user.id):
                btn = [[
                    InlineKeyboardButton("𝖵𝖾𝗋𝗂𝖿𝗒", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                    InlineKeyboardButton("𝖧𝗈𝗐 𝗍𝗈 𝗏𝖾𝗋𝗂𝖿𝗒", url=HOW_TO_VERIFY)
                ]]
                await message.reply_text(
                    text="<b>𝖧𝖾𝗒 {message.from_user.mention}, 𝖸𝗈𝗎𝗋𝖾 𝖭𝗈𝗐 𝖵𝖤𝖱𝖨𝖥𝖨𝖤𝖣!!!\n𝖭𝗈𝗐 𝖸𝗈𝗎 𝖧𝖺𝗏𝖾 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 𝖠𝖼𝖼𝖾𝗌𝗌 𝖥𝗈𝗋 𝖺𝗅𝗅 𝖿𝗂𝗅𝖾𝗌 𝖳𝗂𝗅𝗅 𝗍𝗁𝖾 𝗇𝖾𝗑𝗍 𝗏𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝗐𝗁𝗂𝖼𝗁 𝗂𝗌 𝖺𝖿𝗍𝖾𝗋 𝗁𝖺𝗅𝖿 𝖺 𝖽𝖺𝗒.</b>",
                    protect_content=True if PROTECT_CONTENT else False,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup(
                    [
                     [
                      InlineKeyboardButton('𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖦𝗋𝗈𝗎𝗉', url=GRP_LNK),
                      InlineKeyboardButton('U𝗉𝖽𝖺𝗍𝖾𝗌 𝖢𝗁𝖺𝗇𝗇𝖾𝗅', url=CHNL_LNK)
                   ],[
                      InlineKeyboardButton("𝖬𝖺𝗌𝗍𝖾𝗋𝖪𝖤𝖵", url="t.me/k_ASTRA1")
                     ]
                    ]
                )
            )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply(𝖲𝖧𝖨𝖨 𝖣𝗈𝖾𝗌𝗇𝗍 𝖤𝖷𝖨𝖲𝖳.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    if IS_VERIFY and not await check_verification(client, message.from_user.id):
        btn = [[
            InlineKeyboardButton("𝖵𝖾𝗋𝗂𝖿𝗒", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
            InlineKeyboardButton("𝖧𝗈𝗐 𝗍𝗈 𝗏𝖾𝗋𝗂𝖿𝗒", url=HOW_TO_VERIFY)
        ]]
        await message.reply_text(
            text="<b>𝖸𝗈𝗎𝗋𝖾 𝖭𝖮𝖳 𝖵𝖾𝗋𝗂𝖿𝗂𝖾𝖽!\n𝖪𝗂𝗇𝖽𝗅𝗒 𝖵𝖾𝗋𝗂𝖿𝗒 𝖲𝗈 𝗍𝗁𝖺𝗍 𝗒𝗈𝗎 𝖼𝖺𝗇 𝗀𝖾𝗍 𝖺𝖼𝖼𝖾𝗌𝗌 𝗍𝗈 𝗎𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 𝖿𝗂𝗅𝖾𝗌 𝖿𝗈𝗋 𝗁𝖺𝗅𝖿 𝖺 𝖽𝖺𝗒!</b>",
            protect_content=True if PROTECT_CONTENT else False,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
        reply_markup=InlineKeyboardMarkup(
            [
             [
              InlineKeyboardButton('𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖦𝗋𝗈𝗎𝗉', url=GRP_LNK),
              InlineKeyboardButton('U𝗉𝖽𝖺𝗍𝖾𝗌 𝖢𝗁𝖺𝗇𝗇𝖾𝗅', url=CHNL_LNK)
           ],[
              InlineKeyboardButton("𝖬𝖺𝗌𝗍𝖾𝗋𝖪𝖤𝖵", url="t.me/k_ASTRA1")
             ]
            ]
        )
    )
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("𝖴𝗇𝖾𝗑𝖼𝗉𝖾𝖼𝗍𝖾𝖽 𝖳𝗒𝗉𝖾 𝖮𝖥 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌")

    text = '📑 **𝖨𝗇𝖽𝖾𝗑𝖾𝖽 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌/𝖦𝗋𝗈𝗎𝗉𝗌**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('Logs.txt')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀...⏳", quote=True)
    else:
        await message.reply('𝖱𝖾𝗉𝗅𝗒 𝗐𝗂𝗍𝗁 𝗍𝗁𝖾 𝖿𝗂𝗅𝖾 𝗐𝗁𝗂𝖼𝗁 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝖽𝖾𝗅𝖾𝗍𝖾', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('𝖳𝗁𝗂𝗌 𝗍𝗒𝗉𝖾 𝗈𝖿 𝖿𝗈𝗋𝗆𝖺𝗍 𝗂𝗌 𝗇𝗈𝗍 𝗌𝗎𝗉𝗉𝗈𝗋𝗍𝖾𝖽')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('𝖦𝗈𝗍 𝗋𝗂𝖽 𝗈𝖿 𝗂𝗍 𝗐𝖾 𝗀𝗈𝗈𝖽 𝗇𝗈𝗐?')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('𝖦𝗈𝗍 𝗋𝗂𝖽 𝗈𝖿 𝗂𝗍 𝗐𝖾 𝗀𝗈𝗈𝖽 𝗇𝗈𝗐?')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('𝖦𝗈𝗍 𝗋𝗂𝖽 𝗈𝖿 𝗂𝗍 𝗐𝖾 𝗀𝗈𝗈𝖽 𝗇𝗈𝗐?')
            else:
                await msg.edit('𝖮𝖯𝖯𝖲 𝖢𝖺𝗇𝗍 𝖿𝗂𝗇𝖽 𝗂𝗍')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        '𝖳𝗁𝗂𝗌 𝗐𝗂𝗅𝗅 𝖽𝖾𝗅𝖾𝗍𝖾 𝖺𝗅𝗅 𝗂𝗇𝖽𝖾𝗑𝖾𝖽 𝖿𝗂𝗅𝖾𝗌.\n𝖠𝖱𝖤 𝖸𝖮𝖴 𝖲𝖴𝖱𝖤',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="𝖸𝖤𝖲", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="𝖢𝖠𝖭𝖢𝖤𝖫", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer("𝖠𝖫𝖫 𝖦𝖮𝖭𝖤!!!")
    await message.message.edit('𝖲𝗎𝖼𝖼𝖾𝗌𝖿𝗎𝗅𝗅𝗒 𝖽𝖾𝗅𝖾𝗍𝖾𝖽 𝖾𝗏𝖾𝗋𝗒𝗍𝗁𝗂𝗇𝗀')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"𝖸𝗈𝗎𝗋𝖾 𝖠𝗇𝗈𝗇𝗒𝗆𝗈𝗎𝗌 𝖣𝖴𝖬𝖡𝖮 𝗎𝗌𝖾 /connect {message.chat.id} 𝖨𝖭𝖯𝖬")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("𝖬𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝖨𝗆 𝗉𝗋𝖾𝗌𝖾𝗇𝗍 𝗂𝗇 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉!", quote=True)
                return
        else:
            await message.reply_text("𝖨𝗆 𝗇𝗈𝗍 𝖼𝗈𝗇𝗇𝖾𝖼𝗍𝖾𝖽 𝗍𝗈 𝖺𝗇𝗒 𝗀𝗋𝗈𝗎𝗉𝗌", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return
    
    settings = await get_settings(grp_id)

    try:
        if settings['max_btn']:
            settings = await get_settings(grp_id)
    except KeyError:
        await save_group_settings(grp_id, 'max_btn', False)
        settings = await get_settings(grp_id)
    if 'is_shortlink' not in settings.keys():
        await save_group_settings(grp_id, 'is_shortlink', False)
    else:
        pass

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    '𝖥𝗂𝗅𝗍𝖾𝗋 𝖡𝗎𝗍𝗍𝗈𝗇',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '𝖲𝗂𝗇𝗀𝗅𝖾' if settings["button"] else '𝖣𝖮𝖴𝖡𝖫𝖤',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝖥𝗂𝗅𝖾 𝗌𝖾𝗇𝖽 𝗆𝗈𝖽𝖾',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '𝖬𝖺𝗇𝗎𝖺𝗅 𝖲𝗍𝖺𝗋𝗍' if settings["botpm"] else '𝖠𝗎𝗍𝗈 𝖲𝖾𝗇𝖽',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝖯𝗋𝗈𝗍𝖾𝖼𝗍 𝖢𝗈𝗇𝗍𝖾𝗇𝗍',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ 𝖮𝖭' if settings["file_secure"] else '✘ 𝖮𝖥𝖥',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Iᴍᴅʙ',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ 𝖮𝖭' if settings["imdb"] else '✘ 𝖮𝖥𝖥',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝖲𝖯𝖤𝖫𝖫 𝖢𝖧𝖤𝖢𝖪',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ 𝖮𝖭' if settings["spell_check"] else '✘ 𝖮𝖥𝖥',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝖬𝖲𝖦',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ 𝖮𝖭' if settings["welcome"] else '✘ O𝖥𝖥',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10 𝖬𝗂𝗇𝗌' if settings["auto_delete"] else '✘ O𝖥𝖥',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝖠𝗎𝗍𝗈 𝖥𝗂𝗅𝗍𝖾𝗋',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ 𝖮𝖭' if settings["auto_ffilter"] else '✘ 𝖮𝖥𝖥',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝖬𝖠𝖷 𝖡𝗎𝗍𝗍𝗈𝗇𝗌',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10' if settings["max_btn"] else f'{MAX_B_TN}',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝖲𝗁𝗈𝗋𝗍 𝖫𝗂𝗇𝗄',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ 𝖮𝖭' if settings["is_shortlink"] else '✘ 𝖮𝖥𝖥',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
            ],
        ]

        btn = [[
                InlineKeyboardButton("𝖮𝖯𝖤𝖭 𝖧𝖤𝖱𝖤 ↓", callback_data=f"opnsetgrp#{grp_id}"),
                InlineKeyboardButton("𝖮𝖯𝖤𝖭 𝖨𝖭 𝖯𝖬 ⇲", callback_data=f"opnsetpm#{grp_id}")
              ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply_text(
                text="<b>𝖣𝗈 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗈𝗉𝖾𝗇 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌 𝗁𝖾𝗋𝖾?</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )
        else:
            await message.reply_text(
                text=f"<b>𝖢𝗁𝖺𝗇𝗀𝖾 𝖸𝗈𝗎𝗋 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌 {title} 𝖠𝗌 𝗒𝗈𝗎 𝗐𝗂𝗌𝗁</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )



@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("𝖢𝗁𝖾𝖼𝗄𝗂𝗇𝗀 𝖳𝖾𝗆𝗉𝗅𝖺𝗍𝖾...")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"𝖸𝗈𝗎𝗋𝖾 𝖠𝗇𝗈𝗇𝗒𝗆𝗈𝗎𝗌 𝖣𝖴𝖬𝖡𝖮 𝗎𝗌𝖾 /connect {message.chat.id} 𝖨𝖭 𝖯𝖬")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("𝖬𝖺𝗄𝖾 𝖲𝗎𝗋𝖾 𝖨𝗆 𝖨𝗇 𝗒𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉", quote=True)
                return
        else:
            await message.reply_text("𝖨𝗆 𝗇𝗈𝗍 𝖼𝗈𝗇𝗇𝖾𝖼𝗍𝖾𝖽 𝗍𝗈 𝖺𝗇𝗒 𝗀𝗋𝗈𝗎𝗉𝗌", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("Nᴏ Iɴᴘᴜᴛ!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"𝖲𝗎𝖼𝖼𝖾𝗌𝖿𝗎𝗅𝗅𝗒 𝖢𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝖾𝗆𝗉𝗅𝖺𝗍𝖾 𝖿𝗈𝗋 {title} 𝗍𝗈:\n\n{template}")


@Client.on_message((filters.command(["request", "Request"]) | filters.regex("#request") | filters.regex("#Request")) & filters.group)
async def requests(bot, message):
    if REQST_CHANNEL is None or SUPPORT_CHAT_ID is None: return # Must add REQST_CHANNEL and SUPPORT_CHAT_ID to use this feature
    if message.reply_to_message and SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.reply_to_message.text
        try:
            if REQST_CHANNEL is not None:
                btn = [[
                        InlineKeyboardButton('𝖵𝗂𝖾𝗐 𝖱𝖾𝗊𝗎𝖾𝗌𝗍', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('𝖲𝗁𝗈𝗐 𝖮𝗉𝗍𝗂𝗈𝗇𝗌', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋 : {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾 : {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('𝖵𝗂𝖾𝗐 𝖱𝖾𝗊𝗎𝖾𝗌𝗍', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('𝖲𝗁𝗈𝗐 𝖮𝗉𝗍𝗂𝗈𝗇𝗌', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋 : {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾 : {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>𝖸𝗈𝗎 𝗆𝗎𝗌𝗍 𝗍𝗒𝗉𝖾 𝗒𝗈𝗎𝗋 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 [𝖬𝗂𝗇𝗂𝗆𝗎𝗆 𝗍𝗁𝗋𝖾𝖾 𝖢𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌]. 𝖱𝖾𝗊𝗎𝖾𝗌𝗍𝗌 𝖢𝖺𝗇𝗍 𝖻𝖾 𝖾𝗆𝗉𝗍𝗒.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            pass
        
    elif SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.text
        keywords = ["#request", "/request", "#Request", "/Request"]
        for keyword in keywords:
            if keyword in content:
                content = content.replace(keyword, "")
        try:
            if REQST_CHANNEL is not None and len(content) >= 3:
                btn = [[
                        InlineKeyboardButton('𝖵𝗂𝖾𝗐 𝖱𝖾𝗊𝗎𝖾𝗌𝗍', url=f"{message.link}"),
                        InlineKeyboardButton('𝖲𝗁𝗈𝗐 𝖮𝗉𝗍𝗂𝗈𝗇𝗌', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋 : {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾 : {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('𝖵𝗂𝖾𝗐 𝖱𝖾𝗊𝗎𝖾𝗌', url=f"{message.link}"),
                        InlineKeyboardButton('𝖲𝗁𝗈𝗐 𝖮𝗉𝗍𝗂𝗈𝗇𝗌', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋 : {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾 : {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>𝖸𝗈𝗎 𝗆𝗎𝗌𝗍 𝗍𝗒𝗉𝖾 𝗒𝗈𝗎𝗋 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 [𝖬𝗂𝗇𝗂𝗆𝗎𝗆 𝗍𝗁𝗋𝖾𝖾 𝖢𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌]. 𝖱𝖾𝗊𝗎𝖾𝗌𝗍𝗌 𝖢𝖺𝗇𝗍 𝖻𝖾 𝖾𝗆𝗉𝗍𝗒.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"𝖤𝗋𝗋𝗈𝗋: {e}")
            pass

    else:
        success = False
    
    if success:
        btn = [[
                InlineKeyboardButton('𝖵𝗂𝖾𝗐 𝖱𝖾𝗊𝗎𝖾𝗌𝗍', url=f"{reported_post.link}")
              ]]
        await message.reply_text("<b>𝖸𝗈𝗎𝗋 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖺𝖽𝖽𝖾𝖽 𝗉𝗅𝖾𝖺𝗌𝖾 𝗐𝖺𝗂𝗍.</b>", reply_markup=InlineKeyboardMarkup(btn))

        
@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Usᴇʀs Sᴀᴠᴇᴅ Iɴ DB Aʀᴇ:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>𝖸𝗈𝗎𝗋 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝗎𝖼𝖼𝖾𝗌𝖿𝗎𝗅𝗅𝗒 𝗌𝖾𝗇𝗍 𝗍𝗈 {user.mention}.</b>")
            else:
                await message.reply_text("<b>𝖳𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗁𝖺𝗌𝗇𝗍 𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝗍𝗁𝗂𝗌 𝖻𝗈𝗍!</b>")
        except Exception as e:
            await message.reply_text(f"<b>𝖤𝗋𝗋𝗈𝗋: {e}</b>")
    else:
        await message.reply_text("<b>𝖴𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖺𝗌 𝖺 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺𝗇𝗒 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗁𝖾 𝗍𝖺𝗋𝗀𝖾𝗍 𝖨𝖣 𝖾𝗀:: /send 𝗎𝗌𝖾𝗋𝖨𝖣</b>")

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>𝖧𝖤𝖸!!! {message.from_user.mention}, 𝖳𝗁𝗂𝗌 𝖢𝗈𝗆𝗆𝖺𝗇𝖽 𝗐𝗈𝗇𝗍 𝗐𝗈𝗋𝗄 𝗂𝗇 𝗀𝗋𝗈𝗎𝗉𝗌 𝗂𝗍 𝗈𝗇𝗅𝗒 𝗐𝗈𝗋𝗄𝗌 𝗂𝗇 𝖯𝖬</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>𝖧𝖤𝖸!!! {message.from_user.mention}, 𝗀𝗂𝗏𝖾 𝗆𝖾 𝖺 𝗄𝖾𝗒𝗐𝗈𝗋𝖽 𝖺𝗅𝗈𝗆𝗀 𝗐𝗂𝗍𝗁 𝗍𝗁𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝗍𝗈 𝖽𝖾𝗅𝖾𝗍𝖾 𝖿𝗂𝗅𝖾𝗌.</b>")
    btn = [[
       InlineKeyboardButton("𝖸𝖤𝖲! 𝖢𝗈𝗇𝗍𝗂𝗇𝗎𝖾", callback_data=f"killfilesdq#{keyword}")
       ],[
       InlineKeyboardButton("𝖭𝖮 𝖠𝖻𝗈𝗋𝗍 𝗈𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇", callback_data="close_data")
    ]]
    await message.reply_text(
        text="<b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ? Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ?\n\nNᴏᴛᴇ:- Tʜɪs ᴄᴏᴜʟᴅ ʙᴇ ᴀ ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("shortlink") & filters.user(ADMINS))
async def shortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>𝖧𝖤𝖸!!! {message.from_user.mention}, 𝖳𝗁𝗂𝗌 𝖢𝗈𝗆𝗆𝖺𝗇𝖽 𝗐𝗈𝗇𝗍 𝗐𝗈𝗋𝗄 𝗂𝗇 𝗀𝗋𝗈𝗎𝗉𝗌 𝗂𝗍 𝗈𝗇𝗅𝗒 𝗐𝗈𝗋𝗄𝗌 𝗂𝗇 𝖦𝖱𝖮𝖴𝖯𝖲!</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>𝖸𝗈𝗎 𝖽𝗈𝗇𝗍 𝗁𝖺𝗏𝖾 𝖺𝖼𝖼𝖾𝗌𝗌 𝗍𝗈 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽!</b>")
    else:
        pass
    try:
        command, shortlink_url, api = data.split(" ")
    except:
        return await message.reply_text("<b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽 𝖨𝗇𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝖾 :(\n\n𝖦𝗂𝗏𝖾 𝗆𝖾 𝖺 𝗌𝗁𝗈𝗋𝗍 𝗅𝗂𝗇𝗄 𝖺𝗇𝖽 𝖠𝖯𝖨 𝖺𝗅𝗈𝗇𝗀 𝗐𝗂𝗍𝗁 𝗍𝗁𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽!\n\𝖿𝗈𝗋𝗆𝖺𝗍: <code>/shortlink shorturllink.in 95a8195c40d31e0c3b6baa68813fcecb1239f2e9</code></b>")
    reply = await message.reply_text("<b>𝖯𝗅𝖾𝖺𝗌𝖾 𝖶𝖺𝗂𝗍...</b>")
    await save_group_settings(grpid, 'shortlink', shortlink_url)
    await save_group_settings(grpid, 'shortlink_api', api)
    await save_group_settings(grpid, 'is_shortlink', True)
    await reply.edit_text(f"<b>𝖲𝗎𝖼𝖼𝖾𝗌𝖿𝗎𝗅𝗅𝗒 𝖠𝖣𝖣𝖤𝖣 𝖲𝗁𝗈𝗋𝗍𝖫𝗂𝗇𝗄 𝖠𝖯𝖨 𝖿𝗈𝗋 {title}.\n\n𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖲𝗁𝗈𝗋𝗍𝖫𝗂𝗇𝗄 𝖶𝖾𝖻𝗌𝗂𝗍𝖾: <code>{shortlink_url}</code>\n𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖠𝖯𝖨: <code>{api}</code></b>")
