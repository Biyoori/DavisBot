import discord
import logging
import tracemalloc
from quotes import getQuote
import wavelink
from discord.ext import commands
from typing import cast
from config import *

intents = discord.Intents.default()
intents.message_content = True

tracemalloc.start()

client = commands.Bot(command_prefix, intents=intents)

@client.event
async def on_ready():
    nodes = [wavelink.Node(uri=lavalink_uri, password=lavalink_pass)]

    await wavelink.Pool.connect(nodes=nodes, client=client, cache_capacity=None)

##### KOMENDY #####
@client.command()
async def helpme(ctx):
    await ctx.send("List of available commands:\n !copy \n !quote")

@client.command()
async def copy(ctx, *args):
    arguments = " ".join(args)
    await ctx.send(arguments)
    await ctx.message.delete()

@client.command()
async def quote(ctx):
    await ctx.send(getQuote())


@client.command()
async def play(ctx: commands.Context, *, query: str) -> None:
    """Play a song with the given query."""
    if not ctx.guild:
        return

    player: wavelink.Player
    player = cast(wavelink.Player, ctx.voice_client)  # type: ignore

    if not player:
        try:
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player)  # type: ignore
        except AttributeError:
            await ctx.send("Please join a voice channel first before using this command.")
            return
        except discord.ClientException:
            await ctx.send("I was unable to join this voice channel. Please try again.")
            return

    # Turn on AutoPlay to enabled mode.
    # enabled = AutoPlay will play songs for us and fetch recommendations...
    # partial = AutoPlay will play songs for us, but WILL NOT fetch recommendations...
    # disabled = AutoPlay will do nothing...
    player.autoplay = wavelink.AutoPlayMode.enabled

    # Lock the player to this channel...
    if not hasattr(player, "home"):
        player.home = ctx.channel
    elif player.home != ctx.channel:
        await ctx.send(f"You can only play songs in {player.home.mention}, as the player has already started there.")
        return

    # This will handle fetching Tracks and Playlists...
    # Seed the doc strings for more information on this method...
    # If spotify is enabled via LavaSrc, this will automatically fetch Spotify tracks if you pass a URL...
    # Defaults to YouTube for non URL based queries...
    tracks: wavelink.Search = await wavelink.Playable.search(query)
    if not tracks:
        await ctx.send(f"{ctx.author.mention} - Could not find any tracks with that query. Please try again.")
        return

    if isinstance(tracks, wavelink.Playlist):
        # tracks is a playlist...
        added: int = await player.queue.put_wait(tracks)
        await ctx.send(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
    else:
        track: wavelink.Playable = tracks[0]
        await player.queue.put_wait(track)
        await ctx.send(f"Added **`{track}`** to the queue.")

    if not player.playing:
        # Play now since we aren't playing anything...
        await player.play(player.queue.get(), volume=30)

    # Optionally delete the invokers message...
    try:
        await ctx.message.delete()
    except discord.HTTPException:
        pass

@client.command()
async def skip(ctx: commands.Context) -> None:
    """Skip the current song."""
    player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
    if not player:
        return

    await player.skip(force=True)
    await ctx.message.add_reaction("\u2705")

@client.command()
async def nightcore(ctx: commands.Context) -> None:
    """Set the filter to a nightcore style."""
    player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
    if not player:
        return

    filters: wavelink.Filters = player.filters
    filters.timescale.set(pitch=nightcore_pitch, speed=nightcore_speed, rate=1)
    await player.set_filters(filters)

    await ctx.message.add_reaction("\u2705")

@client.command(aliases=["dc"])
async def disconnect(ctx: commands.Context) -> None:
    """Disconnect the Player."""
    player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
    if not player:
        return

    await player.disconnect()
    await ctx.message.add_reaction("\u2705")

@client.command()
async def nowplaying(ctx: commands.Context) -> None:
    """Show currently played song"""
    player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
    if not player:
        return
    
    
    await ctx.send(f"Now Playing **`{wavelink.Playable.author}`** **`{wavelink.Playable.title}`** **`{wavelink.Playable.uri}`** **`{wavelink.Playable.artwork}`**")


client.run(TOKEN)
