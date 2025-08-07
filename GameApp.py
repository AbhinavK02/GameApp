from time import sleep
from turtle import position
from webbrowser import BackgroundBrowser
from kivy.app import App
from kivy.lang import Builder

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.clock import Clock

from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

from kivy.animation import Animation

from kivy.graphics.vertex_instructions import (Rectangle, Ellipse, Line)
from kivy.graphics.context_instructions import Color

import logging
import random
import os

from kivy.properties import ListProperty, NumericProperty, StringProperty

labelDefaultColor = [0.8, 0.8, 0.8, 1]  # Default color for labels

# Logger setup
logger = logging.getLogger(__name__)

# Kivy file content
Builder.load_file("ui.kv")


# Python code for the game application
class MainMenu(Screen):
    text_color = ListProperty([1, 0, 1, 1])  # RGBA color for text

    def clearText(self, text_input_widget):
        text_input_widget.text = ''\

    def ReadWords(self, theme):
        # To skip blank lines
        file_location = os.getcwd() + '/GameApp/Themes/' + theme + '.txt'
        try:
            with open(file_location, 'r', encoding='utf-8') as file:
                words = [line.strip() for line in file if line.strip()] # Only include if not empty after stripping
        except FileNotFoundError:
            logger.info("Error: The file 'words.txt' was not found. Please ensure it exists.")
        except Exception as e:
            logger.info("An error occurred: {e}")
        logger.info("Words loaded from file.")
        return words

    def AssignWord(self, app):
        # Assign words to players
        Words = app.words  # Get the list of words from the app instance
        word = random.choice(Words)  # Randomly select a word
        logger.info(f"Assigned words: {word}")
        # Update the text inputs with the assigned words
        app.Word = word

    def start_game_action(self):
        # Access player names
        players = [self.ids.player1_name.text, self.ids.player2_name.text, self.ids.player3_name.text]
        # Check if player names are unique
        if((players[0] == players[1]) or (players[0] == players[2]) or (players[1] == players[2])):
            logger.info("Error: Player names must be unique!")
            self.ids.player_name_label.color = [0.8, 0, 0, 0.8]  # Change label color to red to indicate error
            return
        self.ids.player_name_label.color = labelDefaultColor # Reset label color to black
        
        # Check if player names are empty
        if any(name.strip() == '' for name in players):
            players = ["Player 1", "Player 2", "Player 3"]  # Default names if empty"]
            logger.info("One or more player names are empty. Using default names.")
        logger.info(f"Starting game with players: {players}")

        # Check for themes
        if(self.ids.theme_celebrities_checkbox.active):
            theme="celebrities"
        elif(self.ids.theme_movies_checkbox.active):
            theme="movies"
        elif(self.ids.theme_animals_checkbox.active):
            theme="animals"
        else:
            logger.info("No theme selected!")
            self.ids.themes_label.color = [0.8, 0, 0, 0.8]  # Change label color to red to indicate error]
            return
        self.ids.themes_label.color = labelDefaultColor  # Reset label color to black
        logger.info(f"Selected theme: {theme}")


        # Game setup
        Sequence = random.sample(players, len(players))  # Randomly shuffle player names
        impostor = random.choice(Sequence)  # Randomly select an impostor
        app = App.get_running_app()
        app.player_Sequence = Sequence  # Store the sequence in the app instance
        app.current_player_index = 1  # Initialize current player index
        app.impostor = impostor  # Store the impostor in the app instance
        timer = self.ids.timer_max.text  # Get the timer max value from the input
        app.timer_max = int(timer[0])  # Store the timer max value in the app instance
        logger.info(f"Impostor selected: {impostor}")
        logger.info(f"Player sequence: {Sequence}")
        logger.info(f"Timer max value: {app.timer_max}")
        
        # Read words from file
        app.words = self.ReadWords(theme)  # Read words from file
        # Assign words to players
        self.AssignWord(app)
        self.manager.get_screen('game_page').ids.current_player_label.text = f"{Sequence[0]}"
        
        # Finally, switch to the GamePage
        self.manager.transition = SlideTransition(direction='left', duration=0.3)
        self.manager.current = 'game_page'


