from .graficos_desempenho import (
    criar_grafico_comparativo_barras,
    criar_grafico_linha_desempenho,
    criar_grafico_scatter,
    criar_grafico_linha_estados,
    adicionar_linha_tendencia
)

from .componentes import (
    criar_filtros_comparativo,
    criar_filtros_dispersao,
    criar_filtros_estados
)

from .config_graficos import (
    aplicar_layout_padrao, 
    cores_padrao,
    aplicar_tema_grafico
)

from .graficos_aspectos_sociais import (
    criar_grafico_heatmap,
    criar_grafico_barras_empilhadas,
    criar_grafico_sankey,
    criar_grafico_distribuicao,
    criar_grafico_aspectos_por_estado,
    _criar_grafico_vazio
)

from .graficos_geral import (
    criar_histograma,
    criar_grafico_faltas,
    criar_grafico_media_por_estado,
    criar_grafico_comparativo_areas,
    criar_grafico_evasao
)