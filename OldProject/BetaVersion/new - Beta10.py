import pygame
import sys
from pygame.locals import *
from random import randint
from enum import Enum


# 角色
class PC:
    def __init__(self, name):
        self.name = name
        self.position = 0   # 初始位置
        self.money = 1000   # 初始资金
        self.houseCounter = 0
        self.transportation = "无"    # 装备
        self.status = "正常"    # 状态
        self.engine = 0     # 每回合额外移动一格，需激活
        self.chance = False     # 互换资金的机会，需激活
        self.item = "无"    # 持有道具
        self.ill = 0        # 生病冷却，需激活
        self.wind = False   # 传送冷却，需激活
        self.free = False   # 免费冷却，需激活

    def move(self):
        self.engine = 0     # 千里马引擎归零

        if self.status == "监禁":
            self.status = "保释"
            return 0, 0, True
        elif self.status == "保释":
            self.status = "正常"

        # 掷骰子
        point1 = randint(1, 6)
        point2 = 0
        isWind = self.wind
        if self.transportation != "无":
            point2 = randint(1, 6)
        roll = point1 + point2

        if self.ill > 0:
            roll = roll // 2    # 感冒移动速度减半
            if roll == 0:
                roll = 1
            self.ill -= 1
            if self.ill == 0:
                self.status = "正常"
        if self.wind is True:
            roll = randint(1, 50)   # 遭遇大风，随机落地
            self.wind = not self.wind

        # 坐标变化
        if self.position + roll < 50:
            self.position += roll
        else:
            self.position = self.position + roll - 50
            self.money += 500   # 绕地图一圈奖励

        return point1, point2, isWind

    def incidents(self, Ls):
        L = Ls.lands
        incidents = Ls.incidents
        location = self.position
        # 地块买满的奖励
        if Ls.is_full(self.name) is True:
            self.money += self.houseCounter * 100
        # 1.路过敌人房子
        if L[location].owner != self.name and L[location].owner != "事件" and L[location].owner != "系统":
            self.money -= L[location].level * 100
            return L[location].level * 100
        # 特殊事件房间
        elif L[location].owner == "事件" and self.engine == 0:
            # 2.遭遇小偷
            if L[location].incident == incidents[2] and self.transportation == "无":
                self.money -= 500
            # 3.被囚禁
            elif L[location].incident == incidents[3]:
                if self.status != "保释":
                    self.status = "监禁"
            # 4.资金互换
            elif L[location].incident == incidents[4]:
                self.chance = True
            # 5.炸药
            elif L[location].incident == incidents[5]:
                self.item = "炸药"
            # 6.捡钱
            elif L[location].incident == incidents[6]:
                self.money += 1000
            # 7.生病
            elif L[location].incident == incidents[7]:
                self.status = "感冒"
                self.ill = 3
            # 8.传送
            elif L[location].incident == incidents[8]:
                self.wind = True
            # 9.免费
            elif L[location].incident == incidents[9]:
                self.free = True
        return 0

    def messages(self, Ls):
        base_messages = self.__base_messages()
        incidents_messages = self.__incidents_messages(Ls.lands, Ls.incidents)

        return base_messages, incidents_messages

    def __base_messages(self):
        # 准备工作
        messages = list()
        for i in range(3):
            messages.append(list())
        messages[0].append("昵称: %s" % self.name)
        messages[0].append("坐标: %d" % self.position)
        messages[1].append("状态: %s" % self.status)
        messages[1].append("装备: %s" % self.transportation)
        messages[2].append("物品: %s" % self.item)
        messages[2].append("资金: %d金币" % self.money)

        return messages

    def __incidents_messages(self, L, incidents):
        # 准备工作
        messages = list()
        location = self.position
        # 购买或升级地块
        if L[location].owner != "事件":
            level = L[location].level
            if L[location].owner == "系统":
                messages.append("这里是一片无主的荒地")
                messages.append("按B键花费%d金币建立城堡" % ((level + 1) * 100))
                if self.free is True:
                    messages.append("你可以免费建立城堡（仅限一次）")
            elif L[location].owner == self.name:
                messages.append("城墙上的卫兵向你举旗致敬")
                if L[location].level < 5:
                    messages.append("按B键花费%d金币升级城堡" % ((level + 1) * 100))
                    if self.free is True:
                        messages.append("你可以免费升级城堡（仅限一次）")
                else:
                    messages.append("城堡已经很豪华了！")
            else:
                messages.append("高耸的城堡阴沉地矗立于前方")
                messages.append("你到了别人的地盘，不得不支付%d金币过路费" % (level * 100))
                # 炸药使用提示
                if self.item == "炸药":
                    messages.append("按B键使用炸药炸毁城堡")
        # 事件0：到达起点
        elif L[location].incident == incidents[0]:
            messages.append("事件：你到达了起点")
        # 事件1: 到达马场
        elif L[location].incident == incidents[1]:
            messages.append("事件：你来到了马场")
            # 走路状态想买马
            if self.transportation == "无":
                messages.append("按B键花费1000金币购买一匹战马")
                messages.append("你将以双倍速度进行移动！")
            # 买了马想升级
            elif self.transportation == "战马":
                messages.append("按B键花费2000金币将战马升级为千里马")
                messages.append("骑上千里马的你将可以进行额外行动！")
                messages.append("按A键向前一格，按D键向后一格")
            # 战马升级完毕
            elif self.transportation == "千里马":
                messages.append("这里已经没有值得购买的好马了")
                messages.append("你失望地离开了马场")
        # 事件2：遭遇小偷
        elif L[location].incident == incidents[2]:
            messages.append("事件：走在大街上的你遇到了小偷")
            if self.transportation == "无":
                messages.append("你失去了500金币")
            else:
                messages.append("幸运的是，骑在马上的你没有成为小偷的目标")
        # 事件3：逮捕入狱
        elif L[location].incident == incidents[3]:
            if self.status == "正常" or self.status == "监禁":
                messages.append("事件: 你被卷入一场谋杀案，暂时无法脱身")
                messages.append("你本回合无法移动，不掷骰子")
            elif self.status == "保释":
                messages.append("事件: 你已被保释，下一回合将正常移动")
            elif self.status == "感冒":
                messages.append("事件: 你因生病而在医院修养，渡过了平静的一天")
                messages.append("你幸运地避开了谋杀案的牵连")
        # 事件4：资金互换
        elif L[location].incident == incidents[4]:
            messages.append("事件: 你碰巧获得了一个与他人互换财富的机会")
            messages.append("按B键与敌人互换资金")
        # 事件5：获得炸药
        elif L[location].incident == incidents[5]:
            messages.append("事件: 你在路边捡到了炼金术士丢弃的炸药")
            messages.append("在敌人的城堡中按B键使用炸药，仅限一次")
        # 事件6：资产暴增
        elif L[location].incident == incidents[6]:
            messages.append("事件: 你在山间偶然发现了一座金矿")
            messages.append("你得到了1000金币")
        # 事件7：生病
        elif L[location].incident == incidents[7]:
            messages.append("事件: 你发现自己得了感冒，还好病得不算严重")
            messages.append("你在三回合内的移动速度减半")
        # 事件8：遭遇大风
        elif L[location].incident == incidents[8]:
            messages.append("事件:你被一阵狂风卷起，身不由己地飞了起来")
            messages.append("你下次移动后将在随机位置出现，不掷骰子")
        # 事件9：领主结好
        elif L[location].incident == incidents[9]:
            messages.append("事件:你与本地领主建立友谊，得到了他的承诺")
            messages.append("你下次修建或升级城堡完全免费")
        # 千里马移动不能触发事件，不需展示事件提示
        if self.engine != 0 and L[location].owner == "事件" and L[location].incident != "起点":
            messages = list()
            messages.append("事件：千里马的额外移动不能激活事件")

        return messages

    def buy(self, L):
        location = self.position
        # 购买地块
        price = L[location].price(self.name)
        if price != 0:
            self.money -= price if self.free is False else 0
            if price == 100:
                self.houseCounter += 1
            self.free = not self.free if self.free is True else self.free
            L[location].change_property(self.name)
        # 买马以及升级
        elif L[location].incident == "马场":
            if self.money > 1000 and self.transportation == "无":
                self.money -= 1000
                self.transportation = "战马"
            elif self.money > 2000 and self.transportation == "战马":
                self.money -= 2000
                self.transportation = "千里马"


