import json
import aiofiles
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

class JSONDatabase:
    def __init__(self, db_file: str = "data/database.json"):
        self.db_file = db_file
        self.ensure_directory()

    def ensure_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)

    async def read_data(self) -> Dict[str, Any]:
        """Read data from JSON file"""
        try:
            async with aiofiles.open(self.db_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content) if content else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    async def write_data(self, data: Dict[str, Any]):
        """Write data to JSON file"""
        async with aiofiles.open(self.db_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=4, ensure_ascii=False))

    async def get_guild_settings(self, guild_id: str) -> Dict[str, Any]:
        """Get guild-specific settings"""
        data = await self.read_data()
        return data.get('guilds', {}).get(guild_id, {})

    async def set_guild_settings(self, guild_id: str, settings: Dict[str, Any]):
        """Set guild-specific settings"""
        data = await self.read_data()
        if 'guilds' not in data:
            data['guilds'] = {}
        data['guilds'][guild_id] = settings
        await self.write_data(data)

    async def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user-specific data"""
        data = await self.read_data()
        return data.get('users', {}).get(user_id, {})

    async def set_user_data(self, user_id: str, user_data: Dict[str, Any]):
        """Set user-specific data"""
        data = await self.read_data()
        if 'users' not in data:
            data['users'] = {}
        data['users'][user_id] = user_data
        await self.write_data(data)

    async def increment_user_requests(self, user_id: str):
        """Increment user request count"""
        user_data = await self.get_user_data(user_id)
        user_data['total_requests'] = user_data.get('total_requests', 0) + 1
        user_data['last_used'] = datetime.now().isoformat()
        
        if 'first_used' not in user_data:
            user_data['first_used'] = datetime.now().isoformat()
            
        await self.set_user_data(user_id, user_data)

    # ✅ ENHANCED MEMORY SYSTEM - CHANNEL WIDE MEMORY
    async def get_channel_memory(self, channel_id: str) -> List[Dict[str, str]]:
        """Get channel's conversation memory"""
        data = await self.read_data()
        return data.get('channel_memory', {}).get(channel_id, [])

    async def add_to_channel_memory(self, channel_id: str, username: str, role: str, content: str):
        """Add message to channel memory"""
        data = await self.read_data()
        
        if 'channel_memory' not in data:
            data['channel_memory'] = {}
            
        if channel_id not in data['channel_memory']:
            data['channel_memory'][channel_id] = []
        
        # Add new message with username
        data['channel_memory'][channel_id].append({
            'username': username,
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 messages per channel (increased limit)
        data['channel_memory'][channel_id] = data['channel_memory'][channel_id][-20:]
        
        await self.write_data(data)

    async def clear_channel_memory(self, channel_id: str):
        """Clear channel's conversation memory"""
        data = await self.read_data()
        if 'channel_memory' in data and channel_id in data['channel_memory']:
            data['channel_memory'][channel_id] = []
            await self.write_data(data)

    async def get_user_memory(self, user_id: str) -> List[Dict[str, str]]:
        """Get user's personal conversation memory"""
        user_data = await self.get_user_data(user_id)
        return user_data.get('conversation_memory', [])

    async def add_to_user_memory(self, user_id: str, role: str, content: str):
        """Add message to user's personal memory"""
        user_data = await self.get_user_data(user_id)
        
        if 'conversation_memory' not in user_data:
            user_data['conversation_memory'] = []
        
        user_data['conversation_memory'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 15 messages per user
        user_data['conversation_memory'] = user_data['conversation_memory'][-15:]
        
        await self.set_user_data(user_id, user_data)

    async def clear_user_memory(self, user_id: str):
        """Clear user's personal memory"""
        user_data = await self.get_user_data(user_id)
        user_data['conversation_memory'] = []
        await self.set_user_data(user_id, user_data)

    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global bot statistics"""
        data = await self.read_data()
        return data.get('global_stats', {
            'total_requests': 0,
            'unique_users': 0,
            'guild_count': 0,
            'file_analyses': 0,
            'projects_built': 0
        })

    async def update_global_stats(self, stats: Dict[str, Any]):
        """Update global bot statistics"""
        data = await self.read_data()
        data['global_stats'] = stats
        await self.write_data(data)

    # ✅ FILE ANALYSIS TRACKING
    async def log_file_analysis(self, user_id: str, filename: str, file_type: str, analysis_result: str):
        """Log file analysis for statistics"""
        user_data = await self.get_user_data(user_id)
        
        if 'file_analyses' not in user_data:
            user_data['file_analyses'] = []
            
        user_data['file_analyses'].append({
            'filename': filename,
            'file_type': file_type,
            'timestamp': datetime.now().isoformat(),
            'result_length': len(analysis_result)
        })
        
        user_data['file_analyses'] = user_data['file_analyses'][-50:]
        await self.set_user_data(user_id, user_data)

    # ✅ BUILD PROJECTS TRACKING
    async def log_build_project(self, user_id: str, project_type: str, language: str, success: bool):
        """Log project builds for statistics"""
        user_data = await self.get_user_data(user_id)
        
        if 'build_projects' not in user_data:
            user_data['build_projects'] = []
            
        user_data['build_projects'].append({
            'project_type': project_type,
            'language': language,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        
        await self.set_user_data(user_id, user_data)

    async def get_user_file_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user file analysis statistics"""
        user_data = await self.get_user_data(user_id)
        analyses = user_data.get('file_analyses', [])
        builds = user_data.get('build_projects', [])
        
        return {
            'total_files_analyzed': len(analyses),
            'total_projects_built': len(builds),
            'recent_files': analyses[-5:] if analyses else [],
            'successful_builds': len([b for b in builds if b.get('success', False)])
        }

# Database instance
db = JSONDatabase()
