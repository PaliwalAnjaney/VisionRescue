# vision_rescue.py

import threading
import cv2
from deepface import DeepFace
import os

UPLOAD_FOLDER = "static/uploads"

def verify_face(reference_path, frame):
    try:
        return DeepFace.verify(frame, reference_path)['verified']
    except ValueError:
        return False

def runcameracheck():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    uploaded_images = [
        os.path.join(UPLOAD_FOLDER, f)
        for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith(("jpg", "jpeg", "png"))
    ]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        match_found = None
        for img_path in uploaded_images:
            if verify_face(img_path, frame):
                match_found = img_path
                break

        if match_found:
            label = "Match Found!"
            color = (0, 255, 0)
            update_report_status(match_found)
        else:
            label = "No Match"
            color = (0, 0, 255)

        cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.imshow("Vision Rescue Live", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

def update_report_status(filename_path):
    import json

    filename = os.path.basename(filename_path)
    try:
        with open("reports.json", "r") as f:
            reports = []
            for line in f:
                try:
                    item = json.loads(line)
                    if isinstance(item, list):
                        reports.extend(item)
                    else:
                        reports.append(item)
                except json.JSONDecodeError as e:
                    print("Skipping bad line:", e)

        for r in reports:
            if r["filename"] == filename:
                r["status"] = "found"

        with open("reports.json", "w") as f:
            for r in reports:
                f.write(json.dumps(r) + "\n")

    except Exception as e:
        print("Failed to update report status:", e)