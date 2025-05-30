from .prepara_dados_desempenho import (
    preparar_dados_comparativo,
    obter_ordem_categorias,
    preparar_dados_grafico_linha,
    preparar_dados_desempenho_geral,
    filtrar_dados_scatter,
    preparar_dados_grafico_linha_desempenho
)

from .validacao_dados import (
    validar_completude_dados,
    verificar_outliers,
    validar_distribuicao_dados
)

from .prepara_dados_aspectos_sociais import (
    preparar_dados_correlacao,
    preparar_dados_distribuicao,
    contar_candidatos_por_categoria,
    ordenar_categorias,
    preparar_dados_heatmap,
    preparar_dados_barras_empilhadas,
    preparar_dados_sankey,
    preparar_dados_grafico_aspectos_por_estado
)

from .prepara_dados_geral import (
    preparar_dados_histograma,
    preparar_dados_grafico_faltas,
    preparar_dados_metricas_principais,
    preparar_dados_media_geral_estados,
    preparar_dados_comparativo_areas,
    preparar_dados_evasao  # Adicionando a função que estava faltando
)