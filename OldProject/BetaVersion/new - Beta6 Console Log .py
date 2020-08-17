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
            print("PC因感冒移动速度减半")
        if self.wind is True:
            roll = randint(1, 50)   # 遭遇大风，随机落地
            self.wind = not self.wind
            print("PC因遭遇大风，随机落地")

        # 坐标变化
        if self.position + roll < 50:
            self.position += roll
        else:
            self.position = self.position + roll - 50
            self.money += 500   # 绕地图一圈奖励

        return point1, point2, isWind

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
                messages.append(font.render("事件: 你已被保释，本回合将正常移动", True, [0, 0, 255]))
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
            if self.free is False:
                print("PC花费" + str(price) + "金币购买或升级了一座房子")
            else:
                print("PC免费购买或升级了一座房子")
            self.free = not self.free if self.free is True else self.free
            L[location].change_property(self.name)
        # 买马以及升级
        elif L[location].incident == "马场":
            if self.money > 1000 and self.transportation == "无":
                self.money -= 1000
                self.transportation = "战马"
                print("PC购买了一匹战马")
            elif self.money > 2000 and self.transportation == "战马":
                self.money -= 2000
                self.transportation = "千里马"
                print("PC购买了一匹千里马")

    def incidents(self, Ls):
        L = Ls.lands
        incidents = Ls.incidents
        location = self.position
        # 地块买满的奖励
        if Ls.is_full(self.name) is True:
            self.money += self.houseCounter * 100
            print("PC获得了地块被买满的奖励")
        # 1.路过敌人房子
        if L[location].owner != self.name and L[location].owner != "事件" and L[location].owner != "系统":
            self.money -= L[location].level * 100
            print("PC到达了NPC的房屋并付了租金" + str(L[location].level * 100) + "金币")
            return L[location].level * 100
        elif L[location].owner == "系统":
            print("PC到了一片无主的荒地")
        elif L[location].owner == self.name:
            print("PC到达了自己的地块")
        # 特殊事件房间
        elif L[location].owner == "事件" and self.engine == 0:
            # 0.到达起点
            if L[location].incident == incidents[0]:
                print("PC到达了起点")
            # 1.到达马场
            elif L[location].incident == incidents[1]:
                print("PC到达了马场")
            # 2.遭遇小偷
            if L[location].incident == incidents[2]:
                print("PC遭遇了小偷，", end="")
                if self.transportation == "无":
                    self.money -= 500
                    print("并失去了500金币")
                else:
                    print("幸运的是骑着马的PC没有成为小偷的目标")
            # 3.被囚禁
            elif L[location].incident == incidents[3]:
                if self.status != "保释":
                    self.status = "监禁"
                    print("PC被逮捕入狱了")
                elif self.status == "保释":
                    print("PC被保释了")
                elif self.status == "感冒":
                    print("PC因感冒避免了谋杀案的牵连")
            # 4.资金互换
            elif L[location].incident == incidents[4]:
                self.chance = True
            # 5.炸药
            elif L[location].incident == incidents[5]:
                self.item = "炸药"
                print("PC获得了炼金术士的炸药")
            # 6.捡钱
            elif L[location].incident == incidents[6]:
                self.money += 1000
                print("PC偶然间在山间发现了一座金矿，获得了1000金币")
            # 7.生病
            elif L[location].incident == incidents[7]:
                self.status = "感冒"
                self.ill = 3
                print("PC得了感冒")
            # 8.传送
            elif L[location].incident == incidents[8]:
                self.wind = True
                print("PC遭遇了大风")
            # 9.免费
            elif L[location].incident == incidents[9]:
                self.free = True
                print("PC与当地领主接好")
        if self.engine != 0 and L[location].owner == "事件" and L[location].incident != "起点":
            print("千里马的额外移动不能激活事件")
        return 0


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
            print("NPC因感冒移动速度减半")
        if self.wind is True:
            roll = randint(1, 50)   # 遭遇大风，随机落地
            self.wind = not self.wind
            print("NPC因遭遇大风，随机落地")

        # 坐标变化
        if self.position + roll < 50:
            self.position += roll
        else:
            self.position = self.position + roll - 50
            self.money += 500   # 绕地图一圈奖励

        return point1, point2, isWind

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
                messages.append(font.render("事件: 你已被保释，本回合将正常移动", True, [0, 0, 255]))
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
                    if self.free is False:
                        print("NPC花费了" + str(price) + "金币购买或升级了房屋")
                    else:
                        print("NPC免费购买或升级了房屋")
                    self.free = not self.free if self.free is True else self.free
                    L[location].change_property(self.name)
            # 买马以及升级
            elif L[location].incident == "马场":
                if self.money > 1600 and self.transportation == "无":
                    self.money -= 1000
                    self.transportation = "战马"
                    print("NPC购买了战马")
                elif self.money > 2600 and self.transportation == "战马":
                    self.money -= 2000
                    self.transportation = "千里马"
                    print("NPC购买了千里马")

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
            print("NPC到达了PC的房屋并付了租金" + str(L[location].level * 100) + "金币")
            return L[location].level * 100
        elif L[location].owner == "系统":
            print("NPC到达了一片无主的荒地")
        elif L[location].owner == self.name:
            print("NPC到达了自己的地块")
        # 特殊事件房间
        elif L[location].owner == "事件" and self.engine == 0:
            # 0.到达起点
            if L[location].incident == incidents[0]:
                print("NPC到达了起点")
            # 1.到达马场
            elif L[location].incident == incidents[1]:
                print("NPC到达了马场")
            # 2.遭遇小偷
            if L[location].incident == incidents[2]:
                print("NPC遭遇了小偷，", end="")
                if self.transportation == "无":
                    self.money -= 500
                    print("并失去了500金币")
                else:
                    print("幸运的是骑着马的NPC没有成为小偷的目标")
            # 3.被囚禁
            elif L[location].incident == incidents[3]:
                if self.status != "保释":
                    self.status = "监禁"
                    print("NPC被监禁了")
                elif self.status == "保释":
                    print("NPC被保释了")
                elif self.status == "感冒":
                    print("NPC因感冒避免了谋杀案的牵连")
            # 4.资金互换
            elif L[location].incident == incidents[4]:
                self.chance = True
            # 5.炸药
            elif L[location].incident == incidents[5]:
                self.item = "炸药"
                print("NPC获得了炼金术士的炸药")
            # 6.捡钱
            elif L[location].incident == incidents[6]:
                self.money += 1000
                print("NPC在山间发现了一座金矿，获得了1000金币")
            # 7.生病
            elif L[location].incident == incidents[7]:
                self.status = "感冒"
                self.ill = 3
                print("NPC得了感冒")
            # 8.传送
            elif L[location].incident == incidents[8]:
                self.wind = True
                print("NPC遭遇了大风")
            # 9.免费
            elif L[location].incident == incidents[9]:
                self.free = True
                print("NPC与当地领主接好")
        if self.engine != 0 and L[location].owner == "事件" and L[location].incident != "起点":
            print("千里马的额外移动不能激活事件")
        return 0

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


