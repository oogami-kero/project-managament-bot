import discord
import datetime
import pytz
import os
from discord import app_commands, utils
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot

time = datetime.datetime.now()
mst_now = time.astimezone(pytz.timezone('America/Denver'))
mst_format= mst_now.strftime("%Y/%m/%d %H:%M:%S")

# token here
# TOKEN = ''

class aclient(discord.Client):
  # sync slash commands
  def __init__(self):
    super().__init__(intents = discord.Intents.all())
    self.synced = False
    self.added = False
    
  # check if slash commands synced
  async def on_ready(self):
    await self.wait_until_ready()
    if not self.synced:
      await cogs.sync(guild = discord.Object(id = 1067969922258456626))
      self.synced = True

    # make ticket button persist over restarts  
    if not self.added:
      self.add_view(ticket_launcher())
      self.added = True

    # print ready message and set bot status  
    await bot.change_presence(activity=discord.Game('TICKET SYSTEM PROGRESS ■■■■■■□□□□ 60%'))
    print(f'Bot connected as {bot.user}')
    print(mst_format)
  


bot = aclient()
cogs = app_commands.CommandTree(bot)

class ticket_launcher(discord.ui.View):
  def __init__(slef) -> None:
    super().__init__(timeout = None)

  @discord.ui.button(label = "Create a Ticket",
                     style = discord.ButtonStyle.blurple,
                     custom_id = "ticket_button")
  async def ticket(self, interaction: discord.Interaction,
                   button: discord.ui.Button):

    # check if ticket exists already
    ticket = utils.get(interaction.guild.text_channels,
                       name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}")
    if ticket is not None:
      await interaction.response.send_message(f"You already have a ticket open at {ticket.mention}!", ephemeral = True)

    else:
      # permission overwrites for ticket channel
      overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
        interaction.user: discord.PermissionOverwrite(view_channel = True,
                                                      send_messages = True,
                                                      attach_files = True,
                                                      embed_links = True),
        interaction.guild.me: discord.PermissionOverwrite(view_channel = True,
                                                           send_messages = True,
                                                           read_message_history = True)
      }
      
      # create ticket channel
      channel = await interaction.guild.create_text_channel(name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}",
                                                            overwrites = overwrites,
                                                            reason = f"Ticket for {interaction.user}")
      await channel.send(f"{interaction.user.mention} created a ticket!")
      await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}!", ephemeral = True)

# ticket system initialization command
@cogs.command(guild = discord.Object(id = 1067969922258456626), name = 'ticket', description='launches the ticketing system')
async def ticketing(interaction: discord.Interaction):
  embed = discord.Embed(title = "If you need support, click the button below to create a new ticket!",
                        color = discord.Colour.teal())
  await interaction.channel.send(embed = embed, view = ticket_launcher())
  await interaction.response.send_message("Ticketing system initiated successfully", ephemeral = True)


bot.run(TOKEN)
