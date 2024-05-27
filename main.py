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
        self.index = 0

    def setup(self):
        self.driver.get("https://www.nytimes.com/games/wordle/index.html")
        time.sleep(1)
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/button[2]").click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/dialog/div/div/button").click()
        time.sleep(0.5)

    def find_keys(self):
        spaces = self.driver.find_elements(By.CLASS_NAME, "Tile-module_tile__UWEHN")
        for column in range(5):
            current_space = spaces[self.index]
            state = current_space.get_attribute("data-state")
            key = current_space.text.lower()
            if state == "correct":
                self.letters_correct[column] = key
                if key in self.letters_absent[column]:
                    self.letters_absent[column] = [letter for letter in self.letters_absent[column] if letter != key]
                if key in self.letters_present:
                    self.letters_present = [letter for letter in self.letters_present if letter != key]
            if state == "present":
                if key not in self.letters_present:
                    self.letters_present.append(key)
                self.letters_absent[column].append(key)
            if state == "absent":
                for count in range(5):
                    if key not in self.letters_correct[count] and key not in self.letters_absent[count]:
                        self.letters_absent[count].append(key)
            self.index += 1

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
        time.sleep(2)

        self.find_keys()
        self.find_possible_words()
        return random.choice(self.words_list)


bot = WordleBot()
bot.setup()
guessed_word = bot.make_guess(STARTING_WORD)

for row in range(5):
    if "" in bot.letters_correct:
        guessed_word = bot.make_guess(guessed_word)
