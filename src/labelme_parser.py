import json
import numpy as np
import cv2
import os

def load_labelme_json(json_path, target_shape=(900, 1600)):
    """
    Carrega as anotações geradas pelo LabelMe em formato JSON.
    Suporta shapes do tipo 'polygon' e 'circle'.
    
    Retorna:
        dict:
            - 'shapes': lista dos shapes originais
            - 'gt_boxes': lista de bboxes [xmin, ymin, xmax, ymax]
            - 'gt_masks': lista de máscaras individuais (uint8, 0 ou 255)
            - 'global_mask': máscara binária combinada de todas as sementes (uint8)
            - 'gt_metrics': lista de métricas morfológicas individuais de referência
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Arquivo de anotação não encontrado: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    img_h = data.get("imageHeight") or target_shape[0]
    img_w = data.get("imageWidth") or target_shape[1]
    shape_dim = (img_h, img_w)

    gt_boxes = []
    gt_masks = []
    gt_metrics = []
    global_mask = np.zeros(shape_dim, dtype=np.uint8)

    for idx, shape in enumerate(data.get("shapes", []), start=1):
        points = shape.get("points", [])
        shape_type = shape.get("shape_type", "polygon")
        if not points:
            continue

        mask_i = np.zeros(shape_dim, dtype=np.uint8)

        if shape_type == "circle" and len(points) >= 2:
            center = (int(round(points[0][0])), int(round(points[0][1])))
            radius_pt = (points[1][0], points[1][1])
            radius = int(round(np.hypot(center[0] - radius_pt[0], center[1] - radius_pt[1])))
            cv2.circle(mask_i, center, radius, 255, -1)
            xmin = max(0, center[0] - radius)
            ymin = max(0, center[1] - radius)
            xmax = min(img_w - 1, center[0] + radius)
            ymax = min(img_h - 1, center[1] + radius)
        else: # polygon
            pts = np.array(points, dtype=np.float32)
            pts_int = np.array(points, dtype=np.int32)
            cv2.fillPoly(mask_i, [pts_int], 255)
            xmin = max(0, int(round(pts[:, 0].min())))
            ymin = max(0, int(round(pts[:, 1].min())))
            xmax = min(img_w - 1, int(round(pts[:, 0].max())))
            ymax = min(img_h - 1, int(round(pts[:, 1].max())))

        global_mask = cv2.bitwise_or(global_mask, mask_i)
        bbox = [xmin, ymin, xmax, ymax]
        gt_boxes.append(bbox)
        gt_masks.append(mask_i)

        cnts, _ = cv2.findContours(mask_i, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            area = float(cv2.contourArea(c))
            perim = float(cv2.arcLength(c, True))
            circ = (4.0 * np.pi * area) / (perim ** 2) if perim > 0 else 0.0
        else:
            area = float(cv2.countNonZero(mask_i))
            perim = 0.0
            circ = 0.0

        gt_metrics.append({
            "id": idx,
            "bbox": bbox,
            "area": area,
            "perimetro": perim,
            "circularidade": circ
        })

    return {
        "count": len(gt_boxes),
        "gt_boxes": gt_boxes,
        "gt_masks": gt_masks,
        "global_mask": global_mask,
        "gt_metrics": gt_metrics
    }