class GamePage(Screen):
    def revealHide(self, button_state):
        app = App.get_running_app()
        currentIndex = app.current_player_index
        current_player = app.player_Sequence[currentIndex-1]
        logger.info(f"Current player: {current_player} at index {currentIndex}")
        impostor = app.impostor
        if((button_state == 1) and (current_player == impostor)):
            logger.info(f"Impostor!")
            self.ids.revealHide_button.text = "Impostor"
        elif((button_state == 1) and (current_player != impostor)):
            word = app.Word # Get the word for the non impostor player
            logger.info(f"Not an impostor, word: {word}")
            self.ids.revealHide_button.text = word
        else:
            logger.info("Hiding word")
            self.ids.revealHide_button.text = "Tap to reveal"

    def go_to_main_menu(self):
        """
        Resets the toggle button state and navigates back to the main menu.
        """
        logger.info("Returning to Main Menu from GamePage.")
        # Reset the toggle button state before leaving the page
        self.ids.revealHide_button.state = 'normal'
        # Call revealHide with 0 to ensure the label is reset if it was showing a secret
        self.revealHide(0)
        self.manager.transition = SlideTransition(direction='right', duration=0.3)
        self.manager.current = 'main_menu'

    def NextPlayerAction(self):
        content = self.ids.container
        app = App.get_running_app()
        current_Index = app.current_player_index
        if(current_Index < len(app.player_Sequence)):
            app.current_player_index += 1
        else:
            app.current_player_index = -1
        if(app.current_player_index == -1):
            logger.info("Moving to timer screen")
            self.ids.revealHide_button.text = "Tap to reveal"
            self.ids.revealHide_button.state = 'normal'  # Reset the toggle button state
            self.manager.transition = SlideTransition(direction='left', duration=0.3)
            self.manager.current = 'timer_page'
        else:
            anim_out = Animation(y=self.height, duration=0.3)  # Move the content up
            
            def after_slide_out(*args):
                current_player = app.player_Sequence[current_Index]
                logger.info(f"Next player: {current_player} at index {app.current_player_index}")
                self.ids.current_player_label.text = f"{current_player}"
                self.ids.revealHide_button.state = 'normal'  # Reset the toggle button state
                self.ids.revealHide_button.text = "Tap to reveal"  # Reset the button text
                content.y = -self.height  # move it off-screen below (to come up next)
                anim_in = Animation(y=0, duration=0.3)
                anim_in.start(content)

            anim_out.bind(on_complete=after_slide_out)
            anim_out.start(content)

class GameOver(Screen):
    def go_to_main_menu(self):
        self.manager.transition = SlideTransition(direction='right', duration=0.3)
        self.manager.current = 'main_menu'

class TimerPage(Screen):
    timer_text = StringProperty("00:00")
    def on_enter(self):
        """
        Called when the TimerPage is entered.
        Starts the timer countdown.
        """
        logger.info("Entering TimerPage")
        app = App.get_running_app()
        timer = app.timer_max
        self.timer_text = "0" + str(timer) + ":00"

    def start_timer(self):
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        # Update the timer every second
        time = self.timer_text.split(":")
        minutes = int(time[0])
        seconds = int(time[1])
        if seconds == 0:
            if minutes == 0:
                # Timer finished, navigate to GameOver screen
                logger.info("Timer finished, navigating to GameOver screen.")
                self.manager.transition = SlideTransition(direction='left', duration=0.3)
                self.manager.current = 'game_over'
                return False
            else:
                minutes -= 1
                seconds = 59
        else:
            seconds -= 1
        # Format the timer text
        self.timer_text = f"{minutes:02}:{seconds:02}"

    def skip_timer(self):
        """
        Skips the timer and navigates to GameOver screen.
        """
        #self.timer_text.text = "00:00"  # Reset the timer text
        logger.info("Skipping timer, navigating to Impostor Reveal screen.")
        self.manager.transition = SlideTransition(direction='left', duration=0.3)
        self.manager.current = 'impostor_reveal'

class ImpostorReveal(Screen):
    # This property will hold the text for the revealing label
    revealing_impostor_name = StringProperty("...")

    def on_pre_enter(self, *args):
        # Reset the label text before entering, so it starts with "..."
        self.revealing_impostor_name = "..."
        # Schedule the reveal after 2 seconds
        Clock.schedule_once(self.reveal_impostor, 2)

    def reveal_impostor(self, dt): # dt is delta time, passed by Clock
        app = App.get_running_app()
        impostor = app.impostor
        # Set the property, which will update the label in KV
        self.ids.revealing_label.text = impostor
        print(f"The impostor is: {impostor}")

    def backToMenu(self):
        """
        Navigates back to the main menu.
        """
        self.ids.revealing_label.text = "..."  # Reset the label text
        logger.info("Returning to Main Menu from Impostor Reveal screen.")
        self.manager.transition = SlideTransition(direction='left', duration=0.3)
        self.manager.current = 'main_menu'
    
class GameApp(App):
    def build(self):
        # Create the ScreenManager and add screens
        logger.info("Building GameApp")
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='main_menu'))
        sm.add_widget(GamePage(name='game_page'))
        sm.add_widget(GameOver(name='game_over'))
        sm.add_widget(TimerPage(name='timer_page'))
        sm.add_widget(ImpostorReveal(name='impostor_reveal'))
        return sm


if __name__ == '__main__':
    log_directory = "GameApp\GameLogs"  # You can change this to any desired directory
    log_file_name = "gameApp.log"
    log_file_path = os.path.join(log_directory, log_file_name)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    # Set the logger's overall level
    logger.setLevel(logging.INFO)

    # Create a FileHandler
    file_handler = logging.FileHandler(log_file_path, mode='a')
    file_handler.setLevel(logging.INFO) # Set level for file output

    # Create a Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the FileHandler to the logger
    logger.addHandler(file_handler)

    # Add a StreamHandler to also print to console (optional but highly recommended for debugging)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG) # Console can be more verbose
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.info("Starting GameApp")
    GameApp().run()