import pygame
from random import randint
from enum import Enum
from pygame import display
from pygame import event
from pygame import mixer
from pygame import font
from pygame import image
from pygame.locals import *
from pygame import time


class Incidents(Enum):
    start = 0                       # 起点
    horseField = 1                  # 马场
    encounterThief = 2              # 遭遇小偷
    involvedMurder = 3              # 卷入谋杀案
    changeMoney = 4                 # 资金互换
    explosive = 5                   # 炸药
    reachGoldMine = 6               # 到达金矿
    haveACold = 7                   # 感冒
    strongWind = 8                  # 遭遇大风
    friendshipWithLord = 9          # 与当地领主结好
    houseFiled = 10                 # 空地块
    house = 11                      # 房间


class PlayerTurn(Enum):
    start = 0       # 游戏开始
    PCMove = 1      # PC移动
    NPCMove = 2     # NPC移动
    PCAct = 3       # PC行动
    NPCAct = 4      # NPC行动


class GameStatus(Enum):
    start = 0       # 游戏开始界面
    waitIn = 1      # 等待进入游戏
    initial = 2     # 实例化角色对象、地块对象、掷骰子对象
    playing = 3     # 进入游戏
    over = 4        # 游戏结束界面
    end = 5         # 游戏结束界面绘制完毕
    quit = 6        # 退出游戏


