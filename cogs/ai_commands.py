import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from groq import Groq
from datetime import datetime, timedelta
import aiohttp
import io

class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.conversations = {}
        self.user_stats = {}
        self.cooldowns = {}

    async def get_ai_response(self, user_input):
        """Get AI response - used by both commands and auto-response"""
        try:
            # Check if API key is set
            if not os.getenv("GROQ_API_KEY"):
                return "❌ **Configuration Error:** Groq API key not set. Please check environment variables."
            
            prompt = f"""
You are DigamberGPT, an advanced AI assistant created by DIGAMBER. 
You are helpful, creative, and intelligent. 
Never mention that you are an AI model or your training data.
Respond naturally and helpfully.

User: {user_input}
"""
            
            response = self.groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower():
                return "❌ **API Error:** Invalid Groq API key. Please check your environment variables."
            elif "rate limit" in error_msg.lower():
                return "⚠️ **Rate Limit:** Too many requests. Please try again in a moment."
            else:
                return f"❌ **Error:** {error_msg}"

    @commands.hybrid_command(name="ask", description="Ask anything to AI")
    @app_commands.describe(question="Your question")
    async def ask_ai(self, ctx, question: str):
        """AI command for non-AI channels"""
        await ctx.defer()
        
        reply = await self.get_ai_response(question)
        await ctx.followup.send(f"**{ctx.author.display_name}:** {question}\n\n**DigamberGPT:** {reply}")

    # ✅ NEW COMMAND: ANALYZE CODE/FILE
    @commands.hybrid_command(name="analyze", description="Analyze code/file for errors and improvements")
    @app_commands.describe(code="Paste your code or describe the file")
    async def analyze_code(self, ctx, *, code: str):
        """Analyze code for errors and improvements"""
        await ctx.defer()
        
        try:
            prompt = f"""
            CODE ANALYSIS REQUEST:
            
            Code/File Content:
            {code}
            
            Please analyze this code/file and provide:
            1. **Errors/Bugs**: Any syntax errors, logical errors, or issues
            2. **Fix Suggestions**: How to fix the problems
            3. **Optimizations**: Ways to improve performance/readability
            4. **Security Issues**: Any vulnerabilities
            5. **Best Practices**: Coding standards to follow
            
            Provide detailed analysis in Hindi/English mix.
            """
            
            response = self.groq.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            # Format response
            embed = discord.Embed(
                title="🔍 Code Analysis Report",
                description=analysis[:4090] + "..." if len(analysis) > 4090 else analysis,
                color=0x3498db,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Analysis failed: {str(e)}")

    # ✅ NEW COMMAND: FIX CODE
    @commands.hybrid_command(name="fix", description="Fix errors in your code")
    @app_commands.describe(code="Paste your broken code", issue="Describe the issue (optional)")
    async def fix_code(self, ctx, *, code: str, issue: str = "Not specified"):
        """Fix errors in code"""
        await ctx.defer()
        
        try:
            prompt = f"""
            CODE FIXING REQUEST:
            
            Issue Description: {issue}
            
            Code to Fix:
            {code}
            
            Please:
            1. Identify all errors
            2. Provide the fixed code
            3. Explain what was wrong and how you fixed it
            4. Suggest improvements
            
            Return the fixed code in a code block.
            """
            
            response = self.groq.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.2
            )
            
            fix_result = response.choices[0].message.content
            
            embed = discord.Embed(
                title="🔧 Code Fix Report",
                description=f"**Issue:** {issue}\n\n{fix_result}",
                color=0x2ecc71,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Fixed for {ctx.author.display_name}")
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Fix failed: {str(e)}")

    # ✅ NEW COMMAND: CONVERT CODE
    @commands.hybrid_command(name="convert", description="Convert code between programming languages")
    @app_commands.describe(code="Code to convert", from_lang="Source language", to_lang="Target language")
    async def convert_code(self, ctx, code: str, from_lang: str, to_lang: str):
        """Convert code between programming languages"""
        await ctx.defer()
        
        try:
            prompt = f"""
            CODE CONVERSION REQUEST:
            
            Convert from {from_lang} to {to_lang}:
            
            Source Code ({from_lang}):
            {code}
            
            Please:
            1. Convert the code accurately to {to_lang}
            2. Explain any major differences between languages
            3. Provide the converted code in a proper code block
            4. Mention any limitations or considerations
            """
            
            response = self.groq.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            conversion = response.choices[0].message.content
            
            embed = discord.Embed(
                title="🔄 Code Conversion",
                description=f"**{from_lang} → {to_lang}**\n\n{conversion}",
                color=0x9b59b6,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Converted for {ctx.author.display_name}")
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Conversion failed: {str(e)}")

    @commands.hybrid_command(name="clear", description="Clear your conversation history")
    async def clear_chat(self, ctx):
        """Clear AI conversation history"""
        user_id = ctx.author.id
        if user_id in self.conversations:
            self.conversations[user_id] = []
            await ctx.send("✅ Your conversation history cleared!")
        else:
            await ctx.send("ℹ️ No conversation history to clear.")

    @commands.hybrid_command(name="stats", description="Check your AI usage stats")
    async def user_stats(self, ctx):
        """Show user statistics"""
        user_id = ctx.author.id
        stats = self.user_stats.get(user_id, {"requests": 0, "first_use": datetime.now()})
        
        embed = discord.Embed(
            title="📊 Your AI Stats",
            color=0x3498db,
            timestamp=datetime.now()
        )
        embed.add_field(name="Total Requests", value=stats["requests"], inline=True)
        embed.add_field(name="First Use", value=stats["first_use"].strftime("%Y-%m-%d"), inline=True)
        embed.set_footer(text="Keep exploring! 🚀")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ping", description="Check bot status")
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! **Latency:** {latency}ms\n**Status:** Online ✅")

    @commands.hybrid_command(name="test", description="Test AI functionality")
    async def test_ai(self, ctx):
        """Test AI with simple question"""
        await ctx.defer()
        response = await self.get_ai_response("Hello, who are you?")
        
        if "❌" in response or "⚠️" in response:
            await ctx.followup.send(f"❌ **Test Failed:** {response}")
        else:
            await ctx.followup.send(f"✅ **Test Successful!**\n\n**AI Response:** {response}")

    @commands.hybrid_command(name="setchannel", description="Set AI auto-response channel")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Set AI channel for auto-response"""
        try:
            self.bot.ai_channels[str(ctx.guild.id)] = str(channel.id)
            await ctx.send(f"✅ **AI Channel Set!**\nI will auto-respond in {channel.mention}")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

    def update_stats(self, user_id):
        """Update user statistics"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {"requests": 0, "first_use": datetime.now()}
        self.user_stats[user_id]["requests"] += 1

async def setup(bot):
    await bot.add_cog(AICommands(bot))
