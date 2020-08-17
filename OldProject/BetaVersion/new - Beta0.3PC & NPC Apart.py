import pygame
import sys
from pygame.locals import *
from random import randint


# 角色
class PC:
    def __init__(self, name, image):
        self.name = name
        self.position = 0   # 初始位置
        self.money = 1000   # 初始资金
        self.image = image   # 外观图片
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
            return
        elif self.status == "保释":
            self.status = "正常"

        # 掷骰子
        roll = randint(1, 6) if self.transportation == "无" else randint(2, 12)

        if self.ill > 0:
            roll = roll // 2    # 感冒移动速度减半
            if roll == 0:
                roll = 1
            self.ill -= 1
            if self.ill == 0:
                self.status = "正常"
        elif self.wind is True:
            roll = randint(1, 50)   # 遭遇大风，随机落地
            self.wind = not self.wind

        # 坐标变化
        if self.position + roll < 50:
            self.position += roll
        else:
            self.position = self.position + roll - 50
            self.money += 300   # 绕地图一圈奖励

    def display(self, Ls):
        self.__displayBase()
        self.__displayIncidents(Ls.lands, Ls.incidents)

    def __displayBase(self):
        # 准备工作
        messages = list()
        for i in range(3):
            messages.append(list())
        messages[0].append(font.render("姓名: %s" % self.name, True, [0, 0, 0]))
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

    def __displayIncidents(self, L, incidents):
        # 准备工作
        messages = list()
        location = self.position
        # 购买或升级地块
        if L[location].owner != "事件":
            level = L[location].level
            if L[location].owner == "系统":
                messages.append(font.render("这里是一片无主的荒地", True, [0, 0, 255]))
                messages.append(font.render("按B键花费%d金币建立城堡" % ((level + 1) * 100), True, [0, 0, 255]))
                if self.free == 1:
                    messages.append(font.render("你可以免费建立城堡（仅限一次）", True, [0, 0, 255]))
            elif L[location].owner == self.name:
                messages.append(font.render("城墙上的卫兵向你举旗致敬", True, [0, 0, 255]))
                if L[location].level < 5:
                    messages.append(font.render("按B键花费%d金币升级城堡" % ((level + 1) * 100), True, [0, 0, 255]))
                    if self.free == 1:
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
                messages.append(font.render("现在你以双倍速度进行移动！", True, [0, 0, 255]))
            # 买了马想升级
            elif self.transportation == "战马":
                messages.append(font.render("按B键花费2000金币将战马升级为千里马", True, [0, 0, 255]))
                messages.append(font.render("骑上千里马的你可以进行额外行动！", True, [0, 0, 255]))
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
                messages.append(font.render("你本回合无法移动", True, [0, 0, 255]))
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
            messages.append(font.render("你下次移动后将在随机位置出现", True, [0, 0, 255]))
        # 事件9：领主结好
        elif L[location].incident == incidents[9]:
            messages.append(font.render("事件:你与本地领主建立友谊，得到了他的承诺", True, [0, 0, 255]))
            messages.append(font.render("你下次修建或升级城堡完全免费", True, [0, 0, 255]))
        # 信息输出
        for i in range(len(messages)):
            screen.blit(messages[i], (self.messageBoardLocation[1][0], self.messageBoardLocation[1][1] + i * 25))

    def buy(self, L, cattleOfPC):
        location = self.position
        # 购买地块
        price = L[location].price(self.name)
        if price != 0:
            if self.free is False:
                self.money -= price
            else:
                self.free = not self.free
            L[location].changeProperty(self.name, cattleOfPC[L[location].level])
        # 买马以及升级
        if L[location].incident == "马场":
            if self.money > 1000 and self.transportation == "无":
                self.money -= 1000
                self.transportation = "战马"
            elif self.money > 2000 and self.transportation == "战马":
                self.money -= 2000
                self.transportation = "千里马"
                self.engine = 1

    def incidents(self, Ls):
        L = Ls.lands
        incidents = Ls.incidents
        location = self.position
        # 1.路过敌人房子
        if L[location].owner != self.name and L[location].owner != "事件" and L[location].owner != "系统":
            self.money -= L[location].level * 100
            return L[location].level * 100
        # 特殊事件房间
        elif L[location].owner == "事件":
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


