
import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiofiles
from threading import Thread
from flask import Flask
import re

# Keep alive para manter o bot online
app = Flask('')

@app.route('/')
def home():
    return "Security Bot Online"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ID do owner do bot (CONFIGURE AQUI SEU ID)
OWNER_ID = 983196900910039090  # Substitua pelo seu ID real

# Configurações padrão para novos servidores
DEFAULT_CONFIG = {
    'auto_ban_bots': False,
    'auto_ban_new_accounts': False,
    'new_account_days': 7,
    'role_delete_punishment': 'remove_roles',
    'channel_delete_punishment': 'remove_roles',
    'logs_channel_id': None,
    'audit_log_delay': 2,
    'max_logs_history': 100,
    'auto_kick_mass_ping': False,
    'max_mentions': 10,
    'auto_delete_invite_links': False,
    'whitelist_users': [],
    'protection_enabled': True,
    'anti_spam_enabled': False,
    'spam_message_count': 5,
    'spam_time_window': 10,
    'auto_mute_duration': 10,
    'mass_ping_mute_duration': 10,
    'protect_admin_roles': True,
    'backup_channels': True,
    'backup_roles': True
}

COLORS = {
    'danger': 0xff0000,
    'warning': 0xff9900,
    'success': 0x00ff00,
    'info': 0x0099ff,
    'purple': 0x9932cc
}

# Configurações do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True
intents.moderation = True

bot = commands.Bot(command_prefix='!sec_', intents=intents, help_command=None)

# Arquivo para salvar dados de segurança
SECURITY_DATA_FILE = "security_data.json"

class SecurityBot:
    def __init__(self):
        self.guild_configs = {}  # Configurações por servidor
        self.restored_roles = {}  # Para armazenar cargos removidos
        self.security_logs = {}  # Logs por servidor
        self.user_warnings = {}  # Avisos por usuário
        self.spam_tracker = {}  # Rastreamento de spam
        self.backup_data = {}  # Backups de canais/cargos
    
    async def load_data(self):
        """Carrega dados de segurança salvos"""
        try:
            if os.path.exists(SECURITY_DATA_FILE):
                async with aiofiles.open(SECURITY_DATA_FILE, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    self.guild_configs = data.get('guild_configs', {})
                    self.restored_roles = data.get('restored_roles', {})
                    self.security_logs = data.get('security_logs', {})
                    self.user_warnings = data.get('user_warnings', {})
                    self.backup_data = data.get('backup_data', {})
        except Exception as e:
            print(f"❌ Erro ao carregar dados de segurança: {e}")
    
    async def save_data(self):
        """Salva dados de segurança"""
        try:
            data = {
                'guild_configs': self.guild_configs,
                'restored_roles': self.restored_roles,
                'security_logs': self.security_logs,
                'user_warnings': self.user_warnings,
                'backup_data': self.backup_data
            }
            async with aiofiles.open(SECURITY_DATA_FILE, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ Erro ao salvar dados de segurança: {e}")
    
    def get_guild_config(self, guild_id: int):
        """Obtém configuração do servidor"""
        guild_id_str = str(guild_id)
        if guild_id_str not in self.guild_configs:
            self.guild_configs[guild_id_str] = DEFAULT_CONFIG.copy()
        return self.guild_configs[guild_id_str]
    
    async def get_logs_channel(self, guild):
        """Encontra o canal de logs configurado"""
        config = self.get_guild_config(guild.id)
        if config['logs_channel_id']:
            return guild.get_channel(config['logs_channel_id'])
        return None
    
    async def log_security_action(self, guild, title: str, description: str, color: int, fields: List[Dict] = None):
        """Registra ação de segurança no canal de logs"""
        logs_channel = await self.get_logs_channel(guild)
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title=f"🔒 {title}",
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field['name'],
                    value=field['value'],
                    inline=field.get('inline', False)
                )
        
        embed.set_footer(text="Sistema de Segurança Automático")
        
        try:
            await logs_channel.send(embed=embed)
            
            # Salva no histórico
            guild_id_str = str(guild.id)
            if guild_id_str not in self.security_logs:
                self.security_logs[guild_id_str] = []
            
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'title': title,
                'description': description
            }
            self.security_logs[guild_id_str].append(log_entry)
            
            # Mantém apenas os últimos logs
            config = self.get_guild_config(guild.id)
            max_logs = config['max_logs_history']
            self.security_logs[guild_id_str] = self.security_logs[guild_id_str][-max_logs:]
            
            await self.save_data()
            
        except Exception as e:
            print(f"❌ Erro ao enviar log de segurança: {e}")

