import ctypes
import os, sys
import cv2

dll_path = ".dll path ( with windows)"
safetensors_path = ".safetensors path"
input_image_path = "target image"

class Detection(ctypes.Structure):
    _fields_ = [
        ("xmin", ctypes.c_float),
        ("ymin", ctypes.c_float),
        ("xmax", ctypes.c_float),
        ("ymax", ctypes.c_float),
        ("confidence", ctypes.c_float),
        ("class_index", ctypes.c_uint32),
    ]

def load_dll(dll_path):
    if not os.path.exists(dll_path):
        print(f"Error: .dll file not found at {dll_path}")
        sys.exit(1)

    dll = ctypes.CDLL(dll_path)
    dll.get_core_info.argtypes = []
    dll.get_core_info.restype = ctypes.POINTER(ctypes.c_char)

    dll.free_string.argtypes = [ctypes.POINTER(ctypes.c_char)]
    dll.free_string.restype = None

    dll.load_model.argtypes = [ctypes.c_char_p]
    dll.load_model.restype = ctypes.c_int

    dll.set_confidence_threshold.argtypes = [ctypes.c_float]
    dll.set_confidence_threshold.restype = ctypes.c_int

    dll.set_nms_iou_threshold.argtypes = [ctypes.c_float]
    dll.set_nms_iou_threshold.restype = ctypes.c_int

    dll.run_inference.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.POINTER(Detection)), ctypes.POINTER(ctypes.c_int32)]
    dll.run_inference.restype = ctypes.c_int

    dll.free_detections.argtypes = [ctypes.POINTER(Detection), ctypes.c_int32]
    dll.free_detections.restype = None

    return dll

def load_safetensors(dll, safetensors_path):
    if not os.path.exists(safetensors_path):
        print(f"Error: .safetensors file not found at {safetensors_path}")
        sys.exit(1)
    result = dll.load_model(safetensors_path.encode('utf-8'))
    if result != 0:
        print(f"Error loading model: {result}")
        sys.exit(1)
    print("Model loaded successfully")

def run_inference(dll, image_path, num_classes=1, model_size=640):
    """
    Run inference on an image and return filtered detections.
    
    Args:
        dll: Loaded DLL object
        image_path: Path to input image
        num_classes: Number of classes in your model (default: 1)
        model_size: Model input size (default: 640)
    
    Returns:
        List of detection dictionaries with 'class_index', 'confidence', and 'bbox'
    """
    if not os.path.exists(image_path):
        print(f"Error: image file not found at {image_path}")
        return []
    
    # Get image dimensions for coordinate scaling
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image")
        return []
    
    orig_h, orig_w = img.shape[:2]
    x_scale = orig_w / model_size
    y_scale = orig_h / model_size
    
    print(f"Image size: {orig_w}x{orig_h}, Model size: {model_size}x{model_size}, Scale: {x_scale:.3f}x{y_scale:.3f}")

    # Run inference
    detections_ptr = ctypes.POINTER(Detection)()
    detections_len = ctypes.c_int32(0)
    result = dll.run_inference(image_path.encode('utf-8'), ctypes.byref(detections_ptr), ctypes.byref(detections_len))
    
    if result != 0:
        print(f"Error: Inference failed with code {result}")
        return []
    
    # Filter and convert detections
    valid_detections = []
    for i in range(detections_len.value):
        det = detections_ptr[i]
        
        # Filter invalid class indices (caused by DLL reading wrong memory layout)
        if det.class_index >= num_classes:
            continue
        
        # Filter invalid confidence
        if not (0.0 <= det.confidence <= 1.0):
            continue
        
        # Rust code now outputs normalized center+wh format: (center_x, center_y, width, height)
        # All values are normalized [0, 1] matching ground truth format
        # Format: class center_x center_y width height (all normalized)
        
        # Convert from normalized center+wh to pixel coordinates
        center_x_norm = det.xmin  # Normalized center_x [0, 1]
        center_y_norm = det.ymin  # Normalized center_y [0, 1]
        width_norm = det.xmax     # Normalized width [0, 1]
        height_norm = det.ymax    # Normalized height [0, 1]
        
        # Convert to pixel coordinates on original image
        center_x_px = center_x_norm * orig_w
        center_y_px = center_y_norm * orig_h
        width_px = width_norm * orig_w
        height_px = height_norm * orig_h
        
        # Convert center+wh to xmin, ymin, xmax, ymax
        xmin = center_x_px - width_px / 2.0
        ymin = center_y_px - height_px / 2.0
        xmax = center_x_px + width_px / 2.0
        ymax = center_y_px + height_px / 2.0
        
        # Validate bbox
        if xmax <= xmin or ymax <= ymin:
            continue
        
        # Clip to image bounds
        xmin = max(0, min(xmin, orig_w))
        ymin = max(0, min(ymin, orig_h))
        xmax = max(0, min(xmax, orig_w))
        ymax = max(0, min(ymax, orig_h))
        
        valid_detections.append({
            "class_index": det.class_index,
            "confidence": det.confidence,
            "bbox": [xmin, ymin, xmax, ymax]
        })
    
    # Free memory
    dll.free_detections(detections_ptr, detections_len)
    
    print(f"Found {len(valid_detections)} valid detections (filtered from {detections_len.value} raw)")
    return valid_detections

if __name__ == "__main__":
    NUM_CLASSES = 1  # Change this to match your model's number of classes
    CONFIDENCE_THRESHOLD = 0.025  # Lower for models with low confidence scores (0.0 to 1.0)
    NMS_IOU_THRESHOLD = 0.45  # 0.0 to 1.0

    dll = load_dll(dll_path)
    load_safetensors(dll, safetensors_path)
    
    # Optional: Set confidence threshold (default is 0.25)
    # Lower values = more detections (more false positives)
    # Higher values = fewer detections (more confident)
    dll.set_confidence_threshold(CONFIDENCE_THRESHOLD)
    dll.set_nms_iou_threshold(NMS_IOU_THRESHOLD)
    
    detections = run_inference(dll, input_image_path, num_classes=NUM_CLASSES)