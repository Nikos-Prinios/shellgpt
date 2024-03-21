import sounddevice as sd  
from scipy.io.wavfile import write  
import requests  
import keyboard  
import re  
import subprocess  
  
# Your API key  
api_key = "Your openai API key here"  
  
  
# Configuration initiale  
sample_rate = 44100  
filename = 'prompt_audio.wav'  
recording = False  
audio_data = None  
  
  
def on_press(event):  
    global recording, audio_data  
    if event.name == 'ctrl':  
        if not recording:  
            print("Début de l'enregistrement...")  
            recording = True  
            audio_data = sd.rec(int(30 * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')  
        else:  
            print("Arrêt de l'enregistrement...")  
            recording = False  
            sd.stop()  
            write(filename, sample_rate, audio_data)  
            print(f"Enregistrement terminé et sauvegardé sous {filename}")  
            process_audio(filename)  
            keyboard.unhook_all()  
  
  
def on_press(event):  
    global recording, audio_data  
    if event.name == 'ctrl':  
        if not recording:  
            print("Début de l'enregistrement...")  
            recording = True  
            audio_data = sd.rec(int(30 * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')  
        else:  
            print("Arrêt de l'enregistrement...")  
            recording = False  
            sd.stop()  
            write(filename, sample_rate, audio_data)  
            print(f"Enregistrement terminé et sauvegardé sous {filename}")  
            process_audio(filename)  
  
  
def process_audio(file_path):  
    transcription_headers = {  
        "Authorization": f"Bearer {api_key}"  
    }  
    with open(file_path, "rb") as audio_file:  
        files = {"file": audio_file, "model": (None, "whisper-1")}  
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=transcription_headers,  
                                 files=files)  
  
    if response.status_code == 200:  
        transcription = response.json()  
        text = transcription['text']  
        print("Transcription réussie :", text)  
        send_to_chatgpt(text)  
    else:  
        print("Échec de la transcription :", response.text)  
  
# Adjust the prompt to your taste (and configuration)  
def send_to_chatgpt(text):  
    text = "What is the shell command for " + text + "? Imagine you're a shell assistant. All your "\  
                                                         "are exclusively shell command lines. Simply give "\  
                                                         "the command, without comment. Your answer must be formatted as "\  
                                                         "shell code. These commands are intended for a Manjaro linux system." \  
                                                         "For information the desktop in my configuration is here: /home/colonel/Bureau/'. " \  
                                                         "File names should always be treated as case-insensitive. "

  
    chat_headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}  
    data = {  
        "model": "gpt-3.5-turbo",  
        "temperature": 0.2,  
        "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": text}]  
    }    response = requests.post("https://api.openai.com/v1/chat/completions", headers=chat_headers, json=data)  
  
    if response.status_code == 200:  
        result = response.json()  
        command = result.get('choices')[0]['message']['content'] if result.get('choices') else "Pas de réponse."  
        print("Réponse de ChatGPT:", command)  
        execute_shell_commands_from_chatgpt(command)  
    else:  
        print("Échec de l'envoi à ChatGPT:", response.text)  
  
  
def execute_shell_commands_from_chatgpt(response):  
    shell_commands = re.findall(r'```shell\n(.*?)\n```', response, re.DOTALL)  
    for command in shell_commands:  
        command = command.strip()  
        safe_execute_shell_commands(command)  
  
  
def safe_execute_shell_commands(command):  
    # Validation et exécution sécurisée des commandes shell  
    print(f"Exécution de la commande shell validée : {command}")  
    try:  
        output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  
        print("Sortie de la commande :")  
        print(output.stdout)  
        if output.stderr:  
            print("Erreur de la commande :")  
            print(output.stderr)  
    except subprocess.CalledProcessError as e:  
        print(f"Erreur lors de l'exécution de la commande '{command}':", e)  
  
  
def start_listening():  
    print("Appuyez sur la touche Control pour démarrer l'enregistrement, puis de nouveau pour l'arrêter.")  
    keyboard.on_press(on_press)  
  
  
  
if __name__ == "__main__":  
    start_listening()  
    keyboard.wait('esc')