class landmasses:
    def __init__(self, PCName, NPCName):
        self.cattleOfPC = list()
        self.cattleOfNPC = list()
        self.wasteland = pygame.image.load("./source/wasteland.png").convert_alpha()
        self.incidents = ["起点", "马场", "小偷", "监狱", "资金互换", "炸药", "资产暴增", "感冒", "大风", "领主"]
        self.lands = list()
        self.PCName = str(PCName)
        self.NPCName = str(NPCName)
        self.PCAward = False
        self.NPCAward = False

        self.cattleOfPC.append(self.wasteland)
        for i in range(5):
            self.cattleOfPC.append(pygame.image.load("./source/houseA" + str(i + 1) + ".png").convert_alpha())

        self.cattleOfNPC.append(self.wasteland)
        for i in range(5):
            self.cattleOfNPC.append(pygame.image.load("./source/houseB" + str(i + 1) + ".png").convert_alpha())

        class OneLand:
            def __init__(self, position, image=self.wasteland, owner="系统", incident="无"):
                self.owner = owner
                self.position = position
                self.level = 0
                self.image = image
                self.incident = incident

            def price(self, who):
                if (who == self.owner and self.level < 5) or self.owner == "系统":
                    return (self.level + 1) * 100
                return 0

            def change_property(self, who, pcName=self.PCName, cattlePC=self.cattleOfPC, cattleNPC=self.cattleOfNPC):
                self.owner = who
                self.level += 1
                self.incident = who + "的房间"
                if who == pcName:
                    self.image = cattlePC[self.level]
                else:
                    self.image = cattleNPC[self.level]
                print("第" + str(self.position) + "地块被" + who + "购买或升级了")

            def bang(self, wasteland=self.wasteland):
                self.owner = "系统"
                self.level = 0
                self.image = wasteland
                self.incident = "无"
                print("第" + str(self.position) + "地块被炸毁了")

        counter = 0
        for i in range(50):
            if (i + 1) % 5 == 1:
                self.lands.append(OneLand(i, owner="事件", incident=self.incidents[counter]))
                counter += 1
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
        self.final_image = list()
        self.image_location = [(22 * 25, 18 * 25 + 5), (19 * 25 + 12, 18 * 25 + 5), (24 * 25 + 13, 18 * 25 + 5)]
        self.random_series = list()
        for i in range(6):
            self.image.append(pygame.image.load("./source/" + str(i + 1) + ".png").convert_alpha())

    def __prepare_image(self, points):
        self.final_image = []
        if points[2] is False:
            self.final_image.append(self.image[points[0] - 1])
            if points[1] != 0:
                self.final_image.append(self.image[points[1] - 1])

    def __get_random_series(self):
        for i in range(10):
            self.random_series.append(randint(0, 5))

    def set_dice(self, points):
        location = list()
        self.__prepare_image(points)
        print("准备骰子图片")
        self.__get_random_series()
        print("生成随机数列")
        if points[1] == 0:
            location.append(self.image_location[0])
        else:
            location.append(self.image_location[1])
            location.append(self.image_location[2])
        print("初始化骰子位置")
        return location


