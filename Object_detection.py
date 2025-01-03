import cv2
import numpy as np
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

yolo_net = cv2.dnn.readNet("C:/Users/snehi/Downloads/yolov3.weights", "C:/Users/snehi/Downloads/yolov3 (1).cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]

with open("C:/Users/snehi/Downloads/coco (1).names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

cap = cv2.VideoCapture(0)

last_detected_object = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    yolo_net.setInput(blob)
    detections = yolo_net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(obj[0] * frame.shape[1])
                center_y = int(obj[1] * frame.shape[0])
                w = int(obj[2] * frame.shape[1])
                h = int(obj[3] * frame.shape[0])

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    if len(indices) > 0:
        indices = indices.flatten()
        closest_object = None
        max_area = 0

        for i in indices:
            x, y, w, h = boxes[i]
            area = w * h
            if area > max_area:
                max_area = area
                closest_object = (x, y, w, h, class_ids[i])

        if closest_object:
            x, y, w, h, class_id = closest_object
            label = str(classes[class_id])

            if label != last_detected_object:
                print("Detected Object:", label)
                engine.say("Detected " + label)
                engine.runAndWait()
                last_detected_object = label

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Object Detection - Closest Object", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()