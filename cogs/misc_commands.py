import datetime

import disnake as discord
import requests
from disnake.ext import commands

from utils.bot_utils import load_cogs
from utils.chicopee_work_sched import work_embed

from utils.print_screen import get_image

from utils.probability import one_in


class Misc_Slash_Commands(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(description="Flip a coin")
    async def flip_a_coin(self, inter):
        choice = await one_in()
        coin = "Heads" if choice else "Tails"
        await inter.response.send_message(f"You got {coin}")

    @commands.slash_command(description="Get a picture of the hill",
                            name="chic-o-peek-cam",
                            install_types=discord.ApplicationInstallTypes.all(),
                            contexts=discord.InteractionContextTypes.all(), )
    async def chic_o_peek_cam(self, inter):
        await inter.response.defer()
        if 4 <= datetime.datetime.now().month < 9:
            embed_colour = 0x2B5336

        else:
            embed_colour = 0x58A5D6

        embed = discord.Embed(title="Chic-o-Peek Webcam", timestamp=datetime.datetime.now(),
                              url="http://webcam.chicopeetubepark.com/webcam/camera.jpg",
                              type="image",
                              colour=embed_colour)
        response = requests.get("http://webcam.chicopeetubepark.com/webcam/camera.jpg", stream=True)

        if not response.ok:
            print(response)

        with open('images/camera.jpg', 'wb') as file:
            file.write(response.content)

        embed.set_image(file=discord.File('images/camera.jpg'))
        await inter.followup.send(embed=embed)

    # Creates the /reload Command
    # Reloads the bots cogs
    @commands.slash_command(description="Reloads the bots cogs")
    @commands.default_member_permissions(administrator=True)
    async def reload(self, inter: discord.ApplicationCommandInteraction):
        load_cogs(self.bot, True)
        await inter.response.send_message("Reloaded cogs.", ephemeral=True, delete_after=5)

    @commands.Cog.listener()
    async def on_button_click(self, inter: discord.MessageInteraction):
        # This is for the Again button on /prnt.sc
        if inter.component.custom_id == "Again":
            await self.prntsc(inter)
        if inter.component.label == "Refresh":
            name = inter.component.custom_id
            url = inter.message.embeds[0].url
            embed = work_embed(url, name)
            await inter.response.defer()
            await inter.message.edit(embed=embed)

    # Creates the /prntsc Command
    # Gets a random image from https://prnt.sc
    @commands.slash_command(description="Scrapes a random image from Prnt.sc",
                            install_types=discord.ApplicationInstallTypes.all(),
                            contexts=discord.InteractionContextTypes.all(), )
    async def prntsc(self, inter: discord.ApplicationCommandInteraction):
        try:
            await inter.response.defer(with_message=True)
            # Builds the Embed
            embed = discord.Embed(title="Print-screen Image", color=discord.Color.blue(),
                                  timestamp=datetime.datetime.now())
            embed.set_footer(text=f"@{inter.user.name}")
            # Gets image from prnt.sc
            image, url = get_image()
            # Set the image of the embed to the one we got from prnt.sc
            embed.set_image(file=discord.File(image))
            embed.url = url

            # Sends a message embed that has a button
            await inter.followup.send(embed=embed, components=[
                discord.ui.Button(label="Again", style=discord.ButtonStyle.blurple, custom_id="Again")
            ])
        except discord.errors.NotFound:
            await self.prntsc(inter)

    # Creates the /work_sched Command
    # Displays the work schedule(For Chicopee employees only)
    @commands.slash_command(description="Displays your work schedule (For Chicopee employees only)",
                            install_types=discord.ApplicationInstallTypes.all(),
                            contexts=discord.InteractionContextTypes.all(), )
    async def work_sched(self, inter: discord.ApplicationCommandInteraction, url: str, name: str):
        embed = work_embed(url, name)
        await inter.response.defer(with_message=True)
        await inter.followup.send(embed=embed, components=[
            discord.ui.Button(label="Refresh", style=discord.ButtonStyle.gray, custom_id=f"{name}")
        ])

    # Creates the /delete Command
    # Deletes a message in a DM Channel
    # Only works in a DM Channel and on a message created by the bot
    @commands.message_command(name="Delete")
    async def delete_dm(self, inter: discord.MessageCommandInteraction, message: discord.Message):
        author = message.author
        bot = self.bot.user
        channel_type = inter.channel.type

        if author == bot and channel_type is discord.ChannelType.private:
            await inter.response.send_message("Message deleted", ephemeral=True, delete_after=1)
            await message.delete()
        else:
            await inter.response.send_message("Must be used in a DM Channel and on a message created by the bot.",
                                              ephemeral=True, delete_after=5)


def setup(bot):
    bot.add_cog(Misc_Slash_Commands(bot))
