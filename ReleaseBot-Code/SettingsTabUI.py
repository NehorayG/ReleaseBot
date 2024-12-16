import json
import os
import tkinter as tk
from tkinter import messagebox
import UI

# Global variables
jira_email = ""
jira_api_key = ""

class Settings:
    def __init__(self, root):
        self.root = root
        self.settings_window = None
        self.load_account_settings()
        self.create_settings_window()

    def create_settings_window(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = tk.Toplevel(self.root)
            self.settings_window.title("Settings")
            self.settings_window.geometry("500x200")
            self.settings_window.config(bg="#f4f4f9")

            # Jira Email
            jira_label = tk.Label(self.settings_window, text="Jira Email:", font=("Segoe UI", 14), bg="#f4f4f9")
            jira_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            self.jira_email_entry = tk.Entry(self.settings_window, font=("Segoe UI", 14), width=30, bg="#e4e7ea", fg="#2e3a45")
            self.jira_email_entry.grid(row=0, column=1, padx=10)
            self.jira_email_entry.insert(0, jira_email)

            # Jira API Key
            jira_api_key_label = tk.Label(self.settings_window, text="Jira API Key:", font=("Segoe UI", 14), bg="#f4f4f9")
            jira_api_key_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
            self.jira_api_key_entry = tk.Entry(self.settings_window, font=("Segoe UI", 14), width=30, show="*", bg="#e4e7ea", fg="#2e3a45")
            self.jira_api_key_entry.grid(row=1, column=1, padx=10)
            self.jira_api_key_entry.insert(0, jira_api_key)

            # Save All button
            save_all_button = tk.Button(self.settings_window, text="Save All", font=("Segoe UI", 14), bg="#2196F3", fg="white", relief="flat", command=self.save_all)
            save_all_button.grid(row=2, column=1, pady=20)

    def save_all(self):
        global jira_email, jira_api_key
        jira_email = self.jira_email_entry.get()
        jira_api_key = self.jira_api_key_entry.get()

        data = {
            "jira_email": jira_email,
            "jira_api_key": jira_api_key
        }
        os.makedirs("ReleaseBotFiles", exist_ok=True)
        file_path = os.path.join("ReleaseBotFiles", "Information_ReleaseBot.json")
        with open(file_path, "w") as file:
            json.dump(data, file)

        messagebox.showinfo("Saved", "All settings have been saved successfully!")


    def load_account_settings(self):
        global jira_email, jira_api_key

        file_path = os.path.join("ReleaseBotFiles", "Information_ReleaseBot.json")

        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                jira_email = data.get("jira_email", "")
                jira_api_key = data.get("jira_api_key", "")
        else:
            if not isinstance(self, UI.UI):
                messagebox.showinfo("Info", "No saved settings found. Please enter your settings.")
                self.create_settings_window()
