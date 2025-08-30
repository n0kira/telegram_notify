import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Cartella dove c'è lo script del bot
BOT_SCRIPT = "telegram_version.py"

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_bot()

    def start_bot(self):
        if self.process:
            self.process.terminate()  # ferma bot vecchio
        self.process = subprocess.Popen(["python", BOT_SCRIPT])

    def on_modified(self, event):
        if event.src_path.endswith(BOT_SCRIPT):
            print("⚡ Bot modificato, riavvio...")
            self.start_bot()

if __name__ == "__main__":
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()
    print("👀 Monitoraggio attivo. Modifica amazon_bot.py per riavviare il bot.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