class NPC:
    def __init__(self, name):
        self.name = name
        self.position = 0   # 初始位置
        self.money = 1000   # 初始资金
        self.houseCounter = [0, 0, 0, 0, 0]
        self.transportation = "无"    # 装备
        self.status = "正常"    # 状态
        self.engine = 0     # 每回合额外移动一格，需激活
        self.chance = False     # 互换资金的机会，需激活
        self.item = "无"    # 持有道具
        self.ill = 0        # 生病冷却，需激活
        self.wind = False   # 传送冷却，需激活
        self.free = False   # 免费冷却，需激活
        self.cheat = [0, 0, 0]

    def move(self):
        self.engine = 0     # 千里马引擎归零

        if self.status == "监禁":
            self.status = "保释"
            return 0, 0, True
        elif self.status == "保释":
            self.status = "正常"

        # 掷骰子
        point1 = randint(1, 6)
        point2 = 0
        isWind = self.wind
        if self.transportation != "无":
            point2 = randint(1, 6)
        roll = point1 + point2

        if self.ill > 0:
            roll = roll // 2    # 感冒移动速度减半
            if roll == 0:
                roll = 1
            self.ill -= 1
            if self.ill == 0:
                self.status = "正常"
        if self.wind is True:
            roll = randint(1, 50)   # 遭遇大风，随机落地
            self.wind = not self.wind

        # 坐标变化
        if self.position + roll < 50:
            self.position += roll
        else:
            self.position = self.position + roll - 50
            self.money += 500   # 绕地图一圈奖励

        return point1, point2, isWind

    def incidents(self, Ls):
        L = Ls.lands
        incidents = Ls.incidents
        location = self.position
        # 地块买满的奖励
        if Ls.is_full(self.name) is True:
            self.money += self.houseCounter[0] * 100
        # 1.路过敌人房子
        if L[location].owner != self.name and L[location].owner != "事件" and L[location].owner != "系统":
            self.money -= L[location].level * 100
            return L[location].level * 100
        # 特殊事件房间
        elif L[location].owner == "事件" and self.engine == 0:
            # 2.遭遇小偷
            if L[location].incident == incidents[2] and self.transportation == "无":
                self.money -= 500
            # 3.被囚禁
            elif L[location].incident == incidents[3]:
                if self.status != "保释":
                    self.status = "监禁"
            # 4.资金互换
            elif L[location].incident == incidents[4]:
                self.chance = True
            # 5.炸药
            elif L[location].incident == incidents[5]:
                self.item = "炸药"
            # 6.捡钱
            elif L[location].incident == incidents[6]:
                self.money += 1000
            # 7.生病
            elif L[location].incident == incidents[7]:
                self.status = "感冒"
                self.ill = 3
            # 8.传送
            elif L[location].incident == incidents[8]:
                self.wind = True
            # 9.免费
            elif L[location].incident == incidents[9]:
                self.free = True
        return 0

    def check(self):
        if self.cheat[0] * self.cheat[1] * self.cheat[2] == 1:
            return True
        return False

    def messages(self, Ls):
        if self.check() is True:
            base_messages = self.__base_messages()
            incidents_messages = self.__incidents_messages(Ls.lands, Ls.incidents)
            return base_messages, incidents_messages
        else:
            first_line = list()
            first_line.append(u"依次按下DWQ进入开发者模式")
            second_line = list()
            second_line.append(u"查看NPC的状态")
            return first_line, second_line

    def __base_messages(self):
        # 准备工作
        messages = list()
        for i in range(3):
            messages.append(list())
        messages[0].append("昵称: %s" % self.name)
        messages[0].append("坐标: %d" % self.position)
        messages[1].append("状态: %s" % self.status)
        messages[1].append("装备: %s" % self.transportation)
        messages[2].append("物品: %s" % self.item)
        messages[2].append("资金: %d金币" % self.money)

        return messages

    def __incidents_messages(self, L, incidents):
        # 准备工作
        messages = list()
        location = self.position
        if self.engine != 0:
            return
        # 购买或升级地块
        if L[location].owner != "事件":
            level = L[location].level
            if L[location].owner == "系统":
                messages.append("这里是一片无主的荒地")
                messages.append("花费%d金币建立城堡" % ((level + 1) * 100))
                if self.free is True:
                    messages.append("你可以免费建立城堡（仅限一次）")
            elif L[location].owner == self.name:
                messages.append("城墙上的卫兵向你举旗致敬")
                if L[location].level < 5:
                    messages.append("花费%d金币升级城堡" % ((level + 1) * 100))
                    if self.free is True:
                        messages.append("你可以免费升级城堡（仅限一次）")
                else:
                    messages.append("城堡已经很豪华了！")
            else:
                messages.append("高耸的城堡阴沉地矗立于前方")
                messages.append("你到了别人的地盘，不得不支付%d金币过路费" % (level * 100))
                # 炸药使用提示
                if self.item == "炸药":
                    messages.append("使用炸药炸毁城堡")
        # 事件0：到达起点
        elif L[location].incident == incidents[0]:
            messages.append("事件：你到达了起点")
        # 事件1: 到达马场
        elif L[location].incident == incidents[1]:
            messages.append("事件：你来到了马场")
            # 走路状态想买马
            if self.transportation == "无":
                messages.append("花费1000金币购买一匹战马")
                messages.append("你将以双倍速度进行移动！")
            # 买了马想升级
            elif self.transportation == "战马":
                messages.append("花费2000金币将战马升级为千里马")
                messages.append("骑上千里马的你将可以进行额外行动！")
            # 战马升级完毕
            elif self.transportation == "千里马":
                messages.append("这里已经没有值得购买的好马了")
                messages.append("你失望地离开了马场")
        # 事件2：遭遇小偷
        elif L[location].incident == incidents[2]:
            messages.append("事件：走在大街上的你遇到了小偷")
            if self.transportation == "无":
                messages.append("你失去了500金币")
            else:
                messages.append("幸运的是，骑在马上的你没有成为小偷的目标")
        # 事件3：逮捕入狱
        elif L[location].incident == incidents[3]:
            if self.status == "正常" or self.status == "监禁":
                messages.append("事件: 你被卷入一场谋杀案，暂时无法脱身")
                messages.append("你本回合无法移动，不掷骰子")
            elif self.status == "保释":
                messages.append("事件: 你已被保释，下一回合将正常移动")
            elif self.status == "感冒":
                messages.append("事件: 你因生病而在医院修养，渡过了平静的一天")
                messages.append("你幸运地避开了谋杀案的牵连")
        # 事件4：资金互换
        elif L[location].incident == incidents[4]:
            messages.append("事件: 你碰巧获得了一个与他人互换财富的机会")
        # 事件5：获得炸药
        elif L[location].incident == incidents[5]:
            messages.append("事件: 你在路边捡到了炼金术士丢弃的炸药")
            messages.append("在敌人的城堡中使用炸药，仅限一次")
        # 事件6：资产暴增
        elif L[location].incident == incidents[6]:
            messages.append("事件: 你在山间偶然发现了一座金矿")
            messages.append("你得到了1000金币")
        # 事件7：生病
        elif L[location].incident == incidents[7]:
            messages.append("事件: 你发现自己得了感冒，还好病得不算严重")
            messages.append("你在三回合内的移动速度减半")
        # 事件8：遭遇大风
        elif L[location].incident == incidents[8]:
            messages.append("事件:你被一阵狂风卷起，身不由己地飞了起来")
            messages.append("你下次移动后将在随机位置出现，不掷骰子")
        # 事件9：领主结好
        elif L[location].incident == incidents[9]:
            messages.append("事件:你与本地领主建立友谊，得到了他的承诺")
            messages.append("你下次修建或升级城堡完全免费")
        # 千里马移动不能触发事件，不需展示事件提示
        if self.engine != 0 and L[location].owner == "事件" and L[location].incident != "起点":
            messages = list()
            messages.append("事件：千里马的额外移动不能激活事件")

        return messages

    def buy(self, Ls):
        L = Ls.lands
        location = self.position
        price = L[location].price(self.name)
        if (self.money - price) >= self.__money_left_line() or self.free is True:
            # 购买及升级地块
            if price != 0:
                level = L[location].level
                if level == 0 or self.free or (level == 1 and self.houseCounter[0] > 15) or \
                  (level == 2 and self.houseCounter[1] > 10) or (level == 3 and self.houseCounter[2] > 7)\
                   or level >= 4 or Ls.is_full(self.name) is True:
                    self.houseCounter[L[location].level] += 1
                    self.money -= price if self.free is False else 0
                    self.free = not self.free if self.free is True else self.free
                    L[location].change_property(self.name)
            # 买马以及升级
            elif L[location].incident == "马场":
                if self.money > 1600 and self.transportation == "无":
                    self.money -= 1000
                    self.transportation = "战马"
                elif self.money > 2600 and self.transportation == "战马":
                    self.money -= 2000
                    self.transportation = "千里马"

    def __money_left_line(self):
        extra_money_for_thief = 0
        if self.transportation == "无" and (self.position + 1 < 10 and self.position + 6 >= 10):
            extra_money_for_thief = 500
        if self.houseCounter[0] <= 15:
            return 500 + extra_money_for_thief
        if self.houseCounter[1] <= 10:
            return 700 + extra_money_for_thief
        if self.houseCounter[2] <= 7:
            return 800 + extra_money_for_thief
        return 900 + extra_money_for_thief