class PC:
    def __init__(self, name):
        self.name = name
        self.position = 0                   # 初始位置
        self.money = 1000                   # 初始资金
        self.houseCounter = [0, 0, 0, 0, 0]
        self.transportation = "无"          # 装备
        self.status = "正常"                # 状态
        self.engine = 0                     # 每回合额外移动一格，需激活
        self.chance = False                 # 互换资金的机会，需激活
        self.item = "无"                    # 持有道具
        self.ill = 0                        # 生病冷却，需激活
        self.wind = False                   # 传送冷却，需激活
        self.free = False                   # 免费冷却，需激活

    def move(self):
        self.engine = 0                                     # 千里马引擎归零

        wind_or_in_jail = False
        point1 = randint(1, 6)
        point2 = 0
        if self.transportation != "无":
            point2 = randint(1, 6)

        if self.status == "监禁":
            self.status = "保释"
            point1, point2, wind_or_in_jail = 0, 0, True
        elif self.status == "保释":
            self.status = "正常"

        roll = point1 + point2

        if self.ill > 0:
            roll = roll // 2                                # 感冒移动速度减半
            roll = 1 if roll == 0 else roll
            self.ill -= 1
            self.status = "正常" if self.ill == 0 else self.status

        if self.wind is True:
            wind_or_in_jail = self.wind
            roll = randint(1, 50)                           # 遭遇大风，随机落地
            self.wind = not self.wind

        self.position += roll
        self.money += 0 if self.position < 50 else 500      # 绕地图一圈奖励
        self.position -= 0 if self.position < 50 else 50    # 坐标限位

        return point1, point2, wind_or_in_jail

    def swift_horse_move(self, forward):
        if self.transportation == "千里马":
            if forward is False:                           # 后退
                if self.engine == 0 or self.engine == 1:
                    self.position -= 1 if self.position > 0 else -49
                    self.engine -= 1
            elif forward is True:                          # 前进
                if self.engine == 0 or self.engine == -1:
                    self.position += 1 if self.position < 49 else -49
                    self.engine += 1

    def incidents(self, all_lands):
        land = all_lands.lands[self.position]
        # 地块买满的奖励
        if all_lands.is_full(self.name) is True:
            self.money += self.houseCounter[0] * 100
            all_lands.PCAwardMessage = 2
        # 1.路过敌人房子
        if land.owner != self.name and land.owner != "事件" and land.owner != "系统":
            self.money -= land.level * 100
            return land.level * 100
        # 特殊事件房间
        elif land.owner == "事件" and self.engine == 0:
            if land.incident is Incidents.encounterThief:
                self.money -= 500 if self.transportation == "无" else 0
            elif land.incident is Incidents.involvedMurder:
                self.status = "监禁" if (self.status != "保释" and self.status != "感冒") else self.status
            elif land.incident is Incidents.changeMoney:
                self.chance = True
            elif land.incident is Incidents.explosive:
                self.item = "炸药"
            elif land.incident is Incidents.reachGoldMine:
                self.money += 1000
            elif land.incident is Incidents.haveACold:
                self.status = "感冒"
                self.ill = 3
            elif land.incident is Incidents.strongWind:
                self.wind = True
            elif land.incident == Incidents.friendshipWithLord:
                self.free = True
        return 0

    def messages(self, all_lands):
        base_messages = self.__base_messages()
        incidents_messages = self.__incidents_messages(all_lands)
        return base_messages, incidents_messages

    def __base_messages(self):
        messages = list()
        for j in range(3):
            messages.append(list())
        messages[0].append("昵称: %s" % self.name)
        messages[0].append("坐标: %d" % self.position)
        messages[1].append("状态: %s" % self.status)
        messages[1].append("装备: %s" % self.transportation)
        messages[2].append("物品: %s" % self.item)
        messages[2].append("资金: %d金币" % self.money)

        return messages

    def __incidents_messages(self, all_lands):
        land = all_lands.lands[self.position]
        messages = list()

        # 购买或升级地块及炸药使用提示
        if land.owner != "事件":
            if land.owner == "系统":
                messages.append("这里是一片无主的荒地")
                if self.free is True:
                    messages.append("你可以按B键免费建立城堡（仅限一次）")
                    messages.append("省去%d金币" % ((land.level + 1) * 100))
                else:
                    messages.append("按B键花费%d金币建立城堡" % ((land.level + 1) * 100))
            elif land.owner == self.name:
                messages.append("城墙上的卫兵向你举旗致敬")
                if land.level < 5:
                    if self.free is True:
                        messages.append("你可以按B键免费升级城堡（仅限一次）")
                        messages.append("省去%d金币" % ((land.level + 1) * 100))
                    else:
                        messages.append("按B键花费%d金币升级城堡" % ((land.level + 1) * 100))
                else:
                    messages.append("城堡已经很豪华了！")
            else:
                messages.append("高耸的城堡阴沉地矗立于前方")
                if self.engine == 0:
                    messages.append("你到了别人的地盘，不得不支付%d金币过路费" % (land.level * 100))
                if self.item == "炸药":
                    messages.append("按B键使用炸药炸毁城堡")

        elif land.incident is Incidents.start:
            messages.append("事件：你到达了起点")

        elif land.incident is Incidents.horseField:
            messages.append("事件：你来到了马场")
            if self.transportation == "无":
                messages.append("按B键花费1000金币购买一匹战马")
                messages.append("你将以双倍速度进行移动！")
            elif self.transportation == "战马":
                messages.append("按B键花费2000金币将战马升级为千里马")
                messages.append("骑上千里马的你将可以进行额外行动！")
            elif self.transportation == "千里马":
                messages.append("这里已经没有值得购买的好马了")
                messages.append("你失望地离开了马场")

        elif land.incident is Incidents.encounterThief:
            messages.append("事件：走在大街上的你遇到了小偷")
            if self.transportation == "无":
                messages.append("你失去了500金币")
            else:
                messages.append("幸运的是，骑在马上的你没有成为小偷的目标")

        elif land.incident is Incidents.involvedMurder:
            if self.status == "正常" or self.status == "监禁":
                messages.append("事件: 你被卷入一场谋杀案，暂时无法脱身")
                messages.append("你本回合无法移动，不掷骰子")
            elif self.status == "保释":
                messages.append("事件: 你已被保释，下一回合将正常移动")
            elif self.status == "感冒":
                messages.append("事件: 你因生病在医院修养，渡过了平静的一天")
                messages.append("你幸运地避开了谋杀案的牵连")

        elif land.incident is Incidents.changeMoney:
            messages.append("事件: 你碰巧获得了一个与他人互换财富的机会")
            messages.append("按B键与敌人互换资金")

        elif land.incident is Incidents.explosive:
            messages.append("事件: 你在路边捡到了炼金术士丢弃的炸药")
            messages.append("在敌人的城堡中按B键使用炸药，仅限一次")

        elif land.incident is Incidents.reachGoldMine:
            messages.append("事件: 你在山间偶然发现了一座金矿")
            messages.append("你得到了1000金币")

        elif land.incident is Incidents.haveACold:
            messages.append("事件: 你发现自己得了感冒，还好病得不算严重")
            messages.append("你在三回合内的移动速度减半")

        elif land.incident is Incidents.strongWind:
            messages.append("事件:你被一阵狂风卷起，身不由己地飞了起来")
            messages.append("你下次移动后将在随机位置出现，不掷骰子")

        elif land.incident is Incidents.friendshipWithLord:
            messages.append("事件:你与本地领主建立友谊，得到了他的承诺")
            messages.append("你下次修建或升级城堡完全免费")

        # 千里马移动不能触发事件，不需展示事件提示
        if self.engine != 0 and land.owner == "事件" and land.incident is not Incidents.start:
            messages = list()
            messages.append("事件：千里马的额外移动不能激活事件")

        # 地块被买满的奖励提示
        if all_lands.PCAwardMessage == 1 and all_lands.PCAward is True:
            messages.append("<地块被买满，奖励将在本回合或下一回合到账>")

        return messages

    def buy(self, land):
        self.__buy_land(land)
        self.__buy_horse() if land.incident is Incidents.horseField else False

    def __buy_land(self, land):
        price = land.price(self.name)
        if price != 0:
            self.money -= price if self.free is False else 0
            self.free = not self.free if self.free is True else self.free
            land.change_property(self.name)
            self.houseCounter[land.level - 1] += 1

    def __buy_horse(self):
        if self.money > 1000 and self.transportation == "无":
            self.money -= 1000
            self.transportation = "战马"
        elif self.money > 2000 and self.transportation == "战马":
            self.money -= 2000
            self.transportation = "千里马"


