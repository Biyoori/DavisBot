import discord
from discord.ext import commands
import wavelink
import logging
import tracemalloc
from config import *
from commands import Commandos

intents = discord.Intents.default()
intents.message_content = True

tracemalloc.start()

client = commands.Bot(command_prefix, intents=intents)
active_track = wavelink.Playable

@client.event
async def on_ready():
    nodes = [wavelink.Node(uri=ll_host, password=ll_pass)]
    await client.add_cog(Commandos(client))
    await wavelink.Pool.connect(nodes=nodes, client=client, cache_capacity=None)

client.run(TOKEN)
