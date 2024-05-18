from tanks import TankController, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT, SHOOT, SHOOT_SUPER, TANK_SIZE, GameState, Tank, normalize_angle
from math import degrees, atan2, sqrt

class Kim_CTankController(TankController):
    def __init__(self, tank_id: str):
        self.tank_id = tank_id

    @property
    def id(self) -> str:
        return "Kim_C"

    def find_closest_enemy_tank(self, gameState: GameState) -> Tank:
        my_tank = next(tank for tank in gameState.tanks if tank.id == self.id)
        alive_enemy_tanks = [tank for tank in gameState.tanks if tank.id != self.id and tank.health > 0]

        min_distance = float('inf')
        closest_enemy = None
        for enemy_tank in alive_enemy_tanks:
            dx = enemy_tank.position[0] - my_tank.position[0]
            dy = enemy_tank.position[1] - my_tank.position[1]
            distance = sqrt(dx * dx + dy * dy)
            if distance < min_distance:
                min_distance = distance
                closest_enemy = enemy_tank

        return closest_enemy

    def detect_nearby_bullets(self, gameState: GameState, my_tank: Tank):
        incoming_bullets = []
        for bullet in gameState.bullets:
            dx = bullet.position[0] - my_tank.position[0]
            dy = bullet.position[1] - my_tank.position[1]
            distance = sqrt(dx * dx + dy * dy)
            if distance < 150 and bullet.tank_id != my_tank.id:
                incoming_bullets.append(bullet)
        return incoming_bullets

    def decide_what_to_do_next(self, gameState: GameState) -> str:
        my_tank = next(tank for tank in gameState.tanks if tank.id == self.id)
        enemy_tank = self.find_closest_enemy_tank(gameState)

        # Detect incoming bullets and evade
        incoming_bullets = self.detect_nearby_bullets(gameState, my_tank)
        if incoming_bullets:
            # Evade by moving forward or backward based on bullet direction
            closest_bullet = incoming_bullets[0]
            bullet_dx = closest_bullet.position[0] - my_tank.position[0]
            bullet_dy = closest_bullet.position[1] - my_tank.position[1]
            bullet_angle = normalize_angle(degrees(atan2(-bullet_dy, bullet_dx)))
            bullet_angle_diff = normalize_angle(bullet_angle - my_tank.angle)
            if abs(bullet_angle_diff) < 90:
                return MOVE_BACKWARD
            else:
                return MOVE_FORWARD

        # Engage enemy tank
        dx = enemy_tank.position[0] - my_tank.position[0]
        dy = enemy_tank.position[1] - my_tank.position[1]
        distance = sqrt(dx * dx + dy * dy)
        desired_angle = normalize_angle(degrees(atan2(-dy, dx)))
        angle_diff = normalize_angle(desired_angle - my_tank.angle)

        # Frequent shooting when aligned with the enemy
        if abs(angle_diff) < 5:
            return SHOOT_SUPER if my_tank.health > 50 else SHOOT

        # Turn to align with the enemy
        if abs(angle_diff) > 3:
            return TURN_LEFT if angle_diff > 0 else TURN_RIGHT

        # Move towards the enemy if not too close
        if distance > max(TANK_SIZE) * 2:
            return MOVE_FORWARD

        # Default action
        return SHOOT

