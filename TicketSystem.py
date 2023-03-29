import discord
import datetime
import pytz
import os
from discord import app_commands, member, utils
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot, has_permissions, MissingPermissions

time = datetime.datetime.now()
mst_now = time.astimezone(pytz.timezone('America/Denver'))
mst_format= mst_now.strftime("%Y/%m/%d %H:%M:%S")

TOKEN = 'MTA3MDQ3NjczMDA0MjY4MzQwMg.G2svck.iswCy_zB1xwvytygeSIG6eTdxeTr5HPN4dATrA'

# Bot Initialization

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
      await tree.sync()
      self.synced = True

    # make ticket button persist over restarts  
    if not self.added:
      self.add_view(ticket_launcher())
      self.add_view(ticket_control())
      self.added = True

    # print ready message and set bot status  
    await bot.change_presence(activity=discord.Game('TICKET SYSTEM'))
    print(f'Bot connected as {bot.user}')
    print(mst_format)

bot = aclient()
tree = app_commands.CommandTree(bot)


#------------------------------------------------------------------------------------------------------#

# Functions for Tickets


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
                                                      embed_links = True,
                                                      read_message_history = True),
        interaction.guild.me: discord.PermissionOverwrite(view_channel = True,
                                                           send_messages = True,
                                                           read_message_history = True)
      }
      
      # create ticket channel
      category = discord.utils.get(interaction.guild.categories, name = "TICKETS")
      if category is None:
        await interaction.guild.create_category("TICKETS", position = 0)
      channel = await interaction.guild.create_text_channel(name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}",
                                                            category = category, overwrites = overwrites, reason = f"Ticket for {interaction.user}")
      await channel.send(f"{interaction.user.mention} created a ticket!", view = ticket_control())
      await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}!", ephemeral = True)

# ticket deletion confirmation button
class confirm(discord.ui.View):
  def __init__(self) -> None:
    super().__init__(timeout = None)

  @discord.ui.button(label = "Yes, I'm sure", style = discord.ButtonStyle.red, custom_id = "confirm")
  async def confirm_button(self, interaction, button):
    try:
      await interaction.channel.delete()
    except:
      await interaction.response.send_message("Channel could not be deleted, ensure 'manage_channels' permission is given!",
                                              ephemeral = True)
# ticket management
class ticket_control(discord.ui.View):
  def __init__(self) -> None:
    super().__init__(timeout = None)

  # close ticket embed
  @discord.ui.button(label = "Close this Ticket", style = discord.ButtonStyle.red, custom_id = "close")
  async def close(self, interaction, button):
    embed = discord.Embed(title = "Are you sure you want to close this ticket?", color = discord.Colour.brand_red())
    await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)

#------------------------------------------------------------------------------------------------------#

# Slash Commands

# ticket system initialization command
@tree.command(name = 'ticket', description = 'Initializes the ticketing system')
@has_permissions(administrator = True)
async def ticketing(interaction: discord.Interaction):
  embed = discord.Embed(title = "If you need support, click the button below to create a new ticket!",
                        color = discord.Colour.dark_teal())
  await interaction.channel.send(embed = embed, view = ticket_launcher())
  await interaction.response.send_message("Ticketing system initiated successfully", ephemeral = True)

# manual ticket close command
@tree.command(name = 'close', description = 'Closes a ticket manually')
async def close(interaction: discord.Interaction):
  if "ticket-for-" in interaction.channel.name:
    embed = discord.Embed(title = "Are you sure you want to close this ticket?", color = discord.Colour.brand_red())
    await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)
  else:
    await interaction.response.send_message("This can only be used in a ticket channel", ephemeral = True)

# add user to ticket command
@tree.command(name = 'add', description = 'Adds user to existing ticket')
@app_commands.describe(user = "User you want to add to the ticket")
async def add(interaction: discord.Interaction, user: discord.Member):
  if "ticket-for-" in interaction.channel.name:
    await interaction.channel.set_permissions(user, view_channel = True, send_messages = True,
                                              attach_files = True, embed_links = True)
    await interaction.response.send_message(f"{user.mention} has been added to the ticket by {interaction.user.mention}!")
  else:
    await interaction.response.send_message("This can only be used in a ticket channel", ephemeral = True)

# remove user from ticket command
@tree.command(name = 'remove', description = 'Removes user from existing ticket')
@app_commands.describe(user = "User you want to remove from the ticket")
async def remove(interaction: discord.Interaction, user: discord.Member):
  if "ticket-for-" in interaction.channel.name:
    await interaction.channel.set_permissions(user, overwrite = None)
    await interaction.response.send_message(f"{user.mention} has been removed from the ticket by {interaction.user.mention}!")
  else:
    await interaction.response.send_message("This can only be used in a ticket channel", ephemeral = True)

#------------------------------------------------------------------------------------------------------#

  
# permission check
@tree.error
async def command_error(bot, error):
    if isinstance(error, MissingPermissions):
        text = "You do not have permissions to do that!"
        await bot.send_message(bot.message.channel, text, ephemeral = True)

bot.run(TOKEN)
