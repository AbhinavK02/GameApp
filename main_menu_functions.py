import os
import logging
import random
from kivy.app import App

# You might need to import other Kivy components if the functions use them
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ListProperty, StringProperty

# Setup logger for this specific module
logger = logging.getLogger(__name__)

default_words = """
Football
Basketball
Tennis
Church
Computer
Pizza
Car
Book
Movie
Music
Game
Art
Monopoly
Science
History
Math
Cooking
"""

# Create a class to hold the functions
class MainMenuFunctions:
    def on_enter(self, screen_instance):
        logger.info("Entering Main Menu")
        foundThemes = self.findThemes()
        logger.info(f"Found themes: {foundThemes}")
        if "Default" in foundThemes:
            logger.info("No Default theme found, creating it.")
            self.createDefaut()
        
        screen_instance.themes = foundThemes

    def findThemes(self):
        themes = []
        found = False
        themes_directory = os.path.join(os.getcwd(), 'GameApp', 'Themes')
        if not os.path.exists(themes_directory):
            logger.info("Themes directory does not exist. Creating it.")
            os.makedirs(themes_directory)
            self.createDefaut()
        for filename in os.listdir(themes_directory):
            if filename.endswith('.txt'):
                found = True
                theme_name = filename[:-4]
                themes.append(theme_name)
        if not found:
            logger.info("No themes found in the Themes directory.")
            themes.append("Default")
        else:
            logger.info(f"Found themes: {themes}")
        return themes

    def createDefaut(self):
        default_theme_path = os.path.join(os.getcwd(), 'GameApp', 'Themes', 'Default.txt')
        if not os.path.exists(default_theme_path):
            with open(default_theme_path, 'w', encoding='utf-8') as file:
                file.write(default_words)
                logger.info("Default theme created with default words.")

    def ReadWords(self, theme):
        file_location = os.getcwd() + '/GameApp/Themes/' + theme + '.txt'
        try:
            with open(file_location, 'r', encoding='utf-8') as file:
                words = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            logger.info("Error: The file 'words.txt' was not found. Please ensure it exists.")
        except Exception as e:
            logger.info(f"An error occurred: {e}")
        logger.info("Words loaded from file.")
        return words

    def AssignWord(self, app):
        Words = app.words
        word = random.choice(Words)
        logger.info(f"Assigned words: {word}")
        app.Word = word

    def clearText(self, text_input_widget):
        text_input_widget.text = ''

    def start_game_action(self, screen_instance):
        # Access player names
        players = [screen_instance.ids.player1_name.text, screen_instance.ids.player2_name.text, screen_instance.ids.player3_name.text]
        # Check if player names are unique
        if((players[0] == players[1]) or (players[0] == players[2]) or (players[1] == players[2])):
            logger.info("Error: Player names must be unique!")
            screen_instance.ids.player_name_label.color = [0.8, 0, 0, 0.8]  # Change label color to red to indicate error
            return
        screen_instance.ids.player_name_label.color = labelDefaultColor # Reset label color to black
        
        # Check if player names are empty
        if any(name.strip() == '' for name in players):
            players = ["Player 1", "Player 2", "Player 3"]  # Default names if empty"]
            logger.info("One or more player names are empty. Using default names.")
        logger.info(f"Starting game with players: {players}")

        # Check for themes
        theme = screen_instance.ids.theme_spinner.text.strip()  # Get the selected theme from the dropdown
        if theme == "Select Theme" or theme == "":
            logger.info("No theme selected!")
            screen_instance.ids.themes_label.color = [0.8, 0, 0, 0.8]  # Change label color to red to indicate error]
            return
        screen_instance.ids.themes_label.color = labelDefaultColor  # Reset label color to black
        logger.info(f"Selected theme: {theme}")


        # Game setup
        Sequence = random.sample(players, len(players))  # Randomly shuffle player names
        impostor = random.choice(Sequence)  # Randomly select an impostor
        app = App.get_running_app()
        app.player_Sequence = Sequence  # Store the sequence in the app instance
        app.current_player_index = 1  # Initialize current player index
        app.impostor = impostor  # Store the impostor in the app instance
        timer = screen_instance.ids.timer_max.text  # Get the timer max value from the input
        app.timer_max = int(timer[0])  # Store the timer max value in the app instance
        logger.info(f"Impostor selected: {impostor}")
        logger.info(f"Player sequence: {Sequence}")
        logger.info(f"Timer max value: {app.timer_max}")
        
        # Read words from file
        app.words = screen_instance.ReadWords(theme)  # Read words from file
        # Assign words to players
        screen_instance.AssignWord(app)
        screen_instance.manager.get_screen('game_page').ids.current_player_label.text = f"{Sequence[0]}"
        
        # Finally, switch to the GamePage
        screen_instance.manager.transition = SlideTransition(direction='left', duration=0.3)
        screen_instance.manager.current = 'game_page'