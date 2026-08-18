import datetime
import webbrowser
import sys

import speech_recognition as sr
import pyttsx3

try:
    import wikipedia
    WIKI_AVAILABLE = True
except ImportError:
    WIKI_AVAILABLE = False


# ---------------------------------------------------------------------------
# 1. SET UP THE TEXT-TO-SPEECH ENGINE
# ---------------------------------------------------------------------------
# NOTE: pyttsx3 has a well-known bug (especially on Windows with the SAPI5
# driver) where reusing ONE global engine across multiple say()/runAndWait()
# calls causes only the FIRST call to actually produce sound -- every call
# after that goes silent, even though no error is raised. The fix is to
# create a brand-new engine instance every time we want to speak.


def speak(text: str) -> None:
    """Speak text out loud AND print it, so you can follow along."""
    print(f"Assistant: {text}")
    engine = pyttsx3.init()          # fresh engine each call -- avoids the "only speaks once" bug
    engine.setProperty("rate", 175)   # speaking speed (words per minute)
    engine.setProperty("volume", 1.0)  # 0.0 to 1.0

    # Optional: pick a different installed voice (uncomment to try)
    # voices = engine.getProperty("voices")
    # engine.setProperty("voice", voices[1].id)  # e.g. a female voice on Windows

    engine.say(text)
    engine.runAndWait()
    engine.stop()                     # release the driver so the next speak() call works cleanly


# ---------------------------------------------------------------------------
# 2. SET UP SPEECH RECOGNITION
# ---------------------------------------------------------------------------
recognizer = sr.Recognizer()


def listen() -> str:
    """
    Listen through the microphone and return what was said as lowercase text.
    Returns an empty string if nothing could be understood.
    """
    with sr.Microphone() as source:
        print("\nListening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # reduce background noise
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("...didn't hear anything.")
            return ""

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)  # free Google Web Speech API
        print(f"You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you repeat it?")
        return ""
    except sr.RequestError:
        speak("Speech service is unavailable right now. Check your internet connection.")
        return ""


# ---------------------------------------------------------------------------
# 3. COMMAND FUNCTIONS -- each one performs a "useful action"
# ---------------------------------------------------------------------------
def tell_time() -> None:
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {now}")


def tell_date() -> None:
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
    speak(f"Today is {today}")


def open_website(name: str, url: str) -> None:
    speak(f"Opening {name}")
    webbrowser.open(url)


def search_wikipedia(query: str) -> None:
    if not WIKI_AVAILABLE:
        speak("The wikipedia package isn't installed, so I can't search that.")
        return
    speak(f"Searching Wikipedia for {query}")
    try:
        summary = wikipedia.summary(query, sentences=2)
        speak(summary)
    except wikipedia.exceptions.DisambiguationError:
        speak("That topic is ambiguous. Could you be more specific?")
    except wikipedia.exceptions.PageError:
        speak("I couldn't find anything on that topic.")


def tell_joke() -> None:
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs.",
        "I told my computer I needed a break, and it said no problem, it will 'sleep' too.",
        "Why do Python programmers wear glasses? Because they can't C.",
    ]
    import random
    speak(random.choice(jokes))


def greet() -> None:
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning!")
    elif hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("I'm your voice assistant. How can I help you?")


# ---------------------------------------------------------------------------
# 4. COMMAND ROUTER -- decides which function to call based on keywords
# ---------------------------------------------------------------------------
def handle_command(command: str) -> bool:
    """
    Look at the recognized text and act on it.
    Returns False if the user wants to quit, True otherwise.
    """
    if not command:
        return True

    if "time" in command:
        tell_time()

    elif "date" in command or "day is it" in command:
        tell_date()

    elif "open youtube" in command:
        open_website("YouTube", "https://youtube.com")

    elif "open google" in command:
        open_website("Google", "https://google.com")

    elif "wikipedia" in command:
        # e.g. "search wikipedia for the eiffel tower" -> "the eiffel tower"
        topic = command.replace("search wikipedia for", "").replace("wikipedia", "").strip()
        if topic:
            search_wikipedia(topic)
        else:
            speak("What would you like me to search for?")

    elif "joke" in command:
        tell_joke()

    elif "hello" in command or "hi assistant" in command:
        greet()

    elif "stop" in command or "exit" in command or "quit" in command or "goodbye" in command:
        speak("Goodbye!")
        return False

    else:
        speak("I heard you, but I don't have a command for that yet.")

    return True


# ---------------------------------------------------------------------------
# 5. MAIN LOOP
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 50)
    print("  PYTHON VOICE ASSISTANT (say 'exit' to quit)")
    print("=" * 50)
    greet()

    running = True
    while running:
        try:
            command = listen()
            running = handle_command(command)
        except KeyboardInterrupt:
            speak("Shutting down.") 
            sys.exit(0)


if __name__ == "__main__":
    main()