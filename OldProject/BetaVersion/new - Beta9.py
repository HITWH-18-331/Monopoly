import pygame
import sys
from pygame.locals import *
from random import randint
from enum import Enum


# 角色
class PC:
    def __init__(self, name, image):
        self.name = name
        self.position = 0   # 初始位置
        self.money = 1000   # 初始资金
        self.image = image   # 外观图片
        self.houseCounter = 0
        self.transportation = "无"    # 装备
        self.status = "正常"    # 状态
        self.engine = 0     # 每回合额外移动一格，需激活
        self.chance = False     # 互换资金的机会，需激活
        self.item = "无"    # 持有道具
        self.ill = 0        # 生病冷却，需激活
        self.wind = False   # 传送冷却，需激活
        self.free = False   # 免费冷却，需激活
        self.messageBoardLocation = [(5 * 25, 4 * 25 + 12), (5 * 25, 8 * 25)]

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

    def display(self, Ls):
        self.__display_base()
        self.__display_incidents(Ls.lands, Ls.incidents)

    def __display_base(self):
        # 准备工作
        messages = list()
        for i in range(3):
            messages.append(list())
        messages[0].append(font.render("昵称: %s" % self.name, True, [0, 0, 0]))
        messages[0].append(font.render("坐标: %d" % self.position, True, [0, 0, 0]))
        messages[1].append(font.render("状态: %s" % self.status, True, [0, 0, 0]))
        messages[1].append(font.render("装备: %s" % self.transportation, True, [0, 0, 0]))
        messages[2].append(font.render("物品: %s" % self.item, True, [0, 0, 0]))
        messages[2].append(font.render("资金: %d金币" % self.money, True, [0, 0, 0]))
        # 信息输出
        for i in range(len(messages)):
            for j in range(len(messages[i])):
                screen.blit(messages[i][j],
                            (self.messageBoardLocation[0][0] + j * 25 * 6,
                             self.messageBoardLocation[0][1] + i * 25))

    def __display_incidents(self, L, incidents):
        # 准备工作
        messages = list()
        location = self.position
        # 购买或升级地块
        if L[location].owner != "事件":
            level = L[location].level
            if L[location].owner == "系统":
                messages.append(font.render("这里是一片无主的荒地", True, [0, 0, 255]))
                messages.append(font.render("按B键花费%d金币建立城堡" % ((level + 1) * 100), True, [0, 0, 255]))
                if self.free is True:
                    messages.append(font.render("你可以免费建立城堡（仅限一次）", True, [0, 0, 255]))
            elif L[location].owner == self.name:
                messages.append(font.render("城墙上的卫兵向你举旗致敬", True, [0, 0, 255]))
                if L[location].level < 5:
                    messages.append(font.render("按B键花费%d金币升级城堡" % ((level + 1) * 100), True, [0, 0, 255]))
                    if self.free is True:
                        messages.append(font.render("你可以免费升级城堡（仅限一次）", True, [0, 0, 255]))
                else:
                    messages.append(font.render("城堡已经很豪华了！", True, [0, 0, 255]))
            else:
                messages.append(font.render("高耸的城堡阴沉地矗立于前方", True, [0, 0, 255]))
                messages.append(font.render("你到了别人的地盘，不得不支付%d金币过路费" % (level * 100), True, [0, 0, 255]))
                # 炸药使用提示
                if self.item == "炸药":
                    messages.append(font.render("按B键使用炸药炸毁城堡", True, [0, 0, 255]))
        # 事件0：到达起点
        elif L[location].incident == incidents[0]:
            messages.append(font.render("事件：你到达了起点", True, [0, 0, 255]))
        # 事件1: 到达马场
        elif L[location].incident == incidents[1]:
            messages.append(font.render("事件：你来到了马场", True, [0, 0, 255]))
            # 走路状态想买马
            if self.transportation == "无":
                messages.append(font.render("按B键花费1000金币购买一匹战马", True, [0, 0, 255]))
                messages.append(font.render("你将以双倍速度进行移动！", True, [0, 0, 255]))
            # 买了马想升级
            elif self.transportation == "战马":
                messages.append(font.render("按B键花费2000金币将战马升级为千里马", True, [0, 0, 255]))
                messages.append(font.render("骑上千里马的你将可以进行额外行动！", True, [0, 0, 255]))
                messages.append(font.render("按A键向前一格，按D键向后一格", True, [0, 0, 255]))
            # 战马升级完毕
            elif self.transportation == "千里马":
                messages.append(font.render("这里已经没有值得购买的好马了", True, [0, 0, 255]))
                messages.append(font.render("你失望地离开了马场", True, [0, 0, 255]))
        # 事件2：遭遇小偷
        elif L[location].incident == incidents[2]:
            messages.append(font.render("事件：走在大街上的你遇到了小偷", True, [0, 0, 255]))
            if self.transportation == "无":
                messages.append(font.render("你失去了500金币", True, [0, 0, 255]))
            else:
                messages.append(font.render("幸运的是，骑在马上的你没有成为小偷的目标", True, [0, 0, 255]))
        # 事件3：逮捕入狱
        elif L[location].incident == incidents[3]:
            if self.status == "正常" or self.status == "监禁":
                messages.append(font.render("事件: 你被卷入一场谋杀案，暂时无法脱身", True, [0, 0, 255]))
                messages.append(font.render("你本回合无法移动，不掷骰子", True, [0, 0, 255]))
            elif self.status == "保释":
                messages.append(font.render("事件: 你已被保释，下一回合将正常移动", True, [0, 0, 255]))
            elif self.status == "感冒":
                messages.append(font.render("事件: 你因生病而在医院修养，渡过了平静的一天", True, [0, 0, 255]))
                messages.append(font.render("你幸运地避开了谋杀案的牵连", True, [0, 0, 255]))
        # 事件4：资金互换
        elif L[location].incident == incidents[4]:
            messages.append(font.render("事件: 你碰巧获得了一个与他人互换财富的机会", True, [0, 0, 255]))
            messages.append(font.render("按B键与敌人互换资金", True, [0, 0, 255]))
        # 事件5：获得炸药
        elif L[location].incident == incidents[5]:
            messages.append(font.render("事件: 你在路边捡到了炼金术士丢弃的炸药", True, [0, 0, 255]))
            messages.append(font.render("在敌人的城堡中按B键使用炸药，仅限一次", True, [0, 0, 255]))
        # 事件6：资产暴增
        elif L[location].incident == incidents[6]:
            messages.append(font.render("事件: 你在山间偶然发现了一座金矿", True, [0, 0, 255]))
            messages.append(font.render("你得到了1000金币", True, [0, 0, 255]))
        # 事件7：生病
        elif L[location].incident == incidents[7]:
            messages.append(font.render("事件: 你发现自己得了感冒，还好病得不算严重", True, [0, 0, 255]))
            messages.append(font.render("你在三回合内的移动速度减半", True, [0, 0, 255]))
        # 事件8：遭遇大风
        elif L[location].incident == incidents[8]:
            messages.append(font.render("事件:你被一阵狂风卷起，身不由己地飞了起来", True, [0, 0, 255]))
            messages.append(font.render("你下次移动后将在随机位置出现，不掷骰子", True, [0, 0, 255]))
        # 事件9：领主结好
        elif L[location].incident == incidents[9]:
            messages.append(font.render("事件:你与本地领主建立友谊，得到了他的承诺", True, [0, 0, 255]))
            messages.append(font.render("你下次修建或升级城堡完全免费", True, [0, 0, 255]))
        # 千里马移动不能触发事件，不需展示事件提示
        if self.engine != 0 and L[location].owner == "事件" and L[location].incident != "起点":
            messages = list()
            messages.append(font.render("事件：千里马的额外移动不能激活事件", True, [0, 0, 255]))
        # 信息输出
        for i in range(len(messages)):
            screen.blit(messages[i], (self.messageBoardLocation[1][0], self.messageBoardLocation[1][1] + i * 25))

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
    def __init__(self, name, image):
        self.name = name
        self.position = 0   # 初始位置
        self.money = 1000   # 初始资金
        self.image = image   # 外观图片
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
        self.messageBoardLocation = [(27 * 25, 4 * 25 + 12), (27 * 25, 8 * 25)]

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

    def display(self, Ls):
        if self.check() is True:
            self.__display_base()
            self.__display_incidents(Ls.lands, Ls.incidents)
        else:
            screen.blit(font.render("依次按下DWQ进入开发者模式", True, [0, 0, 255]), (27 * 25, 7 * 25))
            screen.blit(font.render("查看NPC的状态", True, [0, 0, 255]), (27 * 25, 8 * 25))

    def __display_base(self):
        # 准备工作
        messages = list()
        for i in range(3):
            messages.append(list())
        messages[0].append(font.render("昵称: %s" % self.name, True, [0, 0, 0]))
        messages[0].append(font.render("坐标: %d" % self.position, True, [0, 0, 0]))
        messages[1].append(font.render("状态: %s" % self.status, True, [0, 0, 0]))
        messages[1].append(font.render("装备: %s" % self.transportation, True, [0, 0, 0]))
        messages[2].append(font.render("物品: %s" % self.item, True, [0, 0, 0]))
        messages[2].append(font.render("资金: %d金币" % self.money, True, [0, 0, 0]))
        # 信息输出
        for i in range(len(messages)):
            for j in range(len(messages[i])):
                screen.blit(messages[i][j],
                            (self.messageBoardLocation[0][0] + j * 25 * 6,
                             self.messageBoardLocation[0][1] + i * 25))

    def __display_incidents(self, L, incidents):
        # 准备工作
        messages = list()
        location = self.position
        if self.engine != 0:
            return
        # 购买或升级地块
        if L[location].owner != "事件":
            level = L[location].level
            if L[location].owner == "系统":
                messages.append(font.render("这里是一片无主的荒地", True, [0, 0, 255]))
                messages.append(font.render("花费%d金币建立城堡" % ((level + 1) * 100), True, [0, 0, 255]))
                if self.free is True:
                    messages.append(font.render("你可以免费建立城堡（仅限一次）", True, [0, 0, 255]))
            elif L[location].owner == self.name:
                messages.append(font.render("城墙上的卫兵向你举旗致敬", True, [0, 0, 255]))
                if L[location].level < 5:
                    messages.append(font.render("花费%d金币升级城堡" % ((level + 1) * 100), True, [0, 0, 255]))
                    if self.free is True:
                        messages.append(font.render("你可以免费升级城堡（仅限一次）", True, [0, 0, 255]))
                else:
                    messages.append(font.render("城堡已经很豪华了！", True, [0, 0, 255]))
            else:
                messages.append(font.render("高耸的城堡阴沉地矗立于前方", True, [0, 0, 255]))
                messages.append(font.render("你到了别人的地盘，不得不支付%d金币过路费" % (level * 100), True, [0, 0, 255]))
                # 炸药使用提示
                if self.item == "炸药":
                    messages.append(font.render("使用炸药炸毁城堡", True, [0, 0, 255]))
        # 事件0：到达起点
        elif L[location].incident == incidents[0]:
            messages.append(font.render("事件：你到达了起点", True, [0, 0, 255]))
        # 事件1: 到达马场
        elif L[location].incident == incidents[1]:
            messages.append(font.render("事件：你来到了马场", True, [0, 0, 255]))
            # 走路状态想买马
            if self.transportation == "无":
                messages.append(font.render("花费1000金币购买一匹战马", True, [0, 0, 255]))
                messages.append(font.render("你将以双倍速度进行移动！", True, [0, 0, 255]))
            # 买了马想升级
            elif self.transportation == "战马":
                messages.append(font.render("花费2000金币将战马升级为千里马", True, [0, 0, 255]))
                messages.append(font.render("骑上千里马的你将可以进行额外行动！", True, [0, 0, 255]))
            # 战马升级完毕
            elif self.transportation == "千里马":
                messages.append(font.render("这里已经没有值得购买的好马了", True, [0, 0, 255]))
                messages.append(font.render("你失望地离开了马场", True, [0, 0, 255]))
        # 事件2：遭遇小偷
        elif L[location].incident == incidents[2]:
            messages.append(font.render("事件：走在大街上的你遇到了小偷", True, [0, 0, 255]))
            if self.transportation == "无":
                messages.append(font.render("你失去了500金币", True, [0, 0, 255]))
            else:
                messages.append(font.render("幸运的是，骑在马上的你没有成为小偷的目标", True, [0, 0, 255]))
        # 事件3：逮捕入狱
        elif L[location].incident == incidents[3]:
            if self.status == "正常" or self.status == "监禁":
                messages.append(font.render("事件: 你被卷入一场谋杀案，暂时无法脱身", True, [0, 0, 255]))
                messages.append(font.render("你本回合无法移动，不掷骰子", True, [0, 0, 255]))
            elif self.status == "保释":
                messages.append(font.render("事件: 你已被保释，下一回合将正常移动", True, [0, 0, 255]))
            elif self.status == "感冒":
                messages.append(font.render("事件: 你因生病而在医院修养，渡过了平静的一天", True, [0, 0, 255]))
                messages.append(font.render("你幸运地避开了谋杀案的牵连", True, [0, 0, 255]))
        # 事件4：资金互换
        elif L[location].incident == incidents[4]:
            messages.append(font.render("事件: 你碰巧获得了一个与他人互换财富的机会", True, [0, 0, 255]))
        # 事件5：获得炸药
        elif L[location].incident == incidents[5]:
            messages.append(font.render("事件: 你在路边捡到了炼金术士丢弃的炸药", True, [0, 0, 255]))
            messages.append(font.render("在敌人的城堡中使用炸药，仅限一次", True, [0, 0, 255]))
        # 事件6：资产暴增
        elif L[location].incident == incidents[6]:
            messages.append(font.render("事件: 你在山间偶然发现了一座金矿", True, [0, 0, 255]))
            messages.append(font.render("你得到了1000金币", True, [0, 0, 255]))
        # 事件7：生病
        elif L[location].incident == incidents[7]:
            messages.append(font.render("事件: 你发现自己得了感冒，还好病得不算严重", True, [0, 0, 255]))
            messages.append(font.render("你在三回合内的移动速度减半", True, [0, 0, 255]))
        # 事件8：遭遇大风
        elif L[location].incident == incidents[8]:
            messages.append(font.render("事件:你被一阵狂风卷起，身不由己地飞了起来", True, [0, 0, 255]))
            messages.append(font.render("你下次移动后将在随机位置出现，不掷骰子", True, [0, 0, 255]))
        # 事件9：领主结好
        elif L[location].incident == incidents[9]:
            messages.append(font.render("事件:你与本地领主建立友谊，得到了他的承诺", True, [0, 0, 255]))
            messages.append(font.render("你下次修建或升级城堡完全免费", True, [0, 0, 255]))
        # 千里马移动不能触发事件，不需展示事件提示
        if self.engine != 0 and L[location].owner == "事件" and L[location].incident != "起点":
            messages = list()
            messages.append(font.render("事件：千里马的额外移动不能激活事件", True, [0, 0, 255]))
        # 信息输出
        for i in range(len(messages)):
            screen.blit(messages[i], (self.messageBoardLocation[1][0], self.messageBoardLocation[1][1] + i * 25))

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
        self.cattleOfPC = list()
        self.cattleOfNPC = list()
        self.wasteland = pygame.image.load("./source/wasteland.png").convert_alpha()
        self.incidents = ["起点", "马场", "小偷", "监狱", "资金互换", "炸药", "资产暴增", "感冒", "大风", "领主"]
        self.lands = list()
        self.PCName = PCName
        self.NPCName = NPCName
        self.PCAward = False
        self.NPCAward = False

        self.cattleOfPC.append(self.wasteland)
        for i in range(5):
            self.cattleOfPC.append(pygame.image.load("./source/houseA" + str(i + 1) + ".png").convert_alpha())

        self.cattleOfNPC.append(self.wasteland)
        for i in range(5):
            self.cattleOfNPC.append(pygame.image.load("./source/houseB" + str(i + 1) + ".png").convert_alpha())

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
        self.image = list()
        for i in range(6):
            self.image.append(pygame.image.load("./source/" + str(i + 1) + ".png").convert_alpha())
        self.barrier = pygame.image.load("./source/barrier.png").convert_alpha()
        self.image_location = [(22 * 25, 18 * 25 + 5), (19 * 25 + 12, 18 * 25 + 5), (24 * 25 + 13, 18 * 25 + 5)]
        self.diceLocation = list()
        self.diceLocation.append(self.image_location[0])
        self.steps = (0, 0, True)
        self.random_series = list()
        self.final_image = list()
        self.final_image.append(self.image[0])

    def __prepare_image(self, points):
        self.final_image = []
        if points[2] is False:
            self.final_image.append(self.image[points[0] - 1])
            if points[1] != 0:
                self.final_image.append(self.image[points[1] - 1])

    def __get_random_series(self):
        self.random_series = []
        for i in range(200):
            self.random_series.append(randint(0, 5))

    def set_dice(self, points):
        location = list()
        self.__prepare_image(points)
        self.__get_random_series()
        if points[1] == 0:
            location.append(self.image_location[0])
        else:
            location.append(self.image_location[1])
            location.append(self.image_location[2])
        return location


