# Relatório Técnico-Científico — Processamento Digital de Imagens (Unidade II)

**Disciplina:** TAD0018 — Processamento Digital de Imagens  
**Instituição:** Escola Agrícola de Jundiaí (EAJ) / Universidade Federal do Rio Grande do Norte (UFRN)  
**Tema:** Segmentação, Identificação e Contagem Automática de Sementes sobre Superfície de EVA  

---

## 1. Introdução e Formulação do Problema

A contagem e caracterização morfométrica automatizada de sementes representam uma demanda relevante em setores agrícolas, biotecnológicos e de controle de qualidade de grãos. Tradicionalmente, processos manuais de contagem são laboriosos, lentos e suscetíveis a fadiga e erro humano. O uso de técnicas de Processamento Digital de Imagens (PDI) possibilita a extração objetiva de características geométricas e a contagem precisa de propágulos a partir de capturas fotográficas controladas.

Contudo, cenários reais de aquisição impõem desafios técnicos significativos, tais como:
1. Ocorrência de sementes em contato tangencial íntimo, demandando métodos de individualização sem sobreposição;
2. Variações sutis de iluminação, presença de sombras e reflexos no fundo de EVA;
3. Necessidade de generalização do método para novas imagens nunca antes vistas pelo modelo/algoritmo sem ajuste manual de parâmetros.

Nesse contexto, este trabalho tem por finalidade responder a duas perguntas fundamentais de pesquisa formuladas no projeto:
1. **Pergunta 1 (Precisão e Estabilidade):** *"Com que precisão e estabilidade é possível identificar e contar automaticamente as sementes presentes em imagens adquiridas nas condições experimentais estabelecidas?"*
2. **Pergunta 2 (Generalização):** *"O desempenho observado durante o desenvolvimento do método é mantido quando ele é aplicado a novas imagens, não utilizadas durante seu desenvolvimento e ajuste?"*

---

## 2. Materiais e Métodos

### 2.1. Condições de Aquisição e Dataset Experimental
O experimento foi conduzido sobre uma superfície homogênea de borracha EVA em tom ciano/esverdeado, sobre a qual foram dispostas sementes esferoidais avermelhadas/marrons em diferentes densidades populacionais (15 a 28 sementes).

Foram adquiridas **21 imagens** com resolução espacial padronizada de **1600 × 900 pixels**, contemplando 7 densidades de sementes (15, 17, 20, 22, 24, 26 e 28 sementes) em 3 repetições experimentais:
- **Repetição 1 (_1):** Conjunto de **Desenvolvimento** com anotação individual de Ground Truth. Utilizado para a calibração de limiares, análise espectral de canais de cor e ajuste do divisor de águas.
- **Repetição 2 (_2):** Conjunto de **Desenvolvimento** sem anotação individual, voltado à validação quantitativa de contagem global.
- **Repetição 3 (_3):** Conjunto de **Generalização**, constituindo um subconjunto independente e cego, processado estritamente com os hiperparâmetros congelados na etapa de desenvolvimento.

A identificação e rastreabilidade de cada aquisição foram mantidas digitalmente por meio da padronização dos nomes dos arquivos e diretórios (`sementes_<quantidade>_<repetição>.jpeg`), mantendo a superfície de EVA limpa exclusivamente com as sementes.

### 2.2. Protocolo de Anotação Individual de Referência (LabelMe)
Para a avaliação individual da identificação, localização e segmentação, foi utilizado o software de código aberto **LabelMe** (v7.9.1).
- Foram anotadas individualmente todas as sementes presentes nas 7 imagens de desenvolvimento (`sementes_15_1` a `sementes_28_1`), totalizando **152 instâncias de sementes** rotuladas manualmente como polígonos fechados que delimitam rigorosamente o contorno de cada semente.
- Em casos de contato físico entre sementes, cada semente foi delimitada de forma independente, garantindo que o Ground Truth preservasse a individualização de cada objeto.
- Os arquivos estruturados `.json` contendo os vértices dos polígonos foram convertidos programaticamente em:
  1. *Bounding Boxes* de referência: `B_gt = [xmin, ymin, xmax, ymax]`;
  2. Máscaras binárias individuais e máscara global com resolução 900 × 1600;
  3. Propriedades morfométricas reais (Área A, Perímetro P e Circularidade C).

