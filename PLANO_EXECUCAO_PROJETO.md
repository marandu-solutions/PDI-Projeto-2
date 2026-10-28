# 📋 Plano de Execução do Projeto — PDI Unidade II (UFRN / EAJ)
**Tema:** Segmentação, Identificação e Contagem Automática de Sementes sobre Superfície de EVA  
**Disciplina:** TAD0018 — Processamento Digital de Imagens  
**Alvo:** Entrega Final (Relatório, Código CLI, Dados de Avaliação, Anotações LabelMe e Apresentação)  

---

## 1. Visão Geral e Perguntas de Pesquisa

O objetivo deste projeto é projetar, implementar e validar experimentalmente um método computacional robusto em Python/OpenCV para detecção, individualização, contagem e caracterização morfométrica de sementes dispostas sobre EVA.

O trabalho investiga cientificamente duas questões centrais:
1. **Precisão e Estabilidade:** *"Com que precisão e estabilidade é possível identificar e contar automaticamente as sementes presentes em imagens adquiridas nas condições experimentais estabelecidas?"*
2. **Generalização:** *"O desempenho observado durante o desenvolvimento do método é mantido quando ele é aplicado a novas imagens, não utilizadas durante seu desenvolvimento e ajuste?"*

---

## 2. Conjunto de Dados e Estratégia de Anotação (LabelMe)

### 2.1. Organização do Dataset (21 Imagens Adquiridas)
O conjunto contém 21 imagens com resolução homogênea, abrangendo quantidades de 15 a 28 sementes em 3 repetições:
- **Quantidades:** 15, 17, 20, 22, 24, 26, 28 sementes.
- **Divisão Experimental:**
  - **Repetição 1 (_1):** *Desenvolvimento* (com anotação individual Ground Truth). Usada para calibrar limiares, filtros e parâmetros do Watershed.
  - **Repetição 2 (_2):** *Desenvolvimento* (avaliação quantitativa de contagem global).
  - **Repetição 3 (_3):** *Generalização* (conjunto cego estrito para validação de estabilidade sem ajuste de parâmetros).

Total anotado individualmente no LabelMe: **152 instâncias de sementes** nas 7 imagens de desenvolvimento (supera a exigência do edital).

### 2.2. Protocolo de Anotação no LabelMe
Para criar o Ground Truth fiel e reprodutível:
1. **Ferramenta:** LabelMe (`pip install labelme`).
2. **Geometria:** Polígonos fechados ou círculos envolvendo com precisão os limites visíveis de cada semente.
3. **Rótulo Único:** Nomear cada semente como `semente`.
4. **Individualização:** Em situações de sementes em contato tangencial, cada semente recebe seu próprio polígono independente, sem fundir as regiões.
5. **Formato de Saída:** Arquivos `.json` com o mesmo nome base da imagem (ex.: `sementes_15_1.json`).

---

## 3. Definição Formal das Métricas de Avaliação

O projeto exige quantificação multidimensional do desempenho. As métricas estão agrupadas em quatro pilares:

### 3.1. Características Morfológicas das Sementes
Para cada semente identificada:
- **Área (A):** Número de pixels internos da região da semente (pixels).
- **Perímetro (P):** Comprimento do contorno externo delimitador da semente (pixels).
- **Circularidade (C):** Medida adimensional que avalia a proximidade da forma com um círculo perfeito:
  ```text
  Circularidade = (4 * π * Área) / (Perímetro²)
  ```
  - C = 1.0: Círculo perfeito.
  - C = π/4 ≈ 0.785: Quadrado perfeito.
  - Sementes aglomeradas ou fundidas incorretamente apresentarão contorno complexo com perímetro desproporcional, resultando em queda acentuada na circularidade (C < 0.6).

### 3.2. Qualidade da Contagem Global
Comparação entre o total predito (N_predito) e o total real (N_real):
- **Erro Absoluto (Ea):**
  ```text
  Ea = |N_predito - N_real|
  ```
- **Erro Relativo Percentual (Er%):**
  ```text
  Er% = (|N_predito - N_real| / N_real) * 100%
  ```