class MusicPlay:
    def __init__(self):
        pygame.mixer.init()
        self.music = pygame.mixer.music.load("./source/Dexter Britain - Nothing To Fear.mp3")
        self.musicOn = pygame.image.load("./source/MusicOn.png").convert_alpha()
        self.musicOff = pygame.image.load("./source/MusicOff.png").convert_alpha()
        self.barrier = pygame.image.load("./source/MusicBarrier.png").convert_alpha()
        self.image = self.musicOn
        self.isPlaying = True
        self.buttonRect = Rect(41 * 25, 27 * 25, 100, 75)
        pygame.mixer.music.set_volume(0.618)
        pygame.mixer.music.play(-1)
    
    def pause(self, pos):
        if pos[0] > (41 * 25 + 8) and pos[0] < (41 * 25 + 94) and pos[1] > (27 * 25 + 4) and pos[1] < (27 * 25 + 68):
            if self.isPlaying is True:
                pygame.mixer.music.pause()
                self.image = self.musicOff
            else:
                pygame.mixer.music.unpause()
                self.image = self.musicOn
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


def location_convert(position):
    position += 1
    if position <= 16:
        return (position - 1) * 75, 0
    if position <= 26:
        return 15 * 75, (position - 16) * 75
    if position <= 41:
        return (15 - (position - 26)) * 75, 10 * 75
    if position <= 50:
        return 0, (9 - (position - 42)) * 75


