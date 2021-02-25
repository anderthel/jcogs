import discord
from redbot.core import commands
from redbot.core import checks, commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import escape
from PIL import Image, ImageDraw, ImageFont
import hashlib


class Quotes(commands.Cog):
	"""A quote formatter and poster"""
	
	default_guild = {"quotes": [], "min_role": 0, "next_available_id": 1, "channel": 0}
	default_member = {"dms": False}

	def quoteImg(self, content):
		#variables for image size
		x1 = 1024 
		y1 = 1024
		#define quote
		sentence = content
		#set font
		fnt = ImageFont.truetype('/data/cogs/CogManager/cogs/quotes/font.ttf', 40)
		# color is the backgroundColor of the Image
		img = Image.new('RGB', (x1, y1), color = (0,0,0))
		d = ImageDraw.Draw(img)
		#find the average size of the letter
		sum = 0
		for letter in sentence:
			sum += d.textsize(letter, font=fnt)[0]
		average_length_of_letter = sum/len(sentence)
		#find the number of letters to be put on each line
		number_of_letters_for_each_line = (x1/1.618)/average_length_of_letter
		incrementer = 0
		fresh_sentence = ''
		#add some line breaks
		for letter in sentence:
			if(letter == '-'):
				fresh_sentence += '\n\n' + letter
			elif(incrementer < number_of_letters_for_each_line):
				fresh_sentence += letter
			else:
				if(letter == ' '):
					fresh_sentence += '\n'
					incrementer = 0
				else:
					fresh_sentence += letter
			incrementer+=1
		#render the text in the center of the box
		dim = d.textsize(fresh_sentence, font=fnt)
		x2 = dim[0]
		y2 = dim[1]
		qx = (x1/2 - x2/2)
		qy = (y1/2-y2/2)
		# fill is the text color
		d.text((qx,qy), fresh_sentence ,align="center", font=fnt, fill=(255, 255, 255))
		img.save('image.png')
		return image.png

		

	def __init__(self, bot: Red):
		self.bot = bot
		self.settings = Config.get_conf(self, identifier=59595922, force_registration=True)
		self.settings.register_guild(**self.default_guild)
		self.settings.register_member(**self.default_member)

	@commands.group()
	@commands.guild_only()
	async def quote(self, ctx: commands.Context):
		"""Base command for quote creation tool.
		
		Use quoteset for settings"""
		pass

	@quote.command(name="create")
	async def quote_create(self, ctx, *items):
		"""
		If a minimum required role has been set, users must have that role or
		higher, be in the mod/admin role, or be the guild owner in order to use this command
		
		The quote will only be created if all information is provided properly.
		Porper format is Double quotes surrounding quote followed by double quotes surrounding where its from/who its by
		"""
		items = [escape(c, mass_mentions=True) for c in items]
		if len(items) == 2:
			channel = ctx.guild.get_channel(await self.settings.guild(ctx.guild).channel())
			if channel is None:
				channel = guild.system_channel
			quote = items[0]
			author = items[1]
			content = quote + " - " + author
			quoteimage = self.quoteImg(content)
			embed=discord.Embed(description=content)
			embed.set_image(url="attachment://" + quoteimage)
			await channel.send(embed=embed, file=image)
			await ctx.send("Posted")
			
		else:
			await ctx.send("Not properly formatted. Porper format is double quotes surrounding quote followed by double quotes surrounding where its from/who its by")

	@commands.group()
	@checks.admin_or_permissions(manage_guild=True)
	@commands.guild_only()
	async def quoteset(self, ctx: commands.Context):
		"""quote maker settings"""
		pass

	@quoteset.command(name="role")
	@checks.admin_or_permissions(manage_guild=True)
	async def quoteset_role(self, ctx: commands.Context, *, role: discord.Role = None):
		"""Set the minimum role required to create quotes.
		Default is for everyone to be able to create quotes"""
		guild = ctx.guild
		if role is not None:
			await self.settings.guild(guild).min_role.set(role.id)
			await ctx.send("Role set to {}".format(role))
		else:
			await self.settings.guild(guild).min_role.set(0)
			await ctx.send("Role unset!")

	@quoteset.command(name="channel")
	@checks.admin_or_permissions(manage_guild=True)
	async def quoteset_channel(self, ctx: commands.Context, channel: discord.TextChannel):
		"""
		Sets the channel where quotes will be sent
		If this is not set, the channel will default to the channel used
		for new member messages (Server Settings > Overview > New Member
		Messages Channel on desktop). If that is set to `No new member messages`,
		the event start announcement will not be sent to a channel in the server
		and will only be sent directly to the participants via DM
		"""
		await self.settings.guild(ctx.guild).channel.set(channel.id)
		await ctx.tick()
