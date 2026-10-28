import os
import cv2
import numpy as np
import pandas as pd
from skimage.feature import peak_local_max
from skimage.segmentation import watershed

def read_image_robust(image_path):
    """
    Carrega imagem suportando caracteres não-ASCII (acentos) no Windows.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Arquivo de imagem não encontrado: {image_path}")
    data = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Não foi possível decodificar a imagem: {image_path}")
    return img

def save_image_robust(output_path, img):
    """
    Salva imagem suportando caracteres especiais no Windows.
    """
    ext = os.path.splitext(output_path)[1]
    if not ext:
        ext = ".jpeg"
        output_path += ext
    is_success, buffer = cv2.imencode(ext, img)
    if is_success:
        with open(output_path, "wb") as f:
            f.write(buffer)
    else:
        raise IOError(f"Falha ao codificar a imagem para salvar em: {output_path}")

class SeedSegmentationPipeline:
    """
    Pipeline de Processamento Digital de Imagens para segmentação,
    contagem e caracterização morfométrica de sementes sobre EVA.
    """
    def __init__(self, color_threshold=126, min_peak_distance=20, min_peak_abs=5, min_seed_area=300):
        self.color_threshold = color_threshold
        self.min_peak_distance = min_peak_distance
        self.min_peak_abs = min_peak_abs
        self.min_seed_area = min_seed_area

    def process(self, image_input):
        """
        Executa todas as etapas do pipeline a partir do caminho ou matriz de imagem.
        
        Retorna:
            dict com:
                - 'original_img': imagem BGR original
                - 'bin_mask': máscara binária limpa
                - 'labels': mapa de rótulos do Watershed
                - 'count': quantidade de sementes identificadas
                - 'seeds': lista de dicionários com métricas e bboxes de cada semente
                - 'vis_img': imagem com contornos e bounding boxes desenhados
                - 'segmented_black_bg': imagem das sementes sobre fundo preto
                - 'df_metrics': DataFrame do pandas com as métricas individuais
        """
        if isinstance(image_input, str):
            img = read_image_robust(image_input)
        else:
            img = image_input.copy()

        h, w = img.shape[:2]

        # 1. Espaço de Cores CIE-Lab: canal a* separa com precisão sementes avermelhadas do EVA verde
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        _, a_channel, _ = cv2.split(lab)

        # 2. Suavização Gaussiana para atenuar micro-textura do EVA
        blur_a = cv2.GaussianBlur(a_channel, (5, 5), 0)

        # 3. Limiarização no canal a*
        _, bin_a = cv2.threshold(blur_a, self.color_threshold, 255, cv2.THRESH_BINARY)

        # 4. Operação Morfológica de Abertura para eliminar ruídos de borda
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        bin_clean = cv2.morphologyEx(bin_a, cv2.MORPH_OPEN, kernel_open, iterations=1)

        # 5. Transformada de Distância Euclidiana
        dist = cv2.distanceTransform(bin_clean, cv2.DIST_L2, 5)

        # 6. Detecção de Picos Locais (Centros das Sementes, inclusive em contato)
        coords = peak_local_max(
            dist,
            min_distance=self.min_peak_distance,
            threshold_abs=self.min_peak_abs
        )

        # 7. Construção dos Marcadores para o Watershed
        markers = np.zeros(dist.shape, dtype=np.int32)
        for idx, (r, c) in enumerate(coords, start=1):
            markers[r, c] = idx

        # 8. Watershed Guiado pela Distância Invertida dentro da Máscara
        if len(coords) > 0:
            labels = watershed(-dist, markers, mask=bin_clean)
        else:
            labels = np.zeros(dist.shape, dtype=np.int32)

        # 9. Extração Individual de Contornos, Bounding Boxes e Morfometria
        seeds = []
        valid_id = 1
        refined_labels = np.zeros(labels.shape, dtype=np.int32)

        for l_idx in range(1, len(coords) + 1):
            seed_mask = (labels == l_idx).astype(np.uint8)
            area_px = int(cv2.countNonZero(seed_mask))

            # Filtragem de segurança contra ruídos minúsculos
            if area_px < self.min_seed_area:
                continue

            cnts, _ = cv2.findContours(seed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not cnts:
                continue
            c = max(cnts, key=cv2.contourArea)
            perim_px = float(cv2.arcLength(c, True))
            circ = (4.0 * np.pi * area_px) / (perim_px ** 2) if perim_px > 0 else 0.0

            x, y, bw, bh = cv2.boundingRect(c)
            bbox = [int(x), int(y), int(x + bw), int(y + bh)]

            refined_labels[seed_mask > 0] = valid_id

            seeds.append({
                "id_semente": valid_id,
                "xmin": bbox[0],
                "ymin": bbox[1],
                "xmax": bbox[2],
                "ymax": bbox[3],
                "area": area_px,
                "perimetro": round(perim_px, 2),
                "circularidade": round(circ, 4),
                "contour": c
            })
            valid_id += 1

        total_count = len(seeds)

        # 10. Geração das Saídas Visuais Obrigatórias
        # Saída Visual 1: Imagem com Bounding Boxes e Contornos Individuais
        vis_img = img.copy()
        for s in seeds:
            # Desenha contorno em verde
            cv2.drawContours(vis_img, [s["contour"]], -1, (0, 255, 0), 2)
            # Desenha bounding box em azul ciano
            cv2.rectangle(vis_img, (s["xmin"], s["ymin"]), (s["xmax"], s["ymax"]), (255, 255, 0), 2)
            # Rótulo de identificação
            label_text = f"#{s['id_semente']}"
            cv2.putText(
                vis_img, label_text, (s["xmin"], max(15, s["ymin"] - 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2
            )

        # Saída Visual 2: Imagem com Sementes Segmentadas (Pixels Originais) sobre Fundo Preto
        segmented_black_bg = np.zeros_like(img)
        binary_seeds_mask = (refined_labels > 0).astype(np.uint8) * 255
        segmented_black_bg[binary_seeds_mask == 255] = img[binary_seeds_mask == 255]

        # Saída Tabular: DataFrame
        records = [{k: v for k, v in s.items() if k != "contour"} for s in seeds]
        df_metrics = pd.DataFrame(records)

        return {
            "original_img": img,
            "bin_mask": bin_clean,
            "labels": refined_labels,
            "count": total_count,
            "seeds": seeds,
            "vis_img": vis_img,
            "segmented_black_bg": segmented_black_bg,
            "df_metrics": df_metrics
        }
