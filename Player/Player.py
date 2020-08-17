from random import randint
from abc import ABCMeta, abstractmethod


class Player:
    __metaclass__ = ABCMeta

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

    @abstractmethod
    def swift_horse_move(self, forward):
        pass

    @abstractmethod
    def incidents(self, all_lands):
        pass

    def messages(self, all_lands):
        base_messages = self.__base_messages()
        incidents_messages = self.incidents_messages(all_lands)
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

    @abstractmethod
    def incidents_messages(self, all_lands):
        pass

    @abstractmethod
    def buy(self):
        pass

    @abstractmethod
    def buy_land(self):
        pass

    @abstractmethod
    def buy_horse(self):
        pass
