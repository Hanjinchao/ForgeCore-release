import ctypes
import os, sys

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

def run_inference(dll, safetensors_path, image_path):
    if not os.path.exists(image_path):
        print(f"Error: image file not found at {image_path}")
        sys.exit(1)
    detections_ptr = ctypes.POINTER(Detection)()
    detections_len = ctypes.c_int32(0)

    result = dll.run_inference(image_path.encode('utf-8'), ctypes.byref(detections_ptr), ctypes.byref(detections_len))
    if result == 0:
        print(f"Found {detections_len.value} detections:")
        for i in range(detections_len.value):
            det = detections_ptr[i]
            print(f"  Detection {i}: class={det.class_index}, confidence={det.confidence:.2f}, "
                  f"bbox=({det.xmin:.1f}, {det.ymin:.1f}, {det.xmax:.1f}, {det.ymax:.1f})")
    else:
        print(f"Error: failed to run inference: {result}")

if __name__ == "__main__":
    dll = load_dll(dll_path)
    load_safetensors(dll, safetensors_path)
    
    # Optional: Set confidence threshold (default is 0.25)
    # Lower values = more detections (more false positives)
    # Higher values = fewer detections (more confident)
    confidence_threshold = 0.008  # Change this value as needed (0.0 to 1.0)
    result = dll.set_confidence_threshold(confidence_threshold)
    if result != 0:
        print(f"Error setting confidence threshold: {result}")
    
    # Optional: Set NMS IoU threshold (default is 0.45)
    # Lower values = more aggressive merging (fewer duplicates)
    # Higher values = less aggressive (keeps more separate detections)
    nms_iou_threshold = 0.45  # Change this value as needed (0.0 to 1.0)
    result = dll.set_nms_iou_threshold(nms_iou_threshold)
    if result != 0:
        print(f"Error setting NMS IoU threshold: {result}")
    
    run_inference(dll, safetensors_path, input_image_path)