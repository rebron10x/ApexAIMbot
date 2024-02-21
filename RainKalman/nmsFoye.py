import numpy as np

def nms(infer_result: np.ndarray,  
        conf_thres: float, 
        sigma: float, 
        iou_thres: float) -> np.ndarray:
    """非极大值抑制"""
    pred = np.squeeze(infer_result)

    conf_mask = pred[..., 4] > conf_thres
    boxes = pred[conf_mask]
    scores = boxes[:, 4]
    classes = np.argmax(boxes[:, 5:], axis=-1)
    unique_classes = np.unique(classes)

    output = []
    for cls in unique_classes:
        cls_mask = classes == cls
        cls_boxes = boxes[cls_mask]
        cls_scores = scores[cls_mask]
        cls_boxes[:, 5] = cls

        cls_boxes[:, 0] -= cls_boxes[:, 2] / 2
        cls_boxes[:, 1] -= cls_boxes[:, 3] / 2
        cls_boxes[:, 2] += cls_boxes[:, 0]
        cls_boxes[:, 3] += cls_boxes[:, 1]

        order = cls_scores.argsort()[::-1]
        
        while order.size > 0:
            i = order[0]
            output.append(cls_boxes[i])

            cls_boxes_order = cls_boxes[order[1:], :]
            w = np.maximum(0.0, (np.minimum(cls_boxes[i, 2], cls_boxes_order[:, 2]) - np.maximum(cls_boxes[i, 0], cls_boxes_order[:, 0])))
            h = np.maximum(0.0, (np.minimum(cls_boxes[i, 3], cls_boxes_order[:, 3]) - np.maximum(cls_boxes[i, 1], cls_boxes_order[:, 1])))
            inter = w * h
            ovr_denominator = (cls_boxes[i, 2] - cls_boxes[i, 0]) * (cls_boxes[i, 3] - cls_boxes[i, 1]) + (cls_boxes_order[:, 2] - cls_boxes_order[:, 0]) * (cls_boxes_order[:, 3] - cls_boxes_order[:, 1]) - inter
            ovr = inter / ovr_denominator

            weight = np.exp(-(ovr ** 2) / sigma)
            cls_scores[order[1:]] *= weight
            inds = np.where(cls_scores[order[1:]] > iou_thres)[0]
            order = order[inds + 1]

    result = np.array(output)
    result = [sublist[:-1] for sublist in result]
    return result if output else np.empty((0, 6))
