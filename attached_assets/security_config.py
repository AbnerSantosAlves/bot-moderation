
"""
🔒 Configurações do Sistema de Segurança
Configure aqui todas as opções do bot de segurança
"""

# 🔐 WHITELIST - IDs de usuários que podem deletar canais/cargos sem punição
# Adicione seus IDs e de admins confiáveis aqui
WHITELIST_IDS = [
    983196900910039090,  # Seu ID (substitua pelo seu ID real)
    # 123456789012345678,  # ID de admin confiável
    # 987654321098765432,  # ID de outro admin
]

# ⚙️ CONFIGURAÇÕES PADRÃO
DEFAULT_CONFIG = {
    # 🤖 Banir bots automaticamente quando entrarem
    'auto_ban_bots': True,
    
    # 🎭 Punição por deletar cargos: 'remove_roles' ou 'ban'
    'role_delete_punishment': 'remove_roles',
    
    # 📺 Nome do canal onde os logs serão enviados
    'logs_channel_name': 'logs',
    
    # 🔥 Punir exclusão de canais
    'punish_channel_delete': True,
    
    # 🎭 Punir exclusão de cargos
    'punish_role_delete': True,
    
    # ⏱️ Tempo de espera antes de verificar audit log (segundos)
    'audit_log_delay': 2,
    
    # 📊 Máximo de logs para manter no histórico
    'max_logs_history': 100
}

# 🚨 MENSAGENS PERSONALIZÁVEIS
MESSAGES = {
    'channel_deleted': "🚨 AÇÃO SUSPEITA DETECTADA - Canal Deletado",
    'role_deleted': "🚨 AÇÃO SUSPEITA DETECTADA - Cargo Deletado", 
    'bot_banned': "🤖 Bot Banido Automaticamente",
    'user_whitelisted': "Canal/Cargo Deletado - Usuário Autorizado",
    'roles_removed': "Todos os cargos removidos",
    'user_banned': "Usuário banido",
    'restoration_available': "Use `!sec_restore` para reverter"
}

# 🎨 CORES DOS EMBEDS (em hexadecimal)
COLORS = {
    'danger': 0xff0000,      # Vermelho - ações suspeitas
    'warning': 0xff9900,     # Laranja - avisos
    'success': 0x00ff00,     # Verde - ações bem-sucedidas
    'info': 0x0099ff,        # Azul - informações
    'authorized': 0x00ff00   # Verde - usuário autorizado
}

# 🔧 PERMISSÕES NECESSÁRIAS PARA O BOT
REQUIRED_PERMISSIONS = [
    'view_audit_log',
    'manage_roles', 
    'ban_members',
    'manage_channels',
    'send_messages',
    'embed_links'
]

# 📋 DESCRIÇÕES DAS CONFIGURAÇÕES
CONFIG_DESCRIPTIONS = {
    'auto_ban_bots': 'Banir bots automaticamente quando entrarem no servidor',
    'role_delete_punishment': 'Tipo de punição por deletar cargos (remove_roles/ban)',
    'logs_channel_name': 'Nome do canal onde os logs serão enviados',
    'punish_channel_delete': 'Aplicar punições por deletar canais',
    'punish_role_delete': 'Aplicar punições por deletar cargos',
    'audit_log_delay': 'Tempo de espera antes de verificar audit log',
    'max_logs_history': 'Máximo de logs para manter no histórico'
}

# 🛡️ TIPOS DE EVENTOS MONITORADOS
MONITORED_EVENTS = {
    'channel_delete': {
        'enabled': True,
        'punishment': 'auto_ban',
        'log_color': COLORS['danger']
    },
    'role_delete': {
        'enabled': True, 
        'punishment': 'auto_ban',  # remove_roles ou ban
        'log_color': COLORS['danger']
    },
    'bot_join': {
        'enabled': True,
        'punishment': 'ban',
        'log_color': COLORS['warning']
    }
}
