import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import json
import requests
import keyboard
import pyperclip
import pyautogui
import configparser

def on_closing():
    root.withdraw()

def send_request(prompt, api_key, model):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        data=json.dumps(data),
    )
    return response.json()

def on_submit():
    prompt = entry.get()
    progressbar.grid(column=0, row=1, columnspan=3, padx=5, pady=5)
    root.update()
    response = send_request(prompt, api_key, model)
    answer = response["choices"][0]["message"]["content"]
    pyperclip.copy(answer.strip())
    entry.delete(0, tk.END)
    root.withdraw()
    pyautogui.hotkey("ctrl", "v")
    progressbar.grid_remove()

def settings():
    global api_key, model
    settings_window = tk.Toplevel(root)
    settings_window.title("Paramètres")

    key_label = tk.Label(settings_window, text="Clé API:")
    key_label.grid(column=0, row=0, padx=10, pady=10)
    key_entry = tk.Entry(settings_window)
    key_entry.grid(column=1, row=0, padx=10, pady=10)
    key_entry.insert(0, api_key)

    model_label = tk.Label(settings_window, text="Modèle:")
    model_label.grid(column=0, row=1, padx=10, pady=10)
    model_combobox = ttk.Combobox(settings_window, values=["gpt-3.5-turbo", "gpt-4"], state="readonly")
    model_combobox.grid(column=1, row=1, padx=10, pady=10)
    model_combobox.set(model)


    def save_settings():
        global api_key, model
        api_key = key_entry.get()
        model = model_combobox.get()
        config.set("ChatGPT", "api_key", api_key)
        config.set("ChatGPT", "model", model)
        save_config(config)
        settings_window.destroy()

    save_button = tk.Button(settings_window, text="Enregistrer", command=save_settings)
    save_button.grid(column=1, row=2, padx=10, pady=10)

def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if "ChatGPT" not in config.sections():
        config.add_section("ChatGPT")
        config.set("ChatGPT", "api_key", "")
        config.set("ChatGPT", "model", "gpt-3.5-turbo")
        save_config(config)
    return config

def save_config(config):
    with open("config.ini", "w") as config_file:
        config.write(config_file)


config = load_config()
api_key = config.get("ChatGPT", "api_key")
model = config.get("ChatGPT", "model")

keyboard.add_hotkey("ctrl+alt+p", lambda: (entry.focus_set(), root.deiconify()))

root = ThemedTk(theme="clearlooks")
root.protocol("WM_DELETE_WINDOW", on_closing)
root.withdraw()
root.title("ChatGPT DEW")

entry = tk.Entry(root)
entry.grid(column=0, row=0, padx=5, pady=5)

submit_button = tk.Button(root, text="Lancer", command=on_submit)
submit_button.grid(column=1, row=0, padx=5, pady=5)

settings_button = tk.Button(root, text="Paramètres", command=settings)
settings_button.grid(column=2, row=0, padx=5, pady=5)

progressbar = ttk.Progressbar(root, mode="indeterminate")
progressbar.grid_remove()

entry.bind("<Return>", lambda event: on_submit())

root.mainloop()