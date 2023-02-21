import threading
import tkinter as tk
import requests
import random
import time
from tkinter import filedialog

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
'Accept-Encoding': 'gzip, deflate, br',
'Referer': 'https://www.twitch.tv/'
}

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # Label pour le fichier de liste de proxy
        self.file_label = tk.Label(self, text="Fichier de liste de proxy :")
        self.file_label.pack()
        
        # Entry pour le chemin du fichier de liste de proxy
        self.file_path_entry = tk.Entry(self)
        self.file_path_entry.pack()

        # Bouton pour choisir le fichier de liste de proxy
        self.file_button = tk.Button(self, text="Parcourir", command=self.choose_file)
        self.file_button.pack()

        self.file_label = tk.Label(self, text="Nom de la chaîne Twitch :")
        self.file_label.pack()

        self.name = tk.Entry(self)
        self.name.pack()

        # Label pour le nombre de threads
        self.threads_label = tk.Label(self, text="Nombre de threads :")
        self.threads_label.pack()

        # Entry pour le nombre de threads
        self.threads_entry = tk.Entry(self)
        self.threads_entry.pack()

        # Label pour le timeout des requêtes
        self.timeout_label = tk.Label(self, text="Timeout des requêtes (en secondes) :")
        self.timeout_label.pack()

        # Entry pour le timeout des requêtes
        self.timeout_entry = tk.Entry(self)
        self.timeout_entry.pack()

        # Label pour afficher le nombre de threads en cours d'exécution
        self.threads_running_label = tk.Label(self, text="")
        self.threads_running_label.pack()

        # Bouton pour lancer l'exécution
        self.run_button = tk.Button(self, text="Lancer", command=self.run_execution)
        self.run_button.pack()
        

    def choose_file(self):
        # Ouvre la boîte de dialogue pour choisir le fichier
        file_path = filedialog.askopenfilename()
        # Met à jour l'Entry pour afficher le chemin du fichier
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

    def run_execution(self):
        try:
            # Obtient le chemin du fichier de liste de proxy, le nom de la chaîne Twitch, le nombre de threads et le timeout
            file_path = self.file_path_entry.get()
            name = self.name.get()
            num_threads = int(self.threads_entry.get())
            timeout = float(self.timeout_entry.get())

            # Lit le fichier de liste de proxy et crée une liste de proxies
            with open(file_path, 'r') as f:
                proxies = f.read().splitlines()

            # Crée une fonction qui envoie une requête à une URL cible en utilisant un proxy aléatoire
            def send_request(url, timeout):
                session = requests.Session()
                session.keep_alive = True
                while True:
                    proxy = {
                        'http': 'http://' + random.choice(proxies)
                    }
                    try:
                        time.sleep(random.randint(1, 5))
                        response = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
                        if response.status_code == 200:
                            print('Requête envoyée avec succès en utilisant le proxy', proxy)
                        else:
                            print('La requête a échoué en utilisant le proxy', proxy)
                    except requests.exceptions.RequestException as e:
                        print(f"Une erreur s'est produite: {e}")
          
            threads = []
            for i in range(num_threads):
                t = threading.Thread(target=send_request, args=(f'https://www.twitch.tv/{name}',timeout))
                threads.append(t)
                t.start()

            # Attends que tous les threads aient terminé
            for t in threads:
                t.join()
        except Exception as e:
            print(f"Une erreur s'est produite: {e}")

root = tk.Tk()
app = Application(master=root)
app.mainloop()
