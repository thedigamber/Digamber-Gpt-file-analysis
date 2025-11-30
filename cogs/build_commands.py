import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp
import json
import asyncio
from groq import Groq
from datetime import datetime

class BuildCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.build_services = {
            "android": "📱 APK Builder",
            "web": "🌐 Web Project", 
            "python": "🐍 Python App",
            "javascript": "⚡ JavaScript App",
            "java": "☕ Java App",
            "cpp": "🔧 C++ Project"
        }

    # ✅ NEW: APK BUILDING COMMAND
    @commands.hybrid_command(name="buildapk", description="Build APK from source code")
    @app_commands.describe(
        source_code="Paste your Android/Java code",
        project_name="Name of your project",
        description="Brief description (optional)"
    )
    async def build_apk(self, ctx, source_code: str, project_name: str = "MyApp", description: str = "Android Application"):
        """Build APK from source code"""
        await ctx.defer()
        
        try:
            # Step 1: Analyze and prepare build
            build_prep = await ctx.followup.send("🔧 Preparing APK build...")
            
            # Step 2: Generate complete Android project
            prompt = f"""
            ANDROID APK BUILD REQUEST:
            
            Project Name: {project_name}
            Description: {description}
            
            Source Code:
            {source_code}
            
            Please create a complete Android Studio project that can be built into APK:
            1. Generate proper directory structure
            2. Create AndroidManifest.xml
            3. Create build.gradle files
            4. Organize Java/Kotlin code properly
            5. Include all necessary resources
            6. Provide build instructions
            
            Return the complete project structure with all files.
            """
            
            response = self.groq.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.2
            )
            
            project_structure = response.choices[0].message.content
            
            # Step 3: Create build instructions
            build_instructions = """
            **📱 APK Build Instructions:**
            
            **Method 1: Android Studio**
            1. Create new project in Android Studio
            2. Replace generated files with provided code
            3. Build → Build Bundle(s) / APK(s)
            4. Locate APK in app/build/outputs/apk/
            
            **Method 2: Command Line**
            ```bash
            ./gradlew assembleDebug
            ```
            
            **Method 3: Online Build Services**
            • **GitHub Actions** (Free)
            • **Bitrise** (Free tier)
            • **Codemagic** (Free for open source)
            """
            
            # Create embed with project details
            embed = discord.Embed(
                title=f"📱 {project_name} - APK Project",
                description=f"**Description:** {description}\n\n**Project Structure:**\n```\n{project_structure[:2000]}...\n```",
                color=0x4CAF50,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="🚀 Build Methods",
                value=build_instructions,
                inline=False
            )
            
            embed.add_field(
                name="📦 Next Steps",
                value="1. Copy the project structure\n2. Follow build instructions\n3. Test your APK\n4. Deploy to Google Play",
                inline=False
            )
            
            embed.set_footer(text=f"Built for {ctx.author.display_name}")
            
            await build_prep.edit(content="✅ APK Project Generated!", embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ APK build failed: {str(e)}")

    # ✅ NEW: WEB PROJECT BUILDER
    @commands.hybrid_command(name="buildweb", description="Create complete web project")
    @app_commands.describe(
        description="Describe your web project",
        features="List features you want",
        technology="Preferred tech stack (optional)"
    )
    async def build_web(self, ctx, description: str, features: str = "Basic website", technology: str = "HTML/CSS/JS"):
        """Build complete web project"""
        await ctx.defer()
        
        try:
            prompt = f"""
            WEB PROJECT BUILD REQUEST:
            
            Description: {description}
            Features: {features}
            Technology: {technology}
            
            Please create a complete web project structure:
            1. HTML files with proper structure
            2. CSS styling (modern and responsive)
            3. JavaScript functionality
            4. Project organization
            5. Deployment instructions
            
            Provide complete, ready-to-run code.
            """
            
            response = self.groq.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0.3
            )
            
            web_project = response.choices[0].message.content
            
            embed = discord.Embed(
                title="🌐 Web Project Generated",
                description=f"**Description:** {description}\n**Features:** {features}\n**Tech:** {technology}",
                color=0x2196F3,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📁 Project Code",
                value=f"```\n{web_project[:2000]}...\n```",
                inline=False
            )
            
            embed.add_field(
                name="🚀 Deployment",
                value="""
                **Free Hosting Options:**
                • **Netlify** - Drag & drop
                • **Vercel** - GitHub integration  
                • **GitHub Pages** - Free for repos
                • **Render** - Full stack apps
                """,
                inline=False
            )
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Web project build failed: {str(e)}")

    # ✅ NEW: MULTI-LANGUAGE PROJECT BUILDER
    @commands.hybrid_command(name="build", description="Build project in any programming language")
    @app_commands.describe(
        language="Programming language",
        project_type="Type of project",
        requirements="Project requirements/features"
    )
    async def build_project(self, ctx, language: str, project_type: str, requirements: str):
        """Build project in any programming language"""
        await ctx.defer()
        
        try:
            prompt = f"""
            PROJECT BUILD REQUEST:
            
            Language: {language}
            Project Type: {project_type}
            Requirements: {requirements}
            
            Please create a complete, runnable project:
            1. Proper project structure
            2. All necessary files
            3. Installation instructions
            4. Running instructions
            5. Dependencies list
            
            Make it production-ready and well-documented.
            """
            
            response = self.groq.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2800,
                temperature=0.3
            )
            
            project = response.choices[0].message.content
            
            embed = discord.Embed(
                title=f"🔧 {language} Project - {project_type}",
                description=f"**Requirements:** {requirements}",
                color=0xFF9800,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📦 Complete Project",
                value=f"```\n{project[:2000]}...\n```",
                inline=False
            )
            
            embed.add_field(
                name="⚡ Quick Start",
                value=f"""
                1. Create project directory
                2. Add provided files
                3. Install dependencies
                4. Run according to instructions
                5. Customize as needed
                """,
                inline=False
            )
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Project build failed: {str(e)}")

    # ✅ NEW: GITHUB SETUP HELPER
    @commands.hybrid_command(name="github", description="Generate GitHub repository setup")
    @app_commands.describe(
        project_name="Name of your project",
        description="Project description",
        language="Main programming language"
    )
    async def github_setup(self, ctx, project_name: str, description: str, language: str = "Multiple"):
        """Generate GitHub repository setup"""
        await ctx.defer()
        
        try:
            prompt = f"""
            GITHUB REPOSITORY SETUP:
            
            Project: {project_name}
            Description: {description}
            Language: {language}
            
            Please provide:
            1. Complete README.md with badges
            2. .gitignore file for the language
            3. LICENSE file (MIT recommended)
            4. GitHub Actions CI/CD setup
            5. Contribution guidelines
            6. Issue and PR templates
            
            Make it professional and complete.
            """
            
            response = self.groq.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.2
            )
            
            github_setup = response.choices[0].message.content
            
            embed = discord.Embed(
                title=f"🐙 GitHub Setup - {project_name}",
                description=f"**Description:** {description}\n**Language:** {language}",
                color=0x333333,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📄 Repository Files",
                value=f"```\n{github_setup[:1500]}...\n```",
                inline=False
            )
            
            embed.add_field(
                name="🚀 Setup Steps",
                value="""
                1. Create new repo on GitHub
                2. Add these files to your repo
                3. Push your code
                4. Enable GitHub Pages (if web project)
                5. Set up GitHub Actions
                """,
                inline=False
            )
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ GitHub setup failed: {str(e)}")

    # ✅ NEW: BUILD SERVICES INFO
    @commands.hybrid_command(name="buildservices", description="Show available build services")
    async def build_services_info(self, ctx):
        """Show available build services"""
        embed = discord.Embed(
            title="🔧 Available Build Services",
            description="I can help you build projects in these technologies:",
            color=0x9C27B0,
            timestamp=datetime.now()
        )
        
        for lang, desc in self.build_services.items():
            embed.add_field(name=desc, value=f"`/{lang} projects`", inline=True)
            
        embed.add_field(
            name="📱 APK Building",
            value="Use `/buildapk` with your Android code",
            inline=False
        )
        
        embed.add_field(
            name="🌐 Web Projects", 
            value="Use `/buildweb` for HTML/CSS/JS projects",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Custom Projects",
            value="Use `/build` for any programming language",
            inline=False
        )
        
        embed.set_footer(text="Upload files for automatic analysis!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BuildCommands(bot))
