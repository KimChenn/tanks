from tanks import TankController, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT, SHOOT, SHOOT_SUPER, TANK_SIZE, GameState, Tank, normalize_angle, check_collision, TREE_RADIUS, BULLET_RADIUS
from math import degrees, atan2, sqrt, radians, cos, sin

class Kim_CTankController(TankController):
    def __init__(self, tank_id: str):
        self.tank_id = tank_id
        self.previous_action = None
        self.previous_enemy_position = None
        self.evade_mode = False
        self.move_forward_count = 0

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

    def check_for_obstacles(self, position, angle, gameState: GameState) -> bool:
        new_x = position[0] + cos(radians(angle)) * TANK_SIZE[0]
        new_y = position[1] - sin(radians(angle)) * TANK_SIZE[1]
        new_position = (new_x, new_y)
        for tree in gameState.trees:
            if check_collision(new_position, tree.position, max(TANK_SIZE) / 2, TREE_RADIUS):
                return True
        return False

    def detect_nearby_bullets(self, gameState: GameState, my_tank: Tank):
        incoming_bullets = []
        for bullet in gameState.bullets:
            dx = bullet.position[0] - my_tank.position[0]
            dy = bullet.position[1] - my_tank.position[1]
            distance = sqrt(dx * dx + dy * dy)
            if distance < 150 and bullet.tank_id != my_tank.id:  # Detecting nearby bullets within a threshold distance
                incoming_bullets.append((bullet, distance))
        return incoming_bullets

    def decide_what_to_do_next(self, gameState: GameState) -> str:
        my_tank = next(tank for tank in gameState.tanks if tank.id == self.id)
        enemy_tank = self.find_closest_enemy_tank(gameState)
        
        dx = enemy_tank.position[0] - my_tank.position[0]
        dy = enemy_tank.position[1] - my_tank.position[1]

        distance = sqrt(dx * dx + dy * dy)
        desired_angle = normalize_angle(degrees(atan2(-dy, dx)))
        angle_diff = normalize_angle(desired_angle - my_tank.angle)

        # Detect nearby bullets and avoid them while shooting back
        incoming_bullets = self.detect_nearby_bullets(gameState, my_tank)
        if incoming_bullets:
            closest_bullet, _ = incoming_bullets[0]
            bullet_dx = closest_bullet.position[0] - my_tank.position[0]
            bullet_dy = closest_bullet.position[1] - my_tank.position[1]
            bullet_angle = normalize_angle(degrees(atan2(-bullet_dy, bullet_dx)))
            bullet_angle_diff = normalize_angle(bullet_angle - my_tank.angle)

            self.evade_mode = True
            if abs(bullet_angle_diff) < 90:  # If the bullet is coming from the front, move backward
                if abs(angle_diff) < 10:  # If the tank is aligned towards the bullet, shoot back
                    self.previous_action = SHOOT
                    return SHOOT
                self.previous_action = MOVE_BACKWARD
                return MOVE_BACKWARD
            else:  # If the bullet is coming from behind, move forward
                if abs(angle_diff) < 10:  # If the tank is aligned towards the bullet, shoot back
                    self.previous_action = SHOOT
                    return SHOOT
                self.previous_action = MOVE_FORWARD
                return MOVE_FORWARD

        # Exit evade mode if no bullets are detected
        self.evade_mode = False

        # Proactive shooting when a tank is close
        if distance < 200:  # If enemy tank is close
            if abs(angle_diff) < 10:  # Tolerance for shooting
                self.previous_action = SHOOT_SUPER if my_tank.health > 50 else SHOOT
                return SHOOT_SUPER if my_tank.health > 50 else SHOOT
            self.previous_action = TURN_LEFT if angle_diff > 0 else TURN_RIGHT
            return TURN_LEFT if angle_diff > 0 else TURN_RIGHT

        # Avoid obstacles
        if self.check_for_obstacles(my_tank.position, my_tank.angle, gameState):
            self.move_forward_count = 0  # Reset the forward move counter
            self.previous_action = TURN_LEFT if angle_diff > 0 else TURN_RIGHT
            return TURN_LEFT if angle_diff > 0 else TURN_RIGHT

        # Movement logic to prevent standing still
        if abs(angle_diff) > 10:
            self.previous_action = TURN_LEFT if angle_diff > 0 else TURN_RIGHT
            return TURN_LEFT if angle_diff > 0 else TURN_RIGHT
        else:
            self.move_forward_count += 1
            if self.move_forward_count > 10:  # Move backward after moving forward for a while
                self.move_forward_count = 0
                self.previous_action = MOVE_BACKWARD
                return MOVE_BACKWARD
            self.previous_action = MOVE_FORWARD
            return MOVE_FORWARD

        self.previous_action = MOVE_FORWARD
        return MOVE_FORWARD
