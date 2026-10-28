import argparse
import os
import sys

# Garante importacao do modulo src tanto da raiz quanto internamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline import SeedSegmentationPipeline, save_image_robust

def main():
    parser = argparse.ArgumentParser(
        description="Identificação, segmentação, contagem e caracterização morfométrica de sementes sobre EVA."
    )
    parser.add_argument(
        "image_path",
        type=str,
        help="Caminho para o arquivo de imagem adquirido (ex.: imagens/desenvolvimento/sementes_15_1.jpeg)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="saidas",
        help="Diretório base para salvar as saídas visuais e tabulares (padrão: saidas)"
    )

    args = parser.parse_args()
    image_path = args.image_path
    output_dir = args.output_dir

    if not os.path.exists(image_path):
        print(f"Erro: Arquivo de imagem não encontrado no caminho: {image_path}")
        sys.exit(1)

    # Diretórios de saída
    vis_dir = os.path.join(output_dir, "visualizacoes")
    seg_dir = os.path.join(output_dir, "segmentadas")
    csv_dir = os.path.join(output_dir, "csv_imagens")
    os.makedirs(vis_dir, exist_ok=True)
    os.makedirs(seg_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)

    # Inicializa e executa o pipeline
    pipeline = SeedSegmentationPipeline()
    try:
        results = pipeline.process(image_path)
    except Exception as e:
        print(f"Erro durante o processamento da imagem: {e}")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(image_path))[0]

    # 1. Quantidade de sementes na imagem (saída de console obrigatória)
    total_seeds = results["count"]
    print("=" * 60)
    print(f"Processamento concluído com sucesso!")
    print(f"Imagem: {os.path.basename(image_path)}")
    print(f"Quantidade de sementes identificadas: {total_seeds}")
    print("=" * 60)

    # 2. Imagem contendo bounding boxes e contornos individuais
    vis_filename = os.path.join(vis_dir, f"{base_name}_contornos_bbox.jpeg")
    save_image_robust(vis_filename, results["vis_img"])

    # 3. Imagem com sementes segmentadas sobre fundo preto
    seg_filename = os.path.join(seg_dir, f"{base_name}_segmentadas_fundo_preto.jpeg")
    save_image_robust(seg_filename, results["segmented_black_bg"])

    # 4. Arquivo CSV com posições (bounding box), área, perímetro e circularidade
    csv_filename = os.path.join(csv_dir, f"{base_name}_metricas.csv")
    df = results["df_metrics"]
    df.to_csv(csv_filename, index=False, encoding="utf-8")

    print(f"Artefatos gerados:")
    print(f" - [Visualização BBox/Contornos]: {vis_filename}")
    print(f" - [Sementes em Fundo Preto]:     {seg_filename}")
    print(f" - [Planilha CSV de Métricas]:    {csv_filename}")
    print("=" * 60)

if __name__ == "__main__":
    main()
