import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import aiohttp

class ModCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="setchannel", description="Set AI auto-response channel for this server")
    @commands.has_permissions(administrator=True)
    @app_commands.describe(channel="Channel where AI will auto-respond to messages")
    async def set_ai_channel(self, ctx, channel: discord.TextChannel):
        """Set AI channel for auto-response"""
        self.bot.ai_channels[str(ctx.guild.id)] = str(channel.id)
        
        embed = discord.Embed(
            title="✅ AI Channel Setup Complete",
            description=f"**{channel.mention}** is now the AI channel!",
            color=0x00ff00
        )
        embed.add_field(
            name="How it works:", 
            value="• **In this channel**: Just type anything - AI will auto-reply\n• **Other channels**: Use `/ask` command\n• **No commands needed** in AI channel!\n• **File uploads**: Auto-analyze any uploaded files",
            inline=False
        )
        embed.set_footer(text="ChatGPT-style experience activated! 🚀")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="removechannel", description="Remove AI auto-response channel")
    @commands.has_permissions(administrator=True)
    async def remove_ai_channel(self, ctx):
        """Remove AI channel"""
        guild_id = str(ctx.guild.id)
        if guild_id in self.bot.ai_channels:
            del self.bot.ai_channels[guild_id]
            await ctx.send("✅ AI auto-response disabled for this server.")
        else:
            await ctx.send("ℹ️ No AI channel was set for this server.")

    @commands.hybrid_command(name="aistatus", description="Check AI channel status")
    async def ai_status(self, ctx):
        """Check AI channel status"""
        guild_id = str(ctx.guild.id)
        if guild_id in self.bot.ai_channels:
            channel_id = self.bot.ai_channels[guild_id]
            channel = ctx.guild.get_channel(int(channel_id))
            embed = discord.Embed(
                title="🤖 AI Channel Status",
                description=f"**Auto-Response Channel:** {channel.mention if channel else 'Channel not found'}\n\n**Mode:** ChatGPT-style (No commands needed)\n**Features:** Text chat + File analysis",
                color=0x3498db
            )
        else:
            embed = discord.Embed(
                title="🤖 AI Channel Status", 
                description="No AI channel set. Use `/setchannel` to enable auto-response mode.",
                color=0xe74c3c
            )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="purge", description="Delete multiple messages")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    async def purge_messages(self, ctx, amount: int = 10):
        """Bulk delete messages"""
        if amount < 1 or amount > 100:
            await ctx.send("❌ Amount must be between 1-100", ephemeral=True)
            return
            
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"✅ Deleted {len(deleted) - 1} messages", delete_after=5)

    # ✅ FIXED: Method name changed from bot_info to bot_information
    @commands.hybrid_command(name="botinfo", description="Show detailed bot information")
    async def bot_information(self, ctx):  # ✅ NAME CHANGED
        """Show bot information"""
        embed = discord.Embed(
            title="🤖 DigamberGPT Super Bot",
            description="Advanced AI Bot with File Analysis & Project Building",
            color=0x3498db,
            timestamp=ctx.message.created_at
        )
        
        embed.add_field(
            name="🚀 Core Features",
            value="• Advanced AI Chat (Groq)\n• File Analysis & Auto-Fix\n• APK/Project Building\n• Code Conversion\n• Multi-language Support",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Build Services", 
            value="• Android APK Builder\n• Web Project Generator\n• GitHub Setup Helper\n• Any Language Projects\n• 100MB File Support",
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"• Servers: {len(self.bot.guilds)}\n• Users: {sum(g.member_count for g in self.bot.guilds)}\n• Uptime: Calculating...",
            inline=False
        )
        
        embed.add_field(
            name="💡 Quick Start",
            value="1. Upload any file for analysis\n2. Use `/buildapk` for Android apps\n3. Use `/analyze` for code review\n4. Set AI channel with `/setchannel`",
            inline=False
        )
        
        embed.set_footer(text="Created with ❤️ by DIGAMBER")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverstats", description="Show server statistics with bot features")
    async def server_stats(self, ctx):
        """Show server statistics"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title="📊 Server Statistics",
            color=0x9b59b6,
            timestamp=ctx.message.created_at
        )
        
        embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
        embed.add_field(name="📁 Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
        
        ai_channel_set = str(guild.id) in self.bot.ai_channels
        embed.add_field(
            name="🤖 Bot Features", 
            value=f"• AI Channel: {'✅ Enabled' if ai_channel_set else '❌ Disabled'}\n• File Analysis: ✅ Active\n• APK Building: ✅ Ready\n• Code Fixing: ✅ Available",
            inline=False
        )
        
        embed.add_field(
            name="🚀 Available Commands",
            value="• `/ask` - AI Chat\n• `/analyze` - Code analysis\n• `/buildapk` - APK builder\n• `/fix` - Code fixing\n• Upload files for auto-analysis",
            inline=False
        )
        
        embed.set_footer(text=f"Server ID: {guild.id}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ModCommands(bot))
