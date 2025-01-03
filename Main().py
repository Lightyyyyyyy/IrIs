import speech_recognition as sr
import pyttsx3
import json
import difflib
import datetime
import requests
import time
from threading import Thread
import wikipedia
import cv2
import numpy as np

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 190)
engine.setProperty('volume', 1)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Initialize YOLO object detection model
yolo_net = cv2.dnn.readNet("C:/Users/snehi/Downloads/yolov3.weights", "C:/Users/snehi/Downloads/yolov3 (1).cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]

with open("C:/Users/snehi/Downloads/coco (1).names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Global variables
last_detected_object = None
camera_on = False


# Functions for assistant and object detection

def speak(text):
    print(f": {text}")
    engine.say(text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        try:
            audio = recognizer.listen(source)
            print("Recognizing...")
            command = recognizer.recognize_google(audio, language='en-in')
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            speak("Sorry, I didn't catch that.")
        except sr.RequestError:
            print("Sorry, there was an error.")
            speak("Sorry, there was an error.")
        return ""


def load_user_data():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_user_data(data):
    with open("users.json", "w") as file:
        json.dump(data, file)


def find_closest_match(user_voice, user_data):
    matches = difflib.get_close_matches(user_voice, user_data.keys(), n=1, cutoff=0.8)
    return matches[0] if matches else None


def authenticate_user():
    user_data = load_user_data()
    speak("Welcome! Please authenticate by saying the secret code.")
    user_voice = listen()

    if user_voice:
        matched_voice = find_closest_match(user_voice, user_data)
        if matched_voice:
            speak(f"Authentication successful. Welcome back, {user_data[matched_voice]}!")
            return user_data[matched_voice]
        else:
            speak("You are not recognized. Would you like to register?")
            if "register" in listen():
                speak("What is your name?")
                name = listen()
                if name:
                    user_data[user_voice] = name
                    save_user_data(user_data)
                    speak(f"Welcome, {name}! Your account has been created.")
                    return name
                else:
                    speak("Sorry, I couldn't register you. Please try again later.")
            else:
                speak("Authentication failed. Exiting.")
                return None
    else:
        speak("Could not recognize the voice. Exiting.")
        return None


def wish_me():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")


def get_weather(city):
    api_key = "fea380d0a30e28c5718845407f629e0b"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        if data.get("cod") != "404":
            main = data["main"]
            weather_desc = data["weather"][0]["description"]
            temp = main["temp"]
            report = f"The weather in {city} is {weather_desc} with a temperature of {temp}°C."
            speak(report)
            print(report)
        else:
            speak("City not found.")
    except requests.exceptions.RequestException as e:
        speak(f"Error fetching weather data: {e}")
        print(f"Error fetching weather data: {e}")


def set_alarm(alarm_time):
    speak(f"Alarm set for {alarm_time}.")
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")
        if current_time == alarm_time:
            speak("Wake up! It's time!")
            break
        time.sleep(1)


def add_reminder(task, remind_time):
    speak(f"Reminder set for {remind_time} to {task}.")
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")
        if current_time == remind_time:
            speak(f"Reminder: It's time to {task}.")
            break
        time.sleep(1)


def read_wikipedia(topic):
    speak(f"Searching Wikipedia for {topic}.")
    try:
        summary = wikipedia.summary(topic, sentences=3)
        speak(f"According to Wikipedia, {summary}")
        print(f"Wikipedia: {summary}")
    except wikipedia.DisambiguationError:
        speak("The topic is too ambiguous. Please be more specific.")
    except wikipedia.PageError:
        speak("Sorry, I couldn't find anything on Wikipedia for that topic.")
    except Exception as e:
        speak(f"An error occurred while fetching information from Wikipedia: {e}")
        print(f"Error: {e}")


def get_news():
    api_key = "0f14a79319c7478ea8c26ef04a4333e8"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "ok":
            articles = data.get("articles", [])[:3]
            speak("Here are the top news headlines.")
            for i, article in enumerate(articles, start=1):
                headline = article["title"]
                speak(f"News {i}: {headline}")
                print(f"News {i}: {headline}")
        else:
            speak("Sorry, I couldn't fetch the news at the moment.")
    except requests.exceptions.RequestException as e:
        speak(f"Error fetching news data: {e}")
        print(f"Error fetching news data: {e}")


def start_object_detection():
    global camera_on, last_detected_object
    if camera_on:
        speak("Camera is already on.")
        return

    camera_on = True
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened correctly
    if not cap.isOpened():
        speak("Unable to access the camera. Please check your camera connection.")
        print("Unable to access the camera.")
        camera_on = False
        return

    while camera_on:
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
                    speak("Detected " + label)
                    last_detected_object = label

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Object Detection - Closest Object", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    camera_on = False


def handle_query(query):
    global camera_on

    if 'hello' in query:
        speak("Hello there!")
        wish_me()
        speak("How may I help you?")

    elif 'how are you' in query:
        speak("I am fine. I hope you are doing well too.")

    elif 'weather' in query:
        speak("Please tell me the city name.")
        city = listen()
        if city:
            get_weather(city)

    elif 'set alarm' in query:
        speak("Please tell me the time to set the alarm in HH:MM format.")
        alarm_time = listen()
        if alarm_time:
            Thread(target=set_alarm, args=(alarm_time,)).start()

    elif 'reminder' in query:
        speak("What should I remind you about?")
        task = listen()
        if task:
            speak("Please tell me the time for the reminder in HH:MM format.")
            remind_time = listen()
            if remind_time:
                Thread(target=add_reminder, args=(task, remind_time)).start()

    elif 'wikipedia' in query:
        speak("What topic would you like me to search on Wikipedia?")
        topic = listen()
        if topic:
            read_wikipedia(topic)

    elif 'news' in query:
        get_news()

    elif 'camera on' in query and not camera_on:
        speak("Turning on the camera for object detection.")
        Thread(target=start_object_detection).start()

    elif 'terminate' in query and camera_on:
        speak("Terminating object detection and returning to normal mode.")
        camera_on = False

    elif any(word in query for word in ['bye', 'exit', 'quit', 'stop']):
        speak("Goodbye! Call me any time!")
        return False

    else:
        speak("This was an inappropriate command")

    return True


if _name_ == "_main_":
    user_name = authenticate_user()

    if user_name:
        wish_me()
        speak(f"I am Iris. How may I help you, {user_name}?")

        while True:
            query = listen()
            if query:
                if not handle_query(query):
                    break