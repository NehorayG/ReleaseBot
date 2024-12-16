from jira import JIRA, JIRAError

import DeserializeUserData


class JiraFetch:
    def __init__(self, jira_url, username, api_token):
        self.jira_url = jira_url
        self.username = username
        self.api_token = api_token
        self.jira = JIRA(server=self.jira_url, basic_auth=(self.username, self.api_token))


    def fetch_issue_details(self, issue_key):
        try:
            issue = self.jira.issue(issue_key)

            known_limitations = issue.fields.customfield_11202
            release_notes_title = issue.fields.customfield_12235
            release_notes_description = issue.fields.customfield_11111
            issue_links = issue.fields.issuelinks
            case_ids = []

            if known_limitations is None:
                known_limitations = "N/A"

            for link in issue_links:
                if hasattr(link, 'type') and link.type.name == "Blocks":
                    if hasattr(link, 'outwardIssue'):
                        case_ids.append(link.outwardIssue.key)
                    elif hasattr(link, 'inwardIssue'):
                        case_ids.append(link.inwardIssue.key)

            filtered_case_ids = [case for case in case_ids if 'DFR' in case or 'DFT' in case]

            if not filtered_case_ids:
                filtered_case_ids = [issue_key]

            filtered_case_ids = [case.upper() for case in filtered_case_ids]

            return release_notes_title, release_notes_description, filtered_case_ids, known_limitations
        except JIRAError as e:
            return None, None, None, [
                f"Error: Unable to fetch details for the given Ticket ID. {str(e)}"]

    def fetch_caused_by_tickets(self, issue_key):
        try:
            issue = self.jira.issue(issue_key)

            # Get the issue links (looking for 'Caused by' or similar links)
            issue_links = issue.fields.issuelinks
            caused_by_tickets = []


            for link in issue_links:
                if hasattr(link, 'type') and link.type.name:
                    # If the link type is Problem/Incident or Caused by, process the inwardIssue
                    if "Caused by" in link.type.name or "Problem/Incident" in link.type.name:
                        if hasattr(link, 'inwardIssue'):
                            caused_by_tickets.append(link.inwardIssue.key)

            # Remove duplicates and return the list as upper case tickets
            caused_by_tickets = list(set(caused_by_tickets))  # Remove duplicates
            caused_by_tickets = [ticket.upper() for ticket in caused_by_tickets]  # Ensure all tickets are upper case

            # If no 'Caused by' links are found, set an appropriate message
            if not caused_by_tickets:
                caused_by_tickets = ["No 'Caused by' tickets found"]

            return caused_by_tickets

        except JIRAError as e:
            return [
                f"Error: Unable to fetch 'Caused by' tickets for the given Ticket ID. {str(e)}"]