class OneLand:
    def __init__(self, position, owner="系统", incident="无"):
        self.owner = owner
        self.position = position
        self.level = 0
        self.incident = incident

    def price(self, who):
        if (who == self.owner and self.level < 5) or self.owner == "系统":
            return (self.level + 1) * 100
        return 0

    def change_property(self, who):
        self.owner = who
        self.level += 1
        self.incident = who + "的房间"

    def bang(self):
        self.owner = "系统"
        self.level = 0
        self.incident = "无"


class Landmasses:
    def __init__(self, PCName, NPCName):
        self.incidents = ["起点", "马场", "小偷", "监狱", "资金互换", "炸药", "资产暴增", "感冒", "大风", "领主"]
        self.lands = list()
        self.PCName = PCName
        self.NPCName = NPCName
        self.PCAward = False
        self.NPCAward = False

        for i in range(50):
            if (i + 1) % 5 == 1:
                self.lands.append(OneLand(i, owner="事件", incident=self.incidents[i // 5]))
            else:
                self.lands.append(OneLand(i))

    def is_full(self, name):
        if name == self.PCName and self.PCAward is True:
            return False
        if name == self.NPCName and self.NPCAward is True:
            return False
        counter = 0
        for one_land in self.lands:
            if one_land.level != 0:
                counter += 1
        if counter == 40:
            if name == self.PCName:
                self.PCAward = True
            else:
                self.NPCAward = True
            return True
        return False


class ShootDice:
    def __init__(self):
        self.random_series = list()
        self.finalPoints = list()
        self.finalPoints.append(0)

    def __set_final_points(self, points):
        self.finalPoints = []
        if points[2] is False:
            self.finalPoints.append(points[0] - 1)
            if points[1] != 0:
                self.finalPoints.append(points[1] - 1)

    def __get_random_series(self):
        self.random_series = []
        for i in range(200):
            self.random_series.append(randint(0, 5))

    def set_dice(self, points):
        self.__set_final_points(points)
        self.__get_random_series()


class MusicPlay:
    def __init__(self):
        self.music = pygame.mixer.music.load("./source/Dexter Britain - Nothing To Fear.mp3")
        self.isPlaying = True
        pygame.mixer.music.set_volume(0.618)
        pygame.mixer.music.play(-1)
    
    def pause(self, pos):
        if pos[0] > (41 * 25 + 8) and pos[0] < (41 * 25 + 94) and pos[1] > (27 * 25 + 4) and pos[1] < (27 * 25 + 68):
            pygame.mixer.music.pause() if self.isPlaying is True else pygame.mixer.music.unpause()
            self.isPlaying = not self.isPlaying
            return True
        return False
        

class PlayerTurn(Enum):
    start = 0       # 游戏开始
    PCMove = 1      # PC移动
    NPCMove = 2     # NPC移动
    PCAct = 3       # PC行动
    NPCAct = 4      # NPC行动


class GameTurn(Enum):
    start = 0       # 游戏开始界面
    waitIn = 1      # 等待进入游戏
    playing = 2     # 进入游戏
    over = 3        # 游戏结束界面
    end = 4         # 游戏结束界面绘制完毕


class GameManager:
    def __init__(self):
        pygame.init()                                                        # pygame初始化
        self.clock = pygame.time.Clock()                                     # 帧率控制
        self.font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 20)      # 游戏字体
        self.screen = pygame.display.set_mode((1200, 825))                   # 窗口初始化
        pygame.display.set_icon(pygame.image.load("./source/dog.ico").convert_alpha())
        pygame.display.set_caption("大富翁")
        
        self.playAgain = False                                               # 多次进行游戏
        self.gameTurn = GameTurn.start                                       # 游戏状态
        self.playerTurn = PlayerTurn.start                                   # 玩家行动回合
        self.keySpace = pygame.event                                         # 用于存储空格被按下的事件
        self.winner = ""                                                     # 胜利者

        self.start = pygame.image.load("./source/start.png").convert_alpha()
        self.gameOver = pygame.image.load("./source/gameover.png").convert_alpha()
        self.gameWin = pygame.image.load("./source/gamewin.png").convert_alpha()
        self.gameMap = pygame.image.load("./source/map.png").convert_alpha()

        self.musicOn = pygame.image.load("./source/MusicOn.png").convert_alpha()
        self.musicOff = pygame.image.load("./source/MusicOff.png").convert_alpha()
        self.musicImage = self.musicOn
        self.musicBarrier = pygame.image.load("./source/MusicBarrier.png").convert_alpha()
        self.musicButtonLocation = (41 * 25, 27 * 25)
        self.musicButtonRect = Rect(41 * 25, 27 * 25, 100, 75)

        self.PCName = ""
        self.PCImage = pygame.image.load("./source/PC.png").convert_alpha()
        self.PCFixImage = pygame.image.load("./source/PCBeginning.png").convert_alpha()
        self.PCBoard = [(5 * 25, 4 * 25 + 12), (5 * 25, 8 * 25)]

        self.NPCName = ""
        self.NPCImage = pygame.image.load("./source/NPC.png").convert_alpha()
        self.NPCFixImage = pygame.image.load("./source/NPCBeginning.png").convert_alpha()
        self.NPCBoard = [(27 * 25, 4 * 25 + 12), (27 * 25, 8 * 25)]

        self.diceImages = list()
        for i in range(6):
            self.diceImages.append(pygame.image.load("./source/" + str(i + 1) + ".png").convert_alpha())
        self.diceBarrier = pygame.image.load("./source/barrier.png").convert_alpha()
        self.diceBoard = [(22 * 25, 18 * 25 + 5), (19 * 25 + 12, 18 * 25 + 5), (24 * 25 + 13, 18 * 25 + 5)]
        self.diceLocation = list()
        self.diceLocation.append(self.diceBoard[0])
        self.diceSteps = (0, 0, True)

        self.cattleOfPC = list()
        self.wasteland = pygame.image.load("./source/wasteland.png").convert_alpha()
        self.cattleOfPC.append(self.wasteland)
        for i in range(5):
            self.cattleOfPC.append(pygame.image.load("./source/houseA" + str(i + 1) + ".png").convert_alpha())

        self.cattleOfNPC = list()
        self.cattleOfNPC.append(self.wasteland)
        for i in range(5):
            self.cattleOfNPC.append(pygame.image.load("./source/houseB" + str(i + 1) + ".png").convert_alpha())

    def get_character_name(self, PC, NPC):
        self.PCName = PC
        self.NPCName = NPC

    @staticmethod
    def draw_beginning():
        for i in range(150):
            gameManager.clock.tick(150)
            gameManager.screen.blit(gameManager.gameMap, (0, 0))
            gameManager.screen.blit(gameManager.PCFixImage, (6 * 25 + 13 + i * 1 - 10, 6 * 25 + 13 - 10))
            gameManager.screen.blit(gameManager.NPCFixImage, (38 * 25 + 13 - i * 1 - 10, 6 * 25 + 13 - 10))
            gameManager.screen.blit(gameManager.start, (175, 325))
            gameManager.screen.blit(gameManager.musicImage, (41 * 25, 27 * 25))
            pygame.display.update()

    def draw_land(self, all_lands):
        for land in all_lands:
            if land.owner == self.PCName:
                self.screen.blit(self.cattleOfPC[land.level], self.__location_convert(land.position))
            elif land.owner == self.NPCName:
                self.screen.blit(self.cattleOfNPC[land.level], self.__location_convert(land.position))
            else:
                self.screen.blit(self.wasteland, self.__location_convert(land.position))

    def draw_character(self, PC_pos, NPC_pos):
        # 动态位置绘制
        self.screen.blit(self.NPCImage, self.__location_convert(NPC_pos))
        self.screen.blit(self.PCImage, self.__location_convert(PC_pos))
        # 固定位置绘制
        self.screen.blit(self.PCFixImage, (19 * 25 - 21, 4 * 25))
        self.screen.blit(self.NPCFixImage, (41 * 25 - 21, 4 * 25))

    def draw_messages(self, messages):
        PC_messages = messages[0]
        for i in range(len(PC_messages[0])):
            for j in range(len(PC_messages[0][i])):
                self.screen.blit(self.font.render(PC_messages[0][i][j], True, [0, 0, 0]),
                                 (self.PCBoard[0][0] + j * 25 * 6, self.PCBoard[0][1] + i * 25))
        for i in range(len(PC_messages[1])):
            self.screen.blit(self.font.render(PC_messages[1][i], True, [0, 0, 255]),
                             (self.PCBoard[1][0], self.PCBoard[1][1] + i * 25))

        NPC_messages = messages[1]
        if len(NPC_messages[0]) != 1:
            for i in range(len(NPC_messages[0])):
                for j in range(len(NPC_messages[0][i])):
                    self.screen.blit(self.font.render(NPC_messages[0][i][j], True, [0, 0, 0]),
                                     (self.NPCBoard[0][0] + j * 25 * 6, self.NPCBoard[0][1] + i * 25))
            for i in range(len(NPC_messages[1])):
                self.screen.blit(self.font.render(NPC_messages[1][i], True, [0, 0, 255]),
                                 (self.NPCBoard[1][0], self.NPCBoard[1][1] + i * 25))
        else:
            self.screen.blit(self.font.render(NPC_messages[0][0], True, [0, 0, 255]), (27 * 25, 7 * 25))
            self.screen.blit(self.font.render(NPC_messages[1][0], True, [0, 0, 255]), (27 * 25, 8 * 25))
    
    def draw_music_button_change(self, is_playing):
        if is_playing is True:
            self.musicImage = self.musicOn
        else:
            self.musicImage = self.musicOff
        self.screen.blit(self.musicImage, self.musicButtonLocation)     # Button Down
        pygame.display.update(self.musicButtonRect)
        pygame.time.delay(100)
        self.screen.blit(self.musicBarrier, self.musicButtonLocation)
        self.screen.blit(self.musicImage, self.musicButtonLocation)     # Button Up
        pygame.display.update(self.musicButtonRect)
            
    def set_dice_image(self):
        self.diceLocation = []
        if self.diceSteps[1] == 0:
            self.diceLocation.append(self.diceBoard[0])
        else:
            self.diceLocation.append(self.diceBoard[1])
            self.diceLocation.append(self.diceBoard[2])
    
    def draw_dice(self, final_points, random_series):
        if (self.playerTurn is (PlayerTurn.PCMove or PlayerTurn.NPCMove)) and self.diceSteps[2] is False:
            len_of_dice_location = len(self.diceLocation)
            self.clock.tick(10 * len_of_dice_location)
            for rand in random_series:
                self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))
                for i in range(len_of_dice_location):
                    self.screen.blit(self.diceImages[rand], self.diceLocation[i])
                pygame.display.update()
            self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))
            for i in range(len_of_dice_location):
                self.screen.blit(self.diceImages[final_points[i]], self.diceLocation[i])
            pygame.display.update()
            pygame.time.delay(700)
    
    def draw_fix_dice(self, final_points):
        for i in range(len(self.diceLocation)):
            self.screen.blit(self.diceImages[final_points[i]], self.diceLocation[i])
    
    def turn_change(self):
        if self.playerTurn is PlayerTurn.PCMove:
            self.playerTurn = PlayerTurn.NPCMove
        elif self.playerTurn is PlayerTurn.NPCMove:
            self.playerTurn = PlayerTurn.PCAct
        elif self.playerTurn is PlayerTurn.NPCAct:
            self.playerTurn = PlayerTurn.start
            pygame.event.post(self.keySpace)  # 抛出一个空格被按下的事件，提高游戏的操作简便性
    
    def game_end_check(self, PC_money, NPC_money):
        if (PC_money <= 0 or NPC_money <= 0) and self.gameTurn is not GameTurn.end:
            self.winner = self.NPCName if PC_money < NPC_money else self.PCName
            self.gameTurn = GameTurn.over
    
    def draw_game_end(self):
        if self.gameTurn is GameTurn.over:
            self.gameTurn = GameTurn.end
            self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))
            if self.winner == self.PCName:
                self.screen.blit(self.gameWin, (175, 325))
            else:
                self.screen.blit(self.gameOver, (175, 325))
            pygame.display.update()
    
    def play_again_check(self):
        if self.playAgain is True:
            self.gameTurn = GameTurn.start
            self.playerTurn = PlayerTurn.start
            self.playAgain = not self.playAgain

    @staticmethod
    def __location_convert(position):
        position += 1
        if position <= 16:
            return (position - 1) * 75, 0
        if position <= 26:
            return 15 * 75, (position - 16) * 75
        if position <= 41:
            return (15 - (position - 26)) * 75, 10 * 75
        if position <= 50:
            return 0, (9 - (position - 42)) * 75


