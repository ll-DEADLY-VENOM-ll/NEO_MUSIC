import uvloop

uvloop.install()

import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.errors.exceptions.bad_request_400 import BadRequest # Import BadRequest specifically
import config

from ..logging import LOGGER


class ChampuBot(Client):
    def __init__(self):
        LOGGER(__name__).info(f"sᴛᴀʀᴛɪɴɢ ʙᴏᴛ...")
        super().__init__(
            "ChampuMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.mention = self.me.mention

        LOGGER(__name__).info(f"Bot info obtained: Name={self.name}, Username=@{self.username}, ID={self.id}")

        # Create the inline button for adding to groups
        add_to_group_button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏",
                        url=f"https://t.me/{self.username}?startgroup=true",
                    )
                ]
            ]
        )

        # --- Logging Group Initialization ---
        if config.LOGGER_ID:
            log_message = f"""
╔════❰𝗪𝗘𝗟𝗖𝗢𝗠𝗘❱════❍⊱❁۪۪
║
║┣⪼🥀ʙᴏᴛ sᴛᴀʀᴛᴇᴅ🎉
║
║┣⪼ {self.name}
║
║┣⪼🎈ɪᴅ:- `{self.id}` 
║
║┣⪼🎄@{self.username} 
║ 
║┣⪼💖ᴛʜᴀɴᴋs ғᴏʀ ᴜsɪɴɢ😍
║
╚════════════════❍⊱❁
"""
            LOGGER(__name__).info(f"Attempting to send startup message to LOGGER_ID: {config.LOGGER_ID}")
            try:
                # First, try to send photo with caption
                await self.send_photo(
                    chat_id=config.LOGGER_ID,
                    photo=config.START_IMG_URL,
                    caption=log_message,
                    reply_markup=add_to_group_button,
                )
                LOGGER(__name__).info("Startup photo message sent successfully to log group.")
            except ChatWriteForbidden:
                LOGGER(__name__).warning(
                    f"Bot cannot send photo/message to log group (ChatWriteForbidden 403) at {config.LOGGER_ID}. Falling back to text message."
                )
                try:
                    # If 403, try sending just a text message
                    await self.send_message(
                        chat_id=config.LOGGER_ID,
                        text=log_message,
                        reply_markup=add_to_group_button,
                    )
                    LOGGER(__name__).info("Startup text message sent successfully to log group after 403 fallback.")
                except BadRequest as e:
                    LOGGER(__name__).error(
                        f"Failed to send startup text message to log group (400 Bad Request): {e}. "
                        f"Check if LOGGER_ID '{config.LOGGER_ID}' is correct and bot is a member."
                    )
                except Exception as e:
                    LOGGER(__name__).error(
                        f"An unexpected error occurred while sending startup text message to log group: {e}",
                        exc_info=True # This will print the full traceback
                    )
            except BadRequest as e:
                LOGGER(__name__).error(
                    f"Failed to send startup photo message to log group (400 Bad Request): {e}. "
                    f"This could be due to an invalid LOGGER_ID '{config.LOGGER_ID}', "
                    f"an invalid START_IMG_URL '{config.START_IMG_URL}', or bot not being a member. Trying text message fallback."
                )
                try:
                    # If 400 from photo, try sending just a text message
                    await self.send_message(
                        chat_id=config.LOGGER_ID,
                        text=log_message,
                        reply_markup=add_to_group_button,
                    )
                    LOGGER(__name__).info("Startup text message sent successfully to log group after 400 fallback.")
                except Exception as e:
                    LOGGER(__name__).error(
                        f"Failed to send startup text message after photo 400 error: {e}",
                        exc_info=True
                    )
            except Exception as e:
                LOGGER(__name__).error(
                    f"An unexpected error occurred during initial log group message attempt: {e}",
                    exc_info=True
                )
        else:
            LOGGER(__name__).warning(
                "config.LOGGER_ID is not set. Skipping log group notifications."
            )

        # --- Setting Bot Commands ---
        if config.SET_CMDS:
            LOGGER(__name__).info("Attempting to set bot commands...")
            try:
                # Private Chats Commands
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"),
                        BotCommand("help", "ɢᴇᴛ ᴛʜᴇ ʜᴇʟᴘ ᴍᴇɴᴜ"),
                        BotCommand("ping", "ᴄʜᴇᴄᴋ ʙᴏᴛ ɪs ᴀʟɪᴠᴇ ᴏʀ ᴅᴇᴀᴅ"),
                    ],
                    scope=BotCommandScopeAllPrivateChats(),
                )
                LOGGER(__name__).info("Private chat commands set.")

                # All Group Chats Commands (Music related)
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "Start playing requested song"),
                        BotCommand("stop", "Stop the current song"),
                        BotCommand("pause", "Pause the current song"),
                        BotCommand("resume", "Resume the paused song"),
                        BotCommand("queue", "Check the queue of songs"),
                        BotCommand("skip", "Skip the current song"),
                        BotCommand("volume", "Adjust the music volume"),
                        BotCommand("lyrics", "Get lyrics of the song"),
                    ],
                    scope=BotCommandScopeAllGroupChats(),
                )
                LOGGER(__name__).info("All group chat commands set.")

                # All Chat Administrators Commands (Admin and fun commands)
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "❥ ✨ᴛᴏ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ✨"),
                        BotCommand("ping", "❥ 🍁ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ ᴘɪɴɢ🍁"),
                        BotCommand("help", "❥ 🥺ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ🥺"),
                        BotCommand("vctag", "❥ 😇ᴛᴀɢᴀʟʟ ғᴏʀ ᴠᴄ🙈"),
                        BotCommand("stopvctag", "❥ 📍sᴛᴏᴘ ᴛᴀɢᴀʟʟ ғᴏʀ ᴠᴄ 💢"),
                        BotCommand("tagall", "❥ 🔻ᴛᴀɢ ᴀʟʟ ᴍᴇᴍʙᴇʀs ʙʏ ᴛᴇxᴛ🔻"),
                        BotCommand("cancel", "❥ 🔻ᴄᴀɴᴄᴇʟ ᴛʜᴇ ᴛᴀɢɢɪɴɢ🔻"),
                        BotCommand("settings", "❥ 🔻ᴛᴏ ɢᴇᴛ ᴛʜᴇ sᴇᴛᴛɪɴɢs🔻"),
                        BotCommand("reload", "❥ 🪐ᴛᴏ ʀᴇʟᴏᴀᴅ ᴛʜᴇ ʙᴏᴛ🪐"),
                        BotCommand("play", "❥ ❣️ᴛᴏ ᴘʟᴀʏ ᴛʜᴇ sᴏɴɢ❣️"),
                        BotCommand("vplay", "❥ ❣️ᴛᴏ ᴘʟᴀʏ ᴛʜᴇ ᴍᴜsɪᴄ ᴡɪᴛʜ ᴠɪᴅᴇᴏ❣️"),
                        BotCommand("pause", "❥ 🥀ᴛᴏ ᴘᴀᴜsᴇ ᴛʜᴇ sᴏɴɢs🥀"),
                        BotCommand("resume", "❥ 💖ᴛᴏ ʀᴇsᴜᴍᴇ ᴛʜᴇ sᴏɴɢ💖"),
                        BotCommand("end", "❥ 🐚ᴛᴏ ᴇᴍᴘᴛʏ ᴛʜᴇ ϙᴜᴇᴜᴇ🐚"),
                        BotCommand("queue", "❥ 🤨ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ ϙᴜᴇᴜᴇ🤨"),
                        BotCommand("playlist", "❥ 🕺ᴛᴏ ɢᴇᴛ ᴛʜᴇ ᴘʟᴀʏʟɪsᴛ🕺"),
                        BotCommand("stop", "❥ ❤‍🔥ᴛᴏ sᴛᴏᴘ ᴛʜᴇ sᴏɴɢs❤‍🔥"),
                        BotCommand("lyrics", "❥ 🕊️ᴛᴏ ɢᴇᴛ ᴛʜᴇ ʟʏʀɪᴄs🕊️"),
                        BotCommand("song", "❥ 🔸ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇ sᴏɴɢ🔸"),
                        BotCommand("video", "❥ 🔸ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇ ᴠɪᴅᴇᴏ sᴏɴɢ🔸"),
                        BotCommand("gali", "❥ 🔻ᴛᴏ ʀᴇᴘʟʏ ғᴏʀ ғᴜɴ🔻"),
                        BotCommand("shayri", "❥ 🔻ᴛᴏ ɢᴇᴛ ᴀ sʜᴀʏᴀʀɪ🔻"),
                        BotCommand("love", "❥ 🔻ᴛᴏ ɢᴇᴛ ᴀ ʟᴏᴠᴇ sʜᴀʏᴀʀɪ🔻"),
                        BotCommand("sudolist", "❥ 🌱ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ sᴜᴅᴏʟɪsᴛ🌱"),
                        BotCommand("owner", "❥ 💝ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ ᴏᴡɴᴇʀ💝"),
                        BotCommand("update", "❥ 🐲ᴛᴏ ᴜᴘᴅᴀᴛᴇ ʙᴏᴛ🐲"),
                        BotCommand("gstats", "❥ 💘ᴛᴏ sᴛᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ💘"),
                        BotCommand("repo", "❥ 🍌ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ 𝚁𝙴𝙿𝙾🍌"),
                    ],
                    scope=BotCommandScopeAllChatAdministrators(),
                )
                LOGGER(__name__).info("All chat administrators commands set.")
            except BadRequest as e:
                LOGGER(__name__).error(
                    f"Failed to set bot commands (400 Bad Request): {e}. "
                    f"This could be due to too many commands, invalid command names, or descriptions."
                )
            except Exception as e:
                LOGGER(__name__).error(
                    f"An unexpected error occurred while setting bot commands: {e}",
                    exc_info=True
                )
        else:
            LOGGER(__name__).info("config.SET_CMDS is False. Skipping setting bot commands.")


        # --- Check Bot Admin Status in Logger Group ---
        if config.LOGGER_ID:
            LOGGER(__name__).info(f"Checking bot's admin status in LOGGER_ID: {config.LOGGER_ID}")
            try:
                chat_member_info = await self.get_chat_member(
                    chat_id=config.LOGGER_ID, user_id=self.id
                )
                if chat_member_info.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).error(
                        "WARNING: Bot is not an Administrator in the Logger Group! "
                        "Some features requiring admin rights may not work. Please promote Bot as Admin."
                    )
                else:
                    LOGGER(__name__).info("Bot is an Administrator in the Logger Group.")
            except BadRequest as e:
                LOGGER(__name__).error(
                    f"Failed to get chat member info for LOGGER_ID '{config.LOGGER_ID}' (400 Bad Request): {e}. "
                    f"This might mean the LOGGER_ID is incorrect or the bot is not a member of this chat."
                )
            except Exception as e:
                LOGGER(__name__).error(
                    f"An unexpected error occurred while checking bot status in log group: {e}",
                    exc_info=True
                )

        LOGGER(__name__).info(f"ChampuBot Started as {self.name} successfully!")