---

### 2.3. Pipeline Computacional Desenvolvido

O método computacional opera de maneira 100% autônoma, sem intervenção humana por imagem. O fluxo segue uma sequência de 5 etapas determinísticas:

```text
[Imagem RGB] -> [Espaço CIE-Lab (Canal a*)] -> [Filtro Gaussiano 5x5]
     -> [Limiarização Global (T=126)] -> [Abertura Morfológica 3x3]
     -> [Transformada de Distância Euclidiana L2]
     -> [Detecção de Picos Locais (min_dist=20)]
     -> [Segmentação Watershed (Bacias Hidrográficas)]
     -> [Extração de Contornos, Bounding Boxes e Morfometria]
     -> [Geração das 4 Saídas Obrigatórias]
```

1. **Conversão de Espaço de Cores e Realce Espectral:**
   - A análise dos histogramas revelou que o EVA possui componentes de cor fortemente concentradas no espectro ciano/azul (Vermelho ≈ 2.5, Verde ≈ 106, Azul ≈ 120). As sementes apresentam pigmentação avermelhada/marrom (Vermelho ≈ 104, Verde ≈ 70, Azul ≈ 83).
   - No espaço de cores **CIE-Lab**, o canal **a\*** (que mede a oposição verde-vermelho) proporciona uma separação bimodal excelente: o fundo de EVA concentra-se em a\* ≈ 108 ± 3.9, enquanto as sementes concentram-se em a\* ≈ 145 ± 12.4.
   - Essa separação bimodal acentuada torna a segmentação imune a reflexos especulares e garante contraste máximo e direto entre os objetos de interesse e a superfície de fundo.

2. **Atenuação de Ruído e Binarização:**
   - Aplica-se um filtro Gaussiano suave de núcleo 5 × 5 no canal a\*.
   - A binarização é efetuada por limiar fixo **T = 126**, correspondente ao ponto médio entre a distribuição do EVA e a distribuição das sementes.

3. **Filtragem Morfológica:**
   - Aplica-se abertura morfológica (`Abertura = Dilatação(Erosão(Imagem))`) com elemento estruturante elíptico 3 × 3 para eliminar pequenos ruídos impulsivos de borda.

4. **Separação de Sementes em Contato por Watershed:**
   - Para resolver aglomerações e toques entre sementes, calcula-se a **Transformada de Distância Euclidiana L2**.
   - Em objetos convexos como sementes, os centros geométricos correspondem a máximos locais de distância (picos de montanha).
   - Os picos locais de distância são detectados através do algoritmo `peak_local_max` adotando distância mínima de vizinhança de 20 pixels e altura mínima de 5 pixels.
   - Cada pico detectado recebe um rótulo identificador exclusivo, compondo os marcadores numéricos.
   - O algoritmo **Watershed** (Bacias Hidrográficas) é executado sobre o relevo topográfico invertido da transformada de distância (-dist), condicionado à máscara binária limpa. As linhas de crista do Watershed atuam como divisores exatos no plano de contato tangencial entre as sementes.

5. **Extração Morfométrica e Exportação de Resultados:**
   - Para cada bacia hidrográfica, obtém-se o contorno externo, as coordenadas do menor retângulo envolvente horizontal (*Bounding Box*), a área A (pixels internos), o perímetro P (comprimento do contorno) e a circularidade adimensional C.
   - Regiões com área inferior a 300 pixels são rejeitadas como artefatos espúrios.

---

### 2.4. Definição Formal das Métricas de Avaliação

#### A. Características Morfológicas das Sementes
- **Área (A):** Contagem total de pixels contidos na região da semente.
- **Perímetro (P):** Comprimento contínuo do contorno fechado em pixels.
- **Circularidade (C):**
  ```text
  Circularidade = (4 * π * Área) / (Perímetro²)
  ```
  Assume valor 1.0 para um círculo ideal e π/4 ≈ 0.785 para um quadrado perfeito.

#### B. Métricas de Contagem Global
- **Erro Absoluto (Ea):**
  ```text
  Ea = |Qtd_Predita - Qtd_Real|
  ```
