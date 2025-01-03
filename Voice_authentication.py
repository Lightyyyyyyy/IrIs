import speech_recognition as sr
import pyttsx3
import json
import difflib

def speak(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()
    
def recognize_user():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        speak("Listening...")
        try:
            audio = recognizer.listen(source)
            user_voice = recognizer.recognize_google(audio)
            return user_voice.lower().strip()
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            speak("Sorry, I could not understand the audio.")
            return None

def load_user_data():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open("users.json", "w") as file:
        json.dump(data, file)

def sign_up(user_voice):
    speak("You are not recognized. Please sign up.")
    print("What is your name?")
    speak("What is your name?")
    name = recognize_user()
    if name:
        user_data[user_voice] = name
        save_user_data(user_data)
        print("Welcome, {name}! Your account has been created.")
        speak(f"Welcome, {name}! Your account has been created.")
    else:
        speak("Sorry, I could not recognize your name. Please try again.")

def find_closest_match(user_voice, user_data):
    matches = difflib.get_close_matches(user_voice, user_data.keys(), n=1, cutoff=0.8)
    return matches[0] if matches else None

if __name__ == "__main__":
    user_data = load_user_data()

    speak("welcome ! ,please say the secret code!")
    user_voice = recognize_user()

    if user_voice:
        matched_voice = find_closest_match(user_voice, user_data)
        if matched_voice:
            speak(f"Welcome back, {user_data[matched_voice]}!")
        else:
            sign_up(user_voice)
    else:
        speak("Could not recognize the user. Exiting.")