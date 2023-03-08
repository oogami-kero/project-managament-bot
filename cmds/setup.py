import discord
from discord import app_commands
from discord.utils import get
from discord.ext import commands
from discord.ui import Select, View

client = discord.Client(intents = discord.Intents.all())

class connectionsSelect(Select):
    def __init__(self) -> None:
        super().__init__(
            min_values = 1,
            max_values = 3,
            placeholder = 'Choose your connections',
            options = [
                discord.SelectOption(
                    label = 'GitHub', 
                    emoji = '🤖', 
                    description = 'GitHub connection'
                ),
                discord.SelectOption(
                    label = 'Trello',
                    emoji = '📆',
                    description = 'Trello connection'
                ),
                discord.SelectOption(
                    label = 'Microsoft Teams',
                    emoji = '🤝',
                    description = 'Microsoft Teams connection',
                )
            ])
    
    async def callback(self, interaction):
        await interaction.response.send_message('Beginning your server setup!')
        
        # Delete all initial categories, then delete the remaining channels
        for channel in interaction.guild.channels:
            await channel.delete()
        for category in interaction.guild.categories:
            await category.delete()

        # Setup the categories to hold the channels
        updates = await interaction.guild.create_category(name='Updates', position = 0, reason = 'New update channel')
        tracker = await interaction.guild.create_category(name = 'Schedule/Calendar', position = 1, reason = 'New tracking channel')
        ticket = await interaction.guild.create_category(name = 'Tickets', position = 2, reason = 'New ticketing channel')
        voice = await interaction.guild.create_category(name = 'Voice Channels', position = 3, reason = 'New Voice Channels')

        # Create the actual channels within the new categories
        general = await updates.create_text_channel(name = 'General')
        for connect in self.values:
            await updates.create_text_channel(name = connect + '-updates')

        await tracker.create_text_channel(name = 'Team-member-scheduler')
        await tracker.create_text_channel(name = 'Upcoming meetings')

        await ticket.create_text_channel(name = 'Submit-a-ticket')

        for i in range(1, 6):
            await voice.create_voice_channel(name = 'Voice ' + str(i))

        await general.send('Your server is now setup!')

class Setup(commands.Cog, name = "setup"):
    def __init__(self, bot):
        self.bot = bot

    text = 'A command to quickly set up your collabrative environment'
    @commands.hybrid_command(name = 'setup', with_app_command = True, description = text)
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):

        select = connectionsSelect()

        view = View()
        view.add_item(select)
        await ctx.send('Please select your connections!', view=view)

    @setup.error
    async def setp_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            msg = f"{ctx.message.author.mention}, You lack the required permissions for this command."
            await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Setup(bot))