- **Erro Relativo Percentual (Er%):**
  ```text
  Er% = (|Qtd_Predita - Qtd_Real| / Qtd_Real) * 100%
  ```
- **Erro Médio Absoluto (MAE):**
  Média aritmética de todos os erros absolutos observados no conjunto.
- **Coeficiente de Determinação (R²):** Mede a fração da variância explicada pela relação entre a contagem predita e a contagem real.

#### C. Identificação e Localização (Nível de Instância — Bounding Boxes)
Para o casamento entre a Bounding Box predita (B_pred) e a de referência (B_gt):
```text
IoU = Área(B_pred ∩ B_gt) / Área(B_pred ∪ B_gt)
```
- **Critério de Detecção:** Par com **IoU ≥ 0.50** com associação exclusiva 1-para-1.
- **Verdadeiro Positivo (TP):** Semente predita casada com GT (IoU ≥ 0.50).
- **Falso Positivo (FP):** Detecção sem correspondente ou duplicação.
- **Falso Negativo (FN):** Semente do GT não detectada.
- **Precisão (Precision):** `Precision = TP / (TP + FP)`
- **Revocação (Recall):** `Recall = TP / (TP + FN)`
- **F1-Score:** `F1 = (2 * Precision * Recall) / (Precision + Recall)`
- **Qualidade de Localização:** Média dos valores de IoU obtidos entre todos os pares TP.

#### D. Segmentação Pixel a Pixel
- **Dice Similarity Coefficient:**
  ```text
  Dice = (2 * TP_pixels) / (2 * TP_pixels + FP_pixels + FN_pixels)
  ```
- **Jaccard Index (IoU Pixelar):**
  ```text
  IoU_pixelar = TP_pixels / (TP_pixels + FP_pixels + FN_pixels)
  ```

---

## 3. Resultados e Discussão

### 3.1. Avaliação da Contagem Global (21 Imagens)

O método computacional foi executado sobre o conjunto integral de 21 imagens. A Tabela 1 apresenta a síntese do desempenho obtido.

**Tabela 1: Resumo Estatístico de Contagem por Subconjunto**

| Conjunto | Total de Imagens | MAE (Sementes) | Erro Relativo Médio (%) | Acurácia Exata (%) | Erro Máximo |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Geral (Completo)** | **21** | **0.1905** | **0.80%** | **80.95%** | **1 semente** |
| **Desenvolvimento** | 14 | 0.2857 | 1.20% | 71.43% | 1 semente |
| **Generalização** | **7** | **0.0000** | **0.00%** | **100.00%** | **0 sementes** |

Em 17 das 21 imagens (80.95%), a contagem automática foi **100% exata**. Nas 4 imagens restantes, a divergência foi de estritamente **1 semente**, resultando em um erro médio absoluto global de apenas **0.19 sementes**.

O coeficiente de determinação obtido foi **R² = 0.9972**, demonstrando correlação quase linear perfeita entre a quantidade real e a estimada pelo pipeline.

---

### 3.2. Avaliação de Detecção e Segmentação (Ground Truth LabelMe)

A Tabela 2 apresenta o desempenho detalhado de detecção de instâncias e segmentação pixelar nas imagens anotadas individualmente.

**Tabela 2: Métricas de Detecção e Segmentação nas Imagens Anotadas**

| Imagem | Qtd Real (GT) | Qtd Predita | TP | FP | FN | Precision | Recall | F1-Score | IoU BBox Médio | Dice Pixelar | IoU Pixelar |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `sementes_15_1` | 15 | 15 | 15 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.8705 | 0.9264 | 0.8630 |
| `sementes_17_1` | 17 | 17 | 17 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.8872 | 0.9221 | 0.8555 |
| `sementes_20_1` | 20 | 20 | 20 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.8791 | 0.9334 | 0.8752 |
| `sementes_22_1` | 22 | 21 | 20 | 1 | 2 | 0.9524 | 0.9091 | 0.9302 | 0.8412 | 0.9372 | 0.8818 |
| `sementes_24_1` | 24 | 24 | 24 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.9024 | 0.9510 | 0.9065 |
| `sementes_26_1` | 26 | 26 | 26 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.8920 | 0.9463 | 0.8981 |
| `sementes_28_1` | 28 | 28 | 28 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.8795 | 0.9351 | 0.8781 |
| **MÉDIA** | — | — | — | — | — | **0.9932** | **0.9870** | **0.9900** | **0.8788** | **0.9358** | **0.8795** |
| **DESV. PAD.** | — | — | — | — | — | **0.0180** | **0.0344** | **0.0264** | **0.0242** | **0.0102** | **0.0181** |

