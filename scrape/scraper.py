import os
import time
# import requests
from bs4 import BeautifulSoup
# import webbrowser
from PIL import ImageGrab, Image
# import numpy
# import pyautogui
from selenium import webdriver


class Scraper:
    def __init__(self):
        self.scraper = None
        self.html_request = None
        self.html_data = None
        self.game = None
        self.dirpath = os.path.dirname(os.path.abspath(__file__)) + '/../'
        self.image_path = self.dirpath + '/screenshots/snap1.jpg'
        self.board_size_original = {'height': 318, 'width': 500}
        self.box_size_original = 16
        self.box_size = 40
        self.box_scale = self.box_size / self.box_size_original
        self.start = (25, 273)
        self.colors = self.data()
        self.board = []
        self.board_size = (16, 30)
        self.alive_status = True
        self.classes = {'blank': None, 'open0': 0, 'open1': 1, 'open2': 2, 'open3': 3, 'open4': 4, 'open5': 5,
                        'open6': 6, 'open7': 7, 'open8': 8,
                        'bombflagged': 9, 'bombrevealed': 9, 'bombdeath': 9, 'bombmisflagged': 9}
        self.make_board()

    def request(self, url):
        driver = webdriver.Chrome(self.dirpath + '/driver/chromedriver.exe')
        driver.get(url)
        action = webdriver.ActionChains(driver)
        while True:
            self.parse(driver)
            print('update')
            self.algorithm(driver, action)
            time.sleep(0.5)

    def algorithm(self, driver, action):
        clicked = False
        if all(None in sublist for sublist in self.board):
            driver.find_element_by_id('1_1').click()
        for r in range(len(self.board)):
            if any(self.board[r]) is not None:
                for c in range(len(self.board[r])):
                    if self.board[r][c] is not None:
                        mine_counter = 0
                        possible_mines = []
                        for i in range(r - 1, r + 2):
                            for j in range(c - 1, c + 2):
                                if i == r and j == c:
                                    continue
                                try:
                                    if self.board[i][j] is None or self.board[i][j] == 9:
                                        mine_counter += 1
                                        if self.board[i][j] is None:
                                            possible_mines.append([i, j])
                                except:
                                    continue
                        if self.board[r][c] > 0 and self.board[r][c] == mine_counter:
                            driver.find_element_by_id(str(r + 1) + '_' + str(c + 1)).click()
                            for mine in possible_mines:
                                action.context_click(driver.find_element_by_id(str(mine[0]) + '_' + str(mine[1] + 1))).perform()
                            clicked = True
        if not clicked:
            done = False
            for r in range(len(self.board)):
                for c in range(len(self.board[r])):
                    if self.board[r][c] is None:
                        driver.find_element_by_id(str(r + 1) + '_' + str(c + 1)).click()
                        done = True
                        break
                if done:
                    break

    def parse(self, driver):
        self.html_request = driver.page_source
        self.html_data = BeautifulSoup(self.html_request, 'html.parser')
        self.game = \
        self.html_data.contents[0].contents[2].contents[9].contents[0].contents[0].contents[0].contents[0].contents[
            3].contents[1].contents[3].contents
        for piece in self.game:
            if piece.attrs['class'][0] == 'facedead':
                self.alive_status = False
                driver.find_element_by_id(piece.attrs['id']).click()
                self.alive_status = True
            if piece.attrs['class'][0] == 'square' and 'style' not in piece.attrs:
                position = piece.attrs['id'].split('_')
                position = [int(point) for point in position]
                self.board[position[0] - 1][position[1] - 1] = self.classes[piece.attrs['class'][1]]
                if position == [1, 1]:
                    print(piece.attrs['class'])
                    # driver.find_element_by_id(piece.attrs['id']).click()  # click that box

    def parse_image(self):
        self.make_board()
        im = Image.open(self.image_path)
        px = im.load()
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                color = 0
                for i in range(self.start[0] + (self.box_size * c), self.start[0] + (self.box_size * (c + 1)) + 1):
                    for j in range(self.start[1] + (self.box_size * r), self.start[1] + (self.box_size * (r + 1)) + 1):
                        if px[i, j] in self.colors.keys():
                            color = self.colors[px[i, j]]  # doesn't do 0 or None well
                            break
                    if color != 0:
                        break
                self.board[r][c] = color

    def make_board(self):
        for i in range(self.board_size[0]):
            self.board.append([None for n in range(self.board_size[1])])
            # for j in range(self.board_size[1]):

    def screenshot(self):
        snapshot = ImageGrab.grab()
        save_path = self.image_path
        snapshot.save(save_path)

    def data(self):
        colors = {(254, 254, 254): None,  # these kinda suck
                  # (189, 189, 189): 0,
                  (160, 240, 120): 1,
                  (0, 125, 0): 2,
                  (250, 6, 6): 3,
                  (): 4,
                  (131, 0, 2): 5,
                  (): 6,
                  (): 7,
                  (): 8}
        return colors


if __name__ == '__main__':
    scraper_object = Scraper()
    test_url = 'http://minesweeperonline.com/'
    # test_url = 'http://minesweeperonline.com/minesweeper.min.js?v=1592954863'
    # test_url = 'https://www.google.com/'
    scraper_object.request(test_url)
    debug = 'here'
