
import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiofiles
from dotenv import load_dotenv
from keep_alive import keep_alive


# Importa configurações personalizáveis
try:
    from security_config import WHITELIST_IDS, DEFAULT_CONFIG, MESSAGES, COLORS, MONITORED_EVENTS
    print("✅ Configurações personalizadas carregadas!")
except ImportError:
    print("⚠️ Usando configurações padrão...")
    # Configurações padrão caso o arquivo não exista
    WHITELIST_IDS = [983196900910039090]
    DEFAULT_CONFIG = {
        'auto_ban_bots': True,
        'role_delete_punishment': 'remove_roles',
        'logs_channel_name': 'logs',
        'audit_log_delay': 2,
        'max_logs_history': 100
    }
    MESSAGES = {
        'channel_deleted': "🚨 AÇÃO SUSPEITA DETECTADA - Canal Deletado",
        'role_deleted': "🚨 AÇÃO SUSPEITA DETECTADA - Cargo Deletado",
        'bot_banned': "🤖 Bot Banido Automaticamente"
    }
    COLORS = {
        'danger': 0xff0000,
        'warning': 0xff9900,
        'success': 0x00ff00,
        'info': 0x0099ff
    }

# Configurações do bot de segurança
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!sec_', intents=intents, help_command=None)

# Arquivo para salvar dados de segurança
SECURITY_DATA_FILE = "security_data.json"

