# 🎙️ Estrutura e Roteiro dos Slides da Apresentação Final (10 Minutos)

**Disciplina:** TAD0018 — Processamento Digital de Imagens (UFRN / EAJ)  
**Projeto da Unidade II:** Segmentação, Identificação e Contagem Automática de Sementes sobre EVA  
**Tempo Limite Obrigatório:** 10 minutos (ritmo de aproximadamente 1 minuto por slide)  

---

## Slide 1: Capa e Identificação (00:00 - 00:45)
- **Título:** Segmentação, Identificação e Contagem Automática de Sementes
- **Subtítulo:** Abordagem por Processamento Digital de Imagens com Watershed e Análise Morfométrica
- **Equipe:** Componentes do Grupo
- **Disciplina:** TAD0018 — PDI | Turma 01 | Prof. Responsável
- **Fala Sugerida:** *"Bom dia a todos e ao professor. Hoje apresentamos o projeto da Unidade II de Processamento Digital de Imagens, cujo objetivo é desenvolver e validar um método computacional autônomo para identificar, segmentar, contar e caracterizar sementes sobre superfície de EVA."*

---

## Slide 2: Contexto e Perguntas de Pesquisa (00:45 - 01:45)
- **Desafio:** Contagem manual lenta, fadigante e sujeita a erros operacionais.
- **Cenário:** Sementes de densidades variadas, situações de contato físico e fundo de EVA.
- **Duas Questões Centrais:**
  1. *Com que precisão e estabilidade é possível identificar e contar automaticamente as sementes?*
  2. *O desempenho é mantido quando o método é aplicado a imagens inéditas de generalização?*
- **Fala Sugerida:** *"Nosso estudo foi desenhado para responder cientificamente a duas perguntas: a precisão e estabilidade nas condições experimentais e a capacidade do método de generalizar sem qualquer ajuste manual para novas imagens."*

---

## Slide 3: Aquisição Experimental e Divisão dos Dados (01:45 - 02:45)
- **Materiais:** Sementes esferoidais avermelhadas sobre base de EVA ciano/verde.
- **Dataset (21 Imagens no total):**
  - Resolução padronizada: 1600 × 900 pixels.
  - 7 densidades populacionais: 15, 17, 20, 22, 24, 26 e 28 sementes.
  - 3 repetições por densidade.
- **Separação Metodológica:**
  - **Desenvolvimento:** 14 imagens (repetições `_1` e `_2`), sendo as 7 da repetição `_1` com Ground Truth individual completo.
  - **Generalização:** 7 imagens (repetição `_3`), subconjunto independente e cego.
- **Fala Sugerida:** *"Padronizamos a aquisição em 21 imagens de alta resolução. As imagens foram rigorosamente divididas entre conjunto de desenvolvimento e um conjunto estritamente cego de generalização."*

---

## Slide 4: Anotação Ground Truth com LabelMe (02:45 - 03:45)
- **Ferramenta:** LabelMe v7.9.1.
- **Instâncias Anotadas:** 152 sementes delimitadas individualmente por polígonos fechados.
- **Tratamento de Contatos:** Cada semente possui seu próprio polígono, sem fusão nas regiões de toque tangencial.
- **Conversão Programática:** Extração automática de Bounding Boxes, máscaras binárias e valores de referência de Área, Perímetro e Circularidade.
- **Fala Sugerida:** *"Para validar o método no nível de pixel e de objeto, anotamos individualmente as sementes no LabelMe. Mesmo nos contatos mais íntimos, preservamos a individualização de cada propágulo."*

---

## Slide 5: Pipeline Computacional de PDI (03:45 - 05:00)
- **Etapa 1:** Conversão para o espaço **CIE-Lab**. Uso exclusivo do canal a\* (invariante espectral com separação bimodal nítida: EVA em a\* ≈ 108, sementes em a\* ≈ 145).
- **Etapa 2:** Suavização Gaussiana 5 × 5 e Binarização fixa (T = 126).
- **Etapa 3:** Abertura morfológica com elemento elíptico 3 × 3 para remover ruídos.
- **Etapa 4 (O Segredo dos Contatos):** **Transformada de Distância Euclidiana L2** + detecção de máximos locais (`peak_local_max`).
- **Etapa 5:** **Watershed condicionado à distância invertida**, seccionando o relevo nos pontos exatos de toque tangencial.
- **Fala Sugerida:** *"A chave do nosso pipeline está na escolha do espaço de cores CIE-Lab: o canal a\* isola perfeitamente o EVA verde das sementes avermelhadas com alto contraste. Para separar sementes em contato, usamos a Transformada de Distância Euclidiana guiando o algoritmo Watershed."*