- **Erro Médio Absoluto (MAE):**
  Média aritmética dos erros absolutos em todas as imagens avaliadas.
- **Coeficiente de Determinação (R²):** Avaliação da linearidade entre N_predito e N_real.

### 3.3. Identificação e Localização (Nível de Instância — Bounding Boxes)
Para verificar a correspondência entre a Bounding Box predita (B_pred) e a Bounding Box de referência (B_gt):
- **Intersection over Union (IoU de BBox):**
  ```text
  IoU = Área(B_pred ∩ B_gt) / Área(B_pred ∪ B_gt)
  ```
- **Critério de Detecção (Threshold IoU ≥ 0.50):**
  - **Verdadeiro Positivo (TP):** Semente predita com IoU ≥ 0.50 em relação a uma semente do Ground Truth (associação 1-para-1).
  - **Falso Positivo (FP):** Detecção espúria (ruído de fundo, sombra intensa) ou detecção dupla da mesma semente.
  - **Falso Negativo (FN):** Semente real não detectada pelo algoritmo.
- **Métricas Derivadas:**
  ```text
  Precisão (Precision) = TP / (TP + FP)
  Revocação (Recall) = TP / (TP + FN)
  F1-Score = (2 * Precision * Recall) / (Precision + Recall)
  ```
- **Qualidade Média de Localização:** Média do IoU obtido entre todos os pares TP.

### 3.4. Qualidade da Segmentação (Nível de Pixel)
Comparação pixel a pixel entre a máscara binária predita (M_pred) e a máscara binária de referência (M_gt):
- **Dice Similarity Coefficient (F1 pixelar):**
  ```text
  Dice = (2 * TP_pixels) / (2 * TP_pixels + FP_pixels + FN_pixels)
  ```
- **Jaccard Index (IoU pixelar):**
  ```text
  IoU_pixelar = TP_pixels / (TP_pixels + FP_pixels + FN_pixels)
  ```
- **Critério de Individualização de Instâncias:** Se duas sementes em contato forem fundidas em um único blob, haverá penalização no nível de objeto (1 TP e 1 FN, ou inflação de FP), garantindo que a fusão não seja considerada segmentação correta.

### 3.5. Avaliação da Generalização e Análise Estatística
- **Medidas de Tendência Central e Variabilidade:**
  Média, Mediana, Desvio Padrão e Coeficiente de Variação (CV% = [Desvio Padrão / Média] * 100%).
- **Estabilidade do Desempenho:**
  Desvio padrão das métricas (MAE, F1, Dice) entre as 21 imagens.
- **Teste de Generalização:**
  Comparação direta do desempenho no conjunto de Desenvolvimento contra o conjunto de Generalização (teste cego sem recalibração de parâmetros).

---

## 4. Arquitetura do Pipeline PDI Proposto

O método computacional opera de forma 100% autônoma, sem intervenção manual ou hiperparâmetros ajustados por imagem.

```text
[Imagem de Entrada (.jpeg)] 
       ↓
[Pré-processamento & Filtro Gaussiano 5x5]
       ↓
[Conversão de Cores (CIE-Lab / Canal a*)]
       ↓
[Limiarização Global T=126]
       ↓
[Operações Morfológicas (Abertura 3x3)]
       ↓
[Transformada de Distância Euclidiana L2]
       ↓
[Detecção de Picos / Marcadores de Centroide]
       ↓
[Algoritmo Watershed (Bacias Hidrográficas)]
       ↓
[Extração Individual de Contornos e BBoxes]
       ↓
[Cálculo de Área, Perímetro e Circularidade]
       ↓
[Geração das 4 Saídas Obrigatórias do Edital]
```

### Detalhes das Etapas:
1. **Isolamento da Região de Interesse e Atenuação de Sombras:**
   - O contraste entre o EVA (fundo) e as sementes é maximizado no canal a\* do espaço CIE-Lab (EVA ≈ 108, sementes ≈ 145).
   - Filtro Gaussiano 5 × 5 remove micro-ruídos da textura do EVA sem degradar bordas.