# pygame初始化
pygame.init()

# 窗口初始化
pygame.display.init()
screen = pygame.display.set_mode((1200, 825))
pygame.display.set_icon(pygame.image.load("./source/dog.ico").convert_alpha())
pygame.display.set_caption("大富翁")

# 载入图片
start = pygame.image.load("./source/start.png").convert_alpha()
gameOver = pygame.image.load("./source/gameover.png").convert_alpha()
gameWin = pygame.image.load("./source/gamewin.png").convert_alpha()
gameMap = pygame.image.load("./source/map.png").convert_alpha()
PCImage = pygame.image.load("./source/PC.png").convert_alpha()
PCFixImage = pygame.image.load("./source/PCBeginning.png").convert_alpha()
NPCImage = pygame.image.load("./source/NPC.png").convert_alpha()
NPCFixImage = pygame.image.load("./source/NPCBeginning.png").convert_alpha()

backgroundMusic = MusicPlay()           # 音乐播放
clock = pygame.time.Clock()             # 帧率控制
keySpace = pygame.event                 # 用于存储空格被按下的事件
gameTurn = GameTurn.start               # 游戏状态
winner = ""                             # 胜利者
playAgain = False                       # 多次进行游戏

# 游戏字体
font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 20)

# 进入游戏
while True:
    if gameTurn is GameTurn.start:
        gameTurn = GameTurn.waitIn

        shootDice = ShootDice()                     # 骰子管理类
        playerTurn = PlayerTurn.start               # 行动回合
        hero = PC("Naruto", PCImage)                # PC
        enemy = NPC("Sasuke", NPCImage)             # NPC
        lands = Landmasses(hero.name, enemy.name)   # 地块初始化

        # 开始界面
        for i in range(150):
            clock.tick(150)
            screen.blit(gameMap, (0, 0))
            screen.blit(PCFixImage, (6 * 25 + 13 + i * 1 - 10, 6 * 25 + 13 - 10))
            screen.blit(NPCFixImage, (38 * 25 + 13 - i * 1 - 10, 6 * 25 + 13 - 10))
            screen.blit(start, (175, 325))
            screen.blit(backgroundMusic.image, (41 * 25, 27 * 25))
            pygame.display.update()

    if gameTurn is not GameTurn.start:
        if gameTurn is GameTurn.playing:
            clock.tick(10)  # 帧数
            screen.blit(gameMap, (0, 0))

            # 地块绘制
            for land in lands.lands:
                if land.owner == hero.name:
                    screen.blit(lands.cattleOfPC[land.level], location_convert(land.position))
                elif land.owner == enemy.name:
                    screen.blit(lands.cattleOfNPC[land.level], location_convert(land.position))
                else:
                    screen.blit(lands.wasteland, location_convert(land.position))

            # 人物绘制
            screen.blit(enemy.image, location_convert(enemy.position))
            screen.blit(hero.image, location_convert(hero.position))

            # 固定位置人物绘制
            screen.blit(PCFixImage, (19 * 25 - 21, 4 * 25))
            screen.blit(NPCFixImage, (41 * 25 - 21, 4 * 25))

            # 音乐播放状态图片展示
            screen.blit(backgroundMusic.image, (41 * 25, 27 * 25))

            # 信息显示
            hero.display(lands)
            enemy.display(lands)

            # 骰子掷过之后将骰子保留在原位置
            for i in range(len(shootDice.diceLocation)):
                screen.blit(shootDice.final_image[i], shootDice.diceLocation[i])

        # 结束判定
        if (hero.money <= 0 or enemy.money <= 0) and gameTurn is not GameTurn.end:
            winner = enemy.name if hero.money <= 0 else hero.name
            gameTurn = GameTurn.over

        for event in pygame.event.get():
            # 退出游戏
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_e):
                if backgroundMusic.isPlaying is True:
                    pygame.mixer.music.fadeout(1500)
                    pygame.time.delay(1500)
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN and gameTurn is not GameTurn.end:
                # 开发者模式
                if enemy.check() is False and gameTurn is GameTurn.playing:
                    if event.key == K_d:
                        enemy.cheat[0] = 1
                    if enemy.cheat[0] == 1 and event.key == K_w:
                        enemy.cheat[1] = 1
                    if enemy.cheat[1] == 1 and event.key == K_q:
                        enemy.cheat[2] = 1

                if event.key == pygame.K_SPACE:
                    # 进入游戏
                    if gameTurn is GameTurn.waitIn:
                        gameTurn = GameTurn.playing
                        keySpace = event

                    # 人物回合切换
                    elif gameTurn is GameTurn.playing:
                        if playerTurn is PlayerTurn.start:
                            playerTurn = PlayerTurn.PCMove
                            shootDice.steps = hero.move()
                            if shootDice.steps[2] is False:
                                shootDice.diceLocation = shootDice.set_dice(shootDice.steps)
                            enemy.money += hero.incidents(lands)
                        elif playerTurn is PlayerTurn.PCAct:
                            playerTurn = PlayerTurn.NPCAct
                            break

                # PC购买地块、交换金钱、使用炸药
                if event.key == pygame.K_b and playerTurn is PlayerTurn.PCAct:
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
                if hero.transportation == "千里马" and playerTurn is PlayerTurn.PCAct:
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
                playAgain = True

            # 音乐播放控制的鼠标事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if backgroundMusic.pause(event.pos) is True:
                    screen.blit(backgroundMusic.image, (41 * 25, 27 * 25))      # Button Down
                    pygame.display.update(backgroundMusic.buttonRect)
                    pygame.time.delay(100)
                    screen.blit(backgroundMusic.barrier, (41 * 25, 27 * 25))
                    screen.blit(backgroundMusic.image, (41 * 25, 27 * 25))      # Button Up
                    pygame.display.update(backgroundMusic.buttonRect)

        if playerTurn is PlayerTurn.NPCMove:
            shootDice.steps = enemy.move()
            if shootDice.steps[2] is False:
                shootDice.diceLocation = shootDice.set_dice(shootDice.steps)
            hero.money += enemy.incidents(lands)
        elif playerTurn is PlayerTurn.NPCAct:
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

        # 掷骰子动画播放
        if (playerTurn is PlayerTurn.PCMove or playerTurn is PlayerTurn.NPCMove) and shootDice.steps[2] is False:
            lenOfDiceLocation = len(shootDice.diceLocation)
            clock.tick(10 * lenOfDiceLocation)
            for rand in shootDice.random_series:
                screen.blit(shootDice.barrier, (18 * 25, 17 * 25))
                for i in range(lenOfDiceLocation):
                    screen.blit(shootDice.image[rand], shootDice.diceLocation[i])
                pygame.display.update()
            screen.blit(shootDice.barrier, (18 * 25, 17 * 25))
            for i in range(lenOfDiceLocation):
                screen.blit(shootDice.final_image[i], shootDice.diceLocation[i])
            pygame.display.update()
            pygame.time.delay(700)

        # 回合切换
        if playerTurn is PlayerTurn.PCMove:
            playerTurn = PlayerTurn.NPCMove
        elif playerTurn is PlayerTurn.NPCMove:
            playerTurn = PlayerTurn.PCAct
        elif playerTurn is PlayerTurn.NPCAct:
            playerTurn = PlayerTurn.start
            pygame.event.post(keySpace)  # 抛出一个空格被按下的事件，提高游戏的操作简便性

    if gameTurn is GameTurn.over:
        gameTurn = GameTurn.end
        screen.blit(shootDice.barrier, (18 * 25, 17 * 25))
        screen.blit(gameWin, (175, 325)) if winner == hero.name else screen.blit(gameOver, (175, 325))
        pygame.display.update()
    if gameTurn is not GameTurn.end:
        pygame.display.update()

    if playAgain is True:
        gameTurn = GameTurn.start
        playerTurn = playerTurn.start
        playAgain = not playAgain
