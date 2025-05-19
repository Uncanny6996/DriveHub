import cv2

def blur_plate_with_haar(image_path):
    try:
        # Load the Haar cascade
        plate_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
        )

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect plates with tuned params
        plates = plate_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,  # You can try 2 or 4 if needed
            minSize=(30, 30),  # Decrease if plates are too small
        )

        if len(plates) == 0:
            print(f"[INFO] No plates detected in {image_path}")
        else:
            print(f"[INFO] Detected {len(plates)} plates in {image_path}")

        # Apply Gaussian blur
        for (x, y, w, h) in plates:
            plate_region = image[y:y+h, x:x+w]
            blurred = cv2.GaussianBlur(plate_region, (99, 99), 30)
            image[y:y+h, x:x+w] = blurred

        # Overwrite original
        cv2.imwrite(image_path, image)

    except Exception as e:
        print(f"[HAAR ERROR] {e}")
