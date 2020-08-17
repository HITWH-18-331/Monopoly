from Enums import Incidents


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