# Instância global do sistema de segurança
security_system = SecurityBot()

@bot.event
async def on_ready():
    """Evento executado quando o bot está pronto"""
    await security_system.load_data()
    print("🔒 Sistema de Segurança está ONLINE!")
    print("=" * 50)
    print(f"✅ Conectado em {len(bot.guilds)} servidores")
    print("✅ Proteções ativas por servidor:")
    print("  • Detecção de exclusão de canais/cargos")
    print("  • Banimento automático de bots")
    print("  • Anti-spam e proteção contra mass ping")
    print("  • Sistema de logs personalizável")
    print("  • Backup automático de canais/cargos")
    print("  • Sistema de avisos e punições")
    print("=" * 50)

@bot.event
async def on_guild_channel_delete(channel):
    """🔥 Detecta exclusão de canais"""
    try:
        guild = channel.guild
        config = security_system.get_guild_config(guild.id)
        
        if not config['protection_enabled']:
            return
        
        # Salva backup do canal
        if config['backup_channels']:
            guild_id_str = str(guild.id)
            if guild_id_str not in security_system.backup_data:
                security_system.backup_data[guild_id_str] = {'channels': [], 'roles': []}
            
            channel_backup = {
                'name': channel.name,
                'type': str(channel.type),
                'category': channel.category.name if channel.category else None,
                'position': channel.position,
                'topic': getattr(channel, 'topic', None),
                'deleted_at': datetime.utcnow().isoformat()
            }
            security_system.backup_data[guild_id_str]['channels'].append(channel_backup)
        
        await asyncio.sleep(config['audit_log_delay'])
        
        async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            if entry.target.id == channel.id:
                executor = entry.user
                
                if executor.id in config['whitelist_users']:
                    await security_system.log_security_action(
                        guild,
                        "Canal Deletado - Usuário Autorizado",
                        f"🟢 {executor.mention} deletou o canal #{channel.name}",
                        COLORS['success']
                    )
                    return
                
                # Aplica punição
                member = guild.get_member(executor.id)
                if member and config['channel_delete_punishment'] == 'remove_roles':
                    original_roles = [role for role in member.roles if role != guild.default_role]
                    if original_roles:
                        security_system.restored_roles[str(executor.id)] = {
                            'roles': [role.id for role in original_roles],
                            'removed_at': datetime.utcnow().isoformat(),
                            'reason': f"Deletou canal #{channel.name}",
                            'guild_id': guild.id
                        }
                        await member.remove_roles(*original_roles, reason="🔒 Segurança: Deletou canal")
                
                await security_system.log_security_action(
                    guild,
                    "🚨 CANAL DELETADO",
                    f"⚠️ {executor.mention} deletou o canal #{channel.name}",
                    COLORS['danger'],
                    [
                        {'name': '📺 Canal', 'value': f"#{channel.name}", 'inline': True},
                        {'name': '👤 Responsável', 'value': executor.mention, 'inline': True},
                        {'name': '⚡ Ação', 'value': config['channel_delete_punishment'], 'inline': True}
                    ]
                )
                break
    except Exception as e:
        print(f"❌ Erro no detector de exclusão de canais: {e}")

