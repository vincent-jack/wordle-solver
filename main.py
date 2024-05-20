from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import random

STARTING_WORD = "slate"


class WordleBot:

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.letters_present = []
        self.letters_absent = []
        self.letters_correct = ["", "", "", "", "",]
        with open("words.txt") as word_file:
            self.words_list = [word.strip() for word in word_file.readlines()]
        self.row_number = 0

    def setup(self):
        self.driver.get("https://www.nytimes.com/games/wordle/index.html")
        time.sleep(1)
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/button[2]").click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/dialog/div/div/button").click()
        time.sleep(0.5)

    def make_guess(self, word):
        self.row_number += 1
        element = self.driver.switch_to.active_element
        element.send_keys(word + Keys.ENTER)
        time.sleep(2)
        for column in range(1, 6):
            try:
                word_square = self.driver.find_element(By.XPATH, f"/html/body/div[2]/div/div[3]/main/div[1]/div/"
                                                                 f"div[{self.row_number}]/div[{column}]/div")
            except NoSuchElementException:
                word_square = self.driver.find_element(By.XPATH,f"/html/body/div[2]/div/div[4]/main/div[1]/div/"
                                                                f"div[{self.row_number}]/div[{column}]/div")
            result = word_square.get_attribute("aria-label")
            letter = result[12].lower()

            if ("absent" in result and letter not in self.letters_absent and letter not in self.letters_correct
                    and letter not in self.letters_present):
                self.letters_absent.append(letter)
            elif "correct" in result and self.letters_correct[column - 1] != letter:
                self.letters_correct[column - 1] = letter
                if letter in self.letters_absent:
                    self.letters_absent.remove(letter)
            elif "present" in result and letter not in self.letters_present:
                self.letters_present.append(letter)

        for absent_letter in self.letters_absent:
            self.words_list = [word for word in self.words_list if absent_letter not in word]

        for present_letter in self.letters_present:
            self.words_list = [word for word in self.words_list if present_letter in word]

        indices = [index for index, letter in enumerate(self.letters_correct) if letter != ""]
        for index in indices:
            self.words_list = [word for word in self.words_list if word[index] == self.letters_correct[index]]
        
        return random.choice(self.words_list)


bot = WordleBot()
bot.setup()
guessed_word = bot.make_guess(STARTING_WORD)

for row in range(5):
    if "" not in bot.letters_correct:
        print(f"The correct word is: {"".join(bot.letters_correct)}")
        break
    else:
        guessed_word = bot.make_guess(guessed_word)
