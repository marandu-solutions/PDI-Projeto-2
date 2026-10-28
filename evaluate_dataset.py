import os
import re
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.pipeline import SeedSegmentationPipeline, save_image_robust, read_image_robust
from src.labelme_parser import load_labelme_json
from src.metrics import evaluate_detection, evaluate_segmentation, evaluate_counting, calculate_summary_stats

def main():
    print("=" * 80)
    print("INICIANDO AVALIAÇÃO QUANTITATIVA E ESTATÍSTICA DO DATASET COMPLETO")
    print("=" * 80)

    # Diretórios
    out_dir = "saidas"
    vis_dir = os.path.join(out_dir, "visualizacoes")
    seg_dir = os.path.join(out_dir, "segmentadas")
    csv_dir = os.path.join(out_dir, "csv_imagens")
    plots_dir = os.path.join(out_dir, "graficos")
    os.makedirs(vis_dir, exist_ok=True)
    os.makedirs(seg_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    # Coletar todas as 21 imagens
    image_paths = sorted(glob.glob("imagens/*/*.jpeg") + glob.glob("imagens/*.jpeg"))
    print(f"Total de imagens encontradas: {len(image_paths)}")

    pipeline = SeedSegmentationPipeline()

    contagem_records = []
    anotadas_records = []
    all_seeds_records = []

    for img_path in image_paths:
        file_name = os.path.basename(img_path)
        base_name = os.path.splitext(file_name)[0]

        match = re.search(r"sementes_(\d+)_(\d+)", file_name)
        if match:
            qtd_real = int(match.group(1))
            rep = int(match.group(2))
        else:
            qtd_real = 0
            rep = 1

        # Definição do conjunto
        if rep == 3:
            conjunto = "Generalização"
        else:
            conjunto = "Desenvolvimento"

        # Executa o pipeline
        res = pipeline.process(img_path)
        pred_count = res["count"]

        # Salva as 4 saídas obrigatórias por imagem
        vis_filename = os.path.join(vis_dir, f"{base_name}_contornos_bbox.jpeg")
        seg_filename = os.path.join(seg_dir, f"{base_name}_segmentadas_fundo_preto.jpeg")
        csv_filename = os.path.join(csv_dir, f"{base_name}_metricas.csv")
        save_image_robust(vis_filename, res["vis_img"])
        save_image_robust(seg_filename, res["segmented_black_bg"])
        res["df_metrics"].to_csv(csv_filename, index=False, encoding="utf-8")

        # Registro de métricas morfométricas de cada semente
        for s in res["seeds"]:
            all_seeds_records.append({
                "imagem": file_name,
                "conjunto": conjunto,
                "id_semente": s["id_semente"],
                "area": s["area"],
                "perimetro": s["perimetro"],
                "circularidade": s["circularidade"]
            })

        # Métrica de contagem
        cont_res = evaluate_counting(qtd_real, pred_count)
        contagem_records.append({
            "Imagem": file_name,
            "Caminho": img_path,
            "Conjunto": conjunto,
            "Repeticao": rep,
            "Qtd_Real": qtd_real,
            "Qtd_Predita": pred_count,
            "Erro_Absoluto": cont_res["erro_absoluto"],
            "Erro_Relativo_Pct": round(cont_res["erro_relativo_pct"], 2)
        })

        # Verificar se existe arquivo de anotação correspondente (.json do LabelMe)
        # Procurar no mesmo diretório ou na pasta desenvolvimento/anotacoes
        possible_json = [
            img_path.replace(".jpeg", ".json"),
            os.path.join("imagens", "desenvolvimento", f"{base_name}.json"),
            os.path.join("anotacoes", f"{base_name}.json")
        ]
        json_path = None
        for pj in possible_json:
            if os.path.exists(pj):
                json_path = pj
                break

        if json_path is not None:
            # Carregar ground truth
            gt_data = load_labelme_json(json_path, target_shape=res["original_img"].shape[:2])
            gt_boxes = gt_data["gt_boxes"]
            gt_mask = gt_data["global_mask"]

            pred_boxes = [[s["xmin"], s["ymin"], s["xmax"], s["ymax"]] for s in res["seeds"]]
            pred_mask = (res["labels"] > 0).astype(np.uint8) * 255

            det_eval = evaluate_detection(gt_boxes, pred_boxes, iou_threshold=0.50)
            seg_eval = evaluate_segmentation(gt_mask, pred_mask)

            anotadas_records.append({
                "Imagem": file_name,
                "Conjunto": conjunto,
                "Qtd_Real_GT": gt_data["count"],
                "Qtd_Predita": pred_count,
                "TP": det_eval["tp"],
                "FP": det_eval["fp"],
                "FN": det_eval["fn"],
                "Precision": round(det_eval["precision"], 4),
                "Recall": round(det_eval["recall"], 4),
                "F1_Score": round(det_eval["f1_score"], 4),
                "Mean_BBox_IoU": round(det_eval["mean_iou"], 4),
                "Dice_Pixel": round(seg_eval["dice"], 4),
                "Pixel_IoU": round(seg_eval["pixel_iou"], 4)
            })
            print(f"[{conjunto}] {file_name:<20} -> Real: {qtd_real:<2} | Pred: {pred_count:<2} | F1: {det_eval['f1_score']:.3f} | Dice: {seg_eval['dice']:.3f} (Anotada)")
        else:
            print(f"[{conjunto}] {file_name:<20} -> Real: {qtd_real:<2} | Pred: {pred_count:<2} | Erro: {cont_res['erro_absoluto']}")

    # DataFrames
    df_contagem = pd.DataFrame(contagem_records)
    df_contagem.to_csv(os.path.join(out_dir, "metricas_contagem_todas.csv"), index=False, encoding="utf-8")

    df_anotadas = pd.DataFrame(anotadas_records)
    if not df_anotadas.empty:
        df_anotadas.to_csv(os.path.join(out_dir, "metricas_anotadas_detec_seg.csv"), index=False, encoding="utf-8")

    df_all_seeds = pd.DataFrame(all_seeds_records)
    df_all_seeds.to_csv(os.path.join(out_dir, "morfometria_todas_sementes.csv"), index=False, encoding="utf-8")

    # Estatísticas Consolidadas
    stats_list = []
    for grupo, df_g in [("Geral (21 Imagens)", df_contagem),
                        ("Desenvolvimento (14 Imagens)", df_contagem[df_contagem["Conjunto"] == "Desenvolvimento"]),
                        ("Generalização (7 Imagens)", df_contagem[df_contagem["Conjunto"] == "Generalização"])]:
        mae = df_g["Erro_Absoluto"].mean()
        err_rel = df_g["Erro_Relativo_Pct"].mean()
        stats_list.append({
            "Grupo": grupo,
            "Total_Imagens": len(df_g),
            "MAE_Contagem": round(mae, 4),
            "Erro_Relativo_Medio_%": round(err_rel, 2),
            "Max_Erro_Absoluto": int(df_g["Erro_Absoluto"].max()),
            "Acuracia_Exata_%": round((df_g["Erro_Absoluto"] == 0).mean() * 100.0, 2)
        })

    df_stats_contagem = pd.DataFrame(stats_list)
    df_stats_contagem.to_csv(os.path.join(out_dir, "estatisticas_contagem.csv"), index=False, encoding="utf-8")

    if not df_anotadas.empty:
        det_stats = {
            "Métrica": ["Precision", "Recall", "F1_Score", "Mean_BBox_IoU", "Dice_Pixel", "Pixel_IoU"],
            "Média_Geral": [
                round(df_anotadas["Precision"].mean(), 4),
                round(df_anotadas["Recall"].mean(), 4),
                round(df_anotadas["F1_Score"].mean(), 4),
                round(df_anotadas["Mean_BBox_IoU"].mean(), 4),
                round(df_anotadas["Dice_Pixel"].mean(), 4),
                round(df_anotadas["Pixel_IoU"].mean(), 4)
            ],
            "Desvio_Padrão": [
                round(df_anotadas["Precision"].std(), 4),
                round(df_anotadas["Recall"].std(), 4),
                round(df_anotadas["F1_Score"].std(), 4),
                round(df_anotadas["Mean_BBox_IoU"].std(), 4),
                round(df_anotadas["Dice_Pixel"].std(), 4),
                round(df_anotadas["Pixel_IoU"].std(), 4)
            ]
        }
        df_det_stats = pd.DataFrame(det_stats)
        df_det_stats.to_csv(os.path.join(out_dir, "estatisticas_detec_seg.csv"), index=False, encoding="utf-8")

    print("\n" + "=" * 60)
    print("RESUMO ESTATÍSTICO DE CONTAGEM:")
    print(df_stats_contagem.to_string(index=False))
    if not df_anotadas.empty:
        print("\nRESUMO ESTATÍSTICO DE DETECÇÃO E SEGMENTAÇÃO (GROUND TRUTH):")
        print(df_det_stats.to_string(index=False))
    print("=" * 60)

    # =========================================================================
    # GERAÇÃO DE GRÁFICOS CIENTÍFICOS PARA O RELATÓRIO E APRESENTAÇÃO
    # =========================================================================
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 11

    # Gráfico 1: Dispersão e Regressão Contagem Real vs Predita
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = {"Desenvolvimento": "#1f77b4", "Generalização": "#2ca02c"}
    for conjunto, grp in df_contagem.groupby("Conjunto"):
        ax.scatter(grp["Qtd_Real"], grp["Qtd_Predita"], label=conjunto, s=90, alpha=0.85, c=colors.get(conjunto, "#333"), edgecolors="black")

    # Linha de identidade perfeita y = x
    min_val = min(df_contagem["Qtd_Real"].min(), df_contagem["Qtd_Predita"].min()) - 1
    max_val = max(df_contagem["Qtd_Real"].max(), df_contagem["Qtd_Predita"].max()) + 1
    ax.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=1.5, label="Identidade Ideal (y = x)")

    # Coeficiente R2
    corr = np.corrcoef(df_contagem["Qtd_Real"], df_contagem["Qtd_Predita"])[0, 1]
    r2 = corr ** 2
    mae_geral = df_contagem["Erro_Absoluto"].mean()

    ax.set_title(f"Contagem Real vs. Estimada pelo Algoritmo (21 Imagens)\n$R^2 = {r2:.4f}$ | MAE = {mae_geral:.3f} sementes", fontsize=13, fontweight="bold")
    ax.set_xlabel("Quantidade Real de Sementes ($N$)", fontsize=11)
    ax.set_ylabel("Quantidade Estimada pelo Pipeline ($\hat{N}$)", fontsize=11)
    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.legend(frameon=True, loc="upper left")
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "grafico_1_contagem_real_vs_predita.png"), dpi=300)
    plt.close(fig)

    # Gráfico 2: Erro Absoluto de Contagem por Imagem
    fig, ax = plt.subplots(figsize=(12, 5))
    x_indices = np.arange(len(df_contagem))
    bar_colors = ["#2ca02c" if c == "Generalização" else "#1f77b4" for c in df_contagem["Conjunto"]]
    bars = ax.bar(x_indices, df_contagem["Erro_Absoluto"], color=bar_colors, edgecolor="black", width=0.6)
    ax.set_xticks(x_indices)
    ax.set_xticklabels([f"{img.replace('.jpeg','')}" for img in df_contagem["Imagem"]], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Erro Absoluto ($|\hat{N} - N|$)", fontsize=11)
    ax.set_title("Erro Absoluto de Contagem por Imagem (Verde: Generalização | Azul: Desenvolvimento)", fontsize=13, fontweight="bold")
    ax.set_yticks(range(0, int(df_contagem["Erro_Absoluto"].max()) + 2))
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{int(h)}",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "grafico_2_erros_contagem_por_imagem.png"), dpi=300)
    plt.close(fig)

    # Gráfico 3: Métricas de Detecção e Segmentação (IoU, F1, Dice) nas Imagens Anotadas
    if not df_anotadas.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        metrics_cols = ["Precision", "Recall", "F1_Score", "Mean_BBox_IoU", "Dice_Pixel", "Pixel_IoU"]
        labels_pt = ["Precisão\n(BBox)", "Revocação\n(BBox)", "F1-Score\n(BBox)", "IoU Médio\n(BBox)", "Dice\n(Pixel)", "IoU\n(Pixel)"]
        means = [df_anotadas[m].mean() for m in metrics_cols]
        stds = [df_anotadas[m].std() for m in metrics_cols]

        x_pos = np.arange(len(metrics_cols))
        ax.bar(x_pos, means, yerr=stds, capsize=5, color="#3b528b", edgecolor="black", width=0.55, alpha=0.9)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels_pt, fontsize=11)
        ax.set_ylim(0.0, 1.1)
        ax.set_ylabel("Valor da Métrica [0 a 1]", fontsize=11)
        ax.set_title("Desempenho Médio de Identificação e Segmentação (Imagens Anotadas)", fontsize=13, fontweight="bold")

        for i, (m_val, s_val) in enumerate(zip(means, stds)):
            ax.text(i, m_val + 0.03, f"{m_val:.3f}", ha="center", va="bottom", fontweight="bold", fontsize=10)

        plt.tight_layout()
        fig.savefig(os.path.join(plots_dir, "grafico_3_metricas_deteccao_segmentacao.png"), dpi=300)
        plt.close(fig)

    # Gráfico 4: Distribuição Morfométrica de Circularidade e Área
    if not df_all_seeds.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Histograma de Circularidade
        ax1.hist(df_all_seeds["circularidade"], bins=20, color="#d95f02", edgecolor="black", alpha=0.85)
        ax1.axvline(df_all_seeds["circularidade"].mean(), color="black", linestyle="--", linewidth=1.5,
                    label=f"Média = {df_all_seeds['circularidade'].mean():.3f}")
        ax1.set_title("Distribuição da Circularidade das Sementes", fontsize=12, fontweight="bold")
        ax1.set_xlabel("Circularidade ($4\pi A / P^2$)", fontsize=11)
        ax1.set_ylabel("Frequência de Sementes", fontsize=11)
        ax1.legend()

        # Histograma de Área
        ax2.hist(df_all_seeds["area"], bins=20, color="#7570b3", edgecolor="black", alpha=0.85)
        ax2.axvline(df_all_seeds["area"].mean(), color="black", linestyle="--", linewidth=1.5,
                    label=f"Média = {df_all_seeds['area'].mean():.0f} px")
        ax2.set_title("Distribuição da Área em Pixels", fontsize=12, fontweight="bold")
        ax2.set_xlabel("Área (pixels)", fontsize=11)
        ax2.set_ylabel("Frequência de Sementes", fontsize=11)
        ax2.legend()

        plt.tight_layout()
        fig.savefig(os.path.join(plots_dir, "grafico_4_distribuicao_circularidade_area.png"), dpi=300)
        plt.close(fig)

    # Gráfico 5: Comparativo Desenvolvimento vs Generalização
    fig, ax = plt.subplots(figsize=(8, 5))
    grupos = ["Desenvolvimento", "Generalização"]
    maes = [
        df_contagem[df_contagem["Conjunto"] == "Desenvolvimento"]["Erro_Absoluto"].mean(),
        df_contagem[df_contagem["Conjunto"] == "Generalização"]["Erro_Absoluto"].mean()
    ]
    acuracias = [
        (df_contagem[df_contagem["Conjunto"] == "Desenvolvimento"]["Erro_Absoluto"] == 0).mean() * 100.0,
        (df_contagem[df_contagem["Conjunto"] == "Generalização"]["Erro_Absoluto"] == 0).mean() * 100.0
    ]

    x = np.arange(len(grupos))
    width = 0.35

    rects1 = ax.bar(x - width/2, maes, width, label="MAE (Erro Médio)", color="#e7298a", edgecolor="black")
    ax2 = ax.twinx()
    rects2 = ax2.bar(x + width/2, acuracias, width, label="Acurácia Exata (%)", color="#1b9e77", edgecolor="black")

    ax.set_ylabel("MAE (Erro Médio de Sementes)", fontsize=11, color="#e7298a")
    ax2.set_ylabel("Acurácia Exata de Contagem (%)", fontsize=11, color="#1b9e77")
    ax.set_xticks(x)
    ax.set_xticklabels(grupos, fontsize=12, fontweight="bold")
    ax.set_ylim(0, 0.5)
    ax2.set_ylim(0, 115)
    ax.set_title("Estabilidade e Generalização do Método", fontsize=13, fontweight="bold")

    for r in rects1:
        h = r.get_height()
        ax.annotate(f"{h:.3f}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontweight="bold")
    for r in rects2:
        h = r.get_height()
        ax2.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "grafico_5_comparativo_desenvolvimento_vs_generalizacao.png"), dpi=300)
    plt.close(fig)

    print(f"\nTodos os gráficos científicos foram salvos em: {plots_dir}")
    print("=" * 80)
    print("AVALIAÇÃO E GERAÇÃO DE ARTEFATOS CONCLUÍDAS COM SUCESSO!")
    print("=" * 80)

if __name__ == "__main__":
    main()