class Turn(Enum):
    start = 0   # 某一轮的开始
    PC = 1      # PC掷骰子
    PC_end = 2  # 等待PC行动
    NPC = 3     # NPC掷骰子及行动


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
print("pygame初始化完成")
# 窗口初始化
pygame.display.init()
screen = pygame.display.set_mode((1200, 825))
pygame.display.set_caption("大富翁")
print("窗口初始化完成")
# 载入图片
icon = pygame.image.load("./source/dog.ico").convert_alpha()
start = pygame.image.load("./source/start.png").convert_alpha()
gameOver = pygame.image.load("./source/gameover.png").convert_alpha()
gameWin = pygame.image.load("./source/gamewin.png").convert_alpha()
gameMap = pygame.image.load("./source/map.png").convert_alpha()
barrier = pygame.image.load("./source/barrier.png").convert_alpha()
PCImage = pygame.image.load("./source/PC.png").convert_alpha()
PCFixImage = pygame.image.load("./source/PCBeginning.png").convert_alpha()
NPCImage = pygame.image.load("./source/NPC.png").convert_alpha()
NPCFixImage = pygame.image.load("./source/NPCBeginning.png").convert_alpha()
print("图片载入完成")
# 游戏字体
font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 20)
print("字体设置完成")
# 帧率控制
clock = pygame.time.Clock()
print("时钟设置完成")
try:
    pygame.display.set_icon(icon)
    print("图标设置完成")
except:
    pass
# 游戏角色
hero = PC("Naruto", PCImage)
enemy = NPC("Sasuke", NPCImage)
print("游戏角色创建完成")
# 骰子管理类
shootDice = ShootDice()
diceLocation = list()
steps = (0, 0, True)
print("骰子管理初始化完成")
# 地块初始化
lands = landmasses(hero.name, enemy.name)
print("地块初始化完成")
# 行动回合
turnControl = Turn.start
# 用于存储空格被按下的事件
keySpace = pygame.event

# 开始界面
for i in range(150):
    clock.tick(150)
    screen.blit(gameMap, (0, 0))
    screen.blit(barrier, (18 * 25, 17 * 25))
    screen.blit(PCFixImage, (6 * 25 + 13 + i * 1 - 10, 6 * 25 + 13 - 10))
    screen.blit(NPCFixImage, (38 * 25 + 13 - i * 1 - 10, 6 * 25 + 13 - 10))
    screen.blit(start, (175, 325))
    pygame.display.update()
