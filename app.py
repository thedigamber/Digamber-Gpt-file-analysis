import discord
from discord.ext import commands, tasks
import os
import json
import asyncio
import aiohttp
from flask import Flask
from datetime import datetime
import traceback
import io
import groq  # Groq AI for analysis

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 DigamberGPT - Operational"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

TOKEN = os.getenv("DISCORD_TOKEN")

class ChatGPTBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.config = config
        self.start_time = datetime.now()
        self.session = None
        self.ai_channels = {}  # Store AI channels per server
        self.groq_client = groq.Client(api_key=os.getenv('GROQ_API_KEY'))  # Groq client

    async def setup_hook(self):
        # Start session
        self.session = aiohttp.ClientSession()
        
        # Load cogs
        cogs = ['cogs.ai_commands', 'cogs.mod_commands', 'cogs.fun_commands', 'cogs.build_commands']
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded: {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
                traceback.print_exc()
        
        # Sync commands
        try:
            print("🔄 Syncing slash commands...")
            synced = await self.tree.sync()
            print(f"✅ Successfully synced {len(synced)} slash commands")
        except Exception as e:
            print(f"❌ Slash command sync failed: {e}")
            traceback.print_exc()
        
        # Start tasks
        self.update_presence.start()

    async def on_ready(self):
        print(f"\n🚀 {self.user} is ONLINE!")
        print(f"📊 Servers: {len(self.guilds)}")
        print(f"👥 Users: {sum(g.member_count for g in self.guilds)}")
        
        commands_list = [cmd.name for cmd in self.tree.get_commands()]
        print(f"🎯 Available commands: {', '.join(commands_list)}")
        
        # Start Flask in background for Render
        if os.environ.get('RENDER'):
            import threading
            threading.Thread(target=run_flask, daemon=True).start()
            print("🌐 Flask server started")

    async def on_guild_join(self, guild):
        """Auto-sync commands when bot joins new server"""
        try:
            await self.tree.sync(guild=guild)
            print(f"✅ Commands synced for new server: {guild.name}")
        except Exception as e:
            print(f"❌ Failed to sync commands for {guild.name}: {e}")

    async def on_message(self, message):
        if message.author.bot:
            return

        # ✅ FILE UPLOAD DETECTION
        if message.attachments:
            await self.process_file_upload(message)
            return

        # ✅ CHAT MESSAGE DETECTION
        guild_id = str(message.guild.id)
        
        if guild_id in self.ai_channels:
            ai_channel_id = self.ai_channels[guild_id]
            
            if str(message.channel.id) == ai_channel_id:
                if not message.content.startswith('!'):
                    await self.process_ai_message(message)
                    return
        
        # ✅ PROCESS REGULAR COMMANDS
        await self.process_commands(message)

    # ✅ AUTO-FIX FILE FUNCTION
    async def auto_fix_file(self, file_content, filename):
        """Auto-fix file content and return fixed version"""
        try:
            # For non-fixable files
            if filename.lower().endswith(('.zip', '.rar', '.7z', '.jpg', '.jpeg', '.png', '.gif')):
                return None, "📦 **I can't fix archive/image files**\n\nPlease upload individual code files:\n• `.py` - Python\n• `.js` - JavaScript\n• `.java` - Java\n• `.txt` - Text\n• `.html` - Web pages"
            
            prompt = f"""
            FIX THIS CODE FILE:
            Filename: {filename}
            
            Fix ALL errors and return ONLY the corrected code.
            Fix: syntax errors, bugs, logic errors, security issues.
            Return PURE fixed code without explanations.
            
            Code to fix:
            {file_content[:3000]}
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.1
            )
            
            fixed_content = response.choices[0].message.content
            
            # Clean code block markers
            if fixed_content.startswith('```'):
                lines = fixed_content.split('\n')
                if len(lines) > 1 and lines[0].startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].startswith('```'):
                    lines = lines[:-1]
                fixed_content = '\n'.join(lines)
            
            return fixed_content.strip(), None
            
        except Exception as e:
            print(f"Auto-fix error: {e}")
            return None, f"❌ Fixing failed"

    # ✅ COMPLETE AUTO-FIX PROCESSOR
    async def process_file_upload(self, message):
        """Process file uploads - AUTO-FIX + SEND FIXED FILE"""
        try:
            for attachment in message.attachments:
                if attachment.size > 100 * 1024 * 1024:
                    await message.reply("❌ File too large (100MB max)")
                    continue
                
                # Step 1: Show processing
                processing_msg = await message.reply(f"🔧 **Auto-Fixing `{attachment.filename}`**\n⏳ Please wait...")
                
                try:
                    # Step 2: Download file
                    file_content = await attachment.read()
                    file_text = file_content.decode('utf-8', errors='ignore')
                    
                    # Step 3: Auto-fix file
                    await processing_msg.edit(content=f"🔧 **Auto-Fixing `{attachment.filename}`**\n🔍 Analyzing errors...")
                    
                    fixed_content, error_msg = await self.auto_fix_file(file_text, attachment.filename)
                    
                    if error_msg:
                        await processing_msg.edit(content=error_msg)
                        return
                    
                    if not fixed_content:
                        await processing_msg.edit(content=f"❌ **Cannot fix `{attachment.filename}`**\nPlease upload code files (.py, .js, .java, etc.)")
                        return
                    
                    # Step 4: Create fixed file
                    await processing_msg.edit(content=f"🔧 **Auto-Fixing `{attachment.filename}`**\n📁 Creating fixed file...")
                    
                    # Create new filename
                    name, ext = os.path.splitext(attachment.filename)
                    fixed_filename = f"{name}_FIXED{ext}"
                    
                    # Create file object
                    fixed_file = discord.File(
                        io.BytesIO(fixed_content.encode('utf-8')),
                        filename=fixed_filename
                    )
                    
                    # Step 5: Send fixed file
                    await processing_msg.delete()  # Remove processing message
                    
                    await message.reply(
                        content=f"✅ **Fixed File Ready!**\n**Original:** `{attachment.filename}`\n**Fixed:** `{fixed_filename}`",
                        file=fixed_file
                    )
                    
                except Exception as file_error:
                    await processing_msg.edit(content=f"❌ **Processing failed**\nPlease try again with a different file.")
                    
        except Exception as e:
            await message.reply("❌ Upload error. Please try again.")

    # ✅ CHAT MESSAGE PROCESSOR WITH CHANNEL MEMORY
    async def process_ai_message(self, message):
        """Process AI messages automatically with CHANNEL MEMORY"""
        try:
            ai_cog = self.get_cog('AICommands')
            if ai_cog:
                async with message.channel.typing():
                    # ✅ PASS CHANNEL ID & USERNAME FOR CHANNEL MEMORY
                    response = await ai_cog.get_ai_response(
                        message.content, 
                        message.author.id,
                        message.channel.id, 
                        message.author.display_name
                    )
                    await message.reply(response)
            else:
                # Fallback if cog not loaded
                await message.reply("🤖 **Chat Feature**\n\nUse `/ask` command to chat with me!\nOr upload files for auto-fixing.")
                
        except Exception as e:
            print(f"AI chat error: {e}")
            await message.reply("💬 **Chat with me using:**\n`/ask [your message]`")

    @tasks.loop(minutes=10)
    async def update_presence(self):
        activities = [
            discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"),
            discord.Activity(type=discord.ActivityType.listening, name="Chat & File Fix"),
            discord.Activity(type=discord.ActivityType.playing, name="/ask to chat!")
        ]
        activity = activities[(datetime.now().minute // 10) % len(activities)]
        await self.change_presence(activity=activity)

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

# Run bot
if __name__ == "__main__":
    bot = ChatGPTBot()
    bot.run(TOKEN)
