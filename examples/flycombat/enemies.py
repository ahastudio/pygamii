from pygamii.objects import Object
from pygamii.action import Action
from pygamii.audio import Audio
from gifts import get_gift
import random
import math


class Enemy(Object):
    is_kill = False
    kill_animation = False
    kill_steps = 5
    explosion_audio = Audio('songs/explosion.ogg')
    weapon = None
    _moving = True
    random_shot = 30

    def __init__(self, *args, **kwargs):
        super(Enemy, self).__init__(*args, **kwargs)
        self.gift_class = get_gift()
        if self.gift_class:
            self.color = self.gift_class.color

    def on_create(self):
        from weapon import BasicEnemyWeapon
        self.weapon = BasicEnemyWeapon(self.scene, self)

    def kill(self):
        if not self.kill_animation:
            self.scene.score.points += 5
            self.explosion_audio.song.set_volume(0.25)
            self.explosion_audio.play()
            self.kill_animation = True
            self.speed = 10

    def is_live(self):
        return not self.is_kill and not self.kill_animation

    def move(self):
        if self.kill_animation:
            if self.kill_steps % 2:
                self.color = 'red'
            else:
                self.color = 'white'
            self.kill_steps -= 1
            if self.kill_steps == 0:
                self.is_kill = True
                if self.gift_class:
                    gift = self.gift_class()
                    gift.x = self.x
                    gift.y = self.y
                    self.scene.add_object(gift)
        else:
            if random.randint(0, self.random_shot) == 7:
                if self.weapon:
                    self.weapon.shot()

    def on_collision(self, obj):
        if self.scene.airplane is obj and obj.is_live():
            self.kill()
            obj.kill()


class SimpleAirplaneEnemy(Enemy):
    y = -2
    height = 4
    width = 5
    color = 'yellow'
    speed = 5
    to_render = '\n'.join([
        ' ▄▄▄ ',
        '  █  ',
        '█████',
        '  ▀  ',
    ])

    def __str__(self):
        return self.to_render

    def move(self):
        super(SimpleAirplaneEnemy, self).move()
        self.y += 1


class HelicopterEnemy(Enemy):
    y = 5
    height = 4
    width = 11
    speed = 100
    color = 'grey'
    i = 0
    random_shot = 150
    y = -2
    _y = -2
    to_right = to_render = '\n'.join([
        '     ▀▀█▀▀ ',
        '▀█▀  ▃▀▀▀▃ ',
        ' ▀████████◗',
        '      ▀▀▀  '
    ])
    to_left = '\n'.join([
        '  ▀▀█▀▀     ',
        '  ▃▀▀▀▃  ▀█▀',
        ' ◖████████▀ ',
        '   ▀▀▀      ',
    ])

    def __str__(self):
        return self.to_render

    def on_create(self):
        super(HelicopterEnemy, self).on_create()
        if random.randint(1, 2) == 1:
            self.to_render = self.to_left

    def move(self):
        super(HelicopterEnemy, self).move()
        self.y = int(self._y + 2 * math.sin(self.i))
        self.i += 0.1
        if int(self.i * 10) % 5 == 0:
            if self.to_right == self.to_render:
                self.x += 1
                if self.x == self.scene.cols - self.width - 1:
                    self.to_render = self.to_left
            else:
                self.x -= 1
                if self.x == 0:
                    self.to_render = self.to_right

        if int(self.i * 10) % 50 == 0:
            self._y += 1


class EnemyGenerator(Action):
    interval = 3

    def __init__(self, scene, *args, **kwargs):
        super(EnemyGenerator, self).__init__(scene, *args, **kwargs)

    def do(self):
        klass = SimpleAirplaneEnemy
        if self.scene.score.points > 50:
            klass = random.choice([
                SimpleAirplaneEnemy,
                SimpleAirplaneEnemy,
                HelicopterEnemy
            ])

        airplane = klass()
        airplane.x = random.randrange(0, self.scene.cols - airplane.width)

        self.scene.add_object(airplane)

    def stop(self):
        super(EnemyGenerator, self).stop()