@bot.event
async def on_guild_role_delete(role):
    """🎭 Detecta exclusão de cargos"""
    try:
        guild = role.guild
        config = security_system.get_guild_config(guild.id)
        
        if not config['protection_enabled']:
            return
        
        # Salva backup do cargo
        if config['backup_roles']:
            guild_id_str = str(guild.id)
            if guild_id_str not in security_system.backup_data:
                security_system.backup_data[guild_id_str] = {'channels': [], 'roles': []}
            
            role_backup = {
                'name': role.name,
                'color': str(role.color),
                'permissions': role.permissions.value,
                'position': role.position,
                'deleted_at': datetime.utcnow().isoformat()
            }
            security_system.backup_data[guild_id_str]['roles'].append(role_backup)
        
        await asyncio.sleep(config['audit_log_delay'])
        
        async for entry in guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            if entry.target.id == role.id:
                executor = entry.user
                
                if executor.id in config['whitelist_users']:
                    await security_system.log_security_action(
                        guild,
                        "Cargo Deletado - Usuário Autorizado",
                        f"🟢 {executor.mention} deletou o cargo @{role.name}",
                        COLORS['success']
                    )
                    return
                
                # Aplica punição
                member = guild.get_member(executor.id)
                punishment = config['role_delete_punishment']
                
                if member:
                    if punishment == 'ban':
                        await member.ban(reason=f"🔒 Segurança: Deletou cargo @{role.name}")
                    else:  # remove_roles
                        original_roles = [r for r in member.roles if r != guild.default_role]
                        if original_roles:
                            security_system.restored_roles[str(executor.id)] = {
                                'roles': [r.id for r in original_roles],
                                'removed_at': datetime.utcnow().isoformat(),
                                'reason': f"Deletou cargo @{role.name}",
                                'guild_id': guild.id
                            }
                            await member.remove_roles(*original_roles, reason="🔒 Segurança: Deletou cargo")
                
                await security_system.log_security_action(
                    guild,
                    "🚨 CARGO DELETADO",
                    f"⚠️ {executor.mention} deletou o cargo @{role.name}",
                    COLORS['danger'],
                    [
                        {'name': '🎭 Cargo', 'value': f"@{role.name}", 'inline': True},
                        {'name': '👤 Responsável', 'value': executor.mention, 'inline': True},
                        {'name': '⚡ Ação', 'value': punishment, 'inline': True}
                    ]
                )
                break
    except Exception as e:
        print(f"❌ Erro no detector de exclusão de cargos: {e}")

@bot.event
async def on_member_join(member):
    """🤖 Eventos quando usuário entra"""
    guild = member.guild
    config = security_system.get_guild_config(guild.id)
    
    if not config['protection_enabled']:
        return
    
    # Ban automático de bots
    if member.bot and config['auto_ban_bots']:
        try:
            await member.ban(reason="🔒 Segurança: Bot banido automaticamente")
            await security_system.log_security_action(
                guild,
                "🤖 Bot Banido",
                f"Bot {member.mention} foi banido automaticamente",
                COLORS['warning']
            )
        except Exception as e:
            print(f"❌ Erro ao banir bot: {e}")
    
    # Ban de contas muito novas
    if not member.bot and config['auto_ban_new_accounts']:
        account_age = (datetime.utcnow() - member.created_at).days
        if account_age < config['new_account_days']:
            try:
                await member.ban(reason=f"🔒 Segurança: Conta muito nova ({account_age} dias)")
                await security_system.log_security_action(
                    guild,
                    "🆕 Conta Nova Banida",
                    f"Usuário {member.mention} banido (conta com {account_age} dias)",
                    COLORS['warning']
                )
            except Exception as e:
                print(f"❌ Erro ao banir conta nova: {e}")

