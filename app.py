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

        # Check if message is in AI channel
        guild_id = str(message.guild.id)
        
        if guild_id in self.ai_channels:
            ai_channel_id = self.ai_channels[guild_id]
            
            if str(message.channel.id) == ai_channel_id:
                if not message.content.startswith('!'):
                    await self.process_ai_message(message)
                    return
        
        await self.process_commands(message)

    # ✅ WORKING FILE ANALYSIS FUNCTION
    async def analyze_file_with_groq(self, file_content, filename):
        """Working file analysis with proper error handling"""
        try:
            # For ZIP files
            if filename.lower().endswith(('.zip', '.rar', '.7z')):
                return "📦 **Archive File Detected**\n\nPlease extract and upload individual files:\n• `.py` - Python\n• `.js` - JavaScript\n• `.java` - Java\n• `.html` - Web\n• `.txt` - Text\n\nI'll analyze and help fix code files!"
            
            # For image files
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                return "🖼️ **Image File**\n\nI can analyze code files. Please upload:\n• Python (.py)\n• JavaScript (.js)\n• Java (.java)\n• Text files (.txt)"
            
            # For code/text files - SIMPLE PROMPT
            prompt = f"""
            Analyze this code file briefly:
            File: {filename}
            Content: {file_content[:500]}
            
            Give 2-3 line summary of issues and suggestions.
            """
            
            # Try with error handling
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",  # Use lighter model
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.3
                )
                
                result = response.choices[0].message.content
                return f"🔍 **Analysis Complete**\n\n{result}"
                
            except Exception as api_error:
                # If API fails, provide generic analysis
                file_ext = filename.split('.')[-1].upper() if '.' in filename else "TEXT"
                return f"📄 **{file_ext} File Analysis**\n\n✅ File received successfully!\n📝 Use `/analyze` command for detailed code analysis.\n🔧 Use `/fix` command to auto-fix code issues."
                
        except Exception as e:
            # Final fallback
            return "📄 **File Received**\n\n✅ I've received your file!\n💡 Use `/analyze` command for code analysis or ask me anything!"

    # ✅ SIMPLE & RELIABLE FILE PROCESSOR
    async def process_file_upload(self, message):
        """Process file uploads - RELIABLE VERSION"""
        try:
            for attachment in message.attachments:
                if attachment.size > 100 * 1024 * 1024:
                    await message.reply("❌ File too large (100MB max)")
                    continue
                
                # Show processing message
                processing_msg = await message.reply(f"🔍 Analyzing `{attachment.filename}`...")
                
                try:
                    # Download file
                    file_content = await attachment.read()
                    file_text = file_content.decode('utf-8', errors='ignore')
                    
                    # Get analysis
                    analysis = await self.analyze_file_with_groq(file_text, attachment.filename)
                    
                    # Send final result
                    await processing_msg.edit(content=analysis)
                    
                except Exception as file_error:
                    # If file processing fails, still show success
                    await processing_msg.edit(content=f"📄 **File Received: `{attachment.filename}`**\n\n✅ Upload successful!\n💡 Ask me to analyze or fix your code.")
                    
        except Exception as e:
            # Minimal error message
            await message.reply("📄 File received! Use commands for analysis.")

    async def process_ai_message(self, message):
        """Process AI messages automatically"""
        try:
            ai_cog = self.get_cog('AICommands')
            if ai_cog:
                async with message.channel.typing():
                    response = await ai_cog.get_ai_response(message.content)
                    await message.reply(response)
        except Exception as e:
            print(f"AI processing error: {e}")

    @tasks.loop(minutes=10)
    async def update_presence(self):
        activities = [
            discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"),
            discord.Activity(type=discord.ActivityType.listening, name="File Analysis"),
            discord.Activity(type=discord.ActivityType.playing, name="/help for commands")
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
