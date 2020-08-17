from enum import Enum


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