class NPC:
    def __init__(self, name):
        self.name = name
        self.position = 0               # 初始位置
        self.money = 1000               # 初始资金
        self.houseCounter = [0, 0, 0, 0, 0]
        self.transportation = "无"      # 装备
        self.status = "正常"            # 状态
        self.engine = 0                 # 每回合额外移动一格，需激活
        self.chance = False             # 互换资金的机会，需激活
        self.item = "无"                # 持有道具
        self.ill = 0                    # 生病冷却，需激活
        self.wind = False               # 传送冷却，需激活
        self.free = False               # 免费冷却，需激活

    def move(self):
        self.engine = 0                                     # 千里马引擎归零

        wind_or_in_jail = False
        point1 = randint(1, 6)
        point2 = 0
        if self.transportation != "无":
            point2 = randint(1, 6)

        if self.status == "监禁":
            self.status = "保释"
            point1, point2, wind_or_in_jail = 0, 0, True
        elif self.status == "保释":
            self.status = "正常"

        roll = point1 + point2

        if self.ill > 0:
            roll = roll // 2                                # 感冒移动速度减半
            roll = 1 if roll == 0 else roll
            self.ill -= 1
            self.status = "正常" if self.ill == 0 else self.status

        if self.wind is True:
            wind_or_in_jail = self.wind
            roll = randint(1, 50)                           # 遭遇大风，随机落地
            self.wind = not self.wind

        # 坐标变化
        self.position += roll
        self.money += 0 if self.position < 50 else 500      # 绕地图一圈奖励
        self.position -= 0 if self.position < 50 else 50    # 坐标限位

        return point1, point2, wind_or_in_jail
    
    def swift_horse_move(self, all_lands, land_is_full):
        if self.money > 900 and self.transportation == "千里马":
            forward = self.position + 1 if self.position < 49 else 0
            backward = self.position - 1 if self.position > 0 else 49
            for j in range(5):
                self.buy(all_lands[forward], land_is_full)
            for j in range(5):
                self.buy(all_lands[backward], land_is_full)

    def incidents(self, all_lands):
        land = all_lands.lands[self.position]
        # 地块买满的奖励
        if all_lands.is_full(self.name) is True:
            self.money += self.houseCounter[0] * 100
            all_lands.NPCAwardMessage = 2
        # 1.路过敌人房子
        if land.owner != self.name and land.owner != "事件" and land.owner != "系统":
            self.money -= land.level * 100
            return land.level * 100
        # 特殊事件房间
        elif land.owner == "事件" and self.engine == 0:
            if land.incident is Incidents.encounterThief:
                self.money -= 500 if self.transportation == "无" else 0
            elif land.incident is Incidents.involvedMurder:
                self.status = "监禁" if (self.status != "保释" and self.status != "感冒") else self.status
            elif land.incident is Incidents.changeMoney:
                self.chance = True
            elif land.incident is Incidents.explosive:
                self.item = "炸药"
            elif land.incident is Incidents.reachGoldMine:
                self.money += 1000
            elif land.incident is Incidents.haveACold:
                self.status = "感冒"
                self.ill = 3
            elif land.incident is Incidents.strongWind:
                self.wind = True
            elif land.incident == Incidents.friendshipWithLord:
                self.free = True
        return 0

    def messages(self, all_lands):
        base_messages = self.__base_messages()
        incidents_messages = self.__incidents_messages(all_lands)
        return base_messages, incidents_messages

    def __base_messages(self):
        messages = list()
        for j in range(3):
            messages.append(list())
        messages[0].append("昵称: %s" % self.name)
        messages[0].append("坐标: %d" % self.position)
        messages[1].append("状态: %s" % self.status)
        messages[1].append("装备: %s" % self.transportation)
        messages[2].append("物品: %s" % self.item)
        messages[2].append("资金: %d金币" % self.money)

        return messages

    def __incidents_messages(self, all_lands):
        land = all_lands.lands[self.position]
        messages = list()

        # 购买或升级地块及炸药使用提示
        if land.owner != "事件":
            if land.owner == "系统":
                messages.append("这里是一片无主的荒地")
                if self.free is True:
                    messages.append("你可以免费建立城堡（仅限一次）")
                    messages.append("省去%d金币" % ((land.level + 1) * 100))
                else:
                    messages.append("你可以花费%d金币建立城堡" % ((land.level + 1) * 100))
            elif land.owner == self.name:
                messages.append("城墙上的卫兵向你举旗致敬")
                if land.level < 5:
                    if self.free is True:
                        messages.append("你可以免费升级城堡（仅限一次）")
                        messages.append("省去%d金币" % ((land.level + 1) * 100))
                    else:
                        messages.append("你可以花费%d金币升级城堡" % ((land.level + 1) * 100))
                else:
                    messages.append("城堡已经很豪华了！")
            else:
                messages.append("高耸的城堡阴沉地矗立于前方")
                if self.engine == 0:
                    messages.append("你到了别人的地盘，不得不支付%d金币过路费" % (land.level * 100))
                if self.item == "炸药":
                    messages.append("使用炸药炸毁城堡")

        elif land.incident is Incidents.start:
            messages.append("事件：你到达了起点")

        elif land.incident is Incidents.horseField:
            messages.append("事件：你来到了马场")
            if self.transportation == "无":
                messages.append("花费1000金币购买一匹战马")
                messages.append("你将以双倍速度进行移动！")
            elif self.transportation == "战马":
                messages.append("花费2000金币将战马升级为千里马")
                messages.append("骑上千里马的你将可以进行额外行动！")
            elif self.transportation == "千里马":
                messages.append("这里已经没有值得购买的好马了")
                messages.append("你失望地离开了马场")

        elif land.incident is Incidents.encounterThief:
            messages.append("事件：走在大街上的你遇到了小偷")
            if self.transportation == "无":
                messages.append("你失去了500金币")
            else:
                messages.append("幸运的是，骑在马上的你没有成为小偷的目标")

        elif land.incident is Incidents.involvedMurder:
            if self.status == "正常" or self.status == "监禁":
                messages.append("事件: 你被卷入一场谋杀案，暂时无法脱身")
                messages.append("你本回合无法移动，不掷骰子")
            elif self.status == "保释":
                messages.append("事件: 你已被保释，下一回合将正常移动")
            elif self.status == "感冒":
                messages.append("事件: 你因生病在医院修养，渡过了平静的一天")
                messages.append("你幸运地避开了谋杀案的牵连")

        elif land.incident is Incidents.changeMoney:
            messages.append("事件: 你碰巧获得了一个与他人互换财富的机会")

        elif land.incident is Incidents.explosive:
            messages.append("事件: 你在路边捡到了炼金术士丢弃的炸药")
            messages.append("在敌人的城堡中使用炸药，仅限一次")

        elif land.incident is Incidents.reachGoldMine:
            messages.append("事件: 你在山间偶然发现了一座金矿")
            messages.append("你得到了1000金币")

        elif land.incident is Incidents.haveACold:
            messages.append("事件: 你发现自己得了感冒，还好病得不算严重")
            messages.append("你在三回合内的移动速度减半")

        elif land.incident is Incidents.strongWind:
            messages.append("事件:你被一阵狂风卷起，身不由己地飞了起来")
            messages.append("你下次移动后将在随机位置出现，不掷骰子")

        elif land.incident is Incidents.friendshipWithLord:
            messages.append("事件:你与本地领主建立友谊，得到了他的承诺")
            messages.append("你下次修建或升级城堡完全免费")

        # 千里马移动不能触发事件，不需展示事件提示
        if self.engine != 0 and land.owner == "事件" and land.incident is not Incidents.start:
            messages = list()
            messages.append("事件：千里马的额外移动不能激活事件")

        # 地块被买满的奖励提示
        if all_lands.NPCAwardMessage == 1 and all_lands.NPCAward is True:
            messages.append("<地块被买满，奖励将在本回合或下一回合到账>")

        return messages

    def buy(self, land, land_is_full):
        price = land.price(self.name)
        if (self.money - price) >= self.__money_left_line() or self.free is True:
            self.__buy_land(land, land_is_full) if price != 0 else False
            self.__buy_horse() if land.incident is Incidents.horseField else False

    def __buy_land(self, land, land_is_full):
        price = land.price(self.name)
        level = land.level
        if level == 0 or self.free or \
           (level == 1 and self.houseCounter[0] > 13) or \
           (level == 2 and self.houseCounter[1] > 10) or \
           (level == 3 and self.houseCounter[2] > 7) \
           or level >= 4 or land_is_full is True or self.money > 2500:
            self.money -= price if self.free is False else 0
            self.free = not self.free if self.free is True else self.free
            land.change_property(self.name)
            self.houseCounter[land.level - 1] += 1

    def __buy_horse(self):
        if self.money >= 1500 and self.transportation == "无":
            self.money -= 1000
            self.transportation = "战马"
        elif self.money > 2600 and self.transportation == "战马":
            self.money -= 2000
            self.transportation = "千里马"

    def __money_left_line(self):
        extra_money_for_thief = 0
        if self.transportation == "无" and (self.position + 1 <= 10 and self.position + 6 >= 10):
            extra_money_for_thief = 500
        if self.houseCounter[0] <= 15:
            return 500 + extra_money_for_thief
        if self.houseCounter[1] <= 10:
            return 700 + extra_money_for_thief
        if self.houseCounter[2] <= 7:
            return 800 + extra_money_for_thief
        return 900 + extra_money_for_thief


