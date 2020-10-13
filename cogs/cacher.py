import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
import datetime

class CacherCog(commands.Cog):
    """"Cog to handle caching of guild data."""
    def __init__(self, bot, guild_data_file):
        self.bot = bot
        self.guild_data_file = guild_data_file

    @staticmethod
    def timestamp():
        """ Easy timestamp generation. """
        return datetime.datetime.now().strftime("%x - [%X]")

    @commands.Cog.listener()
    async def on_ready(self):
        "load guild data and start saving task"
        
        tasks = [t for t in asyncio.Task.all_tasks() if type(t) is discord.client._ClientEventTask]
        tasks.remove(asyncio.Task.current_task())
        await asyncio.wait(tasks)

        #load guild data
        print('Loading guild data...')
        self.load()
        print('Loaded guild data')

        #start periodic save
        if self.periodic_save.current_loop == 0:
            self.periodic_save.start()

    def save(self):
        """save guild data to json"""
        data = {}
        queue_cog = self.bot.get_cog('QueueCog')

        #save guild data for each guild
        for guild in self.bot.guilds:
            guild_queue = queue_cog.guild_queues.get(guild)
            guild_data = {}
            guild_data['queue'] = {}
            guild_data['queue']['active'] = [user.id for user in guild_queue.active]
            guild_data['queue']['bursted'] = [user.id for user in guild_queue.bursted]
            guild_data['queue']['capacity'] = guild_queue.capacity

            data[str(guild.id)] = guild_data
        
        with open(self.guild_data_file, 'w+') as f:
            json.dump(data, f, indent=4)

    
    def load(self):
        """load data from json"""
        if not os.path.exists(self.guild_data_file):
            return

        queue_cog = self.bot.get_cog('QueueCog')
        data = json.load(open(self.guild_data_file, 'r'))

        for guild_id, guild_data in data.items():
            guild = self.bot.get_guild(int(guild_id))

            if guild is None:
                continue

            guild_queue = queue_cog.guild_queues.get(guild)

            if guild_queue and 'queue' in guild_data:
                guild_queue.capacity = guild_data['queue']['capacity']
                active = guild_data['queue']['active']
                bursted = guild_data['queue']['bursted']
                guild_queue.active = [self.bot.get_user(id) for id in active if self.bot.get_user(id)]
                guild_queue.bursted = [self.bot.get_user(id) for id in bursted if self.bot.get_user(id)]

            
    @tasks.loop(minutes=5)
    async def periodic_save(self):
        """save guild data periodically"""
        self.save()
        print(f'{self.timestamp()} Saved guild data')

    @commands.Cog.listener()
    async def on_disconnect(self):
        """save guild data on disconnect to be reloaded when ready"""
        self.save()
        print(f'{self.timestamp()}Saved guild data')
        


