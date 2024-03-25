import discord
from discord.ext import commands
import wavelink
from quotes import getQuote
from typing import cast
from config import *

class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        global active_track
        active_track = payload.track
        if auto_now_playing:
            await payload.player.channel.send(f"Now Playing **`{active_track.title}`** {active_track.uri}" )

    @commands.command()
    async def copy(self, ctx, *args):
        arguments = " ".join(args)
        await ctx.send(arguments)
        await ctx.message.delete()

    @commands.command()
    async def quote(self, ctx):
        await ctx.send(getQuote())


    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str) -> None:
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

    @commands.command()
    async def skip(self, ctx: commands.Context) -> None:
        """Skip the current song."""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.skip(force=True)
        await ctx.message.add_reaction("\u2705")

    @commands.command()
    async def nightcore(self, ctx: commands.Context) -> None:
        """Set the filter to a nightcore style."""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=nightcore_pitch, speed=nightcore_speed, rate=1)
        await player.set_filters(filters)

        await ctx.message.add_reaction("\u2705")

    @commands.command()
    async def slow(self, ctx: commands.Context) -> None:
        """Set the filter to a slow down."""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=slow_pitch, speed=slow_speed, rate=1)
        await player.set_filters(filters)

        await ctx.message.add_reaction("\u2705")

    @commands.command(aliases=["dc"])
    async def disconnect(self, ctx: commands.Context) -> None:
        """Disconnect the Player."""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.disconnect()
        await ctx.message.add_reaction("\u2705")

    @commands.command()
    async def np(self, ctx: commands.Context) -> None:
        """Show currently played song"""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        
        
        await ctx.send(f"Now Playing **`{active_track.title}`** {active_track.uri}" )
