# pygame相关
from pygame.locals import *

# 实体类
from GameManager import GameManager
from Enums import GameStatus, PlayerTurn, Incidents
from LandManage import Landmasses
from ShootDice import ShootDice


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
