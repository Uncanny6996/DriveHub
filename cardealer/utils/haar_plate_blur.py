import cv2
import requests

# Your Plate Recognizer API token here
API_TOKEN = '77646d802e111a1ec7fe4adf7ad5fc9c1cb7536e'

def call_plate_recognizer_api(image_path):
    """Send image to Plate Recognizer API and return detected plate bounding boxes."""
    url = "https://api.platerecognizer.com/v1/plate-reader/"
    headers = {
        "Authorization": f"Token {API_TOKEN}"
    }
    with open(image_path, 'rb') as img_file:
        files = {'upload': img_file}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code != 200:
        print(f"[API ERROR] Status code: {response.status_code} - {response.text}")
        return []

    data = response.json()
    print(f"[DEBUG API RESPONSE] {data}") 
    boxes = []
    for result in data.get('results', []):
        box = result.get('box')
        if box:
            # Box has xmin, ymin, xmax, ymax
            xmin, ymin, xmax, ymax = box['xmin'], box['ymin'], box['xmax'], box['ymax']
            width = xmax - xmin
            height = ymax - ymin
            boxes.append((xmin, ymin, width, height))
    return boxes

def blur_regions(image, boxes):
    """Apply Gaussian blur on given regions of the image."""
    h, w = image.shape[:2]
    for idx, (x, y, bw, bh) in enumerate(boxes):
        x, y, bw, bh = map(int, (x, y, bw, bh))

        # Clip coordinates inside image bounds
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        bw = max(1, min(bw, w - x))
        bh = max(1, min(bh, h - y))

        # Debug info
        print(f"[DEBUG] Blurring plate #{idx}: x={x}, y={y}, w={bw}, h={bh}, image size=({w}, {h})")

        plate_region = image[y:y+bh, x:x+bw]
        if plate_region.size == 0:
            print(f"[DEBUG] Empty region detected, skipping blur for plate #{idx}")
            continue
        blurred = cv2.GaussianBlur(plate_region, (99, 99), 30)
        image[y:y+bh, x:x+bw] = blurred

def blur_plate_with_haar(image_path):
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        print(f"[DEBUG] Image shape: {image.shape}")

        # First try API detection
        api_boxes = call_plate_recognizer_api(image_path)

        if api_boxes:
            print(f"[INFO] API detected {len(api_boxes)} plates in {image_path}")
            blur_regions(image, api_boxes)
        else:
            # Fallback to Haar Cascade detection
            print(f"[INFO] API detected no plates, falling back to Haar cascade")

            plate_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
            )

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            plates = plate_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(30, 30),
            )

            if len(plates) == 0:
                print(f"[INFO] Haar cascade detected no plates in {image_path}")
            else:
                print(f"[INFO] Haar cascade detected {len(plates)} plates in {image_path}")
                blur_regions(image, plates)

        # Save the processed image (overwrite original)
        cv2.imwrite(image_path, image)
        print(f"[INFO] Blurred image saved: {image_path}")

    except Exception as e:
        print(f"[ERROR] {e}")