@bot.event
async def on_message(message):
    """📨 Monitora mensagens para anti-spam e outras proteções"""
    if message.author.bot:
        return
    
    guild = message.guild
    if not guild:
        return
    
    config = security_system.get_guild_config(guild.id)
    
    if not config['protection_enabled']:
        await bot.process_commands(message)
        return
    
    # Anti-spam
    if config['anti_spam_enabled']:
        user_id = str(message.author.id)
        guild_id = str(guild.id)
        
        if guild_id not in security_system.spam_tracker:
            security_system.spam_tracker[guild_id] = {}
        
        if user_id not in security_system.spam_tracker[guild_id]:
            security_system.spam_tracker[guild_id][user_id] = []
        
        now = datetime.utcnow()
        user_messages = security_system.spam_tracker[guild_id][user_id]
        
        # Remove mensagens antigas
        user_messages[:] = [msg_time for msg_time in user_messages 
                           if (now - msg_time).seconds < config['spam_time_window']]
        
        user_messages.append(now)
        
        if len(user_messages) >= config['spam_message_count']:
            try:
                await message.author.timeout(
                    timedelta(seconds=config['auto_mute_duration']),
                    reason="🔒 Anti-spam: Muitas mensagens em pouco tempo"
                )
                await security_system.log_security_action(
                    guild,
                    "🚫 Usuário Mutado por Spam",
                    f"{message.author.mention} foi mutado por {config['auto_mute_duration']}s",
                    COLORS['warning']
                )
                user_messages.clear()
            except Exception as e:
                print(f"❌ Erro ao mutar por spam: {e}")
    
    # Anti mass ping
    if config['auto_kick_mass_ping']:
        mention_count = len(message.mentions)
        if mention_count >= config['max_mentions']:
            try:
                await message.delete()
                await message.author.timeout(
                    timedelta(seconds=config['mass_ping_mute_duration']),
                    reason=f"🔒 Mass ping: {mention_count} menções"
                )
                await security_system.log_security_action(
                    guild,
                    "🚫 Usuário Silenciado por Mass Ping",
                    f"{message.author.mention} silenciado por {config['mass_ping_mute_duration']}s ({mention_count} menções)",
                    COLORS['warning']
                )
            except Exception as e:
                print(f"❌ Erro ao silenciar por mass ping: {e}")
    
    # Anti convite
    if config['auto_delete_invite_links']:
        invite_pattern = r'discord\.gg/\w+'
        if re.search(invite_pattern, message.content):
            try:
                await message.delete()
                await security_system.log_security_action(
                    guild,
                    "🔗 Link de Convite Deletado",
                    f"Mensagem de {message.author.mention} continha convite",
                    COLORS['info']
                )
            except Exception as e:
                print(f"❌ Erro ao deletar convite: {e}")
    
    await bot.process_commands(message)

# === COMANDOS DO BOT (apenas owner) ===

def is_owner():
    def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