gameManager = GameManager()             # 初始化
backgroundMusic = MusicPlay()           # 音乐播放

# 游戏Loop
while True:
    if gameManager.gameTurn is GameTurn.start:
        hero = PC("Naruto")                                       # PC
        enemy = NPC("Sasuke")                                     # NPC
        lands = Landmasses(hero.name, enemy.name)                 # 地块初始化
        shootDice = ShootDice()                                   # 骰子管理类
        gameManager.gameTurn = GameTurn.waitIn                    # 游戏状态切换
        gameManager.get_character_name(hero.name, enemy.name)     # 获取玩家姓名
        gameManager.draw_beginning()                              # 开始界面动画绘制

    if gameManager.gameTurn is not GameTurn.start:
        if gameManager.gameTurn is GameTurn.playing:
            gameManager.clock.tick(10)                                                          # 帧数
            gameManager.screen.blit(gameManager.gameMap, (0, 0))                                # 地图绘制
            gameManager.draw_land(lands.lands)                                                  # 地块绘制
            gameManager.draw_character(hero.position, enemy.position)                           # 人物绘制
            gameManager.draw_messages((hero.messages(lands), enemy.messages(lands)))            # 信息提示绘制
            gameManager.draw_fix_dice(shootDice.finalPoints)                                         # 固定骰子在屏幕上
            gameManager.screen.blit(gameManager.musicImage, gameManager.musicButtonLocation)    # 音乐播放状态图片绘制
            gameManager.game_end_check(hero.money, enemy.money)                                 # 游戏自然结束判定
        
        for event in pygame.event.get():
            # 退出游戏
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_e):
                if backgroundMusic.isPlaying is True:
                    pygame.mixer.music.fadeout(1500)
                    pygame.time.delay(1500)
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN and gameManager.gameTurn is not GameTurn.end:
                # 开发者模式
                if enemy.check() is False and gameManager.gameTurn is GameTurn.playing:
                    if event.key == K_d:
                        enemy.cheat[0] = 1
                    if enemy.cheat[0] == 1 and event.key == K_w:
                        enemy.cheat[1] = 1
                    if enemy.cheat[1] == 1 and event.key == K_q:
                        enemy.cheat[2] = 1

                if event.key == pygame.K_SPACE:
                    # 进入游戏
                    if gameManager.gameTurn is GameTurn.waitIn:
                        gameManager.gameTurn = GameTurn.playing
                        gameManager.keySpace = event

                    # 玩家回合切换
                    elif gameManager.gameTurn is GameTurn.playing:
                        if gameManager.playerTurn is PlayerTurn.start:
                            gameManager.playerTurn = PlayerTurn.PCMove
                            gameManager.diceSteps = hero.move()
                            if gameManager.diceSteps[2] is False:
                                shootDice.set_dice(gameManager.diceSteps)
                                gameManager.set_dice_image()
                            enemy.money += hero.incidents(lands)
                        elif gameManager.playerTurn is PlayerTurn.PCAct:
                            gameManager.playerTurn = PlayerTurn.NPCAct
                            break

                # PC购买地块、交换金钱、使用炸药
                if event.key == pygame.K_b and gameManager.playerTurn is PlayerTurn.PCAct:
                    hero.buy(lands.lands)
                    if lands.lands[hero.position].incident == "资金互换" and hero.chance is True:
                        temp = hero.money
                        hero.money = enemy.money
                        enemy.money = temp
                        hero.chance = not hero.chance
                    elif lands.lands[hero.position].owner == enemy.name and hero.item == "炸药":
                        for i in range(lands.lands[hero.position].level):
                            enemy.houseCounter[i] -= 1
                        lands.lands[hero.position].bang()
                        hero.item = "无"

                # 千里马额外移动
                if hero.transportation == "千里马" and gameManager.playerTurn is PlayerTurn.PCAct:
                    if event.key == pygame.K_a:  # 后退
                        if hero.engine == 0 or hero.engine == 1:
                            hero.position -= 1 if hero.position > 0 else -49
                            hero.engine -= 1
                    elif event.key == pygame.K_d:  # 前进
                        if hero.engine == 0 or hero.engine == -1:
                            hero.position += 1 if hero.position < 49 else -49
                            hero.engine += 1

            # 多次进行游戏
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                gameManager.playAgain = True

            # 音乐播放控制的鼠标事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if backgroundMusic.pause(event.pos) is True:
                    gameManager.draw_music_button_change(backgroundMusic.isPlaying)

        if gameManager.playerTurn is PlayerTurn.NPCMove:
            gameManager.diceSteps = enemy.move()
            if gameManager.diceSteps[2] is False:
                shootDice.set_dice(gameManager.diceSteps)
                gameManager.set_dice_image()
            hero.money += enemy.incidents(lands)
        elif gameManager.playerTurn is PlayerTurn.NPCAct:
            if enemy.chance is True and hero.money > enemy.money and lands.lands[enemy.position].incident == "资金互换":
                temp = hero.money
                hero.money = enemy.money
                enemy.money = temp
                enemy.chance = not enemy.chance
            elif lands.lands[enemy.position].owner == hero.name and enemy.item == "炸药":
                lands.lands[enemy.position].bang()
                enemy.item = "无"
                hero.houseCounter -= 1
            for i in range(5):
                enemy.buy(lands)
            if enemy.transportation == "千里马" and enemy.money > 900:  # 利用千里马多买房子
                now = enemy.position
                forward = now + 1 if now < 49 else 0
                backward = now - 1 if now > 0 else 49
                if lands.lands[forward].owner == "系统" or lands.lands[forward].owner == enemy.name:
                    enemy.position = forward
                    for i in range(5):
                        enemy.buy(lands)
                    enemy.engine = 1
                if lands.lands[backward].owner == "系统" or lands.lands[forward].owner == enemy.name:
                    enemy.position = backward
                    for i in range(5):
                        enemy.buy(lands)
                    enemy.engine = -1
                enemy.position = now

    gameManager.draw_dice(shootDice.finalPoints, shootDice.random_series)             # 掷骰子动画
    gameManager.turn_change()                                                         # 玩家回合切换
    gameManager.draw_game_end()                                                       # 若游戏结束，则绘制游戏结束图片
    pygame.display.update() if gameManager.gameTurn is not GameTurn.end else False    # 若游戏未结束，正常更新画面
    gameManager.play_again_check()                                                    # 重玩游戏检查