2. **Limpeza Morfológica de Fundo:**
   - Abertura morfológica elimina micro-grânulos e imperfeições superficiais do EVA, preservando apenas os corpos das sementes.
3. **Separação de Sementes em Contato (Watershed baseado em Distância):**
   - Aplica-se a Transformada de Distância de Euclides na máscara binária limpa.
   - Os picos locais de distância correspondem aos centros de massa de cada semente individual.
   - O Watershed inunda as bacias topográficas a partir dos marcadores de pico, criando linhas de corte perfeitas no ponto de contato tangencial das sementes.
4. **Extração Morfométrica e Formatação das Saídas:**
   - Para cada bacia, extrai-se o contorno independente (`cv2.findContours`).
   - Bounding box no formato: `[xmin, ymin, xmax, ymax]`.
   - Cálculo das propriedades: Área = `cv2.contourArea`, Perímetro = `cv2.arcLength`, Circularidade = `(4 * π * Área) / (Perímetro²)`.

---

## 5. Estrutura de Diretórios do Projeto

```text
PDI-Projeto-2/
│
├── imagens/                         # 21 imagens brutas (.jpeg) e anotações .json
│   ├── desenvolvimento/             # 7 imagens _1 com anotações .json do LabelMe
│   ├── generalização/               # 7 imagens independentes _3 (conjunto cego)
│   └── sementes_*_2.jpeg            # 7 imagens _2 de desenvolvimento
├── saidas/                          # Saídas geradas pelo pipeline
│   ├── visualizacoes/               # Imagens com bboxes e contornos
│   ├── segmentadas/                 # Imagens das sementes sobre fundo preto
│   ├── csv_imagens/                 # CSV individual por imagem (requisito)
│   └── graficos/                    # 5 gráficos científicos em alta resolução
├── src/
│   ├── __init__.py
│   ├── pipeline.py                  # Classe e funções do pipeline PDI
│   ├── labelme_parser.py            # Conversor de .json do LabelMe para máscaras e bboxes
│   ├── metrics.py                   # Cálculo de IoU, Precision, Recall, Dice, MAE
│   └── main.py                      # CLI exigida: python src/main.py <caminho_imagem>
├── evaluate_dataset.py              # Script de benchmark que roda em lote e gera tabelas
├── referencia_geral.csv             # Tabela com as 21 imagens, Qtd_Real, Conjunto e Anotação
├── relatorio/                       # Relatório Técnico-Científico completo
│   └── RELATORIO_FINAL.md
├── apresentacao/                    # Slides da apresentação (10 minutos)
│   └── SLIDES_APRESENTACAO.md
├── gerar_zip_entrega.py             # Script de empacotamento para o SIGAA
└── README.md                        # Manual de instruções de execução
```

---

## 6. Especificação das 4 Saídas Obrigatórias do Script CLI

O edital exige que o script receba o caminho de uma imagem via linha de comando:
```bash
python src/main.py imagens/desenvolvimento/sementes_20_1.jpeg
```

E gere obrigatoriamente:
1. **No Terminal:**
   ```text
   Imagem processada: sementes_20_1.jpeg
   Quantidade de sementes identificadas: 20
   ```
2. **Saída Visual 1:** `saidas/visualizacoes/sementes_20_1_contornos_bbox.jpeg`  
   Imagem colorida com retângulos delimitadores (bounding boxes) e contornos sobrepostos em cada semente.
3. **Saída Visual 2:** `saidas/segmentadas/sementes_20_1_segmentadas_fundo_preto.jpeg`  
   Imagem contendo os pixels originais das sementes sobre fundo 100% preto (`RGB 0,0,0`).
4. **Saída Tabular (CSV):** `saidas/csv_imagens/sementes_20_1_metricas.csv`  
   Arquivo CSV com as colunas:
   ```csv
   id_semente,xmin,ymin,xmax,ymax,area,perimetro,circularidade
   1,142,350,210,418,3420,212.4,0.952
   2,510,120,580,192,3580,218.1,0.946
   ...
   ```
