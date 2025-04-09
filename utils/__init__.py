# Este arquivo permite que a pasta utils funcione como um pacote Python
from .data_loader import load_data, agrupar_estados_em_regioes, calcular_seguro, filter_data_by_states
from .mappings import get_mappings

# Isso permite importar diretamente:
# from utils import load_data, get_mappings