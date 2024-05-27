from tanks import TankController, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT, SHOOT, TANK_SIZE, GameState, Tank, normalize_angle
from math import degrees, atan2, sqrt, cos, sin
import pygame

class Kim_CTankController(TankController):
    def __init__(self, tank_id: str):
        self.tank_id = tank_id
        self.last_shot_received_time = None
        self.evasion_mode = False
        self.evasion_end_time = 0

    @property
    def id(self) -> str:
        return "Kim_C"

    def find_closest_enemy_tank(self, gameState: GameState) -> Tank:
        my_tank = next(tank for tank in gameState.tanks if tank.id == self.id)
        alive_enemy_tanks = [tank for tank in gameState.tanks if tank.id != self.id and tank.health > 0]
        closest_enemy = min(alive_enemy_tanks, key=lambda tank: sqrt((tank.position[0] - my_tank.position[0])**2 + (tank.position[1] - my_tank.position[1])**2), default=None)
        return closest_enemy

    def evade_bullets(self, gameState: GameState, my_tank: Tank):
        for bullet in gameState.bullets:
            if bullet.tank_id == my_tank.id:
                continue
            if self.will_bullet_hit_me(bullet, my_tank):
                self.evasion_mode = True  
                return self.avoid_bullet_direction(bullet, my_tank)
        return None

    def will_bullet_hit_me(self, bullet, my_tank):
        bullet_travel = sqrt(cos(bullet.angle)**2 + sin(bullet.angle)**2) * 10
        bullet_future_x = bullet.position[0] + bullet_travel * cos(bullet.angle)
        bullet_future_y = bullet.position[1] + bullet_travel * sin(bullet.angle)
        return sqrt((bullet_future_x - my_tank.position[0])**2 + (bullet_future_y - my_tank.position[1])**2) < max(TANK_SIZE)

    def avoid_bullet_direction(self, bullet, my_tank):
        bullet_angle = degrees(atan2(sin(bullet.angle), cos(bullet.angle)))
        if abs(normalize_angle(bullet_angle - my_tank.angle)) < 90:
            return MOVE_BACKWARD
        return MOVE_FORWARD

    def decide_what_to_do_next(self, gameState: GameState):
        current_time = pygame.time.get_ticks()
        my_tank = next(tank for tank in gameState.tanks if tank.id == self.id)

        if self.evasion_mode and current_time < self.evasion_end_time:
            return MOVE_BACKWARD  

        self.evasion_mode = False

        evasion_action = self.evade_bullets(gameState, my_tank)
        if evasion_action:
            self.evasion_end_time = current_time + 2000
            return evasion_action

        enemy_tank = self.find_closest_enemy_tank(gameState)
        if enemy_tank:
            return self.engage_enemy(my_tank, enemy_tank)

        return MOVE_FORWARD

    def engage_enemy(self, my_tank, enemy_tank):
        dx = enemy_tank.position[0] - my_tank.position[0]
        dy = enemy_tank.position[1] - my_tank.position[1]
        distance = sqrt(dx**2 + dy**2)
        angle_to_enemy = degrees(atan2(-dy, dx))
        angle_diff = normalize_angle(angle_to_enemy - my_tank.angle)

        if distance > max(TANK_SIZE) * 3:
            if abs(angle_diff) < 20:  
                return SHOOT
            elif angle_diff > 0:
                return TURN_RIGHT
            return TURN_LEFT
        elif distance < max(TANK_SIZE) * 2:
            return MOVE_BACKWARD  
        return MOVE_FORWARD  

