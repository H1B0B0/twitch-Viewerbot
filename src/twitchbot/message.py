import requests
from twitchio.ext import commands

class Bot(commands.Bot):

    def __init__(self, name, token, channel):
        super().__init__(irc_token=token, name=name, prefix='!',
                         initial_channels=[channel])

    async def event_ready(self):
        print(f'Ready | {self.nick}')

    async def send_message(self, message):
        await self.get_channel(self.initial_channels[0]).send(message)

class TwitchBotManager:

    def __init__(self, account_list):
        self.bots = []
        for account in account_list:
            account_parts = account.split('|')[0].split('=')
            if len(account_parts) > 1:
                oauth_token = account_parts[1].strip()
                name = account.split('|')[1].split(':')[1].strip()
                print(f"Creating bot for {name}")
                print(f"Token: {oauth_token}")
                self.bots.append(Bot(name=name, token=f'oauth:{oauth_token}', channel=name))
            else:
                print(f"Invalid account string: {account}")

    async def run_bots(self):
        for bot in self.bots:
            await bot.start()