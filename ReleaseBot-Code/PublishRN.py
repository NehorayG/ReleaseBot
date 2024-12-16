import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import DeserializeUserData
import SettingsTabUI


class publishRN:
    JIRA_BASE_URL = "https://dome9-security.atlassian.net"
    CONFLUENCE_LINK = JIRA_BASE_URL + "/wiki/spaces/RN/pages/3269427219/test-code-integration"

    @staticmethod
    def add_release_note(page_data):
        title = f"<h2>Deployment {datetime.now().strftime('%B %d, %Y')}</h2>"  # The title with the current date
        modified_page_data = ""

        release_note = publishRN.format_CSPM_release_note()  # The release note

        # Add the release note after the title for the current day, if it doesn't exist create new
        if title in page_data:
            # Find the index of the first occurrence of the key
            title_index = page_data.find(title)
            # Insert the text "found" right after the key
            modified_page_data = page_data[:title_index + len(title)] + release_note + page_data[
                                                                                       title_index + len(title):]
        else:
            # If the title doesn't exist we add a new title
            modified_page_data = title + release_note + page_data

        return modified_page_data

    @staticmethod
    def format_CSPM_release_note():
        link = publishRN.CONFLUENCE_LINK + datetime.now().strftime(
            "%B-%d-%Y")  # The link we add

        # Get Type Color
        color = "Green"
        if DeserializeUserData.DeserializeUserData.publish_type == "FIXED":
            color = "Red"

        # Create individual macros for each affected component, keeping original formatting and adding space between each
        components_str = ' '.join(
            f'<ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="unique-macro-id-{i}">'
            f'<ac:parameter ac:name="colour">None</ac:parameter>'  # Can be adjusted if needed
            f'<ac:parameter ac:name="title">{component}</ac:parameter>'
            f'</ac:structured-macro>' for i, component in
            enumerate(DeserializeUserData.DeserializeUserData.affected_components)
        )

        # Now include this in your special release note
        special_release_note = (
            f'<ac:structured-macro ac:name="info" ac:schema-version="1" ac:macro-id="425c26a7-4a94-4934-b13c-68835660b371">'
            f'<ac:rich-text-body>'
            f'<p>'
            f'<ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="a8de3f78-a8a5-4204-b4d2-39292af5ef64">'
            f'<ac:parameter ac:name="colour">{color}</ac:parameter>'
            f'<ac:parameter ac:name="title">{DeserializeUserData.DeserializeUserData.publish_type}</ac:parameter>'
            f'</ac:structured-macro>'
            f'<strong> {DeserializeUserData.DeserializeUserData.release_notes_title}</strong><br />'
            f'<strong>Description:</strong> {DeserializeUserData.DeserializeUserData.release_notes_description}<br />'
            f'<strong>Case ID:</strong> {", ".join(DeserializeUserData.DeserializeUserData.related_ticket_ids)}<br />'
            f'<strong>Known Limitations:</strong> {DeserializeUserData.DeserializeUserData.known_limitations if DeserializeUserData.DeserializeUserData.known_limitations else "N/A"}<br />'
            f'<strong>Affected Components: </strong>'  # Label for affected components
            f'{components_str}'  # All components with their individual design on the same line
            f'</p>'
            f'</ac:rich-text-body>'
            f'</ac:structured-macro>'
        )

        return special_release_note

    @staticmethod
    def create_RN(ui_instance):
        HTML = ""

        # Getting the page HTML
        ui_instance._write_log("Starting to retrieve the Confluence page...")  # Real-time log
        ui_instance.root.update()  # Refresh the UI for real-time logs
        HTML += publishRN.get_page(SettingsTabUI.jira_api_key, SettingsTabUI.jira_email, publishRN.CONFLUENCE_LINK, ui_instance)

        # updating the HTML to include the RN
        ui_instance._write_log("Page retrieval complete. Updating HTML with new release note...")  # Real-time log
        ui_instance.root.update()  # Refresh the UI for real-time logs
        HTML = publishRN.add_release_note(HTML)

        # Sending the new data to the page
        ui_instance._write_log("Preparing to update Confluence page with modified content...")  # Real-time log
        ui_instance.root.update()  # Refresh the UI for real-time logs
        publishRN.update_page(HTML, SettingsTabUI.jira_api_key, SettingsTabUI.jira_email, publishRN.CONFLUENCE_LINK, ui_instance)

        ui_instance._write_log(
            "Page updated successfully. View the page at: " + publishRN.CONFLUENCE_LINK)
        ui_instance.root.update()  # Refresh the UI for real-time logs

    @staticmethod
    def get_page(api_token, email, page_link, ui_instance):
        try:
            # Base URL for Confluence API
            base_url = page_link.split('/wiki')[0]

            # Extract page ID from the page link
            page_id = page_link.split('/')[-2]

            # Define the API endpoint to get page data, expanding body.storage to get content
            url = f'{base_url}/wiki/rest/api/content/{page_id}?expand=body.storage'

            # Perform the API request with basic authentication
            ui_instance._write_log(f"Fetching content for page ID {page_id}...")  # Real-time log
            ui_instance.root.update()  # Refresh the UI for real-time logs
            response = requests.get(url, auth=HTTPBasicAuth(email, api_token))

            # Check if the request was successful
            if response.status_code == 200:
                page_data = response.json()
                # Get the content from body.storage
                content = page_data['body']['storage']['value']
                ui_instance._write_log(f"Successfully retrieved content for page {page_id}.")  # Real-time log
                ui_instance.root.update()  # Refresh the UI for real-time logs
                return content
            else:
                # Print the full error response if the request fails
                ui_instance._write_log(
                    f"Failed to retrieve the page. Status code: {response.status_code}")  # Real-time log
                ui_instance.root.update()  # Refresh the UI for real-time logs
                ui_instance._write_log(f"Error response: {response.text}")  # Real-time log
                ui_instance.root.update()  # Refresh the UI for real-time logs
                return None

        except Exception as e:
            ui_instance._write_log(f"Error occurred while fetching page: {e}")  # Real-time log
            ui_instance.root.update()  # Refresh the UI for real-time logs
            return None

    @staticmethod
    def update_page(html_content, api_token, email, page_link, ui_instance):
        try:
            # Base URL for Confluence API
            base_url = page_link.split('/wiki')[0]

            # Extract page ID from the page link
            page_id = page_link.split('/')[-2]

            # Define the API endpoint to get current page data
            url = f'{base_url}/wiki/rest/api/content/{page_id}'

            # First, we need to retrieve the existing page version to update it properly
            ui_instance._write_log(f"Retrieving current version for page ID {page_id}...")  # Real-time log
            ui_instance.root.update()  # Refresh the UI for real-time logs
            response = requests.get(url, auth=HTTPBasicAuth(email, api_token))

            if response.status_code != 200:
                ui_instance._write_log(
                    f"Failed to retrieve the current page version. Status code: {response.status_code}")  # Real-time log
                ui_instance.root.update()  # Refresh the UI for real-time logs
                ui_instance._write_log(f"Error response: {response.text}")  # Real-time log
                ui_instance.root.update()  # Refresh the UI for real-time logs
                return None

            # Get the current page data and extract the current version number
            page_data = response.json()
            current_version = page_data['version']['number']

            # Increment the version for the update
            new_version = current_version + 1

            # Prepare the updated data payload with the new content
            update_payload = {
                "id": page_id,
                "type": "page",
                "title": page_data['title'],  # Keep the same title
                "version": {
                    "number": new_version
                },
                "body": {
                    "storage": {
                        "value": html_content,
                        "representation": "storage"
                    }
                }
            }

            # Send the PUT request to update the page with new content
            ui_instance._write_log(f"Updating page ID {page_id} with new content...")  # Real-time log
            ui_instance.root.update()  # Refresh the UI for real-time logs
            update_url = f'{base_url}/wiki/rest/api/content/{page_id}'
            headers = {
                'Content-Type': 'application/json'
            }
            update_response = requests.put(
                update_url,
                headers=headers,
                data=json.dumps(update_payload),
                auth=HTTPBasicAuth(email, api_token)
            )

            # Check for errors
            if update_response.status_code == 200:
                ui_instance._write_log(f"Successfully updated page ID {page_id}.")  # Real-time log
                ui_instance.root.update()  # Refresh the UI for real-time logs
                return "Page updated successfully."
            else:
                # Printing the errors
                ui_instance._write_log(
                    f"Failed to update the page. Status code: {update_response.status_code}")  # Real-time log
                ui_instance.root.update()  # Refresh the UI for real-time logs
                ui_instance._write_log(f"Error response: {update_response.text}")  # Real-time log
                ui_instance.root.update()  # Refresh the UI for real-time logs
                return "Failed to update the page."

        except Exception as e:
            ui_instance._write_log(f"Error occurred while updating the page: {e}")  # Real-time log
            ui_instance.root.update()  # Refresh the UI for real-time logs
            return None
