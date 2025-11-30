import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import aiohttp
import json

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="quote", description="Get an inspirational quote")
    async def inspirational_quote(self, ctx):
        """Get random inspirational quote"""
        quotes = [
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Innovation distinguishes between a leader and a follower. - Steve Jobs", 
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
            "Strive not to be a success, but rather to be of value. - Albert Einstein",
            "The way to get started is to quit talking and begin doing. - Walt Disney",
            "Code is like humor. When you have to explain it, it's bad. - Cory House",
            "First, solve the problem. Then, write the code. - John Johnson",
            "Programming isn't about what you know; it's about what you can figure out. - Chris Pine",
            "The best error message is the one that never shows up. - Thomas Fuchs"
        ]
        
        embed = discord.Embed(
            title="💫 Inspirational Quote",
            description=random.choice(quotes),
            color=0xf39c12
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="poll", description="Create a quick poll")
    @app_commands.describe(question="The poll question", option1="First option", option2="Second option")
    async def create_poll(self, ctx, question: str, option1: str, option2: str):
        """Create a simple poll"""
        embed = discord.Embed(
            title="📊 Poll",
            description=question,
            color=0x9b59b6
        )
        embed.add_field(name="Option 1", value=option1, inline=True)
        embed.add_field(name="Option 2", value=option2, inline=True)
        embed.set_footer(text="React with 1️⃣ or 2️⃣ to vote!")
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")

    # ✅ NEW: PROGRAMMING JOKE COMMAND
    @commands.hybrid_command(name="codejoke", description="Get a programming joke")
    async def code_joke(self, ctx):
        """Get random programming joke"""
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Algorithm: Word used by programmers when they don't want to explain what they did.",
            "Why do Java developers wear glasses? Because they can't C#!",
            "I told my computer I needed a break... now it won't stop sending me Kit-Kat ads.",
            "Why was the JavaScript developer sad? Because he didn't Node how to Express himself!",
            "There are only 10 types of people in the world: those who understand binary and those who don't.",
            "Why do programmers hate nature? It has too many bugs.",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
            "Why did the programmer quit his job? Because he didn't get arrays!",
            "What's a programmer's favorite hangout place? Foo Bar!"
        ]
        
        embed = discord.Embed(
            title="😂 Programming Joke",
            description=random.choice(jokes),
            color=0xe74c3c
        )
        await ctx.send(embed=embed)

    # ✅ NEW: FILE TYPE TRIVIA
    @commands.hybrid_command(name="filefact", description="Get interesting file/code facts")
    async def file_fact(self, ctx):
        """Get random file/code fact"""
        facts = [
            "📁 The first computer virus was created in 1983 called 'Elk Cloner' for Apple II systems.",
            "💾 The average developer creates about 70,000 lines of code per year.",
            "🐛 The term 'bug' came from an actual moth found in a Harvard Mark II computer in 1947.",
            "🔧 APK files are actually ZIP archives with a different extension!",
            "🚀 The first programming language was called 'Plankalkül' created in 1940s.",
            "📱 Android APK stands for 'Android Package Kit'.",
            "💻 The first computer program was written by Ada Lovelace in 1843.",
            "🌐 The world's first website is still online: http://info.cern.ch",
            "⚡ Python is named after Monty Python, not the snake!",
            "🔒 The first password was used at MIT in the 1960s."
        ]
        
        embed = discord.Embed(
            title="📚 Tech Fact",
            description=random.choice(facts),
            color=0x3498db
        )
        await ctx.send(embed=embed)

    # ✅ NEW: RANDOM CODE CHALLENGE
    @commands.hybrid_command(name="codechallenge", description="Get a random coding challenge")
    async def code_challenge(self, ctx):
        """Give random coding challenge"""
        challenges = [
            "**Easy**: Write a function to reverse a string without using built-in reverse methods.",
            "**Easy**: Create a program that finds the largest number in an array.",
            "**Medium**: Build a simple calculator that can add, subtract, multiply, and divide.",
            "**Medium**: Write a function that checks if a string is a palindrome.",
            "**Hard**: Create a todo app with file persistence (save tasks to a file).",
            "**Hard**: Build a simple web server that serves static HTML files.",
            "**Easy**: Write a program that converts Celsius to Fahrenheit.",
            "**Medium**: Create a password generator with customizable length and character sets.",
            "**Hard**: Build a chat application with real-time messaging.",
            "**Expert**: Create your own programming language interpreter!"
        ]
        
        embed = discord.Embed(
            title="💻 Code Challenge",
            description=random.choice(challenges),
            color=0x2ecc71
        )
        embed.set_footer(text="Use /analyze to get your code checked!")
        await ctx.send(embed=embed)

    # ✅ NEW: PROGRAMMING LANGUAGE QUIZ
    @commands.hybrid_command(name="quiz", description="Test your programming knowledge")
    async def programming_quiz(self, ctx):
        """Programming quiz"""
        quizzes = [
            {
                "question": "What does HTML stand for?",
                "options": ["Hyper Text Markup Language", "High Tech Modern Language", "Hyper Transfer Markup Language", "Home Tool Markup Language"],
                "answer": 0
            },
            {
                "question": "Which language is known as the 'mother of all languages'?",
                "options": ["C", "Python", "Java", "Assembly"],
                "answer": 0
            },
            {
                "question": "What does API stand for?",
                "options": ["Application Programming Interface", "Advanced Programming Interface", "Application Process Integration", "Automated Programming Interface"],
                "answer": 0
            },
            {
                "question": "Which company developed Python?",
                "options": ["Google", "Microsoft", "Guido van Rossum", "Facebook"],
                "answer": 2
            }
        ]
        
        quiz = random.choice(quizzes)
        
        embed = discord.Embed(
            title="🧠 Programming Quiz",
            description=quiz["question"],
            color=0x9b59b6
        )
        
        for i, option in enumerate(quiz["options"]):
            embed.add_field(name=f"Option {i+1}", value=option, inline=False)
            
        embed.set_footer(text="Reply with the option number!")
        
        message = await ctx.send(embed=embed)
        
        # Add reactions for answers
        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        for i in range(len(quiz["options"])):
            await message.add_reaction(reactions[i])

    # ✅ NEW: TECH SUPPORT SIMULATOR
    @commands.hybrid_command(name="techsupport", description="Get random tech support advice")
    async def tech_support(self, ctx):
        """Fun tech support simulator"""
        advice = [
            "🔄 **Solution**: Have you tried turning it off and on again?",
            "🔍 **Solution**: Check if it's plugged in properly.",
            "🛠️ **Solution**: Update your drivers and restart.",
            "🧹 **Solution**: Clear your cache and cookies.",
            "📡 **Solution**: Check your internet connection.",
            "🦠 **Solution**: Run a virus scan immediately!",
            "💾 **Solution**: Free up some disk space.",
            "🔧 **Solution**: Reinstall the application.",
            "📚 **Solution**: Read the documentation carefully.",
            "👨‍💻 **Solution**: Contact the developer for support."
        ]
        
        problems = [
            "My computer is running slow...",
            "The app keeps crashing!",
            "I can't connect to the internet.",
            "My files got corrupted!",
            "The screen is flickering...",
            "I forgot my password!",
            "The software won't install.",
            "I'm getting weird error messages.",
            "My code won't compile!",
            "The database connection failed."
        ]
        
        embed = discord.Embed(
            title="👨‍💻 Tech Support",
            description=f"**Problem:** {random.choice(problems)}\n\n{random.choice(advice)}",
            color=0xe67e22
        )
        embed.set_footer(text="Disclaimer: This is for fun only! 😄")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FunCommands(bot))