class NPC:
    def __init__(self, name, image):
        self.name = name
        self.position = 0   # 初始位置
        self.money = 1000   # 初始资金
        self.image = image   # 外观图片
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
            return
        elif self.status == "保释":
            self.status = "正常"

        # 掷骰子
        roll = randint(1, 6) if self.transportation == "无" else randint(2, 12)

        if self.ill > 0:
            roll = roll // 2    # 感冒移动速度减半
            if roll == 0:
                roll = 1
            self.ill -= 1
            if self.ill == 0:
                self.status = "正常"
        elif self.wind is True:
            roll = randint(1, 50)   # 遭遇大风，随机落地
            self.wind = not self.wind

        # 坐标变化
        if self.position + roll < 50:
            self.position += roll
        else:
            self.position = self.position + roll - 50
            self.money += 300   # 绕地图一圈奖励

    def check(self):
        if self.cheat[0] * self.cheat[1] * self.cheat[2] == 1:
            return True
        return False

    def display(self, Ls):
        if self.check() is True:
            self.__displayBase()
            self.__displayIncidents(Ls.lands, Ls.incidents)
        else:
            screen.blit(font.render("依次按下DWQ进入开发者模式", True, [0, 0, 255]), (27 * 25, 7 * 25))
            screen.blit(font.render("查看NPC的状态", True, [0, 0, 255]), (27 * 25, 8 * 25))

    def __displayBase(self):
        # 准备工作
        messages = list()
        for i in range(3):
            messages.append(list())
        messages[0].append(font.render("姓名: %s" % self.name, True, [0, 0, 0]))
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

    def __displayIncidents(self, L, incidents):
        # 准备工作
        messages = list()
        location = self.position
        # 购买或升级地块
        if L[location].owner != "事件":
            level = L[location].level
            if L[location].owner == "系统":
                messages.append(font.render("这里是一片无主的荒地", True, [0, 0, 255]))
                messages.append(font.render("花费%d金币建立城堡" % ((level + 1) * 100), True, [0, 0, 255]))
                if self.free == 1:
                    messages.append(font.render("你可以免费建立城堡（仅限一次）", True, [0, 0, 255]))
            elif L[location].owner == self.name:
                messages.append(font.render("城墙上的卫兵向你举旗致敬", True, [0, 0, 255]))
                if L[location].level < 5:
                    messages.append(font.render("花费%d金币升级城堡" % ((level + 1) * 100), True, [0, 0, 255]))
                    if self.free == 1:
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
                messages.append(font.render("现在你以双倍速度进行移动！", True, [0, 0, 255]))
            # 买了马想升级
            elif self.transportation == "战马":
                messages.append(font.render("花费2000金币将战马升级为千里马", True, [0, 0, 255]))
                messages.append(font.render("骑上千里马的你可以进行额外行动！", True, [0, 0, 255]))
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
                messages.append(font.render("你本回合无法移动", True, [0, 0, 255]))
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
            messages.append(font.render("你下次移动后将在随机位置出现", True, [0, 0, 255]))
        # 事件9：领主结好
        elif L[location].incident == incidents[9]:
            messages.append(font.render("事件:你与本地领主建立友谊，得到了他的承诺", True, [0, 0, 255]))
            messages.append(font.render("你下次修建或升级城堡完全免费", True, [0, 0, 255]))
        # 信息输出
        for i in range(len(messages)):
            screen.blit(messages[i], (self.messageBoardLocation[1][0], self.messageBoardLocation[1][1] + i * 25))

    def buy(self, L, cattleOfNPC):
        location = self.position
        if self.money > 500:
            # 购买地块
            price = L[location].price(self.name)
            if price != 0:
                if self.free is False:
                    self.money -= price
                else:
                    self.free = not self.free
                L[location].changeProperty(self.name, cattleOfNPC[L[location].level])
            # 买马以及升级
            elif L[location].incident == "马场":
                if self.money > 1600 and self.transportation == "无":
                    self.money -= 1000
                    self.transportation = "战马"
                elif self.money > 2300 and self.transportation == "战马":
                    self.money -= 2000
                    self.transportation = "千里马"
                    self.engine = 1

    def incidents(self, Ls):
        L = Ls.lands
        incidents = Ls.incidents
        location = self.position
        # 1.路过敌人房子
        if L[location].owner != self.name and L[location].owner != "事件" and L[location].owner != "系统":
            self.money -= L[location].level * 100
            return L[location].level * 100
        # 特殊事件房间
        elif L[location].owner == "事件":
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


