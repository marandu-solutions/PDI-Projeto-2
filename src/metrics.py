import numpy as np

def bbox_iou(box_a, box_b):
    """
    Calcula a Intersection over Union (IoU) entre duas Bounding Boxes [xmin, ymin, xmax, ymax].
    """
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    inter_width = max(0, x_b - x_a)
    inter_height = max(0, y_b - y_a)
    inter_area = inter_width * inter_height

    box_a_area = max(0, box_a[2] - box_a[0]) * max(0, box_a[3] - box_a[1])
    box_b_area = max(0, box_b[2] - box_b[0]) * max(0, box_b[3] - box_b[1])

    union_area = float(box_a_area + box_b_area - inter_area)
    if union_area <= 0:
        return 0.0
    return inter_area / union_area

def evaluate_detection(gt_boxes, pred_boxes, iou_threshold=0.50):
    """
    Avalia a identificação e localização por bounding boxes:
    Associação 1-para-1 gulosa por maior IoU.
    
    Retorna:
        dict com:
            - tp, fp, fn
            - precision, recall, f1_score
            - mean_iou: qualidade média de localização entre os TPs
    """
    if len(gt_boxes) == 0 and len(pred_boxes) == 0:
        return {
            "tp": 0, "fp": 0, "fn": 0,
            "precision": 1.0, "recall": 1.0, "f1_score": 1.0,
            "mean_iou": 1.0, "matched_ious": []
        }
    if len(gt_boxes) == 0:
        return {
            "tp": 0, "fp": len(pred_boxes), "fn": 0,
            "precision": 0.0, "recall": 1.0, "f1_score": 0.0,
            "mean_iou": 0.0, "matched_ious": []
        }
    if len(pred_boxes) == 0:
        return {
            "tp": 0, "fp": 0, "fn": len(gt_boxes),
            "precision": 1.0, "recall": 0.0, "f1_score": 0.0,
            "mean_iou": 0.0, "matched_ious": []
        }

    # Matriz de IoU
    iou_matrix = np.zeros((len(pred_boxes), len(gt_boxes)), dtype=np.float32)
    for p_idx, p_box in enumerate(pred_boxes):
        for g_idx, g_box in enumerate(gt_boxes):
            iou_matrix[p_idx, g_idx] = bbox_iou(p_box, g_box)

    matched_pred = set()
    matched_gt = set()
    matched_ious = []

    # Matching ordenado pelo maior IoU
    pairs = []
    for p_idx in range(len(pred_boxes)):
        for g_idx in range(len(gt_boxes)):
            val = iou_matrix[p_idx, g_idx]
            if val >= iou_threshold:
                pairs.append((val, p_idx, g_idx))

    pairs.sort(key=lambda x: x[0], reverse=True)

    for val, p_idx, g_idx in pairs:
        if p_idx not in matched_pred and g_idx not in matched_gt:
            matched_pred.add(p_idx)
            matched_gt.add(g_idx)
            matched_ious.append(val)

    tp = len(matched_gt)
    fp = len(pred_boxes) - len(matched_pred)
    fn = len(gt_boxes) - len(matched_gt)

    precision = tp / float(tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / float(tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    mean_iou = float(np.mean(matched_ious)) if matched_ious else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "mean_iou": mean_iou,
        "matched_ious": matched_ious
    }

def evaluate_segmentation(gt_mask, pred_mask):
    """
    Avalia a qualidade da segmentação no nível de pixel:
    - Dice Similarity Coefficient
    - Jaccard Index (IoU pixelar)
    - Pixels TP, FP, FN
    """
    gt_bool = (gt_mask > 0)
    pred_bool = (pred_mask > 0)

    tp_pix = int(np.logical_and(gt_bool, pred_bool).sum())
    fp_pix = int(np.logical_and(~gt_bool, pred_bool).sum())
    fn_pix = int(np.logical_and(gt_bool, ~pred_bool).sum())

    total_gt = int(gt_bool.sum())
    total_pred = int(pred_bool.sum())

    dice_denom = float(total_gt + total_pred)
    dice = (2.0 * tp_pix) / dice_denom if dice_denom > 0 else 1.0

    union_pix = float(tp_pix + fp_pix + fn_pix)
    pixel_iou = tp_pix / union_pix if union_pix > 0 else 1.0

    return {
        "tp_pix": tp_pix,
        "fp_pix": fp_pix,
        "fn_pix": fn_pix,
        "dice": float(dice),
        "pixel_iou": float(pixel_iou)
    }

def evaluate_counting(real_count, pred_count):
    """
    Avalia a qualidade da contagem global.
    """
    err_abs = abs(pred_count - real_count)
    err_rel_pct = (err_abs / float(real_count)) * 100.0 if real_count > 0 else 0.0
    return {
        "real": real_count,
        "pred": pred_count,
        "erro_absoluto": err_abs,
        "erro_relativo_pct": err_rel_pct
    }

def calculate_summary_stats(values):
    """
    Retorna estatísticas descritivas (média, mediana, desvio padrão, CV%).
    """
    if len(values) == 0:
        return {"mean": 0.0, "median": 0.0, "std": 0.0, "cv_pct": 0.0}
    arr = np.array(values, dtype=np.float64)
    mean_val = float(np.mean(arr))
    med_val = float(np.median(arr))
    std_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    cv_pct = (std_val / mean_val * 100.0) if mean_val != 0 else 0.0
    return {
        "mean": mean_val,
        "median": med_val,
        "std": std_val,
        "cv_pct": cv_pct
    }
