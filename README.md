# Processamento Digital de Imagens — Projeto da Unidade II (UFRN / EAJ)
**Tema:** Segmentação, Identificação e Contagem Automática de Sementes sobre Superfície de EVA  
**Disciplina:** TAD0018 — Turma 01  

---

## 🚀 Como Executar o Script Principal (Linha de Comando)

Conforme os requisitos do edital, o método computacional recebe o caminho de uma imagem como argumento e executa de forma 100% autônoma todas as etapas de identificação, segmentação, contagem e caracterização morfométrica:

```bash
python src/main.py imagens/desenvolvimento/sementes_15_1.jpeg
```

### Saídas Geradas Automaticamente pelo Script:
1. **No Terminal:**
   ```text
   ============================================================
   Processamento concluído com sucesso!
   Imagem: sementes_15_1.jpeg
   Quantidade de sementes identificadas: 15
   ============================================================
   ```
2. **Visualização 1 (Bounding Boxes e Contornos):**
   Salvo em: `saidas/visualizacoes/sementes_15_1_contornos_bbox.jpeg`
3. **Visualização 2 (Sementes Recortadas sobre Fundo Preto):**
   Salvo em: `saidas/segmentadas/sementes_15_1_segmentadas_fundo_preto.jpeg`
4. **Planilha CSV Individual com Métricas Morfométricas:**
   Salvo em: `saidas/csv_imagens/sementes_15_1_metricas.csv`  
   Contém as colunas: `id_semente, xmin, ymin, xmax, ymax, area, perimetro, circularidade`.

---

## 📊 Como Reproduzir a Avaliação Completa do Dataset e Gráficos

Para rodar o benchmark em lote sobre as 21 imagens do dataset, confrontar com os arquivos `.json` do LabelMe e gerar todas as tabelas e gráficos estatísticos:

```bash
python evaluate_dataset.py
```

### Artefatos Consolidados Produzidos:
- `saidas/metricas_contagem_todas.csv`: Contagem real vs. predita de todas as 21 imagens.
- `saidas/metricas_anotadas_detec_seg.csv`: Métricas de TP, FP, FN, Precision, Recall, F1, IoU e Dice de cada imagem anotada.
- `saidas/estatisticas_contagem.csv`: Síntese de MAE, erro relativo % e acurácia exata.
- `saidas/estatisticas_detec_seg.csv`: Médias e desvios padrão de todas as métricas de detecção e segmentação.
- `saidas/graficos/`:
  - `grafico_1_contagem_real_vs_predita.png`: Gráfico de dispersão com linha de identidade ($R^2 = 0.9972$).
  - `grafico_2_erros_contagem_por_imagem.png`: Erro absoluto por imagem.
  - `grafico_3_metricas_deteccao_segmentacao.png`: Barras com média e desvio padrão de Precision, Recall, F1, IoU e Dice.
  - `grafico_4_distribuicao_circularidade_area.png`: Histogramas de distribuição morfológica.
  - `grafico_5_comparativo_desenvolvimento_vs_generalizacao.png`: Comparativo de estabilidade e generalização.

---

## 📁 Estrutura do Repositório

```text
├── imagens/                         # 21 imagens do experimento
│   ├── desenvolvimento/             # 7 imagens _1 com anotações .json do LabelMe
│   ├── generalização/               # 7 imagens independentes _3 (conjunto cego)
│   └── sementes_*_2.jpeg            # 7 imagens _2 de desenvolvimento
├── src/
│   ├── __init__.py
│   ├── pipeline.py                  # Pipeline PDI (CIE-Lab a*, Watershed e Morfometria)
│   ├── labelme_parser.py            # Parser de anotações poligonais do LabelMe
│   ├── metrics.py                   # Cálculo de IoU, Dice, Precision, Recall, F1, MAE
│   └── main.py                      # CLI exigida: python src/main.py <imagem>
├── evaluate_dataset.py              # Benchmark automatizado de todas as imagens
├── referencia_geral.csv             # Planilha de controle experimental
├── relatorio/
│   └── RELATORIO_FINAL.md           # Relatório técnico-científico completo
├── apresentacao/
│   └── SLIDES_APRESENTACAO.md       # Roteiro dos slides da apresentação de 10 min
└── saidas/                          # Saídas visuais, CSVs e gráficos gerados
```