print("开始界面绘制完成")
order = False
while order is False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_e):
            print("游戏退出")
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                order = True
                keySpace = event
                print("进入游戏界面并捕获空格事件")

# 日志辅助代码
c = 0

# 游戏界面
while True:
    clock.tick(10)      # 帧数
    screen.blit(gameMap, (0, 0))
    # 地块绘制
    for land in lands.lands:
        screen.blit(land.image, location_convert(land.position))
    # 人物绘制
    screen.blit(enemy.image, location_convert(enemy.position))
    screen.blit(hero.image, location_convert(hero.position))
    # 固定位置人物绘制
    screen.blit(PCFixImage, (19 * 25 - 21, 4 * 25))
    screen.blit(NPCFixImage, (41 * 25 - 21, 4 * 25))
    # 信息显示
    hero.display(lands)
    enemy.display(lands)
    # 结束判定
    if hero.money <= 0 or enemy.money <= 0:
        print("进入失败判定")
        winner = enemy.name if hero.money <= 0 else hero.name
        break

    # 按键操作
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == K_e):
            print("游戏退出")
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # 开发者模式
            if enemy.check() is False:
                if event.key == K_d:
                    enemy.cheat[0] = 1
                if enemy.cheat[0] == 1 and event.key == K_w:
                    enemy.cheat[1] = 1
                if enemy.cheat[1] == 1 and event.key == K_q:
                    enemy.cheat[2] = 1
                    print("开发者模式启用")
            # PC回合
            if event.key == K_SPACE:
                if turnControl is Turn.start:
                    print("PC——————————————————")
                    print("资金：" + str(hero.money) + "金币")
                    print("坐标：" + str(hero.position) + "")
                    if hero.status != "正常":
                        print("状态：" + hero.status + "")
                    if hero.transportation != "无":
                        print("交通工具：" + hero.transportation + "")
                    if hero.item != "无":
                        print("装备：" + hero.item + "")
                    if hero.free is True:
                        print("PC与当地领主结好")
                    steps = hero.move()
                    if steps[2] is False:
                        print("第一个骰子的点数是" + str(steps[0]) + "")
                        if steps[1] != 0:
                            print("第二个骰子的点数是" + str(steps[1]) + "")
                        diceLocation = shootDice.set_dice(steps)
                        print("PC骰子设置参数完毕")
                    else:
                        print("PC遭遇了大风或被监禁，不掷骰子")
                    back = hero.incidents(lands)
                    if back != 0:
                        enemy.money += back
                        print("NPC获得了PC付的租金" + str(back) + "金币")
                    hero.engine = 0
                    turnControl = Turn.PC
                    print("等待PC购买地块、交换金钱、使用炸药或千里马额外移动")
                else:
                    turnControl = Turn.NPC
                    print("PC响应事件完毕，切换到NPC")
                    break
            # 购买地块、交换金钱、使用炸药
            if event.key == K_b:
                if (lands.lands[hero.position].owner != enemy.name and lands.lands[hero.position].owner != "事件")\
                        or lands.lands[hero.position].incident == "马场":
                    hero.buy(lands.lands)
                elif lands.lands[hero.position].incident == "资金互换" and hero.chance is True:
                    temp = hero.money
                    hero.money = enemy.money
                    enemy.money = temp
                    hero.chance = not hero.chance
                    print("PC使用了资金互换")
                elif lands.lands[hero.position].owner == enemy.name and hero.item == "炸药":
                    for i in range(lands.lands[hero.position].level):
                        enemy.houseCounter[i] -= 1
                    lands.lands[hero.position].bang()
                    hero.item = "无"
                    print("PC使用炸药炸毁了NPC的一座房屋")
            # 千里马额外移动
            if hero.transportation == "千里马":
                if event.key == K_a:        # 后退
                    if hero.engine == 0 or hero.engine == 1:
                        hero.position -= 1 if hero.position > 0 else -49
                        hero.engine -= 1
                        print("PC使用千里马的技能向后移动了一格")
                elif event.key == K_d:      # 前进
                    if hero.engine == 0 or hero.engine == -1:
                        hero.position += 1 if hero.position < 49 else -49
                        hero.engine += 1
                        print("PC使用千里马的技能向前移动了一格")

    if turnControl is Turn.NPC:
        print("NPC—————————————————")
        print("资金：" + str(enemy.money) + "金币")
        print("坐标：" + str(enemy.position) + "")
        if enemy.status != "正常":
            print("状态：" + enemy.status + "")
        if enemy.transportation != "无":
            print("交通工具：" + enemy.transportation + "")
        if enemy.item != "无":
            print("装备：" + enemy.item + "")
        if enemy.free is True:
            print("NPC与当地领主结好")
        steps = enemy.move()
        if steps[2] is False:
            print("第一个骰子的点数是" + str(steps[0]) + "")
            if steps[1] != 0:
                print("第二个骰子的点数是" + str(steps[1]) + "")
            diceLocation = shootDice.set_dice(steps)
            print("NPC骰子参数设置完毕")
        else:
            print("NPC因遭遇大风或被监禁，不掷骰子")
        hero.money += enemy.incidents(lands)
        if enemy.chance is True and hero.money > enemy.money and lands.lands[enemy.position].incident == "资金互换":
            temp = hero.money
            hero.money = enemy.money
            enemy.money = temp
            enemy.chance = not enemy.chance
            print("NPC使用了资金互换")
        elif lands.lands[enemy.position].owner == hero.name and enemy.item == "炸药":
            lands.lands[enemy.position].bang()
            enemy.item = "无"
            hero.houseCounter -= 1
            print("NPC使用炸药炸毁了PC的一座房屋")
        for i in range(5):
            enemy.buy(lands)
        if enemy.transportation == "千里马" and enemy.money > 900:
            # 利用千里马多买房子
            now = enemy.position
            forward = now + 1 if now < 49 else 0
            backward = now - 1 if now > 0 else 49
            if lands.lands[forward].owner == "系统" or lands.lands[forward].owner == enemy.name:
                enemy.position = forward
                print("NPC使用千里马的技能向前移动了一格")
                for i in range(5):
                    enemy.buy(lands)
                enemy.engine = 1
            if lands.lands[backward].owner == "系统" or lands.lands[forward].owner == enemy.name:
                enemy.position = backward
                print("NPC使用千里马的技能向后移动了一格")
                for i in range(5):
                    enemy.buy(lands)
                enemy.engine = -1
            enemy.position = now
            enemy.engine = 0
        pygame.event.post(keySpace)     # 提高游戏的操作简便性
        print("NPC抛出了一个空格被按下的事件")
    # 掷骰子动画播放
    if (turnControl is Turn.PC or turnControl is Turn.NPC) and steps[2] is False:
        if len(diceLocation) == 1:
            clock.tick(150)
            for rand in shootDice.random_series:
                screen.blit(shootDice.image[rand], diceLocation[0])
                pygame.display.update()
            screen.blit(shootDice.final_image[0], diceLocation[0])
        else:
            clock.tick(300)
            for rand in shootDice.random_series:
                screen.blit(shootDice.image[rand], diceLocation[0])
                screen.blit(shootDice.image[rand], diceLocation[1])
                pygame.display.update()
            screen.blit(shootDice.final_image[0], diceLocation[0])
            screen.blit(shootDice.final_image[1], diceLocation[1])
        pygame.display.update()
        if turnControl is Turn.PC:
            print("PC的掷骰子动画展示完毕")
        else:
            print("NPC的掷骰子动画展示完毕")
            # 回合计数
            c += 1
            print("第" + str(c) + "个回合结束\n")
        pygame.time.delay(1000)
    turnControl = Turn.PC_end if turnControl is Turn.PC or turnControl is Turn.PC_end else Turn.start
    pygame.display.update()

# 结束界面
screen.blit(barrier, (18 * 25, 17 * 25))
screen.blit(gameWin, (175, 325)) if winner == hero.name else screen.blit(gameOver, (175, 325))
pygame.display.update()
print("游戏结束图片展示完毕")
order = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_e):
            print("游戏退出")
            pygame.quit()
            sys.exit()
