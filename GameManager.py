# pygame相关
import pygame
from pygame import display
from pygame import event
from pygame import font
from pygame import image
from pygame import time
from pygame import mixer
from pygame.locals import *

# 实体类
from MusicPlay import MusicPlay
from Enums import GameStatus, PlayerTurn


class GameManager:
    def __init__(self):
        pygame.init()                                                       # pygame初始化
        self.clock = time.Clock()                                    # 帧率控制
        self.source = "./source/"                                          # 素材文件目录
        self.font = font.Font(self.source + "simhei.ttf", 20)        # 游戏字体
        self.screen = display.set_mode((1200, 825))                  # 窗口初始化
        display.set_icon(self.__image_load("Dog.ico"))
        display.set_caption("大富翁")
        self.music = mixer.music.load(self.source + "BackgroundMusic.mp3")
        self.backgroundMusic = MusicPlay(self.music)                        # 背景音乐播放

        self.initialToPlaying = False                                       # 最初进入游戏的标志变量
        self.gameStatus = GameStatus.start                                  # 游戏状态
        self.playerTurn = PlayerTurn.start                                  # 玩家行动回合
        self.cheat = [0, 0, 0]                                              # 开发者模式标记
        self.spaceKeyDown = event                                    # 用于存储空格被按下的事件
        self.PCActKey = [0, 0, 0]                                           # 存储PCAct按键键值，依次是K_b, K_a, K_d
        self.winner = ""                                                    # 胜利者

        self.start = self.__image_load("Start.png")
        self.gameFail = self.__image_load("GameFail.png")
        self.gameWin = self.__image_load("GameWin.png")
        self.gameMap = self.__image_load("Map.png")
        self.tips = self.__image_load("Tips.png")

        self.musicOn = self.__image_load("MusicOn.png")
        self.musicOff = self.__image_load("MusicOff.png")
        self.musicImage = self.musicOn
        self.musicBarrier = self.__image_load("MusicBarrier.png")
        self.musicButtonLocation = (41 * 25, 27 * 25)
        self.musicButtonRect = Rect(41 * 25, 27 * 25, 100, 75)

        self.activeOn = self.__image_load("ActiveOn.png")
        self.activeOff = self.__image_load("ActiveOff.png")

        self.PCName = ""
        self.PCImage = self.__image_load("PC.png")
        self.PCFixImage = self.__image_load("PCFix.png")
        self.PCBoard = [(5 * 25, 4 * 25 + 12), (5 * 25, 8 * 25)]

        self.NPCName = ""
        self.NPCImage = self.__image_load("NPC.png")
        self.NPCFixImage = self.__image_load("NPCFix.png")
        self.NPCBoard = [(27 * 25, 4 * 25 + 12), (27 * 25, 8 * 25)]

        self.diceImages = list()
        for j in range(6):
            self.diceImages.append(self.__image_load("Dice%d.png" % (j + 1)))
        self.diceBarrier = self.__image_load("DiceBarrier.png")
        self.diceBoard = [(22 * 25, 18 * 25 + 5), (19 * 25 + 12, 18 * 25 + 5), (24 * 25 + 13, 18 * 25 + 5)]
        self.diceLocation = list()
        self.diceLocation.append(self.diceBoard[0])
        self.diceSteps = (0, 0, True)

        self.cattleOfPC = list()
        self.wasteland = self.__image_load("Wasteland.png")
        self.cattleOfPC.append(self.wasteland)
        for j in range(5):
            self.cattleOfPC.append(self.__image_load("HouseA%d.png" % (j + 1)))

        self.cattleOfNPC = list()
        self.cattleOfNPC.append(self.wasteland)
        for j in range(5):
            self.cattleOfNPC.append(self.__image_load("HouseB%d.png" % (j + 1)))

    def event_deal(self):
        for even in event.get():
            if even.type == QUIT or (even.type == KEYDOWN and even.key == K_e):
                self.__quit()

            if even.type == KEYDOWN:
                if even.key == K_r:
                    self.__play_again()

                elif even.key == K_SPACE and self.gameStatus is GameStatus.waitIn:
                    self.gameStatus = GameStatus.initial
                    self.spaceKeyDown = even

                elif even.key == K_SPACE and self.gameStatus is GameStatus.playing:
                    self.turn_change_space()

                elif self.gameStatus is GameStatus.playing and self.__developer_pattern_check() is False:
                    self.__set_developer_pattern(even.key)

                self.__set_PC_act_key(even)

            if even.type == MOUSEBUTTONDOWN and even.button == BUTTON_LEFT:
                self.__music_pause(even.pos)

    def post_space_key_down(self):
        event.post(self.spaceKeyDown)

    def get_character_name(self, PC_name, NPC_name):
        self.PCName = PC_name
        self.NPCName = NPC_name

    @staticmethod
    def image_update():
        display.update()

    def __image_load(self, name):
        return image.load(self.source + name).convert_alpha()

    def draw_beginning(self):
        for j in range(150):
            self.clock.tick(300)
            self.screen.blit(self.gameMap, (0, 0))
            self.screen.blit(self.PCFixImage, (6 * 25 + 13 + j * 1 - 10, 6 * 25 + 13 - 10))
            self.screen.blit(self.NPCFixImage, (38 * 25 + 13 - j * 1 - 10, 6 * 25 + 13 - 10))
            self.screen.blit(self.start, (175, 325))
            self.screen.blit(self.musicImage, (41 * 25, 27 * 25))
            display.update()

    def draw_map(self):
        self.screen.blit(self.gameMap, (0, 0))

    @staticmethod
    def __location_convert(position):
        if position <= 15:
            return position * 75, 0
        if position <= 25:
            return 15 * 75, (position - 15) * 75
        if position <= 40:
            return (15 - (position - 25)) * 75, 10 * 75
        if position <= 49:
            return 0, (9 - (position - 41)) * 75

    def draw_character(self, PC_pos, NPC_pos):
        # 动态位置绘制
        if self.playerTurn is PlayerTurn.PCAct or self.playerTurn is PlayerTurn.NPCMove or \
                self.playerTurn is PlayerTurn.start or self.initialToPlaying is True:
            self.screen.blit(self.NPCImage, self.__location_convert(NPC_pos))
            self.screen.blit(self.PCImage, self.__location_convert(PC_pos))
        else:
            self.screen.blit(self.PCImage, self.__location_convert(PC_pos))
            self.screen.blit(self.NPCImage, self.__location_convert(NPC_pos))
        # 固定位置绘制
        self.screen.blit(self.PCFixImage, (19 * 25 - 21, 4 * 25))
        self.screen.blit(self.NPCFixImage, (41 * 25 - 21, 4 * 25))

    def draw_active_status(self):
        if self.playerTurn is PlayerTurn.PCMove or self.playerTurn is PlayerTurn.PCAct:
            self.screen.blit(self.activeOn, (4 * 25, 4 * 25))
            self.screen.blit(self.activeOn, (4 * 25, 8 * 25))
            self.screen.blit(self.activeOff, (26 * 25, 4 * 25))
            self.screen.blit(self.activeOff, (26 * 25, 8 * 25))
        elif self.playerTurn is PlayerTurn.NPCMove or self.playerTurn is PlayerTurn.NPCAct:
            self.screen.blit(self.activeOff, (4 * 25, 4 * 25))
            self.screen.blit(self.activeOff, (4 * 25, 8 * 25))
            self.screen.blit(self.activeOn, (26 * 25, 4 * 25))
            self.screen.blit(self.activeOn, (26 * 25, 8 * 25))
        else:
            self.screen.blit(self.activeOff, (4 * 25, 4 * 25))
            self.screen.blit(self.activeOff, (4 * 25, 8 * 25))
            self.screen.blit(self.activeOff, (26 * 25, 4 * 25))
            self.screen.blit(self.activeOff, (26 * 25, 8 * 25))

    def draw_lands(self, all_lands):
        for land in all_lands:
            if land.owner == self.PCName:
                self.screen.blit(self.cattleOfPC[land.level], self.__location_convert(land.position))
            elif land.owner == self.NPCName:
                self.screen.blit(self.cattleOfNPC[land.level], self.__location_convert(land.position))
            else:
                self.screen.blit(self.wasteland, self.__location_convert(land.position))

    def draw_tips(self):
        if self.gameStatus is not GameStatus.over:
            self.screen.blit(self.tips, (3 * 25, 27 * 25))

    def __developer_pattern_check(self):
        if self.cheat[0] * self.cheat[1] * self.cheat[2] == 1:
            return True
        return False

    def __set_developer_pattern(self, event_key):
        if event_key == K_d:
            self.cheat[0] = 1
        if self.cheat[0] == 1 and event_key == K_w:
            self.cheat[1] = 1
        if self.cheat[1] == 1 and event_key == K_q:
            self.cheat[2] = 1

    def __set_PC_act_key(self, event):
        if event.key == K_b:
            self.PCActKey[0] = event.key
        if event.key == K_a:
            self.PCActKey[1] = event.key
        if event.key == K_d:
            self.PCActKey[2] = event.key

    def draw_messages(self, messages):
        PC_messages = messages[0]
        for j in range(len(PC_messages[0])):
            for k in range(len(PC_messages[0][j])):
                self.screen.blit(self.font.render(PC_messages[0][j][k], True, [0, 0, 0]),
                                 (self.PCBoard[0][0] + k * 25 * 6, self.PCBoard[0][1] + j * 25))
        for j in range(len(PC_messages[1])):
            self.screen.blit(self.font.render(PC_messages[1][j], True, [0, 0, 255]),
                             (self.PCBoard[1][0], self.PCBoard[1][1] + j * 25))

        NPC_messages = messages[1]
        if self.__developer_pattern_check() is True:
            for j in range(len(NPC_messages[0])):
                for k in range(len(NPC_messages[0][j])):
                    self.screen.blit(self.font.render(NPC_messages[0][j][k], True, [0, 0, 0]),
                                     (self.NPCBoard[0][0] + k * 25 * 6, self.NPCBoard[0][1] + j * 25))
            for j in range(len(NPC_messages[1])):
                self.screen.blit(self.font.render(NPC_messages[1][j], True, [0, 0, 255]),
                                 (self.NPCBoard[1][0], self.NPCBoard[1][1] + j * 25))
        else:
            self.screen.blit(self.font.render("依次按下DWQ进入开发者模式", True, [0, 0, 255]), (27 * 25, 7 * 25))
            self.screen.blit(self.font.render("查看NPC的状态", True, [0, 0, 255]), (27 * 25, 8 * 25))

    def __music_pause(self, mouse_pos):
        if self.backgroundMusic.pause(mouse_pos) is True:
            self.__draw_music_button_change(self.backgroundMusic.isPlaying)

    def draw_music_button(self):
        self.screen.blit(self.musicImage, self.musicButtonLocation)

    def __draw_music_button_change(self, is_playing):
        self.musicImage = self.musicOn if is_playing is True else self.musicOff
        self.screen.blit(self.musicImage, self.musicButtonLocation)     # Button Down
        display.update(self.musicButtonRect)
        time.delay(100)
        self.screen.blit(self.musicBarrier, self.musicButtonLocation)
        self.screen.blit(self.musicImage, self.musicButtonLocation)     # Button Up
        display.update(self.musicButtonRect)

    def __set_dice_location(self):
        self.diceLocation = []
        if self.diceSteps[1] == 0:
            self.diceLocation.append(self.diceBoard[0])
        else:
            self.diceLocation.append(self.diceBoard[1])
            self.diceLocation.append(self.diceBoard[2])

    def draw_dice(self, final_points, random_series):
        if self.diceSteps[2] is False and \
                (self.playerTurn is PlayerTurn.PCMove or self.playerTurn is PlayerTurn.NPCMove):
            self.__set_dice_location()
            len_of_dice_location = len(self.diceLocation)
            self.clock.tick(5 * len_of_dice_location)
            for rand in random_series:
                self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))
                for j in range(len_of_dice_location):
                    self.screen.blit(self.diceImages[rand], self.diceLocation[j])
                display.update()
            self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))
            for j in range(len_of_dice_location):
                self.screen.blit(self.diceImages[final_points[j] - 1], self.diceLocation[j])
            display.update()
            time.delay(700)

    def draw_fix_dice(self, final_points):
        for j in range(len(self.diceLocation)):
            self.screen.blit(self.diceImages[final_points[j] - 1], self.diceLocation[j])

    def turn_change(self):
        if self.playerTurn is PlayerTurn.PCMove:
            self.playerTurn = PlayerTurn.PCAct
        elif self.playerTurn is PlayerTurn.NPCMove:
            self.playerTurn = PlayerTurn.NPCAct

    def turn_change_space(self):
        if self.playerTurn is PlayerTurn.start:
            self.playerTurn = PlayerTurn.PCMove
        elif self.playerTurn is PlayerTurn.PCAct:
            self.playerTurn = PlayerTurn.NPCMove
        elif self.playerTurn is PlayerTurn.NPCAct:
            time.delay(500)      # 用于产生一个较合理的回合切换效果，避免过快
            self.playerTurn = PlayerTurn.PCMove
            self.initialToPlaying = False

    def game_over_check(self, PC_money, NPC_money):
        if (PC_money <= 0 or NPC_money <= 0) and self.gameStatus is not GameStatus.end:
            self.winner = self.NPCName if PC_money < NPC_money else self.PCName
            self.gameStatus = GameStatus.over

    def draw_game_over(self):
        self.gameStatus = GameStatus.end
        self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))
        if self.winner == self.PCName:
            self.screen.blit(self.gameWin, (175, 325))
        else:
            self.screen.blit(self.gameFail, (175, 325))
        display.update()

    def __play_again(self):
        self.gameStatus = GameStatus.start
        self.playerTurn = PlayerTurn.start
        self.PCActKey = [0, 0, 0]
        self.cheat = [0, 0, 0]
        self.diceLocation = list()
        self.diceLocation.append(self.diceBoard[0])
        self.diceSteps = (0, 0, True)

    def __quit(self):
        if self.backgroundMusic.isPlaying is True:
            mixer.music.fadeout(1500)
            time.delay(1500)
        pygame.quit()
        self.gameStatus = GameStatus.quit
