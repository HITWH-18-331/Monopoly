# 大一年度项目计划

大富翁游戏设计与实现，该仓库旨在对我们的大一年度项目计划进行整理，使用更多的模块划分和`OOD`的相关知识

## 所有的仓库地址

- `Github`：[点此前往](https://github.com/HITWH-18-331/Monopoly)，可以在这里获取`Release`文件
- `Gitee`：[点此前往](https://gitee.com/rikdon/Monopoly)
- `Gitlab`：[点此前往](https://gitlab.com/Rik-Don/monopoly)

## 团队成员

- **初征**
- **丁文琪**
- **董成相**
- **付宽**

## 简单的演示动画

<img src="./MonopolySimplePresentation.gif" alt="一个简单的演示动画" style="zoom:90%;" />

## 目录结构介绍

1. `OldProject`：该文件夹是整理前的工程文件，对外部的`source`和`dog.ico`文件有依赖
2. `Player`：该包是游戏角色类的包，包含`Player`超类，`PC`和`NPC`两个子类
3. `source`：该文件夹是游戏用到的图片素材，音乐素材，字体素材
4. `地图制作`：该文件夹包含一些制作游戏地图的过渡文件和一些游戏素材的过渡文件以及某些杂文件
5. `_config.yml`：该文件是`Github Pages`自动生成的主题记录文件
6. `dog.ico`：该文件是程序的图标
7. `Enums.py`：该文件是程序使用到的所有的枚举类
8. `GameManager.py`：该文件是与`Pygame`进行交互的主要承担者，也负责素材的载入工作
9. `LandManage`：该文件则包含了地块管理的两个类：`OneLand`和`Landmasses`，二者分别是单个地块和地图上所有地块的管理类
10. `Main.py`：该文件则是游戏的**主程序体**所在的文件
11. `MusicPlay`：该文件负责管理音乐的播放与暂停
12. `Pygame中文文档`：如其名
13. `ShootDice.py`：该文件则是掷骰子时的数据支撑类
14. `“校长杯”科技竞赛论文`：帮助理解我们的项目，里面进行了详细的介绍，但是与当前的版本略有出入，不过影响不大

## 地图制作

1. 使用到的软件：`Tiled Map Editor`
2. 素材来源：
    1. 爱给——专注免费素材，[点此前往](http://www.aigei.com)
    2. 其他来源，如有侵权请联系我们

## `Releases`打包方式介绍

1. `Pyinstaller`：家喻户晓
2. `Nuitka`：小众打包库，据说可以打包后可以获得`C++`级的运行效率，但是相比`Pyinstaller`打包较慢，[点此前往阅读官方文档](http://www.nuitka.net/doc/user-manual.html)
    1. 使用的`MinGW`版本：x86_64-7.3.0-release-posix-seh-rt_v5-rev0，[点此前往下载](https://sourceforge.net/projects/mingw-w64/files/Toolchains targetting Win64/Personal Builds/mingw-builds/7.3.0/threads-posix/seh/x86_64-7.3.0-release-posix-seh-rt_v5-rev0.7z/)

## `Bug`总结

1. 再次遇到了包引入问题，还是跟`python`大作业一样的问题

    ```python
    # 1. 该方式只引入了文件，没有引入文件中的类
    from Player import Player
    
    # 2. 该方式直接引入了相应的类
    from Player.Player import Player
    ```

2. `Python`私有方法被继承不能重写，或者说重写是没有作用的，又或者是我的用法不对，尚待测试或进一步了解。

## 目前存在的问题

1. 角色类的`incidents`方法和`incidents_message`方法应当可以抽象为父类的方法，冗余代码较多
2. 地块被买满的奖励存在问题，但是这个是历史遗留问题，之前似乎就没处理好
    1. 提示信息存在问题
    2. 地块被买满后的奖励代码存在问题，有可以优化的地方
3. `GameManager`类集成了过多的东西，不符合单一职责原则，考虑优化，但是部头太大，暂且寝之
    1. 不过这样做也有它的优点吧，`GameManager`实际上几乎承担了全部需要与`Pygame`交互的任务，从某种程度上剥离了项目对`Pygame`的依赖（`引擎的侵入性`，似乎有这么个说法）
    2. 诶，写完优点发现，可以给每一个实体类写一个与`Pygame`交互的类，但是**有亿点麻烦**
4. 代码缺少注释，阅读起来较为麻烦
5. 当`PC`与`NPC`到达了同一个位置时，并且其中一方购买了房屋之后会有金币被扣除的`提示`，但是实际上并没有扣除对方的金币余额

## 开源声明

本项目仅作**学习交流**用，任何**直接挪用**该项目的行为都是对我们劳动成果的不尊重，但是热烈欢迎**借鉴**我们的代码。