class landmasses:
    def __init__(self, PCName, NPCName):
        self.cattleOfPC = list()
        self.cattleOfNPC = list()
        self.wasteland = pygame.image.load("./source/wasteland.png")
        self.incidents = ["起点", "马场", "小偷", "监狱", "资金互换", "炸药", "资产暴增", "感冒", "大风", "领主"]
        self.lands = list()
        self.PCName = str(PCName)
        self.NPCName = str(NPCName)

        self.cattleOfPC.append(self.wasteland)
        self.cattleOfPC.append(pygame.image.load("./source/houseA1.png"))
        self.cattleOfPC.append(pygame.image.load("./source/houseA2.png"))
        self.cattleOfPC.append(pygame.image.load("./source/houseA3.png"))
        self.cattleOfPC.append(pygame.image.load("./source/houseA4.png"))
        self.cattleOfPC.append(pygame.image.load("./source/houseA5.png"))

        self.cattleOfNPC.append(self.wasteland)
        self.cattleOfNPC.append(pygame.image.load("./source/houseB1.png"))
        self.cattleOfNPC.append(pygame.image.load("./source/houseB2.png"))
        self.cattleOfNPC.append(pygame.image.load("./source/houseB3.png"))
        self.cattleOfNPC.append(pygame.image.load("./source/houseB4.png"))
        self.cattleOfNPC.append(pygame.image.load("./source/houseB5.png"))


        class oneLand:
            def __init__(self, position, image = self.wasteland, owner = "系统", incident = "无"):
                self.owner = str(owner)
                self.position = position
                self.level = 0
                self.image = image
                self.incident = incident

            def price(self, who):
                if (who == self.owner and self.level < 5) or self.owner == "系统":
                    return (self.level + 1) * 100
                return 0

            def changeProperty(self, who, ensureSubscriptable = self.PCName,
                               cattlePC = self.cattleOfPC, cattleNPC = self.cattleOfNPC):
                self.owner = who
                self.level += 1
                self.incident = who + "的房间"
                if who == "PC":
                    self.image = cattlePC[self.level]
                else:
                    self.image = cattleNPC[self.level]

            def bang(self, wasteland = self.wasteland):
                self.owner = "系统"
                self.level = 0
                self.image = wasteland
                self.incident = "无"

        counter = 0
        for i in range(50):
            if (i + 1) % 5 == 1:
                self.lands.append(oneLand(i, owner = "事件", incident = self.incidents[counter]))
                counter += 1
            else:
                self.lands.append(oneLand(i))


def locationConvert(position):
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
# 载入图片
icon = pygame.image.load("./source/dog.ico")
start = pygame.image.load("./source/start.png")
gameOver = pygame.image.load("./source/gameover.png")
gameWin = pygame.image.load("./source/gamewin.png")
gameMap = pygame.image.load("./source/map.png")

PCImage = pygame.image.load("./source/PC.png")
PCFixImage = pygame.image.load("./source/PCBeginning.png")
NPCImage = pygame.image.load("./source/NPC.png")
NPCFixImage = pygame.image.load("./source/NPCBeginning.png")
# 游戏字体
font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 20)

# 帧率控制
clock = pygame.time.Clock()
# 窗口初始化
pygame.display.init()
try:
    pygame.display.set_icon(icon)
except:
    pass
screen = pygame.display.set_mode((1200, 825))
pygame.display.set_caption("大富翁")

