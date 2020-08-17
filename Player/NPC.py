from Enums import Incidents
from Player.Player import Player


class NPC(Player):
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

    def incidents_messages(self, all_lands):
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
            self.buy_land(land, land_is_full) if price != 0 else False
            self.buy_horse() if land.incident is Incidents.horseField else False

    def buy_land(self, land, land_is_full):
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

    def buy_horse(self):
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