class OneLand:
    def __init__(self, position, owner="系统", incident=Incidents.houseFiled):
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
        self.incident = Incidents.house

    def bang(self):
        self.owner = "系统"
        self.level = 0
        self.incident = Incidents.houseFiled


class Landmasses:
    def __init__(self, PCName, NPCName):
        self.lands = list()
        self.PCName = PCName
        self.NPCName = NPCName
        self.PCAward = False
        self.NPCAward = False
        self.PCAwardMessage = 0
        self.NPCAwardMessage = 0

        for j in range(50):
            if (j + 1) % 5 == 1:
                self.lands.append(OneLand(j, owner="事件", incident=Incidents(j // 5)))
            else:
                self.lands.append(OneLand(j))

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
        self.randomSeries = list()
        self.finalPoints = list()
        self.finalPoints.append(1)

    def __set_final_points(self, points):
        self.finalPoints = []
        self.finalPoints.append(points[0])
        if points[1] != 0:
            self.finalPoints.append(points[1])

    def __get_random_series(self):
        self.randomSeries = []
        for j in range(200):
            self.randomSeries.append(randint(0, 5))

    def set_dice(self, points):
        if points[2] is False:
            self.__set_final_points(points)
            self.__get_random_series()


class MusicPlay:
    def __init__(self, music):
        self.music = music
        self.isPlaying = True
        mixer.music.set_volume(0.618)
        mixer.music.play(-1)
    
    def pause(self, pos):
        if pos[0] > (41 * 25 + 8) and pos[0] < (41 * 25 + 94) and pos[1] > (27 * 25 + 4) and pos[1] < (27 * 25 + 68):
            mixer.music.pause() if self.isPlaying is True else mixer.music.unpause()
            self.isPlaying = not self.isPlaying
            return True
        return False


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


if __name__ == "__main__":
    gameManager = GameManager()
    hero, enemy, landmasses, shootDice = None, None, None, None
    while gameManager.gameStatus is not GameStatus.quit:
        gameManager.event_deal()

        if gameManager.gameStatus is GameStatus.start:
            gameManager.draw_beginning()
            gameManager.gameStatus = GameStatus.waitIn

        if gameManager.gameStatus is GameStatus.initial:
            del hero
            hero = PC("Naruto")
            del enemy
            enemy = NPC("Sasuke")
            del landmasses
            landmasses = Landmasses(hero.name, enemy.name)
            del shootDice
            shootDice = ShootDice()
            gameManager.get_character_name(hero.name, enemy.name)
            gameManager.gameStatus = GameStatus.playing
            gameManager.initialToPlaying = True

        if gameManager.gameStatus is GameStatus.playing:
            gameManager.clock.tick(10)
            gameManager.draw_map()
            gameManager.draw_lands(landmasses.lands)
            gameManager.draw_character(hero.position, enemy.position)
            gameManager.draw_active_status()
            gameManager.draw_messages((hero.messages(landmasses), enemy.messages(landmasses)))
            gameManager.draw_fix_dice(shootDice.finalPoints)
            gameManager.draw_music_button()
            gameManager.game_over_check(hero.money, enemy.money)
            gameManager.draw_tips()

            if gameManager.playerTurn is PlayerTurn.PCMove:
                gameManager.diceSteps = hero.move()
                enemy.money += hero.incidents(landmasses)
                shootDice.set_dice(gameManager.diceSteps)

            elif gameManager.playerTurn is PlayerTurn.PCAct:
                # PC购买地块、交换金钱、使用炸药
                if gameManager.PCActKey[0] is K_b:
                    hero.buy(landmasses.lands[hero.position])
                    if landmasses.lands[hero.position].incident is Incidents.changeMoney and hero.chance is True:
                        hero.money, enemy.money = enemy.money, hero.money
                        hero.chance = not hero.chance
                    elif landmasses.lands[hero.position].owner == enemy.name and hero.item == "炸药":
                        for i in range(landmasses.lands[hero.position].level):
                            enemy.houseCounter[i] -= 1
                        landmasses.lands[hero.position].bang()
                        hero.item = "无"
                    gameManager.PCActKey[0] = gameManager.spaceKeyDown.key                          # 每次响应过按键之后重置

                # 千里马额外移动
                if gameManager.PCActKey[1] is K_a:
                    hero.swift_horse_move(False)
                    gameManager.PCActKey[1] = gameManager.spaceKeyDown.key                          # 每次响应过按键之后重置
                if gameManager.PCActKey[2] is K_d:
                    hero.swift_horse_move(True)
                    gameManager.PCActKey[2] = gameManager.spaceKeyDown.key                          # 每次响应过按键之后重置

            elif gameManager.playerTurn is PlayerTurn.NPCMove:
                gameManager.diceSteps = enemy.move()
                hero.money += enemy.incidents(landmasses)
                shootDice.set_dice(gameManager.diceSteps)

            elif gameManager.playerTurn is PlayerTurn.NPCAct:
                if landmasses.lands[enemy.position].incident is Incidents.changeMoney and hero.money > enemy.money:
                    hero.money, enemy.money = enemy.money, hero.money
                    enemy.chance = not enemy.chance
                elif enemy.item == "炸药":
                    now = enemy.position
                    if landmasses.lands[now].owner == hero.name:
                        enemy.item = "无"
                        for i in range(landmasses.lands[now].level):
                            hero.houseCounter[i] -= 1
                        landmasses.lands[now].bang()
                        for i in range(5):
                            enemy.buy(landmasses.lands[now], landmasses.is_full(enemy.name))
                    elif enemy.transportation == "千里马":
                        forward = now + 1 if now < 49 else 0
                        backward = now - 1 if now > 0 else 49
                        if landmasses.lands[forward].owner == hero.name:
                            enemy.item = "无"
                            for i in range(landmasses.lands[forward].level):
                                hero.houseCounter[i] -= 1
                            landmasses.lands[forward].bang()
                            for i in range(5):
                                enemy.buy(landmasses.lands[forward], landmasses.is_full(enemy.name))
                        elif landmasses.lands[backward].owner == hero.name:
                            enemy.item = "无"
                            for i in range(landmasses.lands[backward].level):
                                hero.houseCounter[i] -= 1
                            landmasses.lands[backward].bang()
                            for i in range(5):
                                enemy.buy(landmasses.lands[backward], landmasses.is_full(enemy.name))
                for i in range(5):
                    enemy.buy(landmasses.lands[enemy.position], landmasses.is_full(enemy.name))
                enemy.swift_horse_move(landmasses.lands, landmasses.is_full(enemy.name))

                gameManager.post_space_key_down()               # 抛出一个空格被按下的事件，NPC所需

            gameManager.draw_dice(shootDice.finalPoints, shootDice.randomSeries)
            gameManager.turn_change()
            gameManager.image_update()

        if gameManager.gameStatus is GameStatus.over:
            gameManager.draw_game_over()