# 游戏角色
hero = PC("PC", PCImage)
enemy = NPC("NPC", NPCImage)

# 地块初始化
lands = landmasses(hero.name, enemy.name)

# 开始界面
for i in range(150):
    clock.tick(80)
    screen.blit(gameMap, (0, 0))
    screen.blit(PCFixImage, (6 * 25 + 13 + i * 1 - 10, 6 * 25 + 13 - 10))
    screen.blit(NPCFixImage, (38 * 25 + 13 - i * 1 - 10, 6 * 25 + 13 - 10))
    screen.blit(start, (175, 325))
    pygame.display.update()
order = False
while order is False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                order = True
            if event.key == K_e:
                pygame.quit()
                sys.exit()

# 行动回合
heroTurn, enemyTurn = True, False

# 游戏界面
while True:
    clock.tick(10)      # 帧数
    screen.blit(gameMap, (0, 0))
    # 地块绘制
    for land in lands.lands:
        screen.blit(land.image, locationConvert(land.position))
    # 人物绘制
    screen.blit(enemy.image, locationConvert(enemy.position))
    screen.blit(hero.image, locationConvert(hero.position))
    # 固定位置人物绘制
    screen.blit(PCFixImage, (19 * 25 - 21, 4 * 25))
    screen.blit(NPCFixImage, (41 * 25 - 21, 4 * 25))
    # 信息显示
    hero.display(lands)
    enemy.display(lands)
    # 结束判定
    if hero.money <= 0 or enemy.money <= 0:
        winner = enemy.name if hero.money <= 0 else hero.name
        break

    # 按键操作
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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
            # 掷骰子
            if heroTurn is True:
                if event.key == K_SPACE:
                    hero.move()
                    enemy.money += hero.incidents(lands)
                    heroTurn, enemyTurn = not heroTurn, not enemyTurn
                    hero.engine = 0
            # 购买地块、交换金钱、使用炸药
            if event.key == K_b:
                if (lands.lands[hero.position].owner != enemy.name and lands.lands[hero.position].owner != "事件")\
                        or lands.lands[hero.position].incident == "马场":
                    hero.buy(lands.lands, lands.cattleOfPC)
                elif lands.lands[hero.position].owner == "事件":
                    if lands.lands[hero.position].incident == "资金互换" and hero.chance is True:
                        temp = hero.money
                        hero.money = enemy.money
                        enemy.money = temp
                        hero.chance = not hero.chance
                elif lands.lands[hero.position].owner == enemy.name and hero.item == "炸药":
                    lands.lands[hero.position].bang()
                    hero.item = "无"
            # 退出游戏
            elif event.key == K_e:
                pygame.quit()
                sys.exit()
            # 引擎移动
            if hero.transportation == "千里马":
                if event.key == K_a:        # 后退
                    if hero.engine == 0 or hero.engine == 1:
                        if hero.position > 1:
                            hero.position -= 1
                            hero.engine -= 1
                elif event.key == K_d:      # 前进
                    if hero.engine == 0 or hero.engine == -1:
                        if hero.position < 50:
                            hero.position += 1
                            hero.engine += 1

    if enemyTurn is True:
        enemy.move()
        hero.money += enemy.incidents(lands)
        if lands.lands[hero.position].incident == "资金互换" and enemy.chance is True and hero.money > enemy.money:
            temp = hero.money
            hero.money = enemy.money
            enemy.money = temp
            enemy.chance = not enemy.chance
        elif lands.lands[enemy.position].owner == hero.name and enemy.item == "炸药":
            lands.lands[enemy.position].bang()
            enemy.item = "无"
        else:
            enemy.buy(lands.lands, lands.cattleOfNPC)
        heroTurn, enemyTurn = not heroTurn, not enemyTurn

    pygame.display.update()

# 结束界面
if winner == hero.name:
    screen.blit(gameWin, (175, 325))
else:
    screen.blit(gameOver, (175, 325))
pygame.display.update()

order = False
while order is False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                order = True

pygame.quit()
