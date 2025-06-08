import pyttsx3
import datetime 

engine = pyttsx3.init("sapi5") #sapi5 is a Microsoft Speech API
voices = engine.getProperty("voices") #get the voices
engine.setProperty("voice", voices[0].id)#set the voice
engine.setProperty("rate", 170)#set the rate of speech

def speak(audio):#function to speak
    engine.say(audio)
    engine.runAndWait() #wait for the speech to finish
    
def greetMe(): #function to greet
    hour = int(datetime.datetime.now().hour) #get the current hour
    if hour>=0 and hour<12:
        speak("Good Morning!, Sir")
    elif hour>=12 and hour<18:
        speak("Good Afternoon!, Sir")
    else:
        speak("Good Evening!, Sir")
        
    speak("I am your AI desktop partner Jarvis. How may I help you?")