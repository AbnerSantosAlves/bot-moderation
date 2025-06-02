import discord
from discord.ext import commands
import json
import random
import asyncio
import aiofiles
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from keep_alive import keep_alive
from dotenv import load_dotenv


# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# IDs dos servidores onde a segurança deve estar ativa
SECURITY_GUILD_IDS = [1097629413711024189, 1369967561218723910]

# Importa configurações de segurança
try:
    from security_config import WHITELIST_IDS, DEFAULT_CONFIG, MESSAGES, COLORS, MONITORED_EVENTS
    print("✅ Configurações de segurança carregadas!")
except ImportError:
    print("⚠️ Usando configurações padrão de segurança...")
    # Configurações padrão de segurança
    WHITELIST_IDS = [983196900910039090]
    DEFAULT_CONFIG = {
        'auto_ban_bots': True,
        'role_delete_punishment': 'remove_roles',
        'logs_channel_name': 'security-logs',
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

# Arquivo para salvar dados de segurança
SECURITY_DATA_FILE = "security_data.json"

# Sistema de ganho automático
import time
from datetime import datetime, timedelta

# Lista de palavrões para filtrar
PALAVROES = [
    'merda', 'porra', 'caralho', 'buceta', 'puta', 'viado', 'gay', 'bicha', 
    'cu', 'cuzão', 'fdp', 'filho da puta', 'desgraça', 'otario', 'idiota',
    'burro', 'imbecil', 'retardado', 'mongol', 'nazi', 'hitler', 'bosta',
    'cacete', 'piroca', 'rola', 'pênis', 'vagina', 'sexo', 'transar'
]

# Dados dos jogadores disponíveis no olheiro
JOGADORES_OLHEIRO = [
    {"nome": "Oliver Pau no Cu Santos", "posicao": "Goleiro", "over": 93, "habilidade": 93, "valor_mercado": 350000},
    {"nome": "Zargão", "posicao": "Zagueiro", "over": 80, "habilidade": 82, "valor_mercado": 45000},
    {"nome": "Bruno", "posicao": "Zagueiro", "over": 84, "habilidade": 86, "valor_mercado": 60000},
    {"nome": "Anthony", "posicao": "Meia", "over": 85, "habilidade": 87, "valor_mercado": 65000},
    {"nome": "Lewis Ferguson", "posicao": "Atacante", "over": 79, "habilidade": 78, "valor_mercado": 40000},
    {"nome": "Saulo Bezerra", "posicao": "Atacante", "over": 88, "habilidade": 89, "valor_mercado": 80000},
    {"nome": "Pedro Caldas", "posicao": "Atacante", "over": 85, "habilidade": 87, "valor_mercado": 65000},
    {"nome": "Brunno Santos", "posicao": "Meio Campo", "over": 80, "habilidade": 82, "valor_mercado": 45000},
    {"nome": "Zau", "posicao": "Goleiro", "over": 88, "habilidade": 89, "valor_mercado": 75000},
    {"nome": "Hiroshi", "posicao": "Goleiro", "over": 84, "habilidade": 86, "valor_mercado": 55000},
    {"nome": "Sassa", "posicao": "Goleiro", "over": 76, "habilidade": 75, "valor_mercado": 35000},
    {"nome": "Oliver Wayne", "posicao": "Zagueiro", "over": 91, "habilidade": 93, "valor_mercado": 350000},
    {"nome": "Corvino", "posicao": "Ponta", "over": 86, "habilidade": 88, "valor_mercado": 70000},
    {"nome": "Pdrz", "posicao": "Atacante", "over": 86, "habilidade": 88, "valor_mercado": 70000},
    {"nome": "Nott", "posicao": "Meio Campo", "over": 83, "habilidade": 85, "valor_mercado": 55000},
    {"nome": "Keven", "posicao": "Atacante", "over": 86, "habilidade": 88, "valor_mercado": 70000},
    {"nome": "Ronaldinho Cruzeiro", "posicao": "Ponta", "over": 84, "habilidade": 86, "valor_mercado": 60000},
    {"nome": "Carlos Cruzeiro", "posicao": "Meio Campo", "over": 85, "habilidade": 87, "valor_mercado": 65000},
    {"nome": "Gustavo Soares", "posicao": "Meia Central", "over": 82, "habilidade": 83, "valor_mercado": 50000},
    {"nome": "Crazy", "posicao": "Ponta", "over": 88, "habilidade": 89, "valor_mercado": 80000},
    {"nome": "Pietro", "posicao": "Volante", "over": 80, "habilidade": 82, "valor_mercado": 45000},
    {"nome": "Matheus Taylor", "posicao": "Ponta Esquerda", "over": 96, "habilidade": 98, "valor_mercado": 150000},
    {"nome": "Juliano Henrique", "posicao": "Atacante", "over": 100, "habilidade": 100, "valor_mercado": 1000000},
    {"nome": "Michael Owen", "posicao": "Goleiro", "over": 99, "habilidade": 100, "valor_mercado": 200000},
    {"nome": "Phillipe Guedes", "posicao": "Atacante", "over": 88, "habilidade": 89, "valor_mercado": 80000},
    {"nome": "Prince", "posicao": "Ponta Direita", "over": 91, "habilidade": 93, "valor_mercado": 100000},
    {"nome": "Hiroshi", "posicao": "Zagueiro", "over": 90, "habilidade": 92, "valor_mercado": 95000},
    {"nome": "Felipe Botelho", "posicao": "Meio Campo", "over": 87, "habilidade": 88, "valor_mercado": 75000},
    {"nome": "M. De Light", "posicao": "Zagueiro", "over": 90, "habilidade": 92, "valor_mercado": 95000},
    {"nome": "Kai Guedes", "posicao": "Ponta Direita", "over": 90, "habilidade": 92, "valor_mercado": 95000},
    {"nome": "Macaé", "posicao": "Atacante", "over": 89, "habilidade": 90, "valor_mercado": 85000},
    {"nome": "Lucas Bask", "posicao": "Zagueiro", "over": 79, "habilidade": 78, "valor_mercado": 40000},
    {"nome": "Sam Ker", "posicao": "Atacante", "over": 75, "habilidade": 74, "valor_mercado": 30000},
    {"nome": "Jake Willy", "posicao": "Atacante", "over": 69, "habilidade": 68, "valor_mercado": 25000},
    {"nome": "Zake Zau", "posicao": "Volante", "over": 80, "habilidade": 82, "valor_mercado": 45000},
    {"nome": "Helena Silva", "posicao": "Zagueira", "over": 70, "habilidade": 70, "valor_mercado": 28000},
    {"nome": "Luan Alves", "posicao": "Goleiro", "over": 69, "habilidade": 68, "valor_mercado": 25000},
    {"nome": "Fernando M.", "posicao": "Atacante", "over": 71, "habilidade": 71, "valor_mercado": 30000},
    {"nome": "Coutinho S.", "posicao": "Meio Campo", "over": 69, "habilidade": 68, "valor_mercado": 25000},
    {"nome": "Kaio Becker", "posicao": "Zagueiro", "over": 67, "habilidade": 66, "valor_mercado": 22000},
    {"nome": "Caio Miguel", "posicao": "Goleiro", "over": 69, "habilidade": 68, "valor_mercado": 25000},
    {"nome": "Alex", "posicao": "Volante", "over": 75, "habilidade": 74, "valor_mercado": 32000},
    {"nome": "Matheus Mtzx", "posicao": "Ponta Direita", "over": 70, "habilidade": 70, "valor_mercado": 28000}
]

# Arquivo para salvar dados
DATA_FILE = "vados_bot_data.json"

# ID do owner (coloque seu ID aqui)
OWNER_ID = 983196900910039090  # Substitua pelo seu ID

class SecurityBot:
    def __init__(self):
        self.restored_roles = {}  # Para armazenar cargos removidos
        self.security_logs = []
        self.config = {
            'auto_ban_bots': True,
            'role_delete_punishment': 'remove_roles',  # 'remove_roles' ou 'ban'
            'logs_channel_name': 'security-logs'
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
        """Encontra o canal de logs específico por ID"""
        # ID do canal específico para logs de segurança
        LOGS_CHANNEL_ID = 1335821136205709332
        
        logs_channel = guild.get_channel(LOGS_CHANNEL_ID)
        
        if not logs_channel:
            print(f"❌ Canal de logs com ID {LOGS_CHANNEL_ID} não encontrado!")
            # Tenta criar um canal com o nome configurado como fallback
            try:
                logs_channel = await guild.create_text_channel(
                    self.config['logs_channel_name'],
                    topic="🔒 Canal de logs de segurança automáticos",
                    reason="Canal de segurança criado automaticamente"
                )
                print(f"✅ Canal de logs criado como fallback: #{logs_channel.name}")
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

class VadosBot:
    def __init__(self):
        self.users_data = {}
        self.ligas = {}
        self.confrontos = {}
        self.emprestimos = {}
        
    async def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                async with aiofiles.open(DATA_FILE, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    self.users_data = data.get('users_data', {})
                    self.ligas = data.get('ligas', {})
                    self.confrontos = data.get('confrontos', {})
                    self.emprestimos = data.get('emprestimos', {})
                    
                    # Limpa jogadores criados por usuários (atualização)
                    for user_id, user_data in self.users_data.items():
                        if 'jogadores' in user_data:
                            user_data['jogadores'] = [j for j in user_data['jogadores'] if j.get('tipo') != 'criado']
                            user_data['jogadores_criados'] = 0
                        
                        # Adiciona campo de time se não existir
                        if 'time' not in user_data:
                            user_data['time'] = None
                    
                    await self.save_data()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
    
    async def save_data(self):
        try:
            data = {
                'users_data': self.users_data,
                'ligas': self.ligas,
                'confrontos': self.confrontos,
                'emprestimos': self.emprestimos
            }
            async with aiofiles.open(DATA_FILE, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    def get_user_data(self, user_id):
        if str(user_id) not in self.users_data:
            self.users_data[str(user_id)] = {
                'dinheiro': 100000,
                'jogadores': [],
                'time': None,  # Novo campo obrigatório
                'escalacao': {
                    'goleiro': None,
                    'zagueiro1': None,
                    'zagueiro2': None,
                    'lateral_esq': None,
                    'lateral_dir': None,
                    'volante': None,
                    'meia': None,
                    'ponta_esq': None,
                    'ponta_dir': None,
                    'atacante1': None,
                    'atacante2': None
                },
                'vitorias': 0,
                'derrotas': 0,
                'empates': 0,
                'jogadores_criados': 0,
                'ultimo_ganho_daily': None
            }
        return self.users_data[str(user_id)]
    
    def verificar_ganho_daily(self, user_id):
        user_data = self.get_user_data(user_id)
        agora = datetime.now()
        
        if user_data['ultimo_daily'] is None:
            user_data['ultimo_daily'] = agora.isoformat()
            return False
        
        ultimo_ganho = datetime.fromisoformat(user_data['ultimo_daily'])
        if agora - ultimo_ganho >= timedelta(hours=24):
            user_data['dinheiro'] += 50000
            user_data['ultimo_daily'] = agora.isoformat()
            return True
        
        return False

def verificar_palavrao(texto):
    """Verifica se o texto contém palavrões"""
    texto_lower = texto.lower()
    for palavrao in PALAVROES:
        if palavrao in texto_lower:
            return True
    return False

def corrigir_posicao(posicao):
    """Corrige a posição para português correto"""
    posicoes_mapping = {
        'goleiro': 'Goleiro',
        'gol': 'Goleiro',
        'goalkeeper': 'Goleiro',
        'zagueiro': 'Zagueiro',
        'zag': 'Zagueiro',
        'defender': 'Zagueiro',
        'defensor': 'Zagueiro',
        'lateral': 'Lateral',
        'lat': 'Lateral',
        'lateral direito': 'Lateral Direito',
        'lateral esquerdo': 'Lateral Esquerdo',
        'volante': 'Volante',
        'vol': 'Volante',
        'meia': 'Meia',
        'meio': 'Meia',
        'meio campo': 'Meio Campo',
        'meio-campo': 'Meio Campo',
        'midfielder': 'Meio Campo',
        'ponta': 'Ponta',
        'ponta direita': 'Ponta Direita',
        'ponta esquerda': 'Ponta Esquerda',
        'atacante': 'Atacante',
        'atk': 'Atacante',
        'forward': 'Atacante',
        'centroavante': 'Atacante',
        'centro-avante': 'Atacante'
    }
    
    posicao_lower = posicao.lower().strip()
    return posicoes_mapping.get(posicao_lower, posicao.title())

async def verificar_time_obrigatorio(ctx):
    """Verifica se o usuário tem time criado, se não, força a criação"""
    # Verifica se é um dos servidores de segurança (comandos de futebol NÃO funcionam lá)
    if ctx.guild and ctx.guild.id in SECURITY_GUILD_IDS:
        embed = discord.Embed(
            title="🔒 Servidor de Segurança",
            description="❌ **Comandos de futebol não funcionam neste servidor.**\n\n🛡️ Este é um servidor exclusivo para **Sistema de Segurança**.\n\n⚽ Use os comandos de futebol em outros servidores!",
            color=0xff0000
        )
        embed.set_footer(text="🔒 Apenas sistema de segurança ativo neste servidor!")
        await ctx.send(embed=embed)
        return False
    
    user_data = vados.get_user_data(ctx.author.id)
    
    if not user_data['time']:
        embed = discord.Embed(
            title="⚠️ Time Obrigatório",
            description="Você precisa criar seu time antes de usar este comando!",
            color=0xff9900
        )
        embed.add_field(
            name="📝 Como criar:",
            value="Use o botão abaixo para criar seu time com uma sigla única.",
            inline=False
        )
        embed.set_footer(text="🏆 Todo jogador deve ter um time!")
        
        view = CriarTimeView(vados, ctx.author)
        await ctx.send(embed=embed, view=view)
        return False
    
    return True

vados = VadosBot()
security_system = SecurityBot()

# Modal para criar time
class CriarTimeModal(discord.ui.Modal):
    def __init__(self, vados_instance, author):
        super().__init__(title="🏆 Criar Seu Time")
        self.vados = vados_instance
        self.author = author
        
        self.nome_time = discord.ui.TextInput(
            label="Nome do Time",
            placeholder="Digite o nome completo do seu time...",
            max_length=30,
            required=True
        )
        
        self.sigla_time = discord.ui.TextInput(
            label="Sigla do Time (máx. 10 caracteres)",
            placeholder="Ex: FLA, PAL, COR...",
            max_length=10,
            required=True
        )
        
        self.add_item(self.nome_time)
        self.add_item(self.sigla_time)
    
    async def on_submit(self, interaction: discord.Interaction):
        nome = self.nome_time.value.strip()
        sigla = self.sigla_time.value.strip().upper()
        
        # Validações
        if verificar_palavrao(nome) or verificar_palavrao(sigla):
            embed = discord.Embed(
                title="❌ Nome Inapropriado",
                description="O nome ou sigla do time contém palavras inapropriadas. Tente novamente com um nome adequado.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if len(sigla) < 2:
            embed = discord.Embed(
                title="❌ Sigla Muito Curta",
                description="A sigla deve ter pelo menos 2 caracteres.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Verifica se sigla já existe
        for user_id, user_data in self.vados.users_data.items():
            if user_data.get('time') and user_data['time']['sigla'] == sigla:
                embed = discord.Embed(
                    title="❌ Sigla Já Existe",
                    description=f"A sigla **{sigla}** já está sendo usada por outro time. Escolha uma sigla diferente.",
                    color=0xff0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Cria o time
        user_data = self.vados.get_user_data(self.author.id)
        user_data['time'] = {
            'nome': nome,
            'sigla': sigla,
            'criado_em': datetime.now().isoformat()
        }
        
        await self.vados.save_data()
        
        embed = discord.Embed(
            title="🏆 Time Criado com Sucesso!",
            description=f"Seu time **{nome}** foi criado!",
            color=0x00ff00
        )
        embed.add_field(name="🏆 Nome", value=nome, inline=True)
        embed.add_field(name="📝 Sigla", value=sigla, inline=True)
        embed.add_field(name="👤 Dono", value=self.author.mention, inline=True)
        embed.set_footer(text="🌟 Agora você pode usar todos os comandos do bot!")
        
        await interaction.response.send_message(embed=embed)

# Modal para criar jogador
class CriarJogadorModal(discord.ui.Modal):
    def __init__(self, vados_instance, author):
        super().__init__(title="⭐ Criar Seu Jogador Único")
        self.vados = vados_instance
        self.author = author
        
        self.nome_jogador = discord.ui.TextInput(
            label="Nome do Jogador",
            placeholder="Digite o nome do jogador...",
            max_length=25,
            required=True
        )
        
        self.posicao_jogador = discord.ui.TextInput(
            label="Posição",
            placeholder="Ex: Atacante, Goleiro, Zagueiro, Meia...",
            max_length=20,
            required=True
        )
        
        self.add_item(self.nome_jogador)
        self.add_item(self.posicao_jogador)
    
    async def on_submit(self, interaction: discord.Interaction):
        nome = self.nome_jogador.value.strip()
        posicao = corrigir_posicao(self.posicao_jogador.value.strip())
        
        # Validações
        if verificar_palavrao(nome):
            embed = discord.Embed(
                title="❌ Nome Inapropriado",
                description="O nome do jogador contém palavras inapropriadas. Tente novamente com um nome adequado.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_data = self.vados.get_user_data(self.author.id)
        
        if user_data['jogadores_criados'] >= 1:
            embed = discord.Embed(
                title="❌ Limite Atingido",
                description="Você já criou seu jogador personalizado! Cada jogador pode criar apenas 1 jogador.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Habilidade aleatória baseada no over inicial
        over_inicial = 50
        habilidade_inicial = over_inicial + random.randint(-5, 10)  # Varia entre 45-60
        
        jogador = {
            'nome': nome,
            'posicao': posicao,
            'habilidade': habilidade_inicial,
            'over': over_inicial,
            'tipo': 'criado',
            'evolucoes': 0
        }
        
        user_data['jogadores'].append(jogador)
        user_data['jogadores_criados'] += 1
        await self.vados.save_data()
        
        embed = discord.Embed(
            title="🎉 Jogador Criado com Sucesso!",
            description=f"✨ **{nome}** foi adicionado ao seu elenco!",
            color=0x00ff00
        )
        
        embed.add_field(name="⚽ Nome", value=nome, inline=True)
        embed.add_field(name="📍 Posição", value=posicao, inline=True)
        embed.add_field(name="📈 Over Inicial", value=over_inicial, inline=True)
        embed.add_field(name="🎯 Habilidade", value=f"{habilidade_inicial}%", inline=True)
        embed.add_field(name="🌟 Tipo", value="Jogador Único", inline=True)
        embed.add_field(name="🔄 Evoluções", value="0", inline=True)
        
        embed.set_footer(text="🌟 Jogador personalizado criado! Use -elenco para visualizar.")
        
        await interaction.response.send_message(embed=embed)

# View para criar time
class CriarTimeView(discord.ui.View):
    def __init__(self, vados_instance, author):
        super().__init__(timeout=300)
        self.vados = vados_instance
        self.author = author
    
    @discord.ui.button(label="🏆 Criar Meu Time", style=discord.ButtonStyle.primary, emoji="🏆")
    async def criar_time(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Apenas quem solicitou pode criar!", ephemeral=True)
            return
        
        modal = CriarTimeModal(self.vados, self.author)
        await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
    await vados.load_data()
    await security_system.load_data()
    print(f'🚀 MXP Football Manager está online e pronto para gerenciar o futebol!')
    print(f'🔒 Sistema de Segurança ativo APENAS nos servidores: {", ".join(map(str, SECURITY_GUILD_IDS))}')
    print('=' * 50)
    print("✅ Proteções ativas (servidor específico):")
    print("  • Detecção de exclusão de canais")
    print("  • Detecção de exclusão de cargos")
    print("  • Banimento automático de bots")
    print("  • Sistema de logs automático")
    print('=' * 50)

# Comando para criar time (se ainda não tiver)
@bot.command(name='criar_time')
async def criar_time(ctx):
    """Cria seu time oficial (obrigatório para jogar)"""
    user_data = vados.get_user_data(ctx.author.id)
    
    if user_data['time']:
        embed = discord.Embed(
            title="⚠️ Time Já Existe",
            description=f"Você já tem o time **{user_data['time']['nome']}** ({user_data['time']['sigla']})!",
            color=0xff9900
        )
        embed.add_field(name="🏆 Seu Time", value=f"{user_data['time']['nome']} ({user_data['time']['sigla']})", inline=False)
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="🏆 Criar Seu Time",
        description="Todo jogador precisa ter um time oficial para participar das competições!",
        color=0x0099ff
    )
    embed.add_field(
        name="📋 Informações:",
        value="• Nome do time (máx. 30 caracteres)\n• Sigla única (máx. 10 caracteres)\n• Não são permitidos palavrões\n• A sigla deve ser única",
        inline=False
    )
    
    view = CriarTimeView(vados, ctx.author)
    await ctx.send(embed=embed, view=view)

# Comando ganho automático
@bot.command(name='daily')
async def daily(ctx):
    """Coleta seu ganho automático de 50.000 reais (a cada 24h)"""
    # Verifica se não é um dos servidores de segurança
    if ctx.guild and ctx.guild.id in SECURITY_GUILD_IDS:
        embed = discord.Embed(
            title="🔒 Comando Não Disponível",
            description="❌ Comandos de futebol não funcionam no servidor de segurança.\n\n⚽ Use este comando em outros servidores!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
        
    if not await verificar_time_obrigatorio(ctx):
        return
        
    user_data = vados.get_user_data(ctx.author.id)
    
    if vados.verificar_daily(ctx.author.id):
        embed = discord.Embed(
            title="💰 Ganho Automático Coletado!",
            description="Você coletou seu ganho automático de **R$ 50.000**!",
            color=0x00ff00
        )
        embed.add_field(name="💵 Valor Recebido", value="R$ 50.000", inline=True)
        embed.add_field(name="💰 Saldo Atual", value=f"R$ {user_data['dinheiro']:,}", inline=True)
        embed.add_field(name="⏰ Próximo Ganho", value="Em 24 horas", inline=True)
        embed.set_footer(text="🎉 MXP Football Manager - Ganho automático coletado!")
        await vados.save_data()
    else:
        # Calcula tempo restante
        if user_data['ultimo_daily']:
            ultimo_ganho = datetime.fromisoformat(user_data['ultimo_daily'])
            proximo_ganho = ultimo_ganho + timedelta(hours=24)
            tempo_restante = proximo_ganho - datetime.now()
            
            if tempo_restante.total_seconds() > 0:
                horas = int(tempo_restante.total_seconds() // 3600)
                minutos = int((tempo_restante.total_seconds() % 3600) // 60)
                
                embed = discord.Embed(
                    title="⏰ Ganho Automático Não Disponível",
                    description=f"Você já coletou seu ganho automático hoje!\n\n⏱️ **Tempo restante:** {horas}h {minutos}min",
                    color=0xff9900
                )
                embed.add_field(name="💰 Saldo Atual", value=f"R$ {user_data['dinheiro']:,}", inline=True)
                embed.add_field(name="💵 Próximo Valor", value="R$ 70.000", inline=True)
            else:
                embed = discord.Embed(
                    title="🔄 Processando...",
                    description="Aguarde um momento e tente novamente.",
                    color=0x0099ff
                )
        else:
            embed = discord.Embed(
                title="🎉 Primeira Coleta!",
                description="Aguarde um momento para processar sua primeira coleta.",
                color=0x0099ff
            )
    
    await ctx.send(embed=embed)

# Eventos de segurança
@bot.event
async def on_guild_channel_delete(channel):
    """🔥 Detecta exclusão de canais, recria automaticamente e pune o responsável"""
    try:
        guild = channel.guild
        
        # Verifica se é um dos servidores com segurança ativa
        if guild.id not in SECURITY_GUILD_IDS:
            return  # Não aplica segurança em outros servidores
        
        # Salva informações do canal antes de tentar recriar
        channel_data = {
            'name': channel.name,
            'type': channel.type,
            'category': channel.category,
            'position': channel.position,
            'topic': getattr(channel, 'topic', None),
            'nsfw': getattr(channel, 'nsfw', False),
            'slowmode_delay': getattr(channel, 'slowmode_delay', 0),
            'overwrites': {str(target.id): overwrite._values for target, overwrite in channel.overwrites.items()}
        }
        
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
                            {'name': '📺 Canal Deletado', 'value': f"#{channel_data['name']}", 'inline': True},
                            {'name': '👤 Responsável', 'value': executor.mention, 'inline': True},
                            {'name': '✅ Status', 'value': "Usuário autorizado - sem recriação", 'inline': True}
                        ]
                    )
                    return
                
                # Se chegou aqui, é uma ação suspeita - RECRIA O CANAL
                try:
                    # Cria o novo canal
                    if channel_data['type'] == discord.ChannelType.text:
                        novo_canal = await guild.create_text_channel(
                            name=channel_data['name'],
                            category=channel_data['category'],
                            topic=channel_data['topic'],
                            nsfw=channel_data['nsfw'],
                            slowmode_delay=channel_data['slowmode_delay'],
                            position=channel_data['position'],
                            reason="🔒 Canal recriado automaticamente pelo sistema de segurança"
                        )
                    elif channel_data['type'] == discord.ChannelType.voice:
                        novo_canal = await guild.create_voice_channel(
                            name=channel_data['name'],
                            category=channel_data['category'],
                            position=channel_data['position'],
                            reason="🔒 Canal recriado automaticamente pelo sistema de segurança"
                        )
                    else:
                        # Para outros tipos de canal, cria como texto
                        novo_canal = await guild.create_text_channel(
                            name=channel_data['name'],
                            category=channel_data['category'],
                            reason="🔒 Canal recriado automaticamente pelo sistema de segurança"
                        )
                    
                    # Tenta restaurar permissões
                    for target_id, overwrite_data in channel_data['overwrites'].items():
                        try:
                            target = guild.get_member(int(target_id)) or guild.get_role(int(target_id))
                            if target:
                                overwrite = discord.PermissionOverwrite(**{k: v for k, v in overwrite_data.items() if v is not None})
                                await novo_canal.set_permissions(target, overwrite=overwrite)
                        except:
                            pass  # Ignora erros de permissão específicas
                    
                    canal_recriado = True
                    canal_novo_id = novo_canal.id
                    
                except Exception as e:
                    print(f"❌ Erro ao recriar canal: {e}")
                    canal_recriado = False
                    canal_novo_id = None
                
                # PUNE O USUÁRIO mesmo com recriação
                member = guild.get_member(executor.id)
                if member:
                    # Salva os cargos antes de remover
                    original_roles = [role for role in member.roles if role != guild.default_role]
                    role_names = [role.name for role in original_roles]
                    
                    # Salva para possível restauração
                    security_system.restored_roles[str(executor.id)] = {
                        'roles': [role.id for role in original_roles],
                        'removed_at': datetime.utcnow().isoformat(),
                        'reason': f"Deletou canal #{channel_data['name']}",
                        'guild_id': guild.id
                    }
                    
                    try:
                        await member.remove_roles(*original_roles, reason="🔒 Segurança: Deletou canal sem autorização")
                        punição_aplicada = "Todos os cargos removidos"
                    except Exception as e:
                        punição_aplicada = f"Erro ao remover cargos: {str(e)[:100]}"
                else:
                    punição_aplicada = "Usuário não encontrado no servidor"
                    role_names = []
                
                # Log detalhado com informações de recriação
                await security_system.log_security_action(
                    guild,
                    "🚨 CANAL DELETADO - RECRIADO AUTOMATICAMENTE",
                    f"⚠️ **{executor.mention}** deletou o canal **#{channel_data['name']}** mas foi recriado automaticamente!",
                    0xff4500,
                    [
                        {'name': '📺 Canal Original', 'value': f"#{channel_data['name']} (ID: {channel.id})", 'inline': True},
                        {'name': '🔄 Canal Recriado', 'value': f"#{novo_canal.name} (ID: {canal_novo_id})" if canal_recriado else "❌ Falha na recriação", 'inline': True},
                        {'name': '👤 Responsável', 'value': f"{executor.mention}\n({executor.id})", 'inline': True},
                        {'name': '⚡ Ação Tomada', 'value': punição_aplicada, 'inline': True},
                        {'name': '🔄 Status Recriação', 'value': "✅ Sucesso" if canal_recriado else "❌ Falhou", 'inline': True},
                        {'name': '📝 Tipo do Canal', 'value': str(channel_data['type']).replace('ChannelType.', ''), 'inline': True},
                        {'name': '🎭 Cargos Removidos', 'value': ', '.join(role_names) if role_names else "Nenhum cargo", 'inline': False},
                        {'name': '🔧 Restauração Manual', 'value': "Use `-sec_restore` para reverter punição", 'inline': True}
                    ]
                )
                
                print(f"🔒 SEGURANÇA: Canal #{channel_data['name']} recriado automaticamente após exclusão por {executor}")
                break
    
    except Exception as e:
        print(f"❌ Erro no detector de exclusão de canais: {e}")

@bot.event
async def on_guild_role_delete(role):
    """🎭 Detecta exclusão de cargos, recria automaticamente e pune o responsável"""
    try:
        guild = role.guild
        
        # Verifica se é um dos servidores com segurança ativa
        if guild.id not in SECURITY_GUILD_IDS:
            return  # Não aplica segurança em outros servidores
        
        # Salva informações do cargo antes de tentar recriar
        role_data = {
            'name': role.name,
            'color': role.color,
            'hoist': role.hoist,
            'mentionable': role.mentionable,
            'permissions': role.permissions,
            'position': role.position,
            'reason': "🔒 Cargo recriado automaticamente pelo sistema de segurança"
        }
        
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
                            {'name': '🎭 Cargo Deletado', 'value': f"@{role_data['name']}", 'inline': True},
                            {'name': '👤 Responsável', 'value': executor.mention, 'inline': True},
                            {'name': '✅ Status', 'value': "Usuário autorizado - sem recriação", 'inline': True}
                        ]
                    )
                    return
                
                # Se chegou aqui, é uma ação suspeita - RECRIA O CARGO
                try:
                    novo_cargo = await guild.create_role(
                        name=role_data['name'],
                        color=role_data['color'],
                        hoist=role_data['hoist'],
                        mentionable=role_data['mentionable'],
                        permissions=role_data['permissions'],
                        reason=role_data['reason']
                    )
                    
                    # Tenta mover o cargo para a posição original
                    try:
                        await novo_cargo.edit(position=role_data['position'])
                    except:
                        pass  # Se não conseguir mover, mantém na posição padrão
                    
                    cargo_recriado = True
                    cargo_novo_id = novo_cargo.id
                    
                except Exception as e:
                    print(f"❌ Erro ao recriar cargo: {e}")
                    cargo_recriado = False
                    cargo_novo_id = None
                
                # PUNE O USUÁRIO mesmo com recriação
                member = guild.get_member(executor.id)
                if member:
                    # Salva os cargos antes de aplicar punição
                    original_roles = [r for r in member.roles if r != guild.default_role]
                    role_names = [r.name for r in original_roles]
                    
                    # Salva para possível restauração
                    security_system.restored_roles[str(executor.id)] = {
                        'roles': [r.id for r in original_roles],
                        'removed_at': datetime.utcnow().isoformat(),
                        'reason': f"Deletou cargo @{role_data['name']}",
                        'guild_id': guild.id
                    }
                    
                    # Aplica punição baseada na configuração
                    if security_system.config['role_delete_punishment'] == 'ban':
                        try:
                            await member.ban(reason=f"🔒 Segurança: Deletou cargo @{role_data['name']} sem autorização")
                            punição_aplicada = "**BANIDO**"
                        except Exception as e:
                            punição_aplicada = f"Erro ao banir: {str(e)[:100]}"
                    else:  # remove_roles (padrão)
                        try:
                            await member.remove_roles(*original_roles, reason=f"🔒 Segurança: Deletou cargo @{role_data['name']} sem autorização")
                            punição_aplicada = "Todos os cargos removidos"
                        except Exception as e:
                            punição_aplicada = f"Erro ao remover cargos: {str(e)[:100]}"
                else:
                    punição_aplicada = "Usuário não encontrado no servidor"
                    role_names = []
                
                # Log detalhado com informações de recriação
                await security_system.log_security_action(
                    guild,
                    "🚨 CARGO DELETADO - RECRIADO AUTOMATICAMENTE",
                    f"⚠️ **{executor.mention}** deletou o cargo **@{role_data['name']}** mas foi recriado automaticamente!",
                    0xff4500,
                    [
                        {'name': '🎭 Cargo Original', 'value': f"@{role_data['name']} (ID: {role.id})", 'inline': True},
                        {'name': '🔄 Cargo Recriado', 'value': f"@{novo_cargo.name} (ID: {cargo_novo_id})" if cargo_recriado else "❌ Falha na recriação", 'inline': True},
                        {'name': '👤 Responsável', 'value': f"{executor.mention}\n({executor.id})", 'inline': True},
                        {'name': '⚡ Ação Tomada', 'value': punição_aplicada, 'inline': True},
                        {'name': '🔄 Status Recriação', 'value': "✅ Sucesso" if cargo_recriado else "❌ Falhou", 'inline': True},
                        {'name': '🎨 Cor Original', 'value': f"{role_data['color']}", 'inline': True},
                        {'name': '🔧 Permissões', 'value': f"{len([p for p, v in role_data['permissions'] if v])} permissões ativas", 'inline': True},
                        {'name': '🎭 Cargos Removidos', 'value': ', '.join(role_names) if role_names else "Nenhum cargo", 'inline': False},
                        {'name': '🔧 Restauração Manual', 'value': "Use `-sec_restore` para reverter punição", 'inline': True}
                    ]
                )
                
                print(f"🔒 SEGURANÇA: Cargo @{role_data['name']} recriado automaticamente após exclusão por {executor}")
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
        
        # Verifica se é um dos servidores com segurança ativa
        if guild.id not in SECURITY_GUILD_IDS:
            return  # Não aplica segurança em outros servidores
        
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

# Event para comandos inválidos
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Comando Não Encontrado",
            description=f"O comando `{ctx.message.content}` não existe!\nUse `-ajuda` para ver todos os comandos disponíveis.",
            color=0xff0000
        )
        embed.set_footer(text="💡 Dica: Verifique se digitou corretamente!")
        print("Comando não encontrado")
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="🚫 Permissões Insuficientes",
            description="Você precisa de permissões de **Administrador** para usar este comando!",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# Comando para ver o time
@bot.command(name='time')
async def ver_time(ctx, usuario: discord.Member = None):
    """Visualiza o time escalado de um jogador"""
    if not await verificar_time_obrigatorio(ctx):
        return
        
    if usuario is None:
        usuario = ctx.author
    
    user_data = vados.get_user_data(usuario.id)
    escalacao = user_data['escalacao']
    
    # Nome do time
    nome_time = "Time sem nome"
    if user_data['time']:
        nome_time = f"{user_data['time']['nome']} ({user_data['time']['sigla']})"
    
    embed = discord.Embed(
        title=f"⚽ {nome_time}",
        color=0x00ff00
    )
    
    # Verifica se tem escalação
    jogadores_escalados = [j for j in escalacao.values() if j is not None]
    
    if not jogadores_escalados:
        embed.description = "❌ Nenhum jogador escalado ainda!\nUse `-escalar` para montar seu time."
        embed.color = 0xff9900
    else:
        # Formação visual melhorada
        formacao = f"""
```
                {escalacao['goleiro']['nome'][:12] if escalacao['goleiro'] else '-----'}
                        ({escalacao['goleiro']['habilidade']}%)

    {escalacao['zagueiro1']['nome'][:8] if escalacao['zagueiro1'] else '-----'}        {escalacao['zagueiro2']['nome'][:8] if escalacao['zagueiro2'] else '-----'}
    ({escalacao['zagueiro1']['habilidade']}%)      ({escalacao['zagueiro2']['habilidade']}%)

{escalacao['lateral_esq']['nome'][:8] if escalacao['lateral_esq'] else '-----'}                            {escalacao['lateral_dir']['nome'][:8] if escalacao['lateral_dir'] else '-----'}
({escalacao['lateral_esq']['habilidade']}%)                          ({escalacao['lateral_dir']['habilidade']}%)

         {escalacao['volante']['nome'][:8] if escalacao['volante'] else '-----'}    {escalacao['meia']['nome'][:8] if escalacao['meia'] else '-----'}
         ({escalacao['volante']['habilidade']}%)  ({escalacao['meia']['habilidade']}%)

    {escalacao['ponta_esq']['nome'][:8] if escalacao['ponta_esq'] else '-----'}                    {escalacao['ponta_dir']['nome'][:8] if escalacao['ponta_dir'] else '-----'}
    ({escalacao['ponta_esq']['habilidade']}%)                  ({escalacao['ponta_dir']['habilidade']}%)

         {escalacao['atacante1']['nome'][:8] if escalacao['atacante1'] else '-----'}    {escalacao['atacante2']['nome'][:8] if escalacao['atacante2'] else '-----'}
         ({escalacao['atacante1']['habilidade']}%)  ({escalacao['atacante2']['habilidade']}%)
```
        """
        
        embed.add_field(name="🏟️ Formação Tática", value=formacao, inline=False)
        
        # Calcula força do time
        forca_total = sum(j['habilidade'] for j in jogadores_escalados) / len(jogadores_escalados)
        embed.add_field(name="💪 Força do Time", value=f"{forca_total:.1f}%", inline=True)
        embed.add_field(name="👥 Jogadores Escalados", value=f"{len(jogadores_escalados)}/11", inline=True)
        
        # Status da escalação
        if len(jogadores_escalados) == 11:
            embed.add_field(name="✅ Status", value="Time Completo!", inline=True)
        else:
            embed.add_field(name="⚠️ Status", value="Time Incompleto", inline=True)
    
    # Estatísticas do jogador
    embed.add_field(
        name="📊 Estatísticas", 
        value=f"🏆 {user_data['vitorias']}V | ❌ {user_data['derrotas']}D | 🤝 {user_data['empates']}E",
        inline=False
    )
    
    embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else None)
    embed.set_footer(text=f"💰 Dinheiro: R$ {user_data['dinheiro']:,}")
    
    await ctx.send(embed=embed)

# Comando criar jogador melhorado com modal
@bot.command(name='criar_jogador')
async def criar_jogador(ctx):
    """Cria um jogador personalizado usando modal (apenas 1 por pessoa)"""
    if not await verificar_time_obrigatorio(ctx):
        return
        
    user_data = vados.get_user_data(ctx.author.id)
    
    if user_data['jogadores_criados'] >= 1:
        embed = discord.Embed(
            title="❌ Limite Atingido",
            description="Você já criou seu jogador personalizado!\nCada jogador pode criar apenas 1 jogador.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="⭐ Criar Seu Jogador Único",
        description="Use o modal para criar seu jogador personalizado com segurança!",
        color=0x0099ff
    )
    embed.add_field(
        name="📋 Informações:",
        value="• Apenas 1 jogador por conta\n• Nome será verificado por palavrões\n• Posição será corrigida automaticamente\n• Habilidade inicial aleatória (45-60%)",
        inline=False
    )
    
    view = CriarJogadorView(vados, ctx.author)
    await ctx.send(embed=embed, view=view)

class CriarJogadorView(discord.ui.View):
    def __init__(self, vados_instance, author):
        super().__init__(timeout=300)
        self.vados = vados_instance
        self.author = author
    
    @discord.ui.button(label="⭐ Criar Jogador", style=discord.ButtonStyle.primary, emoji="⭐")
    async def criar_jogador(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Apenas quem solicitou pode criar!", ephemeral=True)
            return
        
        modal = CriarJogadorModal(self.vados, self.author)
        await interaction.response.send_modal(modal)

# Comando olheiro melhorado - apenas 1 jogador
@bot.command(name='olheiro')
async def olheiro(ctx):
    """Descubra UM jogador disponível no mercado"""
    if not await verificar_time_obrigatorio(ctx):
        return
        
    user_data = vados.get_user_data(ctx.author.id)
    
    # Seleciona UM jogador aleatório baseado na raridade
    chances = []
    for jogador in JOGADORES_OLHEIRO:
        # Quanto maior a habilidade, menor a chance
        chance = max(5, 105 - jogador['habilidade'])
        chances.extend([jogador] * chance)
    
    jogador_encontrado = random.choice(chances)
    
    # Determina raridade baseada na habilidade
    if jogador_encontrado['habilidade'] >= 95:
        raridade = "🌟 LENDÁRIO"
        cor = 0xffd700
    elif jogador_encontrado['habilidade'] >= 90:
        raridade = "💎 ÉPICO"
        cor = 0x9932cc
    elif jogador_encontrado['habilidade'] >= 80:
        raridade = "🔵 RARO"
        cor = 0x0099ff
    else:
        raridade = "⚪ COMUM"
        cor = 0x808080
    
    embed = discord.Embed(
        title="🔍 Relatório do Olheiro",
        description=f"**{raridade}** jogador foi encontrado no mercado!",
        color=cor
    )
    
    embed.add_field(name="👤 Nome", value=f"**{jogador_encontrado['nome']}**", inline=True)
    embed.add_field(name="⚽ Posição", value=jogador_encontrado['posicao'], inline=True)
    embed.add_field(name="📊 Over", value=jogador_encontrado['over'], inline=True)
    embed.add_field(name="🎯 Habilidade", value=f"{jogador_encontrado['habilidade']}%", inline=True)
    embed.add_field(name="💰 Valor de Mercado", value=f"R$ {jogador_encontrado['valor_mercado']:,}", inline=True)
    embed.add_field(name="💳 Seu Dinheiro", value=f"R$ {user_data['dinheiro']:,}", inline=True)
    
    # Adiciona informações extras baseadas na habilidade
    if jogador_encontrado['habilidade'] >= 90:
        embed.add_field(name="📝 Análise", value="⭐ Jogador de elite! Investimento garantido.", inline=False)
    elif jogador_encontrado['habilidade'] >= 80:
        embed.add_field(name="📝 Análise", value="🎯 Bom jogador, pode fazer a diferença no time.", inline=False)
    else:
        embed.add_field(name="📝 Análise", value="💪 Jogador promissor para começar.", inline=False)
    
    embed.set_footer(text="💡 Use os botões abaixo para negociar este jogador!")
    
    view = OlheiroView(jogador_encontrado, user_data, vados, ctx.author)
    await ctx.send(embed=embed, view=view)

class OlheiroView(discord.ui.View):
    def __init__(self, jogador, user_data, vados_instance, author):
        super().__init__(timeout=300)
        self.jogador = jogador
        self.user_data = user_data
        self.vados = vados_instance
        self.author = author
    
    @discord.ui.button(label="💰 Comprar Jogador", style=discord.ButtonStyle.success, emoji="💰")
    async def comprar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Apenas quem usou o comando pode negociar!", ephemeral=True)
            return
            
        if self.user_data['dinheiro'] >= self.jogador['valor_mercado']:
            self.user_data['dinheiro'] -= self.jogador['valor_mercado']
            novo_jogador = {
                'nome': self.jogador['nome'],
                'posicao': self.jogador['posicao'],
                'habilidade': self.jogador['habilidade'],
                'over': self.jogador['over'],
                'tipo': 'comprado'
            }
            self.user_data['jogadores'].append(novo_jogador)
            await self.vados.save_data()
            
            embed = discord.Embed(
                title="🎉 Transferência Concluída!",
                description=f"✅ **{self.jogador['nome']}** foi contratado com sucesso!",
                color=0x00ff00
            )
            embed.add_field(name="⚽ Jogador", value=self.jogador['nome'], inline=True)
            embed.add_field(name="📍 Posição", value=self.jogador['posicao'], inline=True)
            embed.add_field(name="🎯 Habilidade", value=f"{self.jogador['habilidade']}%", inline=True)
            embed.add_field(name="💸 Valor Pago", value=f"R$ {self.jogador['valor_mercado']:,}", inline=True)
            embed.add_field(name="💰 Dinheiro Restante", value=f"R$ {self.user_data['dinheiro']:,}", inline=True)
            embed.add_field(name="📋 Status", value="Adicionado ao Elenco", inline=True)
            embed.set_footer(text="🌟 Jogador permanente adicionado ao seu elenco!")
            
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title="💸 Fundos Insuficientes",
                description=f"❌ Você precisa de **R$ {self.jogador['valor_mercado']:,}**\n💰 Você possui: **R$ {self.user_data['dinheiro']:,}**\n💡 Faltam: **R$ {self.jogador['valor_mercado'] - self.user_data['dinheiro']:,}**",
                color=0xff0000
            )
            embed.add_field(name="💡 Dicas para Ganhar Dinheiro:", value="• Participe de confrontos (vitória = R$ 5,000)\n• Empates também dão R$ 2,000\n• Use `-confronto @usuário` para desafiar", inline=False)
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🤝 Empréstimo (1 jogo)", style=discord.ButtonStyle.secondary, emoji="🤝")
    async def emprestar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Apenas quem usou o comando pode negociar!", ephemeral=True)
            return
            
        preco_emprestimo = self.jogador['valor_mercado'] // 4
        
        if self.user_data['dinheiro'] >= preco_emprestimo:
            self.user_data['dinheiro'] -= preco_emprestimo
            
            user_id = str(interaction.user.id)
            if user_id not in self.vados.emprestimos:
                self.vados.emprestimos[user_id] = []
            
            emprestimo = {
                'nome': self.jogador['nome'],
                'posicao': self.jogador['posicao'],
                'habilidade': self.jogador['habilidade'],
                'over': self.jogador['over'],
                'partidas_restantes': 1
            }
            
            self.vados.emprestimos[user_id].append(emprestimo)
            await self.vados.save_data()
            
            embed = discord.Embed(
                title="🤝 Empréstimo Acordado!",
                description=f"✅ **{self.jogador['nome']}** foi emprestado por 1 partida!",
                color=0x00ff00
            )
            embed.add_field(name="⚽ Jogador", value=self.jogador['nome'], inline=True)
            embed.add_field(name="📍 Posição", value=self.jogador['posicao'], inline=True)
            embed.add_field(name="🎯 Habilidade", value=f"{self.jogador['habilidade']}%", inline=True)
            embed.add_field(name="💸 Valor do Empréstimo", value=f"R$ {preco_emprestimo:,}", inline=True)
            embed.add_field(name="💰 Dinheiro Restante", value=f"R$ {self.user_data['dinheiro']:,}", inline=True)
            embed.add_field(name="⏰ Duração", value="1 Partida", inline=True)
            embed.add_field(name="⚠️ Importante:", value="O jogador retornará automaticamente após 1 confronto!", inline=False)
            embed.set_footer(text="🤝 Jogador temporário adicionado! Use -elenco para ver.")
            
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title="💸 Fundos Insuficientes para Empréstimo",
                description=f"❌ Você precisa de **R$ {preco_emprestimo:,}** para o empréstimo\n💰 Você possui: **R$ {self.user_data['dinheiro']:,}**\n💡 Faltam: **R$ {preco_emprestimo - self.user_data['dinheiro']:,}**",
                color=0xff0000
            )
            embed.add_field(name="💰 Empréstimo vs Compra:", value=f"• **Empréstimo:** R$ {preco_emprestimo:,} (1 jogo)\n• **Compra:** R$ {self.jogador['valor_mercado']:,} (permanente)", inline=False)
            await interaction.response.edit_message(embed=embed, view=self)

# Comando elenco melhorado
@bot.command(name='elenco')
async def elenco(ctx, usuario: discord.Member = None):
    """Visualiza o elenco completo de um jogador"""
    if not await verificar_time_obrigatorio(ctx):
        return
        
    if usuario is None:
        usuario = ctx.author
    
    user_data = vados.get_user_data(usuario.id)
    
    # Nome do time
    nome_time = "Time sem nome"
    if user_data['time']:
        nome_time = f"{user_data['time']['nome']} ({user_data['time']['sigla']})"
    
    embed = discord.Embed(
        title=f"📋 Elenco do {nome_time}",
        color=0x0099ff
    )
    
    if not user_data['jogadores']:
        embed.description = "❌ Elenco vazio!\n💡 Use `-olheiro` para contratar jogadores ou `-criar_jogador` para criar um."
        embed.color = 0xff9900
        await ctx.send(embed=embed)
        return
    
    # Agrupa por posição
    posicoes = {}
    for jogador in user_data['jogadores']:
        pos = jogador['posicao']
        if pos not in posicoes:
            posicoes[pos] = []
        posicoes[pos].append(jogador)
    
    # Adiciona jogadores por posição
    for posicao, jogadores in posicoes.items():
        jogadores_texto = []
        for jogador in jogadores:
            emoji = "⭐" if jogador['tipo'] == 'criado' else "💰"
            jogadores_texto.append(f"{emoji} **{jogador['nome']}** - {jogador['habilidade']}% (Over: {jogador['over']})")
        
        embed.add_field(
            name=f"⚽ {posicao} ({len(jogadores)})",
            value="\n".join(jogadores_texto),
            inline=False
        )
    
    # Jogadores emprestados
    user_id = str(usuario.id)
    if user_id in vados.emprestimos and vados.emprestimos[user_id]:
        emprestados_texto = []
        for emp in vados.emprestimos[user_id]:
            emprestados_texto.append(f"🤝 **{emp['nome']}** - {emp['habilidade']}% ({emp['partidas_restantes']} jogo restante)")
        
        embed.add_field(
            name="🤝 Emprestados",
            value="\n".join(emprestados_texto),
            inline=False
        )
    
    # Estatísticas do elenco
    total_jogadores = len(user_data['jogadores'])
    media_habilidade = sum(j['habilidade'] for j in user_data['jogadores']) / total_jogadores
    
    embed.add_field(name="👥 Total de Jogadores", value=total_jogadores, inline=True)
    embed.add_field(name="📊 Média de Habilidade", value=f"{media_habilidade:.1f}%", inline=True)
    embed.add_field(name="💰 Patrimônio", value=f"R$ {user_data['dinheiro']:,}", inline=True)
    
    embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else None)
    embed.set_footer(text="⭐ = Criado | 💰 = Comprado | 🤝 = Emprestado")
    
    await ctx.send(embed=embed)

# Comando escalar com Select Menu
@bot.command(name='escalar')
async def escalar(ctx):
    """Interface moderna para escalar seu time"""
    if not await verificar_time_obrigatorio(ctx):
        return
        
    user_data = vados.get_user_data(ctx.author.id)
    
    if not user_data['jogadores']:
        embed = discord.Embed(
            title="❌ Elenco Vazio",
            description="Você precisa ter jogadores para escalar!\n💡 Use `-olheiro` ou `-criar_jogador` primeiro.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="⚽ Central de Escalação",
        description="Escolha uma posição para escalar um jogador:",
        color=0x0099ff
    )
    
    # Mostra escalação atual
    escalacao_atual = ""
    for pos, jogador in user_data['escalacao'].items():
        if jogador:
            escalacao_atual += f"✅ **{pos.replace('_', ' ').title()}**: {jogador['nome']} ({jogador['habilidade']}%)\n"
        else:
            escalacao_atual += f"❌ **{pos.replace('_', ' ').title()}**: *Vago*\n"
    
    embed.add_field(name="📋 Escalação Atual", value=escalacao_atual, inline=False)
    
    view = EscalacaoSelectView(user_data, vados, ctx.author)
    await ctx.send(embed=embed, view=view)

class EscalacaoSelectView(discord.ui.View):
    def __init__(self, user_data, vados_instance, author):
        super().__init__(timeout=300)
        self.user_data = user_data
        self.vados = vados_instance
        self.author = author
        
        # Select para posições
        self.add_item(PosicaoSelect(user_data, vados_instance, author))

class PosicaoSelect(discord.ui.Select):
    def __init__(self, user_data, vados_instance, author):
        self.user_data = user_data
        self.vados = vados_instance
        self.author = author
        
        options = [
            discord.SelectOption(label="🥅 Goleiro", value="goleiro", emoji="🥅"),
            discord.SelectOption(label="🛡️ Zagueiro 1", value="zagueiro1", emoji="🛡️"),
            discord.SelectOption(label="🛡️ Zagueiro 2", value="zagueiro2", emoji="🛡️"),
            discord.SelectOption(label="◀️ Lateral Esquerdo", value="lateral_esq", emoji="◀️"),
            discord.SelectOption(label="▶️ Lateral Direito", value="lateral_dir", emoji="▶️"),
            discord.SelectOption(label="⚙️ Volante", value="volante", emoji="⚙️"),
            discord.SelectOption(label="🎯 Meia", value="meia", emoji="🎯"),
            discord.SelectOption(label="◀️ Ponta Esquerda", value="ponta_esq", emoji="◀️"),
            discord.SelectOption(label="▶️ Ponta Direita", value="ponta_dir", emoji="▶️"),
            discord.SelectOption(label="⚽ Atacante 1", value="atacante1", emoji="⚽"),
            discord.SelectOption(label="⚽ Atacante 2", value="atacante2", emoji="⚽"),
        ]
        
        super().__init__(placeholder="Escolha uma posição para escalar...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Apenas quem usou o comando pode escalar!", ephemeral=True)
            return
            
        posicao = self.values[0]
        
        # Cria select para jogadores
        view = JogadorSelectView(self.user_data, self.vados, posicao, self.author)
        
        embed = discord.Embed(
            title=f"⚽ Escalando {posicao.replace('_', ' ').title()}",
            description="Escolha um jogador do seu elenco:",
            color=0x0099ff
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class JogadorSelectView(discord.ui.View):
    def __init__(self, user_data, vados_instance, posicao, author):
        super().__init__(timeout=300)
        self.user_data = user_data
        self.vados = vados_instance
        self.posicao = posicao
        self.author = author
        
        # Select para jogadores
        self.add_item(JogadorSelect(user_data, vados_instance, posicao, author))
        
        # Botão voltar
        voltar_btn = discord.ui.Button(label="← Voltar", style=discord.ButtonStyle.secondary)
        voltar_btn.callback = self.voltar
        self.add_item(voltar_btn)
    
    async def voltar(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Apenas quem usou o comando pode navegar!", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="⚽ Central de Escalação",
            description="Escolha uma posição para escalar um jogador:",
            color=0x0099ff
        )
        
        view = EscalacaoSelectView(self.user_data, self.vados, self.author)
        await interaction.response.edit_message(embed=embed, view=view)

class JogadorSelect(discord.ui.Select):
    def __init__(self, user_data, vados_instance, posicao, author):
        self.user_data = user_data
        self.vados = vados_instance
        self.posicao = posicao
        self.author = author
        
        options = []
        
        # Lista de jogadores já escalados
        jogadores_escalados = []
        for pos, jogador in user_data['escalacao'].items():
            if jogador and pos != posicao:  # Permite reescalar a mesma posição
                jogadores_escalados.append(jogador['nome'])
        
        # Adiciona jogadores próprios (apenas os não escalados)
        for jogador in user_data['jogadores'][:20]:  # Máximo 20
            if jogador['nome'] not in jogadores_escalados:
                tipo = jogador.get('tipo', 'comprado')
                emoji = "⭐" if tipo == 'criado' else "💰"
                options.append(discord.SelectOption(
                    label=f"{jogador['nome']} - {jogador['habilidade']}%",
                    value=f"proprio_{jogador['nome']}",
                    emoji=emoji,
                    description=f"{jogador['posicao']} | Over: {jogador['over']}"
                ))
        
        # Adiciona jogadores emprestados (apenas os não escalados)
        user_id = str(author.id)
        if hasattr(vados_instance, 'emprestimos') and user_id in vados_instance.emprestimos:
            for jogador in vados_instance.emprestimos[user_id]:
                if jogador['nome'] not in jogadores_escalados:
                    options.append(discord.SelectOption(
                        label=f"{jogador['nome']} (EMP) - {jogador['habilidade']}%",
                        value=f"emprestado_{jogador['nome']}",
                        emoji="🤝",
                        description=f"{jogador['posicao']} | {jogador['partidas_restantes']} jogo restante"
                    ))
        
        if not options:
            options.append(discord.SelectOption(label="Nenhum jogador disponível", value="vazio"))
        
        super().__init__(placeholder="Escolha um jogador...", options=options[:25])  # Discord limit
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Apenas quem usou o comando pode escalar!", ephemeral=True)
            return
            
        if self.values[0] == "vazio":
            await interaction.response.send_message("❌ Nenhum jogador disponível!", ephemeral=True)
            return
        
        tipo, nome = self.values[0].split("_", 1)
        
        # Encontra o jogador
        jogador_escalado = None
        if tipo == "proprio":
            for jogador in self.user_data['jogadores']:
                if jogador['nome'] == nome:
                    jogador_escalado = jogador
                    break
        elif tipo == "emprestado":
            user_id = str(interaction.user.id)
            if user_id in self.vados.emprestimos:
                for jogador in self.vados.emprestimos[user_id]:
                    if jogador['nome'] == nome:
                        jogador_escalado = jogador
                        break
        
        if jogador_escalado:
            self.user_data['escalacao'][self.posicao] = jogador_escalado
            await self.vados.save_data()
            
            embed = discord.Embed(
                title="✅ Jogador Escalado!",
                description=f"**{jogador_escalado['nome']}** foi escalado para **{self.posicao.replace('_', ' ').title()}**!",
                color=0x00ff00
            )
            embed.add_field(name="⚽ Jogador", value=jogador_escalado['nome'], inline=True)
            embed.add_field(name="📍 Posição no Time", value=self.posicao.replace('_', ' ').title(), inline=True)
            embed.add_field(name="🎯 Habilidade", value=f"{jogador_escalado['habilidade']}%", inline=True)
            embed.add_field(name="📋 Posição Original", value=jogador_escalado['posicao'], inline=True)
            embed.add_field(name="📊 Over", value=jogador_escalado['over'], inline=True)
            tipo = jogador_escalado.get('tipo', 'comprado')
            embed.add_field(name="🌟 Tipo", value="Criado" if tipo == 'criado' else "Comprado", inline=True)
            
            embed.set_footer(text="✅ Escalação atualizada! Use -time para ver a formação completa.")
            
            await interaction.response.edit_message(embed=embed, view=None)

# Comando x1 melhorado com seleção de jogador
@bot.command(name='x1')
async def x1(ctx, oponente: discord.Member):
    """Desafio x1 - escolha seu jogador"""
    if not await verificar_time_obrigatorio(ctx):
        return
        
    if oponente.id == ctx.author.id:
        embed = discord.Embed(
            title="❌ Autodesafio Impossível",
            description="Você não pode desafiar a si mesmo!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_data = vados.get_user_data(ctx.author.id)
    oponente_data = vados.get_user_data(oponente.id)
    
    if not user_data['jogadores']:
        embed = discord.Embed(
            title="❌ Sem Jogadores",
            description="Você precisa ter pelo menos 1 jogador!\n💡 Use `-olheiro` para contratar jogadores.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if not oponente_data['jogadores']:
        embed = discord.Embed(
            title="❌ Oponente Sem Jogadores",
            description=f"{oponente.mention} precisa ter pelo menos 1 jogador!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Nomes dos times
    nome_time_desafiante = user_data['time']['sigla'] if user_data['time'] else ctx.author.display_name
    nome_time_oponente = oponente_data['time']['sigla'] if oponente_data['time'] else oponente.display_name
    
    embed = discord.Embed(
        title="⚡ Desafio X1",
        description=f"🔥 **{nome_time_desafiante}** desafiou **{nome_time_oponente}** para um X1!\n\n⚽ Escolha seu jogador para o duelo!",
        color=0xff9900
    )
    
    embed.set_footer(text="⏰ Ambos têm 5 minutos para escolher seus jogadores!")
    
    view = X1JogadorSelectView(ctx.author, oponente, user_data, oponente_data, vados)
    await ctx.send(embed=embed, view=view)

class X1JogadorSelectView(discord.ui.View):
    def __init__(self, desafiante, oponente, desafiante_data, oponente_data, vados_instance):
        super().__init__(timeout=300)
        self.desafiante = desafiante
        self.oponente = oponente
        self.desafiante_data = desafiante_data
        self.oponente_data = oponente_data
        self.vados = vados_instance
        self.jogador_desafiante = None
        self.jogador_oponente = None
        
        # Select para o desafiante
        self.add_item(JogadorX1Select(desafiante_data, desafiante, "desafiante", self))
        
        # Select para o oponente
        self.add_item(JogadorX1Select(oponente_data, oponente, "oponente", self))
    
    async def verificar_prontos(self, interaction):
        if self.jogador_desafiante and self.jogador_oponente:
            # Nomes dos times
            nome_time_desafiante = self.desafiante_data['time']['sigla'] if self.desafiante_data['time'] else self.desafiante.display_name
            nome_time_oponente = self.oponente_data['time']['sigla'] if self.oponente_data['time'] else self.oponente.display_name
            
            # Simula o X1 com eventos em tempo real
            embed_inicial = discord.Embed(
                title="⚡ X1 EM ANDAMENTO",
                description=f"🔥 **{nome_time_desafiante} x {nome_time_oponente}** - A partida está começando...",
                color=0xffff00
            )
            embed_inicial.add_field(name=f"⚡ {nome_time_desafiante}", value=f"{self.jogador_desafiante['nome']}", inline=True)
            embed_inicial.add_field(name="🆚", value="**VS**", inline=True)
            embed_inicial.add_field(name=f"⚡ {nome_time_oponente}", value=f"{self.jogador_oponente['nome']}", inline=True)
            
            await interaction.response.edit_message(embed=embed_inicial, view=None)
            
            # Simula eventos
            await self.simular_x1_eventos(interaction, self.jogador_desafiante, self.jogador_oponente, nome_time_desafiante, nome_time_oponente)

    async def simular_x1_eventos(self, interaction, jogador1, jogador2, time1, time2):
        eventos = []
        gols_jogador1 = 0
        gols_jogador2 = 0
        
        # Define se é goleiro
        is_goleiro1 = jogador1['posicao'].lower() == 'goleiro'
        is_goleiro2 = jogador2['posicao'].lower() == 'goleiro'
        
        # Simula eventos durante 5 minutos (representando tempo de jogo)
        for minuto in range(1, 6):
            await asyncio.sleep(2)  # Pausa entre eventos
            
            # Determina quem tem a ação baseado na habilidade
            if random.randint(1, 100) <= (jogador1['habilidade'] * 0.7):
                acao_jogador = jogador1
                defensor = jogador2
                atacante_num = 1
            else:
                acao_jogador = jogador2
                defensor = jogador1
                atacante_num = 2
            
            # Tipos de eventos baseados na posição
            evento_tipo = self.determinar_evento(acao_jogador, defensor)
            
            if evento_tipo == "gol":
                if atacante_num == 1:
                    gols_jogador1 += 1
                    if not is_goleiro1:
                        eventos.append(f"⚽ **GOL!** {acao_jogador['nome']} marca um golaço!")
                    else:
                        eventos.append(f"⚽ **GOL!** O goleiro {acao_jogador['nome']} surpreende e marca!")
                else:
                    gols_jogador2 += 1
                    if not is_goleiro2:
                        eventos.append(f"⚽ **GOL!** {acao_jogador['nome']} marca um golaço!")
                    else:
                        eventos.append(f"⚽ **GOL!** O goleiro {acao_jogador['nome']} surpreende e marca!")
            
            elif evento_tipo == "defesa":
                eventos.append(f"🛡️ {defensor['nome']} faz uma defesa espetacular!")
            
            elif evento_tipo == "bloqueio":
                eventos.append(f"🚫 {defensor['nome']} bloqueia o chute de {acao_jogador['nome']}!")
            
            elif evento_tipo == "contra_ataque":
                eventos.append(f"⚡ {acao_jogador['nome']} inicia um contra-ataque perigoso!")
            
            elif evento_tipo == "chute_fora":
                eventos.append(f"📤 {acao_jogador['nome']} chuta para fora por pouco!")
            
            # Atualiza o embed com os eventos
            embed_evento = discord.Embed(
                title=f"⚡ X1 - Minuto {minuto}",
                description=f"**{time1} {gols_jogador1} x {gols_jogador2} {time2}**",
                color=0x00ff00 if minuto == 5 else 0xffff00
            )
            
            embed_evento.add_field(
                name="📝 Último Evento",
                value=eventos[-1] if eventos else "Início da partida...",
                inline=False
            )
            
            if len(eventos) > 1:
                embed_evento.add_field(
                    name="📜 Eventos Anteriores",
                    value="\n".join(eventos[-3:-1]) if len(eventos) > 3 else "\n".join(eventos[:-1]),
                    inline=False
                )
            
            await interaction.edit_original_response(embed=embed_evento)
        
        # Resultado final
        await asyncio.sleep(2)
        resultado_embed = self.criar_embed_resultado_x1(gols_jogador1, gols_jogador2, jogador1, jogador2, eventos, time1, time2)
        
        # Atualiza dados dos jogadores
        if gols_jogador1 > gols_jogador2:
            self.desafiante_data['vitorias'] += 1
            self.oponente_data['derrotas'] += 1
            self.desafiante_data['dinheiro'] += 3000  # Prêmio menor para X1
        elif gols_jogador2 > gols_jogador1:
            self.oponente_data['vitorias'] += 1
            self.desafiante_data['derrotas'] += 1
            self.oponente_data['dinheiro'] += 3000
        else:
            self.desafiante_data['empates'] += 1
            self.oponente_data['empates'] += 1
            self.desafiante_data['dinheiro'] += 1500
            self.oponente_data['dinheiro'] += 1500
        
        await self.vados.save_data()
        await interaction.edit_original_response(embed=resultado_embed)
    
    def determinar_evento(self, atacante, defensor):
        # Probabilidades baseadas na diferença de habilidade
        diff_habilidade = atacante['habilidade'] - defensor['habilidade']
        
        # Ajusta probabilidades baseado na posição
        prob_gol = 30
        if atacante['posicao'].lower() in ['atacante', 'ponta']:
            prob_gol += 15
        elif atacante['posicao'].lower() == 'goleiro':
            prob_gol -= 20
        
        if defensor['posicao'].lower() in ['zagueiro', 'goleiro']:
            prob_gol -= 10
        
        # Ajusta pela diferença de habilidade
        prob_gol += diff_habilidade // 5
        prob_gol = max(5, min(prob_gol, 70))  # Entre 5% e 70%
        
        rand = random.randint(1, 100)
        
        if rand <= prob_gol:
            return "gol"
        elif rand <= prob_gol + 20:
            return "defesa"
        elif rand <= prob_gol + 35:
            return "bloqueio"
        elif rand <= prob_gol + 50:
            return "contra_ataque"
        else:
            return "chute_fora"
    
    def criar_embed_resultado_x1(self, gols1, gols2, jogador1, jogador2, eventos, time1, time2):
        embed = discord.Embed(
            title="🏁 X1 FINALIZADO!",
            color=0x00ff00
        )
        
        placar = f"**{time1}** {gols1} ⚽ {gols2} **{time2}**"
        embed.add_field(name="📊 Placar Final", value=placar, inline=False)
        
        if gols1 > gols2:
            embed.add_field(name="🏆 Vencedor", value=f"{self.desafiante.mention} ({time1}) 🎉", inline=True)
            embed.add_field(name="💰 Prêmio", value="R$ 3.000", inline=True)
            embed.color = 0x00ff00
        elif gols2 > gols1:
            embed.add_field(name="🏆 Vencedor", value=f"{self.oponente.mention} ({time2}) 🎉", inline=True)
            embed.add_field(name="💰 Prêmio", value="R$ 3.000", inline=True)
            embed.color = 0x00ff00
        else:
            embed.add_field(name="🤝 Resultado", value="Empate! Ambos recebem R$ 1.500", inline=False)
            embed.color = 0xffff00
        
        # Mostra eventos mais importantes
        eventos_importantes = [e for e in eventos if "GOL" in e]
        if eventos_importantes:
            embed.add_field(
                name="⚽ Gols da Partida",
                value="\n".join(eventos_importantes[-5:]),  # Últimos 5 gols
                inline=False
            )
        
        embed.set_footer(text="⚡ X1 finalizado! Use -stats para ver suas estatísticas.")
        
        return embed

class JogadorX1Select(discord.ui.Select):
    def __init__(self, user_data, user, tipo, parent_view):
        self.user_data = user_data
        self.user = user
        self.tipo = tipo
        self.parent_view = parent_view
        
        options = []
        
        # Adiciona jogadores do elenco
        for jogador in user_data['jogadores'][:20]:  # Máximo 20
            tipo_jogador = jogador.get('tipo', 'comprado')
            emoji = "⭐" if tipo_jogador == 'criado' else "💰"
            options.append(discord.SelectOption(
                label=f"{jogador['nome']} - {jogador['habilidade']}%",
                value=f"jogador_{jogador['nome']}",
                emoji=emoji,
                description=f"{jogador['posicao']} | Over: {jogador['over']}"
            ))
        
        # Adiciona jogadores emprestados
        user_id = str(user.id)
        if hasattr(parent_view.vados, 'emprestimos') and user_id in parent_view.vados.emprestimos:
            for jogador in parent_view.vados.emprestimos[user_id]:
                options.append(discord.SelectOption(
                    label=f"{jogador['nome']} (EMP) - {jogador['habilidade']}%",
                    value=f"emprestado_{jogador['nome']}",
                    emoji="🤝",
                    description=f"{jogador['posicao']} | {jogador['partidas_restantes']} jogo restante"
                ))
        
        if not options:
            options.append(discord.SelectOption(label="Nenhum jogador disponível", value="vazio"))
        
        placeholder = f"🎮 {user.display_name}, escolha seu jogador..."
        
        super().__init__(placeholder=placeholder, options=options[:25])  # Discord limit
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Apenas o jogador correspondente pode escolher!", ephemeral=True)
            return
            
        if self.values[0] == "vazio":
            await interaction.response.send_message("❌ Nenhum jogador disponível!", ephemeral=True)
            return
        
        # Encontra o jogador selecionado
        tipo_sel, nome = self.values[0].split("_", 1)
        jogador_selecionado = None
        
        if tipo_sel == "jogador":
            for jogador in self.user_data['jogadores']:
                if jogador['nome'] == nome:
                    jogador_selecionado = jogador
                    break
        elif tipo_sel == "emprestado":
            user_id = str(self.user.id)
            if user_id in self.parent_view.vados.emprestimos:
                for jogador in self.parent_view.vados.emprestimos[user_id]:
                    if jogador['nome'] == nome:
                        jogador_selecionado = jogador
                        break
        
        if jogador_selecionado:
            # Salva o jogador escolhido
            if self.tipo == "desafiante":
                self.parent_view.jogador_desafiante = jogador_selecionado
            else:
                self.parent_view.jogador_oponente = jogador_selecionado
            
            # Desabilita este select
            self.disabled = True
            self.placeholder = f"✅ {self.user.display_name}: {jogador_selecionado['nome']}"
            
            # Atualiza a mensagem
            nome_time_desafiante = self.parent_view.desafiante_data['time']['sigla'] if self.parent_view.desafiante_data['time'] else self.parent_view.desafiante.display_name
            nome_time_oponente = self.parent_view.oponente_data['time']['sigla'] if self.parent_view.oponente_data['time'] else self.parent_view.oponente.display_name
            
            embed = discord.Embed(
                title="⚡ Desafio X1 - Seleção de Jogadores",
                description=f"🔥 **{nome_time_desafiante}** vs **{nome_time_oponente}**",
                color=0xff9900
            )
            
            if self.parent_view.jogador_desafiante:
                embed.add_field(
                    name=f"✅ {nome_time_desafiante}",
                    value=f"{self.parent_view.jogador_desafiante['nome']}\n{self.parent_view.jogador_desafiante['habilidade']}% | {self.parent_view.jogador_desafiante['posicao']}",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"⏳ {nome_time_desafiante}",
                    value="Aguardando seleção...",
                    inline=True
                )
            
            embed.add_field(name="🆚", value="**VS**", inline=True)
            
            if self.parent_view.jogador_oponente:
                embed.add_field(
                    name=f"✅ {nome_time_oponente}",
                    value=f"{self.parent_view.jogador_oponente['nome']}\n{self.parent_view.jogador_oponente['habilidade']}% | {self.parent_view.jogador_oponente['posicao']}",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"⏳ {nome_time_oponente}",
                    value="Aguardando seleção...",
                    inline=True
                )
            
            if self.parent_view.jogador_desafiante and self.parent_view.jogador_oponente:
                embed.set_footer(text="🔥 Ambos jogadores selecionados! Iniciando X1...")
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
                await self.parent_view.verificar_prontos(interaction)
            else:
                embed.set_footer(text="⏰ Aguardando o outro jogador escolher...")
                await interaction.response.edit_message(embed=embed, view=self.parent_view)

# Comando confronto melhorado
@bot.command(name='confronto')
async def confronto(ctx, oponente: discord.Member):
    """Desafie outro usuário para um confronto épico"""
    if not await verificar_time_obrigatorio(ctx):
        return
        
    if oponente.id == ctx.author.id:
        embed = discord.Embed(
            title="❌ Autodesafio Impossível",
            description="Você não pode desafiar a si mesmo!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_data = vados.get_user_data(ctx.author.id)
    oponente_data = vados.get_user_data(oponente.id)
    
    # Verificar se oponente tem time
    if not oponente_data['time']:
        embed = discord.Embed(
            title="❌ Oponente Sem Time",
            description=f"{oponente.mention} precisa criar um time antes de aceitar confrontos!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Verifica escalações
    escalacao_completa = all(pos for pos in user_data['escalacao'].values())
    oponente_escalacao_completa = all(pos for pos in oponente_data['escalacao'].values())
    
    if not escalacao_completa:
        embed = discord.Embed(
            title="❌ Escalação Incompleta",
            description="Você precisa ter uma escalação completa!\n💡 Use `-escalar` para montar seu time.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if not oponente_escalacao_completa:
        embed = discord.Embed(
            title="❌ Oponente Sem Escalação",
            description=f"{oponente.mention} precisa ter uma escalação completa!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Nomes dos times
    nome_time_desafiante = user_data['time']['sigla'] if user_data['time'] else ctx.author.display_name
    nome_time_oponente = oponente_data['time']['sigla'] if oponente_data['time'] else oponente.display_name
    
    embed = discord.Embed(
        title="⚔️ Desafio de Confronto",
        description=f"🔥 **{nome_time_desafiante}** desafiou **{nome_time_oponente}** para um confronto épico!",
        color=0xff9900
    )
    
    # Calcula força dos times
    forca_desafiante = sum(j['habilidade'] for j in user_data['escalacao'].values()) / 11
    forca_oponente = sum(j['habilidade'] for j in oponente_data['escalacao'].values()) / 11
    
    embed.add_field(name=f"💪 {nome_time_desafiante}", value=f"Força: {forca_desafiante:.1f}%", inline=True)
    embed.add_field(name="🆚", value="**VS**", inline=True)
    embed.add_field(name=f"💪 {nome_time_oponente}", value=f"Força: {forca_oponente:.1f}%", inline=True)
    
    embed.set_footer(text="⏰ Oponente tem 5 minutos para responder!")
    
    view = ConfrontoView(ctx.author, oponente, user_data, oponente_data, vados)
    await ctx.send(embed=embed, view=view)

class ConfrontoView(discord.ui.View):
    def __init__(self, desafiante, oponente, desafiante_data, oponente_data, vados_instance):
        super().__init__(timeout=300)
        self.desafiante = desafiante
        self.oponente = oponente
        self.desafiante_data = desafiante_data
        self.oponente_data = oponente_data
        self.vados = vados_instance
    
    @discord.ui.button(label="✅ Aceitar Desafio", style=discord.ButtonStyle.success, emoji="⚔️")
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.oponente.id:
            await interaction.response.send_message("❌ Apenas o desafiado pode aceitar!", ephemeral=True)
            return
        
        # Nomes dos times
        nome_time_desafiante = self.desafiante_data['time']['sigla'] if self.desafiante_data['time'] else self.desafiante.display_name
        nome_time_oponente = self.oponente_data['time']['sigla'] if self.oponente_data['time'] else self.oponente.display_name
        
        # Inicia a partida com eventos em tempo real
        embed_inicial = discord.Embed(
            title="🏟️ PARTIDA EM ANDAMENTO",
            description=f"⚽ **{nome_time_desafiante} x {nome_time_oponente}** - A partida está começando...",
            color=0xffff00
        )
        embed_inicial.add_field(name=f"🔥 {nome_time_desafiante}", value="Preparando time...", inline=True)
        embed_inicial.add_field(name="🆚", value="**VS**", inline=True)
        embed_inicial.add_field(name=f"🔥 {nome_time_oponente}", value="Preparando time...", inline=True)
        
        await interaction.response.edit_message(embed=embed_inicial, view=None)
        
        # Simula eventos em tempo real
        await self.simular_confronto_eventos(interaction, nome_time_desafiante, nome_time_oponente)
        
        # Remove jogadores emprestados
        self.remover_emprestados(str(self.desafiante.id))
        self.remover_emprestados(str(self.oponente.id))
        
        await self.vados.save_data()
    
    @discord.ui.button(label="❌ Recusar", style=discord.ButtonStyle.danger, emoji="🚫")
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.oponente.id:
            await interaction.response.send_message("❌ Apenas o desafiado pode recusar!", ephemeral=True)
            return
        
        nome_time_desafiante = self.desafiante_data['time']['sigla'] if self.desafiante_data['time'] else self.desafiante.display_name
        nome_time_oponente = self.oponente_data['time']['sigla'] if self.oponente_data['time'] else self.oponente.display_name
        
        embed = discord.Embed(
            title="❌ Confronto Recusado",
            description=f"**{nome_time_oponente}** recusou o desafio de **{nome_time_desafiante}**.",
            color=0xff0000
        )
        embed.set_footer(text="🐔 Que pena! Talvez na próxima...")
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    def calcular_forca_time(self, escalacao):
        return sum(j['habilidade'] for j in escalacao.values()) / 11
    
    async def simular_confronto_eventos(self, interaction, time1, time2):
        eventos = []
        gols_desafiante = 0
        gols_oponente = 0
        
        escalacao_desafiante = self.desafiante_data['escalacao']
        escalacao_oponente = self.oponente_data['escalacao']
        
        # Simula 9 minutos de jogo com eventos
        for minuto in range(1, 10):
            await asyncio.sleep(3)  # Pausa entre eventos
            
            # Determina qual time tem a posse
            forca_desafiante = self.calcular_forca_time(escalacao_desafiante)
            forca_oponente = self.calcular_forca_time(escalacao_oponente)
            
            if random.randint(1, 100) <= (forca_desafiante / (forca_desafiante + forca_oponente)) * 100:
                time_atacante = "desafiante"
                escalacao_atacante = escalacao_desafiante
                escalacao_defensor = escalacao_oponente
                nome_time_atacante = time1
                nome_time_defensor = time2
            else:
                time_atacante = "oponente"
                escalacao_atacante = escalacao_oponente
                escalacao_defensor = escalacao_desafiante
                nome_time_atacante = time2
                nome_time_defensor = time1
            
            # Gera evento baseado nas posições dos jogadores
            evento = self.gerar_evento_confronto(escalacao_atacante, escalacao_defensor, nome_time_atacante, nome_time_defensor)
            eventos.append(f"⏱️ {minuto}' - {evento['texto']}")
            
            # Verifica se foi gol
            if evento['tipo'] == 'gol':
                if time_atacante == "desafiante":
                    gols_desafiante += 1
                else:
                    gols_oponente += 1
            
            # Atualiza embed com o evento
            embed_minuto = discord.Embed(
                title=f"🏟️ TEMPO REAL - {minuto}º Minuto",
                description=f"**{time1} {gols_desafiante} x {gols_oponente} {time2}**",
                color=0x00ff00 if evento['tipo'] == 'gol' else 0xffff00
            )
            
            embed_minuto.add_field(
                name="🔥 Último Lance",
                value=evento['texto'],
                inline=False
            )
            
            if len(eventos) > 1:
                eventos_recentes = eventos[-3:] if len(eventos) > 3 else eventos[:-1]
                embed_minuto.add_field(
                    name="📜 Lances Anteriores",
                    value="\n".join(eventos_recentes),
                    inline=False
                )
            
            await interaction.edit_original_response(embed=embed_minuto)
        
        # Resultado final
        await asyncio.sleep(2)
        embed_final = self.criar_embed_resultado_eventos(gols_desafiante, gols_oponente, eventos, time1, time2)
        
        # Atualiza estatísticas e dinheiro
        if gols_desafiante > gols_oponente:
            self.desafiante_data['vitorias'] += 1
            self.oponente_data['derrotas'] += 1
            self.desafiante_data['dinheiro'] += 5000
        elif gols_oponente > gols_desafiante:
            self.oponente_data['vitorias'] += 1
            self.desafiante_data['derrotas'] += 1
            self.oponente_data['dinheiro'] += 5000
        else:
            self.desafiante_data['empates'] += 1
            self.oponente_data['empates'] += 1
            self.desafiante_data['dinheiro'] += 2000
            self.oponente_data['dinheiro'] += 2000
        
        await interaction.edit_original_response(embed=embed_final)
    
    def gerar_evento_confronto(self, escalacao_atacante, escalacao_defensor, nome_atacante, nome_defensor):
        # Seleciona jogadores baseado na probabilidade da posição
        posicoes_ataque = ['atacante1', 'atacante2', 'ponta_esq', 'ponta_dir', 'meia']
        posicoes_meio = ['volante', 'meia']
        posicoes_defesa = ['zagueiro1', 'zagueiro2', 'lateral_esq', 'lateral_dir', 'goleiro']
        
        # Jogador que inicia a jogada
        if random.randint(1, 100) <= 60:  # 60% chance de atacante
            posicoes_iniciais = posicoes_ataque
        else:  # 40% chance de meio-campo
            posicoes_iniciais = posicoes_meio
        
        jogador_atacante = None
        for pos in posicoes_iniciais:
            if escalacao_atacante.get(pos):
                jogador_atacante = escalacao_atacante[pos]
                break
        
        if not jogador_atacante:
            # Fallback para qualquer jogador
            jogador_atacante = next(iter(escalacao_atacante.values()))
        
        # Determina tipo de evento baseado na habilidade
        rand = random.randint(1, 100)
        habilidade_atacante = jogador_atacante['habilidade']
        
        if rand <= 25 + (habilidade_atacante - 75):  # Gol
            return {
                'tipo': 'gol',
                'texto': f"⚽ **GOL DE {jogador_atacante['nome'].upper()}!** Que jogada espetacular do {nome_atacante}!"
            }
        elif rand <= 45:  # Defesa
            # Seleciona defensor
            defensor = self.selecionar_defensor(escalacao_defensor, jogador_atacante)
            if defensor['posicao'].lower() == 'goleiro':
                return {
                    'tipo': 'defesa',
                    'texto': f"🥅 **DEFESA!** {defensor['nome']} faz uma defesa espetacular! {jogador_atacante['nome']} quase marcou!"
                }
            else:
                return {
                    'tipo': 'bloqueio',
                    'texto': f"🛡️ **BLOQUEIO!** {defensor['nome']} bloqueia o chute perigoso de {jogador_atacante['nome']}!"
                }
        elif rand <= 65:  # Contra-ataque
            meio_campista = escalacao_defensor.get('meia') or escalacao_defensor.get('volante')
            if meio_campista:
                return {
                    'tipo': 'contra_ataque',
                    'texto': f"⚡ **CONTRA-ATAQUE!** {meio_campista['nome']} rouba a bola e inicia jogada rápida para o {nome_defensor}!"
                }
            else:
                return {
                    'tipo': 'recuperacao',
                    'texto': f"🔄 **RECUPERAÇÃO!** {nome_defensor} recupera a posse de bola no meio-campo!"
                }
        elif rand <= 80:  # Chute defendido
            return {
                'tipo': 'chute_defendido',
                'texto': f"📤 **PARA FORA!** {jogador_atacante['nome']} chuta forte, mas a bola passa raspando a trave!"
            }
        else:  # Falta ou lateral
            return {
                'tipo': 'falta',
                'texto': f"⚠️ **FALTA!** Jogada dura sobre {jogador_atacante['nome']}, o árbitro marca falta para o {nome_atacante}!"
            }
    
    def selecionar_defensor(self, escalacao_defensor, jogador_atacante):
        pos_atacante = jogador_atacante['posicao'].lower()
        
        # Lógica de quem defende baseado na posição do atacante
        if 'atacante' in pos_atacante or 'ponta' in pos_atacante:
            # Atacantes normalmente enfrentam zagueiros
            defensores_possiveis = ['zagueiro1', 'zagueiro2', 'goleiro']
        elif 'meia' in pos_atacante or 'meio' in pos_atacante:
            # Meias enfrentam volantes ou zagueiros
            defensores_possiveis = ['volante', 'zagueiro1', 'zagueiro2']
        else:
            # Outros enfrentam laterais ou zagueiros
            defensores_possiveis = ['lateral_esq', 'lateral_dir', 'zagueiro1', 'zagueiro2']
        
        # Seleciona defensor disponível
        for pos in defensores_possiveis:
            if escalacao_defensor.get(pos):
                return escalacao_defensor[pos]
        
        # Fallback para goleiro
        return escalacao_defensor.get('goleiro', next(iter(escalacao_defensor.values())))
    
    def criar_embed_resultado_eventos(self, gols_desafiante, gols_oponente, eventos, time1, time2):
        embed = discord.Embed(
            title="🏁 PARTIDA FINALIZADA!",
            color=0x00ff00
        )
        
        placar = f"**{time1}** {gols_desafiante} ⚽ {gols_oponente} **{time2}**"
        embed.add_field(name="📊 Placar Final", value=placar, inline=False)
        
        if gols_desafiante > gols_oponente:
            embed.add_field(name="🏆 Vencedor", value=f"{self.desafiante.mention} ({time1}) 🎉", inline=True)
            embed.add_field(name="💰 Prêmio", value="R$ 5.000", inline=True)
            embed.color = 0x00ff00
        elif gols_oponente > gols_desafiante:
            embed.add_field(name="🏆 Vencedor", value=f"{self.oponente.mention} ({time2}) 🎉", inline=True)
            embed.add_field(name="💰 Prêmio", value="R$ 5.000", inline=True)
            embed.color = 0x00ff00
        else:
            embed.add_field(name="🤝 Resultado", value="Empate! Ambos recebem R$ 2.000", inline=False)
            embed.color = 0xffff00
        
        # Mostra gols da partida
        gols_eventos = [e for e in eventos if "GOL" in e.upper()]
        if gols_eventos:
            embed.add_field(
                name="⚽ Gols da Partida",
                value="\n".join(gols_eventos),
                inline=False
            )
        
        # Mostra lances importantes
        lances_importantes = [e for e in eventos if any(palavra in e.upper() for palavra in ["DEFESA", "BLOQUEIO", "CONTRA-ATAQUE"])]
        if lances_importantes:
            embed.add_field(
                name="🔥 Lances de Destaque",
                value="\n".join(lances_importantes[-3:]),  # Últimos 3 lances importantes
                inline=False
            )
        
        embed.set_footer(text="🏟️ Que partida! Use -stats para ver suas estatísticas atualizadas.")
        
        return embed
    
    def remover_emprestados(self, user_id):
        if user_id in self.vados.emprestimos:
            emprestimos = self.vados.emprestimos[user_id][:]
            for i, emp in enumerate(emprestimos):
                emp['partidas_restantes'] -= 1
                if emp['partidas_restantes'] <= 0:
                    self.vados.emprestimos[user_id].pop(i)
            
            if not self.vados.emprestimos[user_id]:
                del self.vados.emprestimos[user_id]

# Comando stats melhorado
@bot.command(name='stats')
async def stats(ctx, usuario: discord.Member = None):
    """Visualiza estatísticas detalhadas de um jogador"""
    if not await verificar_time_obrigatorio(ctx):
        return
        
    if usuario is None:
        usuario = ctx.author
    
    user_data = vados.get_user_data(usuario.id)
    
    # Nome do time
    nome_time = "Time sem nome"
    if user_data['time']:
        nome_time = f"{user_data['time']['nome']} ({user_data['time']['sigla']})"
    
    embed = discord.Embed(
        title=f"📊 Estatísticas do {nome_time}",
        color=0x0099ff
    )
    
    total_jogos = user_data['vitorias'] + user_data['derrotas'] + user_data['empates']
    
    # Estatísticas principais
    embed.add_field(name="🏆 Vitórias", value=user_data['vitorias'], inline=True)
    embed.add_field(name="❌ Derrotas", value=user_data['derrotas'], inline=True)
    embed.add_field(name="🤝 Empates", value=user_data['empates'], inline=True)
    
    embed.add_field(name="🎮 Total de Jogos", value=total_jogos, inline=True)
    embed.add_field(name="💰 Dinheiro", value=f"R$ {user_data['dinheiro']:,}", inline=True)
    embed.add_field(name="⚽ Jogadores no Elenco", value=len(user_data['jogadores']), inline=True)
    
    if total_jogos > 0:
        aproveitamento = (user_data['vitorias'] / total_jogos) * 100
        embed.add_field(name="📈 Aproveitamento", value=f"{aproveitamento:.1f}%", inline=True)
        
        # Determina rank baseado no aproveitamento
        if aproveitamento >= 80:
            rank = "🏆 Lendário"
            cor = 0xffd700
        elif aproveitamento >= 60:
            rank = "💎 Experiente"
            cor = 0x9932cc
        elif aproveitamento >= 40:
            rank = "🔵 Intermediário"
            cor = 0x0099ff
        else:
            rank = "⚪ Iniciante"
            cor = 0x808080
        
        embed.add_field(name="🎖️ Classificação", value=rank, inline=True)
        embed.color = cor
    
    # Informações do elenco
    if user_data['jogadores']:
        media_habilidade = sum(j['habilidade'] for j in user_data['jogadores']) / len(user_data['jogadores'])
        embed.add_field(name="📊 Média do Elenco", value=f"{media_habilidade:.1f}%", inline=True)
    
    embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else None)
    embed.set_footer(text="🌟 Continue jogando para melhorar suas estatísticas!")
    
    await ctx.send(embed=embed)

# Comandos Admin (apenas owner)
@bot.command(name='add_dinheiro')
async def add_dinheiro(ctx, usuario: discord.Member, quantidade: int):
    """Adiciona dinheiro a um usuário (apenas owner)"""
    if ctx.author.id != OWNER_ID:
        embed = discord.Embed(
            title="🚫 Acesso Negado",
            description="Apenas o owner do bot pode usar este comando!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_data = vados.get_user_data(usuario.id)
    user_data['dinheiro'] += quantidade
    await vados.save_data()
    
    embed = discord.Embed(
        title="💰 Dinheiro Adicionado!",
        description=f"**R$ {quantidade:,}** foram adicionados para {usuario.mention}",
        color=0x00ff00
    )
    embed.add_field(name="👤 Usuário", value=usuario.mention, inline=True)
    embed.add_field(name="💵 Valor Adicionado", value=f"R$ {quantidade:,}", inline=True)
    embed.add_field(name="💰 Saldo Atual", value=f"R$ {user_data['dinheiro']:,}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='add_todos_jogadores')
async def add_todos_jogadores(ctx, usuario: discord.Member):
    """Adiciona todos os jogadores disponíveis a um usuário (apenas owner)"""
    if ctx.author.id != OWNER_ID:
        embed = discord.Embed(
            title="🚫 Acesso Negado",
            description="Apenas o owner do bot pode usar este comando!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_data = vados.get_user_data(usuario.id)
    
    # Adiciona todos os jogadores do olheiro
    for jogador_olheiro in JOGADORES_OLHEIRO:
        jogador = {
            'nome': jogador_olheiro['nome'],
            'posicao': jogador_olheiro['posicao'],
            'habilidade': jogador_olheiro['habilidade'],
            'over': jogador_olheiro['over'],
            'tipo': 'admin_grant'
        }
        user_data['jogadores'].append(jogador)
    
    await vados.save_data()
    
    embed = discord.Embed(
        title="⭐ Todos os Jogadores Adicionados!",
        description=f"**{len(JOGADORES_OLHEIRO)}** jogadores foram adicionados para {usuario.mention}",
        color=0x00ff00
    )
    embed.add_field(name="👤 Usuário", value=usuario.mention, inline=True)
    embed.add_field(name="⚽ Jogadores Adicionados", value=len(JOGADORES_OLHEIRO), inline=True)
    embed.add_field(name="📋 Total no Elenco", value=len(user_data['jogadores']), inline=True)
    embed.set_footer(text="🌟 Todos os jogadores foram concedidos pelo administrador!")
    
    await ctx.send(embed=embed)

# Comandos de segurança
@bot.command(name='sec_config')
async def config_security(ctx, setting: str = None, value: str = None):
    """Configura o sistema de segurança (apenas owner)"""
    # Verifica se é o owner do bot
    if ctx.author.id != OWNER_ID:
        embed = discord.Embed(
            title="🚫 Acesso Negado",
            description="Apenas o owner do bot pode usar este comando!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
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
            value="`-sec_config auto_ban_bots true/false`\n`-sec_config role_delete_punishment remove_roles/ban`\n`-sec_config logs_channel_name nome_do_canal`",
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

@bot.command(name='sec_restore')
async def restore_roles(ctx, user_id: str):
    """Restaura os cargos de um usuário removido pelo sistema (apenas owner)"""
    # Verifica se é o owner do bot
    if ctx.author.id != OWNER_ID:
        embed = discord.Embed(
            title="🚫 Acesso Negado",
            description="Apenas o owner do bot pode usar este comando!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
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

@bot.command(name='sec_whitelist')
async def manage_whitelist(ctx, action: str = None, user_id: str = None):
    """Gerencia a whitelist de usuários autorizados (apenas owner)"""
    # Verifica se é o owner do bot
    if ctx.author.id != OWNER_ID:
        embed = discord.Embed(
            title="🚫 Acesso Negado",
            description="Apenas o owner do bot pode usar este comando!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
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
            value="`-sec_whitelist add <ID>`\n`-sec_whitelist remove <ID>`\n`-sec_whitelist list`",
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
        await ctx.send("❌ Uso: `-sec_whitelist add/remove <ID>`")

@bot.command(name='sec_status')
async def security_status(ctx):
    """Mostra o status do sistema de segurança"""
    # Verifica se é um dos servidores com segurança ativa
    if ctx.guild.id not in SECURITY_GUILD_IDS:
        embed = discord.Embed(
            title="🔒 Sistema de Segurança",
            description=f"❌ **Sistema de segurança INATIVO neste servidor.**\n\n✅ **Ativo nos servidores:** `{', '.join(map(str, SECURITY_GUILD_IDS))}`",
            color=0xff9900
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="🔒 Status do Sistema de Segurança",
        description=f"✅ **Ativo neste servidor:** `{ctx.guild.id}`",
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
    
    embed.set_footer(text="Sistema de Segurança Integrado")
    
    await ctx.send(embed=embed)

# Comando ajuda melhorado
@bot.command(name='ajuda')
async def ajuda(ctx):
    """Central de ajuda completa do MXP Football Manager"""
    # Verifica se é um dos servidores de segurança
    if ctx.guild and ctx.guild.id in SECURITY_GUILD_IDS:
        embed = discord.Embed(
            title="🔒 Sistema de Segurança - Ajuda",
            description="🛡️ **Sistema de Segurança Automático**\n\n❌ **Comandos de futebol não funcionam neste servidor.**",
            color=0xff0000
        )
        
        comandos_seguranca = {
            "🔒 **Sistema de Segurança**": [
                "`-sec_status` - Mostra status do sistema de segurança",
                "`-sec_config` - Configura proteções automáticas",
                "`-sec_restore <ID>` - Restaura cargos removidos",
            ],
            "ℹ️ **Informações**": [
                "`-ajuda` - Mostra esta central de comandos",
            ]
        }
        
        for categoria, lista_comandos in comandos_seguranca.items():
            embed.add_field(
                name=categoria,
                value="\n".join(lista_comandos),
                inline=False
            )
        
        embed.add_field(
            name="🔒 **PROTEÇÕES AUTOMÁTICAS ATIVAS**",
            value="• **Recriação Automática:** Canais/cargos deletados são recriados instantaneamente\n• **Exclusão de Canais:** Remove cargos + recria canal automaticamente\n• **Exclusão de Cargos:** Punição configurável + recria cargo\n• **Bots Invasores:** Banimento automático\n• **Logs Detalhados:** Registra recriações e todas as ações\n• **Whitelist:** Usuários autorizados podem deletar sem recriação",
            inline=False
        )
        
        embed.add_field(
            name="📚 **COMANDOS COMPLETOS**",
            value="[Comandos completos aqui](https://discord.gg/AtKgQHZGks)",
            inline=False
        )
        
        embed.add_field(
            name="⚽ **Para Comandos de Futebol**",
            value="Use este bot em **outros servidores** para acessar todos os comandos de futebol!",
            inline=False
        )
        
        embed.set_footer(text="🔒 Servidor exclusivo para Sistema de Segurança!")
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="🤖 MXP Football Manager + Sistema de Segurança",
        description="⚽ **Seu assistente completo para futebol + proteção automática!**",
        color=0x0099ff
    )
    
    comandos = {
        "🏆 **Gestão de Times**": [
            "`-criar_time` - Cria seu time oficial (obrigatório para jogar)",
        ],
        "👥 **Gestão de Jogadores**": [
            "`-criar_jogador` - Usa modal para criar seu jogador único",
            "`-olheiro` - Descobre jogadores disponíveis no mercado",
            "`-elenco [@usuário]` - Visualiza elenco completo",
        ],
        "⚽ **Time & Escalação**": [
            "`-escalar` - Interface moderna para escalar seu time",
            "`-time [@usuário]` - Vê a escalação e formação do time",
        ],
        "⚔️ **Confrontos**": [
            "`-confronto @usuário` - Desafia outro time (escalação completa)",
            "`-x1 @usuário` - Duelo 1v1 com seleção de jogador",
            "`-stats [@usuário]` - Estatísticas detalhadas",
        ],
        "💰 **Sistema Econômico**": [
            "`-daily` - Coleta R$ 70.000 (a cada 24h)",
        ],
        "🔒 **Sistema de Segurança**": [
            "`-sec_status` - Mostra status do sistema de segurança",
            "`-sec_config` - Configura proteções automáticas",
            "`-sec_restore <ID>` - Restaura cargos removidos",
        ],
        "👑 **Comandos Admin** (Owner only)": [
            "`-add_dinheiro @usuário <valor>` - Adiciona dinheiro",
            "`-add_todos_jogadores @usuário` - Dá todos os jogadores",
        ],
        "ℹ️ **Utilitários**": [
            "`-ajuda` - Mostra esta central de comandos",
        ]
    }
    
    for categoria, lista_comandos in comandos.items():
        embed.add_field(
            name=categoria,
            value="\n".join(lista_comandos),
            inline=False
        )
    
    embed.add_field(
        name="⚠️ **IMPORTANTE - SISTEMA DE TIMES**",
        value="• **TODO JOGADOR DEVE CRIAR UM TIME** antes de usar comandos\n• Times têm nome (máx. 30 chars) e sigla única (máx. 10 chars)\n• Placares mostram: **SIGLA x SIGLA**\n• Palavrões são filtrados automaticamente",
        inline=False
    )
    
    embed.add_field(
        name="🔒 **PROTEÇÕES AUTOMÁTICAS ATIVAS**",
        value="• **Recriação Automática:** Canais/cargos deletados são recriados instantaneamente\n• **Exclusão de Canais:** Remove cargos do responsável + recria canal\n• **Exclusão de Cargos:** Punição configurável + recria cargo\n• **Bots Invasores:** Banimento automático\n• **Logs Detalhados:** Registra recriações e ações\n• **Whitelist:** Usuários autorizados podem deletar sem recriação",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **NOVIDADES**",
        value="• **X1:** Escolha seu jogador para duelos épicos\n• **Modais:** Criação segura de times e jogadores\n• **Segurança:** Proteção automática integrada\n• **Recriação:** Canais/cargos deletados são recriados automaticamente\n• **Times:** Obrigatório para todas as funcionalidades",
        inline=False
    )
    
    embed.add_field(
        name="📚 **COMANDOS COMPLETOS**",
        value="[Comandos completos aqui](https://discord.gg/AtKgQHZGks)",
        inline=False
    )
    
    embed.set_footer(text="🌟 Use o prefixo - antes de cada comando | CRIE SEU TIME PRIMEIRO!")
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None)
    
    await ctx.send(embed=embed)

# Token do bot
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
else:
    print("❌ Token do Discord não encontrado!")
    print("Configure a variável de ambiente DISCORD_BOT_TOKEN ou adicione nas Secrets do Replit")