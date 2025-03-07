import os
import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta

from myserver import server_on


GUILD_ID = 1258132587176530052  # ใส่ ID เซิร์ฟเวอร์ของคุณ
CATEGORY_ID = 1347568220281770045  # ใส่ ID หมวดหมู่ที่ต้องการให้สร้างห้อง
ROLE_ID = 1259918756386312242  # ใส่ ID ของยศที่ต้องการให้เข้าห้องได้

time_to_delete = timedelta(days=5)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class RoomCreationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="สร้างห้อง", style=discord.ButtonStyle.green)
    async def create_room(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("กรุณากรอกชื่อห้องของคุณ:", ephemeral=True)
        
        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel
        
        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
            room_name = msg.content
        except asyncio.TimeoutError:
            await interaction.followup.send("หมดเวลา กรุณาลองใหม่!", ephemeral=True)
            return
        
        guild = bot.get_guild(GUILD_ID)
        category = guild.get_channel(CATEGORY_ID)
        role = guild.get_role(ROLE_ID)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, manage_channels=True),
            role: discord.PermissionOverwrite(view_channel=True)
        }
        
        channel = await guild.create_text_channel(name=room_name, category=category, overwrites=overwrites)
        await interaction.followup.send(f'สร้างห้อง **{room_name}** เรียบร้อยแล้ว! ห้องจะถูกลบใน 5 วัน')
        
        await delete_room_after_delay(channel)

async def delete_room_after_delay(channel):
    await asyncio.sleep(time_to_delete.total_seconds())
    await channel.delete()

@bot.command()
async def send_create_room_button(ctx):
    view = RoomCreationView()
    await ctx.send("กดปุ่มด้านล่างเพื่อสร้างห้องส่วนตัว", view=view)

server_on()

bot.run(os.getenv('TOKEN'))
