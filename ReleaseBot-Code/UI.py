import tkinter as tk
from tkinter import messagebox, scrolledtext
import jira_fetch
from PIL import Image, ImageTk
import DeserializeUserData
import SettingsTabUI
import requests
import PublishRN
from tkinter import simpledialog


class UI:
    deploy_mode_tickets = []
    place = 0
    def __init__(self, root):
        self.root = root
        self.root.title("Jira Ticket Viewer")
        self.root.geometry("1400x900")  # Larger window size
        self.root.config(bg="#f4f4f9")  # Set a modern, clean font and color scheme
        self.LogPage = False
        self.last_saved_data = ""
        self.known_limitations = "N/A"  # Default known limitations

        # Frame for input and button
        self.frame = tk.Frame(self.root, padx=30, pady=30, bg="#f4f4f9")
        self.frame.pack(pady=30)

        # Ticket ID label and input field
        self.ticket_label = tk.Label(self.frame, text="Enter Jira Ticket ID:", font=("Segoe UI", 18), bg="#f4f4f9")
        self.ticket_label.grid(row=0, column=0, sticky="w", padx=10)

        self.ticket_id_entry = tk.Entry(self.frame, font=("Segoe UI", 18), width=40, relief="flat", bd=2, bg="#e4e7ea", fg="#2e3a45")
        self.ticket_id_entry.grid(row=0, column=1, padx=10)

        # Fetch button with a modern look
        self.fetch_button = tk.Button(self.frame, text="Fetch Ticket Info", font=("Segoe UI", 18), bg="#4CAF50", fg="white",
                                      relief="flat", command=self.on_fetch_ticket, width=20)
        self.fetch_button.grid(row=0, column=2, padx=10)

        # Save button to save changes (starts red)
        self.save_button = tk.Button(self.frame, text="Save Changes", font=("Segoe UI", 18), bg="#4CAF50", fg="white", relief="flat",
                                     command=self.on_save_changes, width=20)
        self.save_button.grid(row=1, column=0, columnspan=3, pady=20)

        # Text widget for displaying and editing ticket details
        self.result_text = scrolledtext.ScrolledText(self.root, font=("Courier", 16), width=100, height=30, wrap=tk.WORD, spacing1=10,
                                                    spacing2=10, spacing3=10, bd=2, relief="flat", bg="#f9f9f9", fg="#333")
        self.result_text.pack(pady=20, padx=20, anchor="w")

        self.enable_tags()

        # Bind the text widget to detect edits
        self.result_text.bind("<KeyRelease>", self.on_text_edit)

        self.preview_button = tk.Button(
            self.frame,
            text="Preview",
            font=("Segoe UI", 18),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            command=self.toggle_preview_mode,
            width=20
        )
        self.preview_button.grid(row=1, column=2, pady=20, padx=10, sticky="e")  # Position next to Save Changes button

        # Load the settings icon image
        settings_icon = Image.open("ReleaseBotFiles/settings_icon.png")  # Replace with your icon file path
        settings_icon = settings_icon.resize((35, 35), Image.Resampling.LANCZOS)  # Resize the icon
        settings_icon = ImageTk.PhotoImage(settings_icon)  # Convert to Tkinter-friendly format

        # Create the button with the icon only
        settings_button = tk.Button(
            self.root,  # Place it directly on the root window
            image=settings_icon,  # Use the icon as the image
            command=self.on_settings_tab,
            relief="flat",  # Remove the 3D effect
            width=35,  # Set width to match the image width
            height=35,  # Set height to match the image height
            bg="#f4f4f9",  # Optional background color (can adjust if needed)
            bd=0,  # Remove border to avoid any square around the image
        )

        # Make sure to keep a reference to the image to avoid garbage collection
        settings_button.image = settings_icon

        # Position the button on the root window (top-left corner)
        settings_button.place(x=0, y=10)  # Adjust x, y to fine-tune position
        # Save button to save changes (starts red)
        self.publish_button = tk.Button(self.frame, text="Publish", font=("Segoe UI", 18), bg="#2196F3", fg="white",
                                     relief="flat",
                                     command=self.publish_release_notes, width=20)
        self.publish_button.grid(row=1, column=0, pady=0, padx=0, sticky="e")  # Position next to Save Changes button

        # Create a BooleanVar to track the checkbox state
        self.deploy_mode_var = tk.BooleanVar()

        # Add Deploy Mode Checkbox
        self.deploy_mode_checkbox = tk.Checkbutton(
            self.frame,
            text="Enable Deploy Mode",
            variable=self.deploy_mode_var,
            font=("Segoe UI", 16),
            bg="#f4f4f9",
            activebackground="#f4f4f9",
            fg="#333",
            activeforeground="#000",
            onvalue=True,
            offvalue=False,
            command=self.on_deploy_mode_change
        )
        self.deploy_mode_checkbox.grid(row=0, column=5, sticky="w", padx=10)
        # get Info
        SettingsTabUI.Settings.load_account_settings(self)

    def on_deploy_mode_change(self):
        # If the Deploy Mode checkbox is checked (True)
        if self.deploy_mode_var.get():  # When checked
            self.fetch_button.config(text="Next")

            # Open a custom askstring dialog with a slight enhancement
            deploy_case_id = simpledialog.askstring("Deploy Case ID",
                                                    "Please enter the Deploy Case ID:",
                                                    parent=self.root,
                                                    initialvalue=""  # Set an initial value if needed
                                                    )  # Optionally limit the number of characters

            if not deploy_case_id:
                messagebox.showerror("Input Error", "Please enter a valid Ticket ID.")
                self.reset_deploy_checkbox()
                return

            deploy_case_id = self.process_url(deploy_case_id).strip()

            # Retrieve the linked issues specifically for "Caused by"
            # Jira connection details
            jira_url = PublishRN.publishRN.JIRA_BASE_URL
            username = SettingsTabUI.jira_email
            api_token = SettingsTabUI.jira_api_key

            try:
                # Instantiate the JiraFetch class
                jira_fetch_instance = jira_fetch.JiraFetch(jira_url, username, api_token)

                # Fetch Jira issue details
                UI.deploy_mode_tickets = jira_fetch_instance.fetch_caused_by_tickets(deploy_case_id)

                # Check if the response contains an error or 'No Caused by tickets' message
                if "Error" in UI.deploy_mode_tickets[0]:  # Check if the first element is an error message
                    # Display error message in a message box
                    messagebox.showerror("Error",
                                         "An issue occurred. This could be due to a connection problem, invalid input, or incorrect settings. Please check and try again.")
                    self.reset_deploy_checkbox()
                    return
                elif UI.deploy_mode_tickets == ["No 'Caused by' tickets found"]:
                    # Display info message in a message box indicating no 'Caused by' tickets were found
                    messagebox.showinfo("No 'Caused by' Tickets", "No 'Caused by' tickets found.")
                    self.reset_deploy_checkbox()
                    return

                # click the button
                self.on_fetch_ticket()

            except Exception:
                # Handle potential errors such as connection issues, invalid input, or settings
                messagebox.showerror("Error",
                                     "An issue occurred. This could be due to a connection problem, invalid input, or incorrect settings. Please check and try again.")

        else:
            # When unchecked ,reset value's
            UI.deploy_mode_tickets = []
            UI.place = 0
            self.fetch_button.config(text="Fetch Ticket Info")


    def reset_deploy_checkbox(self):
        self.deploy_mode_checkbox.deselect()
        self.on_deploy_mode_change()

    def publish_release_notes(self):
        """Handle publishing release notes."""
        self.LogPage = True
        # Check for empty fields
        empty_fields = self._validate_fields()

        # If there are empty fields, prompt the user for confirmation
        if empty_fields:
            empty_fields_message = ", ".join(empty_fields)
            confirmation_message = f"The following fields are empty: {empty_fields_message}. Are you sure you want to upload like this?"
            user_confirmation = messagebox.askyesno("Confirm Upload", confirmation_message)
            if not user_confirmation:
                return  # Stop the process if the user cancels

        # Show the log box and start publishing
        self.result_text.pack(fill="x", padx=10, pady=5)
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)

        try:
            self._write_log("Connecting to the server...")
            self.root.update()  # Refresh the UI for real-time logs

            # Simulate publishing process
            PublishRN.publishRN.create_RN(self)

        except Exception as e:
            self._write_log(f"An unexpected error occurred: {e}")
            messagebox.showerror("Error", "An unexpected error occurred. See logs for details.")

        finally:
            self.result_text.config(state="disabled")  # Disable editing

    def _validate_fields(self):
        """Validate fields and return a list of empty fields."""
        # Simulate deserialization and field checks
        DeserializeUserData.DeserializeUserData.deserialize(self.last_saved_data)

        empty_fields = []
        if not DeserializeUserData.DeserializeUserData.release_notes_title:
            empty_fields.append("Release Notes Title")
        if not DeserializeUserData.DeserializeUserData.release_notes_description:
            empty_fields.append("Release Notes Description")
        if not DeserializeUserData.DeserializeUserData.related_ticket_ids:
            empty_fields.append("Related Ticket IDs")
        if not DeserializeUserData.DeserializeUserData.known_limitations or DeserializeUserData.DeserializeUserData.known_limitations == "None":
            empty_fields.append("Known Limitations")
        if not DeserializeUserData.DeserializeUserData.affected_components:
            empty_fields.append("Affected Components")
        if not DeserializeUserData.DeserializeUserData.publish_type:
            empty_fields.append("Publish Type")

        return empty_fields

    def _write_log(self, message):
        """Write a log message to the log box."""
        self.result_text.insert(tk.END, f"{message}\n")
        self.result_text.see(tk.END)  # Scroll to the latest log entry

    def _simulate_publish_process(self):
        """Simulate a publish process with random success or failure."""
        import time
        import random

        time.sleep(1)  # Simulate delay
        self._write_log("Validating data...")
        time.sleep(1)  # Simulate delay
        self._write_log("Uploading release notes...")
        time.sleep(2)  # Simulate delay

        return random.choice([True, False])  # Randomly return success or failure

    def on_settings_tab(self):
        SettingsTabUI.Settings(self.root)

    def toggle_preview_mode(self):

        """Toggle between preview mode and edit mode."""
        if self.preview_button["text"] == "Preview":
            self.original_text = self.result_text.get(1.0, tk.END).strip()  # Save content
            self.original_tags = self._get_text_tags()  # Save tags applied (e.g., bold)

            self.preview_button.config(text="Return Edit Mode")
            self.result_text.config(bg="#f9f9f9")

            # Deserialize and extract data
            DeserializeUserData.DeserializeUserData.deserialize(self.last_saved_data)

            # Now you have access to all fields from the deserialized data
            release_notes_title = DeserializeUserData.DeserializeUserData.release_notes_title
            publish_type = DeserializeUserData.DeserializeUserData.publish_type
            description = DeserializeUserData.DeserializeUserData.release_notes_description
            affected_components = DeserializeUserData.DeserializeUserData.affected_components
            related_ticket_ids = DeserializeUserData.DeserializeUserData.related_ticket_ids
            known_limitations = DeserializeUserData.DeserializeUserData.known_limitations

            # Prepare the text for preview (only show data if available)
            preview_text = f"Type: {publish_type if publish_type else 'N/A'}\n"
            preview_text += f"Title: {release_notes_title if release_notes_title else 'N/A'}\n"
            preview_text += f"Description: {description if description else 'No description available'}\n"
            preview_text += f"Related Tickets: {', '.join(related_ticket_ids) if related_ticket_ids else 'No related tickets'}\n"
            preview_text += f"Known Limitations: {known_limitations if known_limitations else 'N/A'}\n"
            preview_text += f"Affected Components: {", ".join(affected_components) if affected_components else 'No affected components'}"

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, preview_text)  # Insert preview content


            self.result_text.config(state="disabled")  # Disable editing in Preview Mode

        else:
            # Return to Edit Mode
            self.result_text.config(state="normal")  # Enable editing again
            self.result_text.delete(1.0, tk.END)  # Clear current content

            self.result_text.insert(tk.END, self.last_saved_data)  # Restore original content

            # Restore tags for bold or other formatting
            self.enable_tags()

            lines = self.last_saved_data.splitlines()

            # Iterate again to apply tags for display
            for i, line in enumerate(lines):
                # Apply the "title" tag for sections like Release Notes Title, Description, etc.
                if line.lower().startswith("release notes title") or \
                        line.lower().startswith("release notes description") or \
                        line.lower().startswith("related ticket ids") or \
                        line.lower().startswith("known limitations"):
                    self.result_text.tag_add("title", f"{i + 1}.0", f"{i + 1}.{len(line)}")
                else:
                    self.result_text.tag_add("data", f"{i + 1}.0", f"{i + 1}.{len(line)}")


            # Return button to Preview mode
            self.preview_button.config(text="Preview")
            self.result_text.config(bg="#f9f9f9")

    def _get_text_tags(self):
        """Helper method to collect applied tags from the Text widget."""
        tags = {}
        for tag in self.result_text.tag_names():
            tag_range = self.result_text.tag_ranges(tag)
            if tag_range:
                tags[tag] = tag_range
        return tags

    def _apply_tags_to_text(self, title, tag_name):
        """Apply specific tags to a section of the text (e.g., making title bold)."""
        start_index = "1.0"  # Adjust start position based on where the title is inserted
        end_index = f"1.{len(title)}"  # Calculate end position for the title
        self.result_text.tag_add(tag_name, start_index, end_index)
        self.result_text.tag_configure(tag_name, font=("Helvetica", 12, "bold"))


    def enable_tags(self):
        self.result_text.tag_configure("title", font=("Courier", 16, "bold"), foreground="#000000")
        self.result_text.tag_configure("data", font=("Courier", 14), foreground="#555555")
        self.result_text.config(font=("Courier", 14))

    def on_save_changes(self):
        if self.result_text.cget("state") == "disabled":  # Check if in Preview Mode
            messagebox.showerror("Error",
                            "Cannot save changes while in Preview Mode. Return to Edit Mode to save changes.")
            return

        # Retrieve the updated text
        updated_text = self.result_text.get(1.0, tk.END).strip()

        if not updated_text:
            messagebox.showerror("Error", "Please modify the release notes before saving.")
            return

        # Change the button color to green (as the data is saved)
        self.save_button.config(bg="#4CAF50")

        # Show the success message
        messagebox.showinfo("Saved", "Changes have been saved successfully!")

        # Store the updated text as the last saved data
        self.last_saved_data = updated_text

        # Clear the previous content
        self.result_text.delete(1.0, tk.END)

        # Insert the updated text without any additional formatting (reset the font)
        self.result_text.insert(tk.END, updated_text)

        # Reapply the formatting for the title and data tags
        lines = updated_text.splitlines()

        # Configure the "data" font for all regular text sections
        self.enable_tags()

        # Deserialize the content and print the relevant details
        DeserializeUserData.DeserializeUserData.deserialize(updated_text)

        # Iterate again to apply tags for display
        for i, line in enumerate(lines):
            # Apply the "title" tag for sections like Release Notes Title, Description, etc.
            if line.lower().startswith("release notes title") or \
                    line.lower().startswith("release notes description") or \
                    line.lower().startswith("related ticket ids") or \
                    line.lower().startswith("known limitations"):
                self.result_text.tag_add("title", f"{i + 1}.0", f"{i + 1}.{len(line)}")
            else:
                self.result_text.tag_add("data", f"{i + 1}.0", f"{i + 1}.{len(line)}")

    def print_latest_data(self, updated_text):
        # Split the updated text into lines
        lines = updated_text.splitlines()

        # Extract the title, description, and case ID (assuming the order is consistent)
        release_notes_title = ""
        release_notes_description = ""
        related_ticket_ids = []

        for line in lines:
            if line.lower().startswith("release notes title"):
                release_notes_title = line.split(":", 1)[1].strip() if ":" in line else ""
            elif line.lower().startswith("release notes description"):
                release_notes_description = line.split(":", 1)[1].strip() if ":" in line else ""
            elif line.lower().startswith("related ticket ids"):
                related_ticket_ids = line.split(":", 1)[1].strip().split(",") if ":" in line else []


    def on_text_edit(self, event):
        """This function is called when the text is modified."""

        if self.result_text.cget("state") != "disabled":  # Check if in Preview Mode
            current_text = self.result_text.get(1.0, tk.END).strip()

            # If the current text differs from the last saved data, make the button red
            if current_text != self.last_saved_data:
                self.save_button.config(bg="#FF5733")
            else:
                self.save_button.config(bg="#4CAF50")

    def publish_release_notes_to_app(self, release_notes_title, release_notes_description, related_ticket_ids):
        # Clear the ScrolledText widget
        self.result_text.delete(1.0, tk.END)

        # Insert the formatted text with tags
        self.result_text.insert(tk.END, "Release Notes Title:\n", "title")  # Bold Title
        self.result_text.insert(tk.END, f"{release_notes_title}\n\n", "data")  # Normal Data

        self.result_text.insert(tk.END, "Release Notes Description:\n", "title")  # Bold Title
        self.result_text.insert(tk.END, f"{release_notes_description}\n\n", "data")  # Normal Data

        self.result_text.insert(tk.END, "Related Ticket IDs (Case ID):\n", "title")  # Bold Title
        self.result_text.insert(tk.END, f"{', '.join(related_ticket_ids)}\n\n", "data")  # Normal Data

        self.result_text.insert(tk.END, "Known Limitations:\n", "title")  # Bold Title
        self.result_text.insert(tk.END, f"{self.known_limitations}\n", "data")  # Normal Data

    def process_url(self, url):
        prefix = "https://dome9-security.atlassian.net/browse/"
        if prefix in url:
            # Extract the ticket
            return url.split(prefix)[-1]
        # Return the original URL if prefix not found
        return url

    def on_fetch_ticket(self):
        # If I was In Log
        if self.LogPage is True:
            self.result_text.config(state="normal")

        if self.result_text.cget("state") == "disabled":  # Check if in Preview Mode
            messagebox.showerror("Error",
                                 "Cannot fetch data while in Preview Mode. Return to Edit Mode to save changes.")
            return

        if self.deploy_mode_var.get():
            self.ticket_id_entry.delete(0, tk.END)  # Clear any existing text

            if UI.place + 1 > len(UI.deploy_mode_tickets):
                # Show a message box with a message
                messagebox.showinfo("Deploy Finished", "Deploy has Finished! Nice!")
                self.reset_deploy_checkbox()

            self.ticket_id_entry.insert(0,UI.deploy_mode_tickets[UI.place])  # Set the new ticket as value
            UI.place += 1
        ticket_id = self.ticket_id_entry.get().strip()
        ticket_id = self.process_url(ticket_id)

        if not ticket_id:
            messagebox.showerror("Input Error", "Please enter a valid Ticket ID.")
            return

        # Jira connection details
        jira_url = PublishRN.publishRN.JIRA_BASE_URL
        username = SettingsTabUI.jira_email
        api_token = SettingsTabUI.jira_api_key

        try:
            # Instantiate the JiraFetch class
            jira_fetch_instance = jira_fetch.JiraFetch(jira_url, username, api_token)

            # Fetch Jira issue details
            release_notes_title, release_notes_description, related_ticket_ids = jira_fetch_instance.fetch_issue_details(
                ticket_id)

            # Check for error in fetched data
            if "Error" in related_ticket_ids[0]:
                messagebox.showerror("Error", related_ticket_ids[0])
                return

            # Display the result in the text box
            self.result_text.delete(1.0, tk.END)  # Clear previous content
            self.publish_release_notes_to_app(release_notes_title, release_notes_description, related_ticket_ids)

            # After fetching the data, save it and set the button color to green
            self.last_saved_data = self.result_text.get(1.0, tk.END).strip()


        except Exception:
            # Handle potential errors such as connection issues, invalid input, or settings
            messagebox.showerror("Error",
                                 "An issue occurred. This could be due to a connection problem, invalid input, or incorrect settings. Please check and try again.")
