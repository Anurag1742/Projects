import pyttsx3
import speech_recognition
import requests
from bs4 import BeautifulSoup

engine = pyttsx3.init("sapi5")  # sapi5 is a Microsoft Speech API
voices = engine.getProperty("voices")  # get the voices
engine.setProperty("voice", voices[1].id)  # set the voice
engine.setProperty("rate", 170)  # set the rate of speech


def speak(audio):  # function to speak
    engine.say(audio)
    engine.runAndWait()  # wait for the speech to finish


def takeCommand():  # function to take command
    r = speech_recognition.Recognizer()  # recognizer object
    with speech_recognition.Microphone() as source:
        print("Listening...")
        # seconds of non-speaking audio before a phrase is considered complete
        r.pause_threshold = 1
        r.energy_threshold = 100  # minimum audio energy to consider for recording
        audio = r.listen(source, 0, 4)  # listen to the source

    try:
        print("Understanding...")
        query = r.recognize_google(
            audio, language='en-in')  # recognize the audio
        print(f"You said:{query}\n")  # print the query
    except Exception as e:
        print("Say that again please...")
        return "None"
    return query


if __name__ == "__main__":
    speak("Hello sir, Your AI Desktop partner Jarvis is ready sir")

    while True:
        query = takeCommand().lower()
        if "goodbye" in query or "bye" in query:
            speak("Goodbye sir, have a nice day!")
            exit()
        if "wake up" in query:
            from GreetMe import greetMe
            greetMe()

            while True:
                query = takeCommand().lower()
                if "sleep" in query or "bye" in query:
                    speak("Ok sir, you can call me anytime. Have a nice day!")
                    break

                elif "hello" in query:
                    speak("Hello sir, how may I help you?")
                elif "how are you" in query or "how r u" in query:
                    speak("perfect sir, thank you for asking. How are you?")
                elif "i am fine" in query:
                    speak("That's great to hear sir.")
                elif "thank" in query:
                    speak("You're welcome sir.")
                # Searching Web
                elif "google" in query:
                    from SearchNow import searchGoogle
                    searchGoogle(query)
                elif "youtube" in query:
                    from SearchNow import searchYoutube
                    searchYoutube(query)
                elif "wikipedia" in query:
                    from SearchNow import searchWikipedia
                    searchWikipedia(query)
                # Temperature
                elif "temperature" in query:
                    search = "temperature" + query
                    url = f"https://www.google.com/search?q={search}"
                    r = requests.get(url)
                    data = BeautifulSoup(
                        r.text, "html.parser")  # parse the html
                    temp = data.find("div", class_="BNeawe").text
                    speak(f"The temperature is {temp}")
                elif "weather" in query:
                    search = "weather" + query
                    url = f"https://www.google.com/search?q={search}"
                    r = requests.get(url)
                    data = BeautifulSoup(r.text, "html.parser")
                    weather = data.find("div", class_="BNeawe").text
                    speak(f"The current weather is {weather}")
                # Time
                elif "time" in query:
                    from datetime import datetime
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    speak(f"The current time is {current_time}")
                # Finally Sleep or exit jarvis
                elif "exit" in query:
                    speak("Ok Good bye sir. Have a nice day!")
                    exit()
                # Open and close apps/websites: like word, paint and various websites.
                elif "open" in query:
                    from Dictapp import openappweb
                    openappweb(query)
                elif "close" in query:
                    from Dictapp import closeappweb
                    closeappweb(query)
                # Calculator
                elif "calculate" in query:
                    from Calculatenumbers import WolfRamAlpha
                    from Calculatenumbers import Calc
                    query = query.replace("calculate", "")
                    query = query.replace("jarvis", "")
                    Calc(query)
                # Screenshot
                elif "screenshot" in query:
                    import pyautogui  # pip install pyautogui
                    im = pyautogui.screenshot()
                    im.save("ss.jpg")
                # Translator
                elif "translate" in query:
                    from Translator import translategl
                    query = query.replace("jarvis","")
                    query = query.replace("translate","")
                    translategl(query)
