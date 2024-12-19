class DeserializeUserData:
    # Class-level variables
    release_notes_title = ""
    release_notes_description = ""
    related_ticket_ids = []
    known_limitations = "None"
    affected_components = []
    publish_type = ""

    @staticmethod
    def __get_tickets(ticket_line):
        """
        Private function to extract ticket IDs from a line of text.
        :param ticket_line: The line containing ticket IDs separated by commas.
        :return: A list of ticket IDs.
        """
        return [ticket.strip() for ticket in ticket_line.split(",") if ticket.strip()]

    @staticmethod
    def __extract_publish_type(title_line):
        """
        Private function to extract the publish type from the title line.
        :param title_line: The line containing the title.
        :return: The first word of the title in uppercase (FEATURE, IMPROVEMENT, or FIX).
        """
        return title_line.split()[0].upper() if title_line else ""

    @staticmethod
    def __extract_components(components_line):
        """
        Private function to extract affected components from a line of text.
        :param components_line: The line containing affected components separated by commas.
        :return: A list of affected components.
        """
        return [component.strip() for component in components_line.split(",") if component.strip()]

    @classmethod
    def deserialize(cls, text):
        """
        Deserialize the provided text into structured data.
        :param text: The input text to parse.
        :return: A dictionary containing structured data.
        """
        cls.release_notes_title = ""
        cls.release_notes_description = []
        cls.related_ticket_ids = []
        cls.known_limitations = "None"
        cls.affected_components = []
        cls.publish_type = ""
        processed = False  # Flag to track if the line has been processed

        current_section = None

        # Iterate through each line and classify it
        for line in text.splitlines():
            stripped_line = line.strip()

            if stripped_line.startswith("Release Notes Title:"):
                current_section = "title"
                continue

            elif stripped_line.startswith("Release Notes Description:"):
                current_section = "description"
                continue

            elif stripped_line.startswith("Affected Components:"):
                current_section = "affected_components"
                continue

            elif stripped_line.startswith("Related Ticket IDs (Case ID):"):
                current_section = "related_ticket_ids"
                continue

            elif stripped_line.startswith("Known Limitations:"):
                current_section = "known_limitations"
                continue

            # Append content to the appropriate section
            if current_section == "title":
                cls.release_notes_title += stripped_line

            elif current_section == "description":
                cls.release_notes_description.append(line)

            elif current_section == "affected_components":
                cls.affected_components.extend(cls.__extract_components(stripped_line))

            elif current_section == "related_ticket_ids":
                cls.related_ticket_ids.extend(cls.__get_tickets(stripped_line))

            elif current_section == "known_limitations":
                cls.known_limitations += stripped_line

        cls.publish_type = cls.__extract_publish_type(cls.release_notes_title)

        # Check if the line starts with "FIX" or "FIXED" (in uppercase) and set the publish_type as "Fixed"
        if "FIX" in cls.release_notes_title.upper():
            cls.publish_type = "FIXED"


        # Remove publish type from the title for a cleaner output
        title_without_type = " ".join(cls.release_notes_title.split()[1:]).strip()

        # Join description lines and clean up
        description = " ".join(cls.release_notes_description).replace("Release Notes Description:", "").strip()
        cls.release_notes_description = description

        # Move case IDs from affected components to case IDs if necessary
        final_affected_components = []
        for component in cls.affected_components:
            if component not in cls.related_ticket_ids:
                final_affected_components.append(component)

        cls.release_notes_title = title_without_type


        # Return the extracted details in a structured format
        return {
            "title": title_without_type,
            "publish_type": cls.publish_type,
            "description": cls.release_notes_description,
            "affected_components": cls.affected_components,
            "related_ticket_ids": cls.related_ticket_ids,
            "known_limitations": cls.known_limitations,
        }