class SecurityBot:
    def __init__(self):
        self.restored_roles = {}  # Para armazenar cargos removidos
        self.security_logs = []
        self.config = {
            'auto_ban_bots': True,
            'role_delete_punishment': 'ban',  # 'remove_roles' ou 'ban'
            'logs_channel_name': 'logs'
        }
    
    async def load_data(self):
        """Carrega dados de segurança salvos"""
        try:
            if os.path.exists(SECURITY_DATA_FILE):
                async with aiofiles.open(SECURITY_DATA_FILE, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    self.restored_roles = data.get('restored_roles', {})
                    self.security_logs = data.get('security_logs', [])
                    self.config.update(data.get('config', {}))
        except Exception as e:
            print(f"❌ Erro ao carregar dados de segurança: {e}")
    
    async def save_data(self):
        """Salva dados de segurança"""
        try:
            data = {
                'restored_roles': self.restored_roles,
                'security_logs': self.security_logs[-100:],  # Mantém apenas os últimos 100 logs
                'config': self.config
            }
            async with aiofiles.open(SECURITY_DATA_FILE, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ Erro ao salvar dados de segurança: {e}")
    
    async def get_logs_channel(self, guild):
        """Encontra ou cria o canal de logs"""
        logs_channel = discord.utils.get(guild.channels, name=self.config['logs_channel_name'])
        
        if not logs_channel:
            # Cria o canal de logs se não existir
            try:
                logs_channel = await guild.create_text_channel(
                    self.config['logs_channel_name'],
                    topic="🔒 Canal de logs de segurança automáticos",
                    reason="Canal de segurança criado automaticamente"
                )
                print(f"✅ Canal de logs criado: #{logs_channel.name}")
            except Exception as e:
                print(f"❌ Erro ao criar canal de logs: {e}")
                return None
        
        return logs_channel
    
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
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'title': title,
                'description': description,
                'guild_id': guild.id
            }
            self.security_logs.append(log_entry)
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
    print("✅ Proteções ativas:")
    print("  • Detecção de exclusão de canais")
    print("  • Detecção de exclusão de cargos")
    print("  • Banimento automático de bots")
    print("  • Sistema de logs automático")
    print("=" * 50)

@bot.event
async def on_guild_channel_delete(channel):
    """🔥 Detecta exclusão de canais e pune o responsável"""
    try:
        guild = channel.guild
        
        # Aguarda um pouco para o audit log ser atualizado
        await asyncio.sleep(2)
        
        # Busca no audit log quem deletou o canal
        async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            if entry.target.id == channel.id:
                executor = entry.user
                
                # Verifica se o usuário está na whitelist
                if executor.id in WHITELIST_IDS:
                    await security_system.log_security_action(
                        guild,
                        "Canal Deletado - Usuário Autorizado",
                        f"🟢 {executor.mention} deletou o canal, mas está na whitelist.",
                        0x00ff00,
                        [
                            {'name': '📺 Canal Deletado', 'value': f"#{channel.name}", 'inline': True},
                            {'name': '👤 Responsável', 'value': executor.mention, 'inline': True},
                            {'name': '✅ Status', 'value': "Usuário autorizado", 'inline': True}
                        ]
                    )
                    return
                
                # Se chegou aqui, é uma ação suspeita
                member = guild.get_member(executor.id)
                if not member:
                    return
                
                # Salva os cargos antes de remover
                original_roles = [role for role in member.roles if role != guild.default_role]
                role_names = [role.name for role in original_roles]
                
                # Salva para possível restauração
                security_system.restored_roles[str(executor.id)] = {
                    'roles': [role.id for role in original_roles],
                    'removed_at': datetime.utcnow().isoformat(),
                    'reason': f"Deletou canal #{channel.name}",
                    'guild_id': guild.id
                }
                
                # Remove todos os cargos
                try:
                    await member.remove_roles(*original_roles, reason="🔒 Segurança: Deletou canal sem autorização")
                    
                    await security_system.log_security_action(
                        guild,
                        "🚨 AÇÃO SUSPEITA DETECTADA - Canal Deletado",
                        f"⚠️ **{executor.mention}** deletou o canal **#{channel.name}** e teve todos os cargos removidos!",
                        0xff0000,
                        [
                            {'name': '📺 Canal Deletado', 'value': f"#{channel.name}", 'inline': True},
                            {'name': '👤 Responsável', 'value': f"{executor.mention}\n({executor.id})", 'inline': True},
                            {'name': '⚡ Ação Tomada', 'value': "Todos os cargos removidos", 'inline': True},
                            {'name': '🎭 Cargos Removidos', 'value': ', '.join(role_names) if role_names else "Nenhum cargo", 'inline': False},
                            {'name': '🔄 Restauração', 'value': "Use `!sec_restore` para reverter", 'inline': True}
                        ]
                    )
                    
                    print(f"🔒 SEGURANÇA: Cargos removidos de {executor} por deletar canal #{channel.name}")
                    
                except Exception as e:
                    await security_system.log_security_action(
                        guild,
                        "❌ Erro na Remoção de Cargos",
                        f"Não foi possível remover cargos de {executor.mention}",
                        0xff9900,
                        [
                            {'name': '📺 Canal Deletado', 'value': f"#{channel.name}", 'inline': True},
                            {'name': '👤 Responsável', 'value': executor.mention, 'inline': True},
                            {'name': '❌ Erro', 'value': str(e)[:1000], 'inline': False}
                        ]
                    )
                break
    
    except Exception as e:
        print(f"❌ Erro no detector de exclusão de canais: {e}")

@bot.event
async def on_guild_role_delete(role):
    """🎭 Detecta exclusão de cargos e pune o responsável"""
    try:
        guild = role.guild
        
        # Aguarda um pouco para o audit log ser atualizado
        await asyncio.sleep(2)
        
        # Busca no audit log quem deletou o cargo
        async for entry in guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            if entry.target.id == role.id:
                executor = entry.user
                
                # Verifica se o usuário está na whitelist
                if executor.id in WHITELIST_IDS:
                    await security_system.log_security_action(
                        guild,
                        "Cargo Deletado - Usuário Autorizado",
                        f"🟢 {executor.mention} deletou o cargo, mas está na whitelist.",
                        0x00ff00,
                        [
                            {'name': '🎭 Cargo Deletado', 'value': f"@{role.name}", 'inline': True},
                            {'name': '👤 Responsável', 'value': executor.mention, 'inline': True},
                            {'name': '✅ Status', 'value': "Usuário autorizado", 'inline': True}
                        ]
                    )
                    return
                
                # Se chegou aqui, é uma ação suspeita
                member = guild.get_member(executor.id)
                if not member:
                    return
                
                # Salva os cargos antes de aplicar punição
                original_roles = [r for r in member.roles if r != guild.default_role]
                role_names = [r.name for r in original_roles]
                
                # Salva para possível restauração
                security_system.restored_roles[str(executor.id)] = {
                    'roles': [r.id for r in original_roles],
                    'removed_at': datetime.utcnow().isoformat(),
                    'reason': f"Deletou cargo @{role.name}",
                    'guild_id': guild.id
                }
                
                # Aplica punição baseada na configuração
                if security_system.config['role_delete_punishment'] == 'ban':
                    try:
                        await member.ban(reason=f"🔒 Segurança: Deletou cargo @{role.name} sem autorização")
                        
                        await security_system.log_security_action(
                            guild,
                            "🚨 AÇÃO SUSPEITA DETECTADA - Cargo Deletado",
                            f"⚠️ **{executor.mention}** deletou o cargo **@{role.name}** e foi BANIDO!",
                            0xff0000,
                            [
                                {'name': '🎭 Cargo Deletado', 'value': f"@{role.name}", 'inline': True},
                                {'name': '👤 Responsável', 'value': f"{executor.mention}\n({executor.id})", 'inline': True},
                                {'name': '⚡ Ação Tomada', 'value': "**BANIDO**", 'inline': True},
                                {'name': '🎭 Cargos que Tinha', 'value': ', '.join(role_names) if role_names else "Nenhum cargo", 'inline': False}
                            ]
                        )
                        
                        print(f"🔒 SEGURANÇA: {executor} foi BANIDO por deletar cargo @{role.name}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao banir usuário: {e}")
                
                else:  # remove_roles (padrão)
                    try:
                        await member.remove_roles(*original_roles, reason=f"🔒 Segurança: Deletou cargo @{role.name} sem autorização")
                        
                        await security_system.log_security_action(
                            guild,
                            "🚨 AÇÃO SUSPEITA DETECTADA - Cargo Deletado",
                            f"⚠️ **{executor.mention}** deletou o cargo **@{role.name}** e teve todos os cargos removidos!",
                            0xff0000,
                            [
                                {'name': '🎭 Cargo Deletado', 'value': f"@{role.name}", 'inline': True},
                                {'name': '👤 Responsável', 'value': f"{executor.mention}\n({executor.id})", 'inline': True},
                                {'name': '⚡ Ação Tomada', 'value': "Todos os cargos removidos", 'inline': True},
                                {'name': '🎭 Cargos Removidos', 'value': ', '.join(role_names) if role_names else "Nenhum cargo", 'inline': False},
                                {'name': '🔄 Restauração', 'value': "Use `!sec_restore` para reverter", 'inline': True}
                            ]
                        )
                        
                        print(f"🔒 SEGURANÇA: Cargos removidos de {executor} por deletar cargo @{role.name}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao remover cargos: {e}")
                break
    
    except Exception as e:
        print(f"❌ Erro no detector de exclusão de cargos: {e}")

@bot.event
async def on_member_join(member):
    """🤖 Bane bots automaticamente ao entrarem (se configurado)"""
    if not member.bot:
        return
    
    if not security_system.config['auto_ban_bots']:
        return
    
    try:
        guild = member.guild
        
        # Bane o bot automaticamente
        await member.ban(reason="🔒 Segurança: Bot banido automaticamente")
        
        await security_system.log_security_action(
            guild,
            "🤖 Bot Banido Automaticamente",
            f"🚫 **{member.mention}** foi banido automaticamente por ser um bot.",
            0xff9900,
            [
                {'name': '🤖 Bot Banido', 'value': f"{member.mention}\n({member.id})", 'inline': True},
                {'name': '⚡ Ação', 'value': "Banimento automático", 'inline': True},
                {'name': '📅 Data de Criação', 'value': member.created_at.strftime("%d/%m/%Y"), 'inline': True}
            ]
        )
        
        print(f"🔒 SEGURANÇA: Bot {member} banido automaticamente")
        
    except Exception as e:
        print(f"❌ Erro ao banir bot automaticamente: {e}")

# Comandos de administração
@bot.command(name='config')
@commands.has_permissions(administrator=True)
async def config_security(ctx, setting: str = None, value: str = None):
    """Configura o sistema de segurança"""
    if not setting:
        embed = discord.Embed(
            title="🔧 Configurações de Segurança",
            color=0x0099ff
        )
        
        embed.add_field(
            name="auto_ban_bots",
            value="✅ Ativo" if security_system.config['auto_ban_bots'] else "❌ Inativo",
            inline=True
        )
        embed.add_field(
            name="role_delete_punishment",
            value=security_system.config['role_delete_punishment'],
            inline=True
        )
        embed.add_field(
            name="logs_channel_name",
            value=security_system.config['logs_channel_name'],
            inline=True
        )
        
        embed.add_field(
            name="💡 Como usar:",
            value="`!sec_config auto_ban_bots true/false`\n`!sec_config role_delete_punishment remove_roles/ban`\n`!sec_config logs_channel_name nome_do_canal`",
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    if setting == 'auto_ban_bots':
        security_system.config['auto_ban_bots'] = value.lower() == 'true'
    elif setting == 'role_delete_punishment':
        if value in ['remove_roles', 'ban']:
            security_system.config['role_delete_punishment'] = value
        else:
            await ctx.send("❌ Valor inválido. Use: `remove_roles` ou `ban`")
            return
    elif setting == 'logs_channel_name':
        security_system.config['logs_channel_name'] = value
    else:
        await ctx.send("❌ Configuração inválida. Use: `auto_ban_bots`, `role_delete_punishment`, ou `logs_channel_name`")
        return
    
    await security_system.save_data()
    
    embed = discord.Embed(
        title="✅ Configuração Atualizada",
        description=f"**{setting}** foi alterado para: **{value}**",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

@bot.command(name='restore')
@commands.has_permissions(administrator=True)
async def restore_roles(ctx, user_id: str):
    """Restaura os cargos de um usuário removido pelo sistema"""
    if user_id not in security_system.restored_roles:
        embed = discord.Embed(
            title="❌ Usuário Não Encontrado",
            description="Este usuário não tem cargos para restaurar.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    try:
        user_data = security_system.restored_roles[user_id]
        guild = ctx.guild
        member = guild.get_member(int(user_id))
        
        if not member:
            await ctx.send("❌ Usuário não está mais no servidor.")
            return
        
        # Encontra os cargos que ainda existem
        roles_to_restore = []
        for role_id in user_data['roles']:
            role = guild.get_role(role_id)
            if role:
                roles_to_restore.append(role)
        
        if roles_to_restore:
            await member.add_roles(*roles_to_restore, reason=f"🔄 Restauração manual por {ctx.author}")
            
            embed = discord.Embed(
                title="✅ Cargos Restaurados",
                description=f"Cargos de {member.mention} foram restaurados com sucesso!",
                color=0x00ff00
            )
            embed.add_field(
                name="🎭 Cargos Restaurados",
                value=', '.join([role.name for role in roles_to_restore]),
                inline=False
            )
            embed.add_field(
                name="📅 Removidos em",
                value=user_data['removed_at'],
                inline=True
            )
            embed.add_field(
                name="🔍 Motivo Original",
                value=user_data['reason'],
                inline=True
            )
            
            # Remove da lista de restauração
            del security_system.restored_roles[user_id]
            await security_system.save_data()
            
            await ctx.send(embed=embed)
            
            # Log da restauração
            await security_system.log_security_action(
                guild,
                "🔄 Cargos Restaurados Manualmente",
                f"Cargos de {member.mention} foram restaurados por {ctx.author.mention}",
                0x00ff00,
                [
                    {'name': '👤 Usuário', 'value': member.mention, 'inline': True},
                    {'name': '👮 Restaurado por', 'value': ctx.author.mention, 'inline': True},
                    {'name': '🎭 Cargos', 'value': ', '.join([role.name for role in roles_to_restore]), 'inline': False}
                ]
            )
        else:
            await ctx.send("❌ Nenhum cargo válido encontrado para restaurar.")
    
    except Exception as e:
        await ctx.send(f"❌ Erro ao restaurar cargos: {e}")

@bot.command(name='whitelist')
@commands.has_permissions(administrator=True)
async def manage_whitelist(ctx, action: str = None, user_id: str = None):
    """Gerencia a whitelist de usuários autorizados"""
    if not action:
        embed = discord.Embed(
            title="🔐 Whitelist de Segurança",
            description="Usuários na whitelist podem deletar canais e cargos sem punição:",
            color=0x0099ff
        )
        
        whitelist_users = []
        for user_id in WHITELIST_IDS:
            user = bot.get_user(user_id)
            if user:
                whitelist_users.append(f"{user.mention} ({user_id})")
            else:
                whitelist_users.append(f"Usuário Desconhecido ({user_id})")
        
        embed.add_field(
            name="👥 Usuários Autorizados",
            value='\n'.join(whitelist_users) if whitelist_users else "Nenhum usuário na whitelist",
            inline=False
        )
        
        embed.add_field(
            name="💡 Como usar:",
            value="`!sec_whitelist add <ID>`\n`!sec_whitelist remove <ID>`\n`!sec_whitelist list`",
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    if action == 'add' and user_id:
        try:
            user_id_int = int(user_id)
            if user_id_int not in WHITELIST_IDS:
                WHITELIST_IDS.append(user_id_int)
                user = bot.get_user(user_id_int)
                username = user.mention if user else f"ID: {user_id_int}"
                
                embed = discord.Embed(
                    title="✅ Usuário Adicionado à Whitelist",
                    description=f"{username} foi adicionado à whitelist de segurança.",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Usuário já está na whitelist.")
        except ValueError:
            await ctx.send("❌ ID inválido.")
    
    elif action == 'remove' and user_id:
        try:
            user_id_int = int(user_id)
            if user_id_int in WHITELIST_IDS:
                WHITELIST_IDS.remove(user_id_int)
                user = bot.get_user(user_id_int)
                username = user.mention if user else f"ID: {user_id_int}"
                
                embed = discord.Embed(
                    title="✅ Usuário Removido da Whitelist",
                    description=f"{username} foi removido da whitelist de segurança.",
                    color=0xff9900
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Usuário não está na whitelist.")
        except ValueError:
            await ctx.send("❌ ID inválido.")
    
    else:
        await ctx.send("❌ Uso: `!sec_whitelist add/remove <ID>`")

@bot.command(name='status')
async def security_status(ctx):
    """Mostra o status do sistema de segurança"""
    embed = discord.Embed(
        title="🔒 Status do Sistema de Segurança",
        color=0x0099ff,
        timestamp=datetime.utcnow()
    )
    
    # Status geral
    embed.add_field(
        name="🟢 Sistema",
        value="Totalmente Operacional",
        inline=True
    )
    
    embed.add_field(
        name="📊 Logs Salvos",
        value=len(security_system.security_logs),
        inline=True
    )
    
    embed.add_field(
        name="🔄 Restaurações Pendentes",
        value=len(security_system.restored_roles),
        inline=True
    )
    
    # Configurações ativas
    config_status = []
    config_status.append(f"🤖 Auto-ban bots: {'✅' if security_system.config['auto_ban_bots'] else '❌'}")
    config_status.append(f"🎭 Punição por cargo: {security_system.config['role_delete_punishment']}")
    config_status.append(f"📺 Canal de logs: #{security_system.config['logs_channel_name']}")
    
    embed.add_field(
        name="⚙️ Configurações Ativas",
        value='\n'.join(config_status),
        inline=False
    )
    
    # Proteções ativas
    protections = [
        "🔥 Detecção de exclusão de canais",
        "🎭 Detecção de exclusão de cargos",
        "🤖 Banimento automático de bots",
        "📋 Sistema de logs automático",
        "🔐 Whitelist de usuários autorizados",
        "🔄 Sistema de restauração de cargos"
    ]
    
    embed.add_field(
        name="🛡️ Proteções Ativas",
        value='\n'.join(protections),
        inline=False
    )
    
    embed.set_footer(text="Sistema de Segurança Automático")
    
    await ctx.send(embed=embed)

# Comando de ajuda
@bot.command(name='help')
async def security_help(ctx):
    """Central de ajuda do sistema de segurança"""
    embed = discord.Embed(
        title="🔒 Sistema de Segurança - Comandos",
        description="**Proteção automática para seu servidor Discord**",
        color=0x0099ff
    )
    
    commands_admin = [
        "`!sec_config` - Configura o sistema de segurança",
        "`!sec_restore <ID>` - Restaura cargos de um usuário",
        "`!sec_whitelist` - Gerencia usuários autorizados",
        "`!sec_status` - Mostra status do sistema",
        "`!sec_help` - Esta ajuda"
    ]
    
    embed.add_field(
        name="👑 Comandos de Admin",
        value='\n'.join(commands_admin),
        inline=False
    )
    
    protections = [
        "🔥 **Exclusão de Canais**: Remove todos os cargos do responsável",
        "🎭 **Exclusão de Cargos**: Remove cargos ou bane (configurável)",
        "🤖 **Bots Automáticos**: Bane bots que entram no servidor",
        "📋 **Logs Automáticos**: Registra todas as ações no canal #logs",
        "🔐 **Whitelist**: Usuários autorizados não sofrem punições",
        "🔄 **Restauração**: Permite reverter punições aplicadas"
    ]
    
    embed.add_field(
        name="🛡️ Proteções Automáticas",
        value='\n'.join(protections),
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Permissões Necessárias",
        value="• View Audit Log\n• Manage Roles\n• Ban Members\n• Manage Channels",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Configuração Inicial",
        value="1. Execute `!sec_status`\n2. Configure com `!sec_config`\n3. Adicione admins na whitelist\n4. Teste as proteções",
        inline=True
    )
    
    embed.set_footer(text="🔒 Sistema desenvolvido para máxima segurança")
    
    await ctx.send(embed=embed)

# Error handler
@bot.event
async def on_command_error(ctx, error):
    """Tratamento de erros dos comandos"""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="🚫 Permissões Insuficientes",
            description="Você precisa de permissões de **Administrador** para usar este comando!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        return  # Ignora comandos não encontrados
    else:
        print(f"❌ Erro no comando: {error}")

# Inicialização do bot
if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('SECURITY_BOT_TOKEN')
    
    if TOKEN:
        print("🚀 Iniciando Sistema de Segurança...")
        keep_alive()
        bot.run(TOKEN)
    else:
        print("❌ Token do bot de segurança não encontrado!")
        print("Configure a variável SECURITY_BOT_TOKEN nas Secrets do Replit")