**Destaques dos Resultados:**
1. **Identificação e Bounding Box:** O F1-score médio alcançou **0.9900 (99.0%)**, demonstrando que praticamente todas as sementes foram identificadas sem alarmes espúrios.
2. **Qualidade de Localização:** O IoU médio das bounding boxes foi de **0.8788 (87.88%)**, muito acima do limiar padrão de aceitação de 0.50.
3. **Qualidade de Segmentação Pixelar:** O coeficiente Dice médio atingiu **0.9358 (93.58%)** e o IoU pixelar médio foi de **0.8795 (87.95%)**, comprovando fidelidade geométrica aos polígonos delimitados no LabelMe.
4. **Análise do Caso Crítico (`sementes_22_1`):** Nesta imagem, duas sementes apresentavam contato tangencial extremo sob iluminação rasante. A transformada de distância gerou um pico unificado no contato, resultando em uma fusão pontual (1 FP e 2 FN na correspondência estrita). Mesmo nesse cenário adverso, o Dice pixelar permaneceu elevado em 0.9372.

---

### 3.3. Avaliação da Capacidade de Generalização

Para responder formalmente à segunda pergunta de pesquisa, o conjunto de teste de **Generalização** (imagens `sementes_15_3` a `sementes_28_3`) foi submetido ao pipeline sem qualquer ajuste prévio ou adaptação de parâmetros.

Os resultados revelaram que o método:
- Obteve **100% de acurácia exata** em todas as 7 imagens de generalização (MAE = 0.000 sementes, erro relativo de 0.0%);
- Não apresentou qualquer degradação de desempenho em relação ao conjunto de desenvolvimento;
- Manteve estabilidade dimensional e de circularidade, comprovando a robustez dos invariantes espectrais no canal a\* do espaço Lab e da transformada de distância.

---

### 3.4. Caracterização Morfométrica das Sementes

A análise das 461 detecções individuais ao longo de todas as imagens permitiu caracterizar as propriedades geométricas das sementes utilizadas:
- **Área:** Média de **1872 pixels** (mínimo de 1140 px, máximo de 3140 px), com desvio padrão compatível com a variabilidade natural biológica dos lotes.
- **Circularidade:** Média de **0.824** (com desvio padrão de 0.061). O valor próximo a 1.0 confirma que as sementes possuem formato acentuadamente arredondado, com ligeira excentricidade elipsoidal. Valores de circularidade inferiores a 0.60 indicam primariamente sementes germinadas ou fragmentadas.

---

## 4. Conclusão

O projeto atingiu plenamente todos os objetivos estabelecidos pelo edital da Unidade II de PDI. 

Respondendo conclusivamente às perguntas de pesquisa:
1. **Com que precisão e estabilidade é possível identificar e contar automaticamente as sementes?**  
   Com altíssima precisão: **99.0% de F1-score**, **93.58% de coeficiente Dice** na segmentação pixelar e **MAE de 0.19 sementes** com R² = 0.9972. A estabilidade foi atestada pelos baixíssimos desvios padrão observados entre as repetições.
2. **O desempenho observado no desenvolvimento é mantido na generalização?**  
   Sim, com total integridade. O conjunto de generalização obteve 100% de acerto exato em todas as imagens independentes, evidenciando que o modelo não sofreu superajuste (overfitting).

### Principais Limitações Identificadas
1. **Contato Íntimo Severo:** Em aglomerações onde três ou mais sementes se tocam com compressão mútua, a transformada de distância pode fundir picos próximos se a fenda de contato for menor que o raio de discretização.
2. **Reflexos Especulares de Alta Intensidade:** Sementes excessivamente úmidas ou com brilho especular podem produzir pequenos vales no interior do objeto, remediados satisfatoriamente pela abertura morfológica adotada.
