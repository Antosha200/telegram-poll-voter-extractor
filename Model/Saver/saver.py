import json
import os
from datetime import datetime

class PollSaver:
    def __init__(self, base_dir=None):
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        )

        # Setting the default path
        if base_dir is None:
            self.base_dir = os.path.join(
                self.project_root, 'Documents', 'Results'
            )
        else:
            self.base_dir = base_dir

    def save_as_json(self, poll_date: datetime, poll_data: dict, subfolder="Polls") -> str:
        """
        Saves the survey results to a JSON file in a new format

        :param poll_date: Date and time when the survey was created
        :param poll_data: Survey data in a new format
        :param subfolder: A subfolder for categorizing results
        :return: The path to the saved file
        """
        save_dir = os.path.join(self.base_dir, subfolder)
        os.makedirs(save_dir, exist_ok=True)

        filename = f"{poll_date:%Y%m%d_%H%M%S}.json"
        filepath = os.path.join(save_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(poll_data, f, ensure_ascii=False, indent=2)

        return filepath

    #other formats
    def save_as_csv(self, poll_date, poll_data, subfolder="Polls"):
        pass

    def save_as_excel(self, poll_date, poll_data, subfolder="Polls"):
        pass