---

## Slide 6: Resultados Visuais e Saídas Obrigatórias (05:00 - 06:15)
- **Execução CLI via Terminal:** `python src/main.py <imagem>`
- **Exibição das 4 Saídas Obrigatórias:**
  1. *Console:* Quantidade contada exibida no terminal.
  2. *Visual 1:* Imagem com Bounding Boxes e contornos coloridos sobrepostos.
  3. *Visual 2:* Recorte das sementes reais sobre fundo 100% preto.
  4. *Tabular:* Arquivo CSV com `[xmin, ymin, xmax, ymax]`, Área, Perímetro e Circularidade de cada semente.
- *(Mostrar imagem comparativa lado a lado na tela)*
- **Fala Sugerida:** *"Como exigido pelo edital, nosso script de linha de comando gera de forma 100% autônoma as quatro saídas: contagem no console, visualização de contornos e bboxes, imagem recortada em fundo preto e a planilha CSV com as métricas individuais."*

---

## Slide 7: Desempenho de Contagem Global (06:15 - 07:15)
- **Resultados nas 21 Imagens:**
  - Contagem 100% exata em **17 das 21 imagens** (80.95%).
  - Nas 4 imagens com divergência, o erro foi de apenas **1 semente**.
  - **MAE Global:** **0.1905 sementes** (Erro relativo médio de 0.80%).
  - **Coeficiente de Correlação:** R² = 0.9972.
- *(Mostrar o Gráfico 1 de dispersão com linha de identidade ideal)*
- **Fala Sugerida:** *"Avaliando todas as 21 imagens, atingimos um MAE de apenas 0.19 sementes e um R² de 0.9972. Isso comprova que a contagem automática é extremamente precisa e linear."*

---

## Slide 8: Qualidade de Detecção e Segmentação (07:15 - 08:15)
- **Comparação com o Ground Truth do LabelMe (152 instâncias):**
  - **Precisão (Precision):** 0.9932 ± 0.018 (99.32%)
  - **Revocação (Recall):** 0.9870 ± 0.034 (98.70%)
  - **F1-Score:** **0.9900 ± 0.026 (99.00%)**
  - **IoU Médio das Bounding Boxes:** **0.8788 ± 0.024 (87.88%)**
  - **Dice Similarity (Pixel):** **0.9358 ± 0.010 (93.58%)**
  - **IoU Pixelar (Jaccard):** **0.8795 ± 0.018 (87.95%)**
- *(Mostrar o Gráfico 3 com as barras de métricas)*
- **Fala Sugerida:** *"No confronto com as anotações do LabelMe, nosso F1-score de detecção foi de 99%, com IoU médio de caixas delimitadoras de 87.8% e Dice de segmentação de 93.58%. A individualização dos objetos foi plenamente assegurada."*

---

## Slide 9: Avaliação da Generalização (08:15 - 09:15)
- **Pergunta 2:** *O desempenho é mantido em imagens independentes?*
- **Resultados no Conjunto de Generalização (Repetição `_3`):**
  - **MAE:** **0.000 sementes** (100% de acurácia exata em todas as 7 imagens independentes de 15 a 28 sementes).
  - Sem necessidade de recalibração de limiares.
  - Zero sobreajuste (overfitting).
- *(Mostrar o Gráfico 5 comparativo Desenvolvimento vs. Generalização)*
- **Fala Sugerida:** *"Respondendo à segunda pergunta de pesquisa: sim, com louvor! No conjunto cego de generalização, o método acertou exatamente a contagem de 100% das imagens, provando que o modelo é robusto e generalizável."*

---

## Slide 10: Conclusões e Considerações Finais (09:15 - 10:00)
- **Objetivos Alcançados:**
  - Pipeline autônomo e reproduzível em linha de comando.
  - Excelente separação de sementes em contato via Watershed.
  - Conformidade estrita com todos os requisitos do edital da UFRN/EAJ.
- **Limitações:**
  - Situações de compressão física extrema de sementes onde não há fenda de relevo para a transformada de distância.
- **Agradecimentos e Perguntas da Banca:**
  - *"Obrigado pela atenção de todos! Estamos abertos às considerações da banca."*
