import discord
import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import random
import aiofiles
import os

class Helpers:
    @staticmethod
    def format_time(seconds: int) -> str:
        """Format seconds into human readable time"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"

    @staticmethod
    def create_embed(
        title: str,
        description: str = "",
        color: int = 0x3498db,
        fields: List[Dict[str, Any]] = None,
        thumbnail: str = None,
        footer: str = None,
        author: str = None
    ) -> discord.Embed:
        """Create a formatted embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', '\u200b'),
                    value=field.get('value', '\u200b'),
                    inline=field.get('inline', False)
                )
                
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
            
        if footer:
            embed.set_footer(text=footer)
            
        if author:
            embed.set_author(name=author)
            
        return embed

    @staticmethod
    def contains_links(text: str) -> bool:
        """Check if text contains URLs"""
        url_pattern = r'https?://\S+|www\.\S+'
        return bool(re.search(url_pattern, text, re.IGNORECASE))

    @staticmethod
    def clean_content(text: str, max_length: int = 2000) -> str:
        """Clean and truncate text content"""
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
            
        return text

    @staticmethod
    def get_random_color() -> int:
        """Get a random discord color"""
        colors = [
            0x1abc9c, 0x2ecc71, 0x3498db, 0x9b59b6, 
            0xe91e63, 0xf1c40f, 0xe67e22, 0xe74c3c
        ]
        return random.choice(colors)

    @staticmethod
    def is_admin(ctx) -> bool:
        """Check if user has admin permissions"""
        return ctx.author.guild_permissions.administrator

    @staticmethod
    def format_number(number: int) -> str:
        """Format large numbers with K/M suffix"""
        if number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
        else:
            return str(number)

    @staticmethod
    def calculate_uptime(start_time: datetime) -> str:
        """Calculate uptime from start time"""
        uptime = datetime.now() - start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"

    # ✅ NEW: FILE TYPE DETECTION
    @staticmethod
    def detect_file_type(filename: str) -> str:
        """Detect file type from extension"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        file_types = {
            # Programming languages
            'py': 'Python', 'js': 'JavaScript', 'java': 'Java', 'cpp': 'C++', 'c': 'C',
            'html': 'HTML', 'css': 'CSS', 'php': 'PHP', 'rb': 'Ruby', 'go': 'Go',
            'rs': 'Rust', 'ts': 'TypeScript', 'swift': 'Swift', 'kt': 'Kotlin',
            
            # Android
            'apk': 'Android APK', 'aab': 'Android App Bundle',
            
            # Documents
            'txt': 'Text', 'pdf': 'PDF', 'doc': 'Word', 'docx': 'Word',
            'xls': 'Excel', 'xlsx': 'Excel', 'ppt': 'PowerPoint', 'pptx': 'PowerPoint',
            
            # Images
            'jpg': 'Image', 'jpeg': 'Image', 'png': 'Image', 'gif': 'Image',
            'bmp': 'Image', 'svg': 'Image', 'webp': 'Image',
            
            # Archives
            'zip': 'Archive', 'rar': 'Archive', '7z': 'Archive', 'tar': 'Archive',
            'gz': 'Archive',
            
            # Config files
            'json': 'JSON', 'xml': 'XML', 'yaml': 'YAML', 'yml': 'YAML',
            'ini': 'Config', 'cfg': 'Config', 'conf': 'Config',
            
            # Other
            'sql': 'SQL', 'md': 'Markdown', 'csv': 'CSV'
        }
        
        return file_types.get(extension, 'Unknown')

    # ✅ NEW: CODE LANGUAGE DETECTION
    @staticmethod
    def detect_code_language(code: str) -> str:
        """Detect programming language from code snippet"""
        code_lower = code.lower()
        
        if 'import android' in code_lower or 'package com.example' in code_lower:
            return 'Java'
        elif 'fun main()' in code_lower and 'println' in code_lower:
            return 'Kotlin'
        elif 'import React' in code_lower or 'function Component' in code_lower:
            return 'JavaScript'
        elif 'from flask import' in code_lower or 'import django' in code_lower:
            return 'Python'
        elif '#include <iostream>' in code_lower or 'using namespace std;' in code_lower:
            return 'C++'
        elif 'public class' in code_lower and 'public static void main' in code_lower:
            return 'Java'
        elif 'def ' in code_lower and 'import ' in code_lower:
            return 'Python'
        elif 'function ' in code_lower and 'const ' in code_lower:
            return 'JavaScript'
        elif '<?php' in code_lower:
            return 'PHP'
        elif 'fn main()' in code_lower:
            return 'Rust'
        else:
            return 'Unknown'

    # ✅ NEW: FILE SIZE FORMATTER
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.1f}{size_names[i]}"

    # ✅ NEW: SAFE FILENAME CHECK
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe to process"""
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.sh', '.bin', '.dll']
        dangerous_patterns = ['.htaccess', '.env', 'config', 'password', 'secret']
        
        filename_lower = filename.lower()
        
        # Check dangerous extensions
        if any(filename_lower.endswith(ext) for ext in dangerous_extensions):
            return False
            
        # Check dangerous patterns
        if any(pattern in filename_lower for pattern in dangerous_patterns):
            return False
            
        return True

    # ✅ NEW: CODE BLOCK EXTRACTOR
    @staticmethod
    def extract_code_blocks(text: str) -> List[Dict[str, str]]:
        """Extract code blocks from text"""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        
        matches = re.findall(pattern, text, re.DOTALL)
        for lang, code in matches:
            code_blocks.append({
                'language': lang if lang else 'text',
                'code': code.strip()
            })
            
        return code_blocks

    # ✅ NEW: BUILD PROGRESS EMBED
    @staticmethod
    def create_build_embed(stage: str, project_type: str, status: str = "in_progress") -> discord.Embed:
        """Create build progress embed"""
        status_colors = {
            "in_progress": 0xf39c12,
            "success": 0x2ecc71,
            "failed": 0xe74c3c
        }
        
        status_emojis = {
            "in_progress": "🔄",
            "success": "✅",
            "failed": "❌"
        }
        
        embed = discord.Embed(
            title=f"{status_emojis[status]} {project_type} Build - {stage}",
            color=status_colors[status],
            timestamp=datetime.now()
        )
        
        if status == "in_progress":
            embed.description = "Building your project... This may take a moment."
        elif status == "success":
            embed.description = "Build completed successfully! 🎉"
        else:
            embed.description = "Build failed. Check the error details."
            
        return embed

    # ✅ NEW: TECH STACK DETECTOR
    @staticmethod
    def detect_tech_stack(code: str) -> List[str]:
        """Detect technologies/frameworks from code"""
        tech_stack = []
        code_lower = code.lower()
        
        # Frontend frameworks
        if 'react' in code_lower or 'jsx' in code_lower:
            tech_stack.append('React')
        if 'vue' in code_lower:
            tech_stack.append('Vue.js')
        if 'angular' in code_lower:
            tech_stack.append('Angular')
            
        # Backend frameworks
        if 'express' in code_lower:
            tech_stack.append('Express.js')
        if 'flask' in code_lower:
            tech_stack.append('Flask')
        if 'django' in code_lower:
            tech_stack.append('Django')
        if 'spring' in code_lower:
            tech_stack.append('Spring Boot')
            
        # Databases
        if 'mongodb' in code_lower or 'mongoose' in code_lower:
            tech_stack.append('MongoDB')
        if 'mysql' in code_lower or 'postgresql' in code_lower:
            tech_stack.append('SQL Database')
            
        # Mobile
        if 'android' in code_lower:
            tech_stack.append('Android')
        if 'flutter' in code_lower:
            tech_stack.append('Flutter')
            
        return tech_stack if tech_stack else ['Vanilla']

# Helper instance
helpers = Helpers()
