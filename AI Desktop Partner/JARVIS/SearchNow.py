import speech_recognition
import pyttsx3
import pywhatkit
import wikipedia
import webbrowser
def takeCommand():#function to take command
    r = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1 #seconds of non-speaking audio before a phrase is considered complete
        r.energy_threshold = 300 #minimum audio energy to consider for recording
        audio = r.listen(source,0,4) #listen to the source
        
    try:
        print("Understanding...")
        query = r.recognize_google(audio, language='en-in') #recognize the audio
        print(f"You said:{query}\n") #print the query
    except Exception as e:
        print("Say that again please...")
        return "None"
    return query

query = takeCommand().lower()

engine = pyttsx3.init("sapi5") #sapi5 is a Microsoft Speech API
voices = engine.getProperty("voices") #get the voices
engine.setProperty("voice", voices[0].id)#set the voice
engine.setProperty("rate", 170)#set the rate of speech

def speak(audio):#function to speak
    engine.say(audio)
    engine.runAndWait() #wait for the speech to finish
    
def searchGoogle(query):
    if "google" in query:
        import wikipedia as googleScrap
        query = query.replace("jarvis","")
        query = query.replace("google search","")
        query = query.replace("google","")
        speak("This is what I found on google")

        try:
            pywhatkit.search(query)
            result = googleScrap.summary(query,1)
            speak(result)

        except:
            speak("No speakable output available")

def searchYoutube(query):
    if "youtube" in query:
        speak("This is what I found for your search!") 
        query = query.replace("youtube search","")
        query = query.replace("youtube","")
        query = query.replace("jarvis","")
        web  = "https://www.youtube.com/results?search_query=" + query
        webbrowser.open(web)
        pywhatkit.playonyt(query)
        speak("Done, Sir")

def searchWikipedia(query):
    if "wikipedia" in query:
        speak("Searching from wikipedia....")
        query = query.replace("wikipedia","")
        query = query.replace("search wikipedia","")
        query = query.replace("jarvis","")
        results = wikipedia.summary(query,sentences = 2)
        speak("According to wikipedia..")
        print(results)
        speak(results)
