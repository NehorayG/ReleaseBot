# ReleaseBot---Nehoray-Gil

## Introduction
Welcome to the Jira Ticket Viewer! This application allows you to fetch, view, and edit Jira ticket information seamlessly. The interface is designed for ease of use with a modern, clean look.

## Getting Started

### Prerequisites
Before using the application, make sure you have all the required dependencies installed.

### Run the Setup Batch File:
1. Navigate to the `ReleaseBotFiles` directory.
2. Run `run.bat` to install all the necessary libraries.
3. You will see a message: **"All required libraries are installed."** if the setup is successful.

### Configuration
To start using the app, you will need to configure your Jira credentials.

#### **Email & Jira API Key:**
1. In the top-left corner of the app, click the settings icon (gear icon).
2. Fill in your **email** and **Jira API key** in the settings tab.

#### **How to Get Your Jira API Key:**
1. Log in to your Jira account.
2. Navigate to **Account Settings**.
3. Select **Security** and click **Create and Manage API Tokens**.
4. Click **Create API Token**, name it, and generate it.
5. Copy the token and paste it in the app settings.

## Using the App
Once the settings are configured, you can start using the application:

### Fetching Ticket Information:
1. Enter a Jira Ticket ID in the **"Enter Jira Ticket ID"** field.
2. Click **Fetch Ticket Info** to retrieve the ticket's details.

### Editing and Saving Changes:
1. The ticket information will appear in the large text area below.
2. You can make changes to the Release Notes details directly.
3. Click **Save Changes** to save the updated information.

### Preview Mode:
- If you want to view the Release Notes in a preview format (read-only mode), click **Preview**.
- Click **Return Edit Mode** to go back to editing the ticket.

### Publishing Release Notes:
1. Once you have finished editing the ticket, you can publish the release notes by clicking **Publish**.
2. If any required fields are empty, the app will prompt you to confirm the publish process.

## UI Overview
- **Main Interface:**
  - **Ticket ID Input**: Where you enter the Jira ticket ID.
  - **Fetch Ticket Info Button**: Fetches the ticket details from Jira.
  - **Save Changes Button**: Saves any changes you make to the ticket details.
  - **Preview Button**: Switches between preview mode and edit mode.
  - **Publish Button**: Allows you to publish the release notes once all required fields are filled.
  - **Settings Icon**: Located in the top-left corner. Click it to configure your Jira credentials (**email & API key**).

## Release Notes Format Instructions

### **Jira Release Notes Title Format**
The title of the release notes should follow this format:
TYPE TITLE

Where:
- **TYPE** is one of the following:
  - `IMPROVEMENT`
  - `FIX/FIXED`
  - `FEATURE`
- **TITLE** is a concise description of the change or feature.

**Example:**
IMPROVEMENT Azure AppRegistration new property - 11:30 UTC

### **Jira Release Notes Description Format**
The description should be written as follows:
Provide a detailed description of the change or feature (this can span multiple lines if needed).

Followed by the affected components, written on the next line, and in the format:
<br>Affected Components:<br> Component1, Component2, Component3

- The affected components should be listed on the same line under the 
**Affected Components** header.

**Example:**
Added support for a new property in Azure AppRegistration - “assignmentRoles” in Compliance Engine.

Affected Components: <br>
Fetchers, Compliance Engine

### **Case ID**
The **Case ID** will be automatically assigned and is not required to be entered manually.

### **Known Limitations**
Users will need to manually enter any known limitations in the UI before publishing the release notes.

### **Example of a Completed Jira Ticket:**

**Release Notes Title:**
IMPROVEMENT Azure AppRegistration new property - 11:30 UTC

**Release Notes Description:**
Added support for a new property in Azure AppRegistration - “assignmentRoles” in Compliance Engine.

Affected Components:<br> Fetchers, Compliance Engine

### Full Example:
Release Notes Title: FEATURE Azure AppRegistration new property - 11:30 UTC

Release Notes Description: Added support for a new property in Azure AppRegistration - "assignmentRoles" in Compliance Engine. This property enhances the management of assignment roles within the Compliance Engine.

Affected Components:<br> Fetchers, Compliance Engine, UI

Some legacy configurations may not be fully compatible with the new property.
Users need to ensure that their fetcher configurations are updated for compatibility.

## Contributing
If you'd like to contribute to the development of this application, feel free to fork the repository and submit a pull request.