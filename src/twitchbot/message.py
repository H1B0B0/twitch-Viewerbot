import asyncio
import threading
import logging
import aiohttp
from twitchio.ext import commands

logging.basicConfig(level=logging.INFO)
class Bot(commands.Bot):

    def __init__(self, name, irc_token, channel, token):
        super().__init__(token=token, nick=name, irc_token=irc_token, prefix='!',
                         initial_channels=[channel])
        self.name = name  # Add this line
        self.initial_channels = [channel]  # Add this line
        logging.debug(f'Bot initialized: {name}')

    def event_ready(self):
        logging.info(f'Ready | {self.nick}')

    async def start_and_send_message(self, message):
        logging.info(f"Starting bot {self.nick} to send message.")
        try:
            await self.start()
            channel = self.get_channel(self.initial_channels[0])
            logging.info(f"get_channel returned: {channel}")
            print(f"get_channel returned: {channel}")
            if channel:
                logging.info(f"Channel {channel} found, sending message: {message}")
                print(f"Channel {channel} found, sending message: {message}")
                await channel.send(message)
                logging.info(f"Message sent: {message}")
                print(f"Message sent: {message}")
            else:
                logging.error(f"Could not get channel: {self.initial_channels[0]}")
                print(f"Could not get channel: {self.initial_channels[0]}")
        except Exception as e:
            logging.error(f"Error in start_and_send_message: {e}")
            print(f"Error in start_and_send_message: {e}")

class TwitchBotManager:

    def __init__(self, account_list, channel_name):
        self.bots = []
        self.account_list = account_list
        self.channel_name = channel_name

    async def initialize_bots(self):
        for account in self.account_list:
            oauth_token = account.strip()
            logging.info(f"Creating bot for {oauth_token}")
            if await self.is_token_valid(oauth_token):
                self.bots.append(Bot(name=oauth_token, irc_token=f'oauth:{oauth_token}', channel=self.channel_name, token=oauth_token))
            else:
                logging.error(f"Invalid token for account: {oauth_token}")

    async def is_token_valid(self, token):
        url = f"https://id.twitch.tv/oauth2/validate"
        headers = {"Authorization": f"OAuth {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return True
                else:
                    return False

    async def run_bot(self, message, bot):
        logging.info('Running bots')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            await bot.start_and_send_message(message)
        finally:
            loop.close()

    def start(self):
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.initialize_bots())
        threading.Thread(target=run_in_thread).start()