@bot.command(name='config', aliases=['c'])
@is_owner()
async def config_security(ctx, setting: str = None, *, value: str = None):
    """Configura o sistema de segurança"""
    config = security_system.get_guild_config(ctx.guild.id)
    
    if not setting:
        embed = discord.Embed(title="🔧 Configurações de Segurança", color=COLORS['info'])
        
        # Mostra configurações atuais
        embed.add_field(name="🤖 auto_ban_bots", value="✅" if config['auto_ban_bots'] else "❌", inline=True)
        embed.add_field(name="🆕 auto_ban_new_accounts", value="✅" if config['auto_ban_new_accounts'] else "❌", inline=True)
        embed.add_field(name="📅 new_account_days", value=config['new_account_days'], inline=True)
        embed.add_field(name="🛡️ protection_enabled", value="✅" if config['protection_enabled'] else "❌", inline=True)
        embed.add_field(name="📢 anti_spam_enabled", value="✅" if config['anti_spam_enabled'] else "❌", inline=True)
        embed.add_field(name="🚫 auto_kick_mass_ping", value="✅" if config['auto_kick_mass_ping'] else "❌", inline=True)
        embed.add_field(name="🔗 auto_delete_invite_links", value="✅" if config['auto_delete_invite_links'] else "❌", inline=True)
        embed.add_field(name="💾 backup_channels", value="✅" if config['backup_channels'] else "❌", inline=True)
        embed.add_field(name="📺 logs_channel_id", value=f"<#{config['logs_channel_id']}>" if config['logs_channel_id'] else "Não definido", inline=True)
        
        embed.add_field(
            name="💡 Exemplos de uso:",
            value="`!sec_c auto_ban_bots true`\n`!sec_c anti_spam_enabled true`\n`!sec_c auto_mute_duration 10`\n`!sec_c logs_channel_id #logs`",
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    # Aplica configuração
    if setting == 'auto_ban_bots':
        config['auto_ban_bots'] = value.lower() == 'true'
    elif setting == 'auto_ban_new_accounts':
        config['auto_ban_new_accounts'] = value.lower() == 'true'
    elif setting == 'new_account_days':
        config['new_account_days'] = int(value)
    elif setting == 'protection_enabled':
        config['protection_enabled'] = value.lower() == 'true'
    elif setting == 'anti_spam_enabled':
        config['anti_spam_enabled'] = value.lower() == 'true'
    elif setting == 'auto_kick_mass_ping':
        config['auto_kick_mass_ping'] = value.lower() == 'true'
    elif setting == 'auto_delete_invite_links':
        config['auto_delete_invite_links'] = value.lower() == 'true'
    elif setting == 'backup_channels':
        config['backup_channels'] = value.lower() == 'true'
    elif setting == 'backup_roles':
        config['backup_roles'] = value.lower() == 'true'
    elif setting == 'max_mentions':
        config['max_mentions'] = int(value)
    elif setting == 'spam_message_count':
        config['spam_message_count'] = int(value)
    elif setting == 'auto_mute_duration':
        config['auto_mute_duration'] = int(value)
    elif setting == 'mass_ping_mute_duration':
        config['mass_ping_mute_duration'] = int(value)
    elif setting == 'logs_channel_id':
        if value.startswith('#'):
            channel = discord.utils.get(ctx.guild.channels, name=value[1:])
        else:
            channel = ctx.guild.get_channel(int(value.strip('<#>')))
        config['logs_channel_id'] = channel.id if channel else None
    else:
        await ctx.send("❌ Configuração inválida!")
        return
    
    await security_system.save_data()
    
    embed = discord.Embed(
        title="✅ Configuração Atualizada",
        description=f"**{setting}** = **{value}**",
        color=COLORS['success']
    )
    await ctx.send(embed=embed)

@bot.command(name='whitelist', aliases=['w'])
@is_owner()
async def manage_whitelist(ctx, action: str = None, user: discord.Member = None):
    """Gerencia whitelist"""
    config = security_system.get_guild_config(ctx.guild.id)
    
    if not action:
        embed = discord.Embed(title="🔐 Whitelist de Segurança", color=COLORS['info'])
        
        if config['whitelist_users']:
            users = []
            for user_id in config['whitelist_users']:
                user_obj = bot.get_user(user_id)
                users.append(user_obj.mention if user_obj else f"ID: {user_id}")
            embed.add_field(name="👥 Usuários", value='\n'.join(users), inline=False)
        else:
            embed.add_field(name="👥 Usuários", value="Nenhum usuário na whitelist", inline=False)
        
        embed.add_field(name="💡 Uso", value="`!sec_w add @user`\n`!sec_w remove @user`", inline=False)
        await ctx.send(embed=embed)
        return
    
    if not user:
        await ctx.send("❌ Mencione um usuário!")
        return
    
    if action == 'add':
        if user.id not in config['whitelist_users']:
            config['whitelist_users'].append(user.id)
            await security_system.save_data()
            await ctx.send(f"✅ {user.mention} adicionado à whitelist!")
        else:
            await ctx.send("❌ Usuário já está na whitelist!")
    
    elif action == 'remove':
        if user.id in config['whitelist_users']:
            config['whitelist_users'].remove(user.id)
            await security_system.save_data()
            await ctx.send(f"✅ {user.mention} removido da whitelist!")
        else:
            await ctx.send("❌ Usuário não está na whitelist!")

@bot.command(name='restore', aliases=['r'])
@is_owner()
async def restore_roles(ctx, user: discord.Member):
    """Restaura cargos de um usuário"""
    user_id = str(user.id)
    
    if user_id not in security_system.restored_roles:
        await ctx.send("❌ Usuário não tem cargos para restaurar!")
        return
    
    try:
        user_data = security_system.restored_roles[user_id]
        roles_to_restore = []
        
        for role_id in user_data['roles']:
            role = ctx.guild.get_role(role_id)
            if role:
                roles_to_restore.append(role)
        
        if roles_to_restore:
            await user.add_roles(*roles_to_restore, reason=f"Restauração por {ctx.author}")
            del security_system.restored_roles[user_id]
            await security_system.save_data()
            
            await ctx.send(f"✅ Cargos de {user.mention} restaurados!")
        else:
            await ctx.send("❌ Nenhum cargo válido para restaurar!")
    
    except Exception as e:
        await ctx.send(f"❌ Erro: {e}")

@bot.command(name='status', aliases=['s'])
@is_owner()
async def security_status(ctx):
    """Status do sistema"""
    config = security_system.get_guild_config(ctx.guild.id)
    
    embed = discord.Embed(title="🔒 Status do Sistema", color=COLORS['info'])
    
    # Status geral
    guild_id_str = str(ctx.guild.id)
    logs_count = len(security_system.security_logs.get(guild_id_str, []))
    pending_restores = len([r for r in security_system.restored_roles.values() 
                           if r['guild_id'] == ctx.guild.id])
    
    embed.add_field(name="🟢 Sistema", value="Operacional", inline=True)
    embed.add_field(name="📊 Logs", value=logs_count, inline=True)
    embed.add_field(name="🔄 Restaurações", value=pending_restores, inline=True)
    
    # Proteções ativas
    protections = []
    if config['protection_enabled']:
        protections.append("🛡️ Proteção geral ativa")
        if config['auto_ban_bots']:
            protections.append("🤖 Anti-bot")
        if config['anti_spam_enabled']:
            protections.append("📢 Anti-spam")
        if config['auto_kick_mass_ping']:
            protections.append("🚫 Anti mass-ping")
    else:
        protections.append("❌ Proteções desativadas")
    
    embed.add_field(name="🛡️ Proteções", value='\n'.join(protections), inline=False)
    
    # Canal de logs
    logs_channel = "Não configurado"
    if config['logs_channel_id']:
        logs_channel = f"<#{config['logs_channel_id']}>"
    embed.add_field(name="📺 Canal de Logs", value=logs_channel, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='logs', aliases=['l'])
@is_owner()
async def view_logs(ctx, limit: int = 10):
    """Visualiza logs recentes"""
    guild_id_str = str(ctx.guild.id)
    logs = security_system.security_logs.get(guild_id_str, [])
    
    if not logs:
        await ctx.send("❌ Nenhum log encontrado!")
        return
    
    embed = discord.Embed(title="📋 Logs Recentes", color=COLORS['info'])
    
    recent_logs = logs[-limit:]
    for log in recent_logs:
        timestamp = datetime.fromisoformat(log['timestamp']).strftime("%d/%m %H:%M")
        embed.add_field(
            name=f"🕐 {timestamp}",
            value=f"**{log['title']}**\n{log['description'][:100]}...",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='backup', aliases=['b'])
@is_owner()
async def view_backups(ctx):
    """Visualiza backups de canais/cargos deletados"""
    guild_id_str = str(ctx.guild.id)
    backups = security_system.backup_data.get(guild_id_str, {'channels': [], 'roles': []})
    
    embed = discord.Embed(title="💾 Backups Disponíveis", color=COLORS['info'])
    
    # Canais deletados
    if backups['channels']:
        channels_text = []
        for channel in backups['channels'][-5:]:  # Últimos 5
            deleted_date = datetime.fromisoformat(channel['deleted_at']).strftime("%d/%m")
            channels_text.append(f"#{channel['name']} ({deleted_date})")
        embed.add_field(name="📺 Canais Deletados", value='\n'.join(channels_text), inline=True)
    
    # Cargos deletados
    if backups['roles']:
        roles_text = []
        for role in backups['roles'][-5:]:  # Últimos 5
            deleted_date = datetime.fromisoformat(role['deleted_at']).strftime("%d/%m")
            roles_text.append(f"@{role['name']} ({deleted_date})")
        embed.add_field(name="🎭 Cargos Deletados", value='\n'.join(roles_text), inline=True)
    
    if not backups['channels'] and not backups['roles']:
        embed.add_field(name="💾 Status", value="Nenhum backup disponível", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='warn', aliases=['av'])
@is_owner()
async def warn_user(ctx, user: discord.Member, *, reason: str = "Sem motivo especificado"):
    """Aplica aviso a um usuário"""
    user_id = str(user.id)
    guild_id = str(ctx.guild.id)
    
    if guild_id not in security_system.user_warnings:
        security_system.user_warnings[guild_id] = {}
    
    if user_id not in security_system.user_warnings[guild_id]:
        security_system.user_warnings[guild_id][user_id] = []
    
    warning = {
        'reason': reason,
        'moderator': ctx.author.id,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    security_system.user_warnings[guild_id][user_id].append(warning)
    await security_system.save_data()
    
    warnings_count = len(security_system.user_warnings[guild_id][user_id])
    
    embed = discord.Embed(
        title="⚠️ Aviso Aplicado",
        description=f"{user.mention} recebeu um aviso",
        color=COLORS['warning']
    )
    embed.add_field(name="📝 Motivo", value=reason, inline=False)
    embed.add_field(name="📊 Total de Avisos", value=warnings_count, inline=True)
    embed.add_field(name="👮 Moderador", value=ctx.author.mention, inline=True)
    
    await ctx.send(embed=embed)
    
    await security_system.log_security_action(
        ctx.guild,
        "⚠️ Aviso Aplicado",
        f"{user.mention} recebeu aviso de {ctx.author.mention}",
        COLORS['warning'],
        [
            {'name': '📝 Motivo', 'value': reason, 'inline': False},
            {'name': '📊 Total', 'value': warnings_count, 'inline': True}
        ]
    )

@bot.command(name='warnings', aliases=['avisos'])
@is_owner()
async def view_warnings(ctx, user: discord.Member = None):
    """Visualiza avisos de um usuário"""
    if not user:
        user = ctx.author
    
    user_id = str(user.id)
    guild_id = str(ctx.guild.id)
    
    warnings = security_system.user_warnings.get(guild_id, {}).get(user_id, [])
    
    if not warnings:
        await ctx.send(f"✅ {user.mention} não possui avisos!")
        return
    
    embed = discord.Embed(
        title=f"⚠️ Avisos de {user.display_name}",
        color=COLORS['warning']
    )
    
    for i, warning in enumerate(warnings[-10:], 1):  # Últimos 10
        timestamp = datetime.fromisoformat(warning['timestamp']).strftime("%d/%m %H:%M")
        moderator = bot.get_user(warning['moderator'])
        mod_name = moderator.mention if moderator else "Desconhecido"
        
        embed.add_field(
            name=f"Aviso #{i}",
            value=f"**Motivo:** {warning['reason']}\n**Moderador:** {mod_name}\n**Data:** {timestamp}",
            inline=False
        )
    
    embed.add_field(name="📊 Total", value=len(warnings), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='clear_warnings', aliases=['limpar_avisos'])
@is_owner()
async def clear_warnings(ctx, user: discord.Member):
    """Limpa avisos de um usuário"""
    user_id = str(user.id)
    guild_id = str(ctx.guild.id)
    
    if guild_id in security_system.user_warnings and user_id in security_system.user_warnings[guild_id]:
        warnings_count = len(security_system.user_warnings[guild_id][user_id])
        del security_system.user_warnings[guild_id][user_id]
        await security_system.save_data()
        
        await ctx.send(f"✅ {warnings_count} avisos de {user.mention} foram limpos!")
    else:
        await ctx.send(f"❌ {user.mention} não possui avisos para limpar!")

@bot.command(name='mute', aliases=['m'])
@is_owner()
async def mute_user(ctx, user: discord.Member, duration: int = 300, *, reason: str = "Sem motivo"):
    """Muta um usuário temporariamente"""
    try:
        await user.timeout(
            timedelta(seconds=duration),
            reason=f"🔒 Mutado por {ctx.author}: {reason}"
        )
        
        embed = discord.Embed(
            title="🔇 Usuário Mutado",
            description=f"{user.mention} foi mutado por {duration} segundos",
            color=COLORS['warning']
        )
        embed.add_field(name="📝 Motivo", value=reason, inline=False)
        embed.add_field(name="⏱️ Duração", value=f"{duration} segundos", inline=True)
        embed.add_field(name="👮 Moderador", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
        await security_system.log_security_action(
            ctx.guild,
            "🔇 Usuário Mutado",
            f"{user.mention} mutado por {ctx.author.mention}",
            COLORS['warning'],
            [
                {'name': '📝 Motivo', 'value': reason, 'inline': False},
                {'name': '⏱️ Duração', 'value': f"{duration}s", 'inline': True}
            ]
        )
        
    except Exception as e:
        await ctx.send(f"❌ Erro ao mutar usuário: {e}")

@bot.command(name='unmute', aliases=['desmutar'])
@is_owner()
async def unmute_user(ctx, user: discord.Member):
    """Desmuta um usuário"""
    try:
        await user.timeout(None, reason=f"Desmutado por {ctx.author}")
        await ctx.send(f"✅ {user.mention} foi desmutado!")
        
        await security_system.log_security_action(
            ctx.guild,
            "🔊 Usuário Desmutado",
            f"{user.mention} desmutado por {ctx.author.mention}",
            COLORS['success']
        )
        
    except Exception as e:
        await ctx.send(f"❌ Erro ao desmutar usuário: {e}")

@bot.command(name='help', aliases=['h', 'ajuda'])
async def security_help(ctx):
    """Central de ajuda"""
    embed = discord.Embed(
        title="🔒 Sistema de Segurança - Comandos",
        description="**Sistema completo de proteção para Discord**",
        color=COLORS['info']
    )
    
    commands_list = [
        "`!sec_c` - Configurações",
        "`!sec_w` - Whitelist", 
        "`!sec_r` - Restaurar cargos",
        "`!sec_s` - Status do sistema",
        "`!sec_l` - Ver logs",
        "`!sec_b` - Ver backups",
        "`!sec_av` - Aplicar aviso",
        "`!sec_avisos` - Ver avisos",
        "`!sec_m` - Mutar usuário",
        "`!sec_desmutar` - Desmutar",
        "`!sec_h` - Esta ajuda"
    ]
    
    embed.add_field(name="🎮 Comandos", value='\n'.join(commands_list), inline=False)
    
    protections = [
        "🔥 Proteção contra exclusão de canais/cargos (sempre ativo)",
        "🤖 Banimento automático de bots (opcional)",
        "🆕 Proteção contra contas novas (opcional)",
        "📢 Sistema anti-spam - silencia por 10s (opcional)",
        "🚫 Anti mass-ping - silencia por 10s (opcional)",
        "🔗 Bloqueio de convites automático (opcional)",
        "💾 Sistema de backup automático (opcional)",
        "⚠️ Sistema de avisos e punições",
        "🔇 Sistema de mute temporário",
        "📋 Logs detalhados por servidor"
    ]
    
    embed.add_field(name="🛡️ Proteções Disponíveis", value='\n'.join(protections), inline=False)
    
    embed.add_field(
        name="⚠️ Importante",
        value="• Apenas o owner do bot pode usar comandos\n• Configurações são por servidor\n• Configure canal de logs primeiro",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="🚫 Acesso Negado",
            description="Apenas o owner do bot pode usar este comando!",
            color=COLORS['danger']
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        print(f"❌ Erro no comando: {error}")

# Inicialização
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    if TOKEN:
        print("🚀 Iniciando Sistema de Segurança Avançado...")
        print("⚙️ Configurações padrão:")
        print("  • Proteção de canais/cargos: SEMPRE ATIVO")
        print("  • Anti-spam: OPCIONAL (10s de silenciamento)")
        print("  • Anti mass-ping: OPCIONAL (10s de silenciamento)")
        print("  • Outras proteções: CONFIGURÁVEIS por servidor")
        keep_alive()
        bot.run(TOKEN)
    else:
        print("❌ Token não encontrado! Configure DISCORD_BOT_TOKEN nas Secrets")
