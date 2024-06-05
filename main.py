from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

STARTING_WORD = "slate"


class WordleBot:

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.letters_present = []
        self.letters_absent = [[], [], [], [], []]
        self.letters_correct = ["", "", "", "", "",]
        with open("words.txt") as word_file:
            self.words_list = [word.strip() for word in word_file.readlines()]
        self.rows = None
        self.row_count = 0

    def setup(self):
        self.driver.get("https://www.nytimes.com/games/wordle/index.html")
        time.sleep(1)
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/button[2]").click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/dialog/div/div/button").click()
        time.sleep(0.5)
        all_spaces = self.driver.find_elements(By.CLASS_NAME, "Tile-module_tile__UWEHN")
        self.rows = [all_spaces[i:i + 5] for i in range(0, len(all_spaces), 5)]

    def find_characters(self):
        current_row = self.rows[self.row_count]
        for space in current_row:
            if space.get_attribute("data-state") == "correct":
                self.letters_correct[current_row.index(space)] = space.text.lower()
        for space in current_row:
            if space.get_attribute("data-state") == "present":
                if space.text.lower() not in self.letters_present:
                    self.letters_present.append(space.text.lower())
                self.letters_absent[current_row.index(space)].append(space.text.lower())
        for space in current_row:
            if space.get_attribute("data-state") == "absent":
                if space.text.lower() in self.letters_present:
                    self.letters_absent[current_row.index(space)].append(space.text.lower())
                else:
                    for position in self.letters_absent:
                        if space.text.lower() not in position and space.text.lower() not in self.letters_correct[self.letters_absent.index(position)]:
                            position.append(space.text.lower())
        self.row_count += 1

    def find_possible_words(self):
        for count in range(5):
            self.words_list = [word for word in self.words_list if word[count] not in self.letters_absent[count]]
            if self.letters_correct[count] != "":
                self.words_list = [word for word in self.words_list if word[count] == self.letters_correct[count]]
        for letter in self.letters_present:
            self.words_list = [word for word in self.words_list if letter in word]

    def make_guess(self, word):
        element = self.driver.switch_to.active_element
        element.send_keys(word + Keys.ENTER)
        time.sleep(1.6)

        self.find_characters()
        self.find_possible_words()
        return random.choice(self.words_list)


bot = WordleBot()
bot.setup()
guessed_word = bot.make_guess(STARTING_WORD)

for row in range(5):
    if "" in bot.letters_correct:
        guessed_word = bot.make_guess(guessed_word)
