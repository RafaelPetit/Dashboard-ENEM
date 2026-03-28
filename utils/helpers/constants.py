"""
Constantes extraídas de mappings — importar daqui em vez de repetir
`mappings = get_mappings(); X = mappings['key']` em cada módulo.

get_mappings() é cacheado com lru_cache(1), então a extração aqui
acontece uma única vez no ciclo de vida do processo.
"""
from utils.helpers.mappings import get_mappings

_m = get_mappings()

# Listas de colunas
COLUNAS_NOTAS = _m['colunas_notas']
COMPETENCIA_MAPPING = _m['competencia_mapping']

# Mapeamentos de dados
RACE_MAPPING = _m['race_mapping']
SEXO_MAPPING = _m['sexo_mapping']
DESEMPENHO_MAPPING = _m['desempenho_mapping']
INFRAESTRUTURA_MAPPING = _m['infraestrutura_mapping']
FAIXA_SALARIAL_MAPPING = _m['faixa_salarial']
REGIOES_MAPPING = _m['regioes_mapping']
VARIAVEIS_CATEGORICAS = _m['variaveis_categoricas']
VARIAVEIS_SOCIAIS = _m['variaveis_sociais']

# Configurações
CONFIG_PROCESSAMENTO = _m['config_processamento']
CONFIG_VISUALIZACAO = _m['config_visualizacao']

# Limiares
LIMIARES = _m['limiares']
LIMIARES_ESTATISTICOS = _m['limiares_estatisticos']
LIMIARES_PROCESSAMENTO = _m['limiares_processamento']

# Mapeamento de desempenho
MAPEAMENTO_DESEMPENHO = _m['mapeamento_desempenho']
MAPEAMENTO_FAIXAS_SALARIAIS = _m['mapeamento_faixas_salariais']

# Limpar referência temporária
del _m
