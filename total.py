from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

place_block_sound = Audio('plac_block.wav', autoplay=False)
remove_block_sound = Audio('block_remove.mp3', autoplay=False)

# ----- 기본 설정 -----
ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4, 4))
Sky()

# ----- 플레이어 설정 -----
class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hp = 100
        self.health_bar = Entity(parent=camera.ui, model='quad', color=color.red, scale=(0.3, 0.03), position=(-0.65, 0.45))
        self.health_text = Text(f'{self.hp} HP', position=(-0.75, 0.5), scale=1.2, color=color.white)

player = Player()

# ----- 벽돌 구간 설정 -----
brick_positions = []
bricks = []

def generate_random_map():
    """랜덤 벽돌 맵 생성"""
    global bricks, brick_positions

    # 기존 벽돌 제거
    for brick in bricks:
        destroy(brick)
    bricks.clear()
    brick_positions.clear()

    # 새로운 벽돌 생성
    for _ in range(random.randint(20, 40)):  # 벽돌 개수 랜덤
        x = random.randint(5, 15)
        z = random.randint(5, 15)
        pos = (x, 1, z)
        if pos not in brick_positions:
            brick_positions.append(pos)
            create_brick(pos, color=color.rgb(150, 75, 0))

def create_brick(position, color=color.brown):
    """벽돌을 생성하고 리스트에 추가"""
    brick = Entity(
        model='cube',
        scale=(1, 1, 1),
        position=position,
        color=color,
        collider='box'
    )
    bricks.append(brick)
    return brick

# ----- 괴물 설정 -----
class Monster(Entity):
    def __init__(self, target=None, **kwargs):
        super().__init__(
            model='cube',
            scale=(2, 2, 2),
            collider='box',
            color=color.red,
            **kwargs
        )
        self.hp = 100
        self.speed = 2
        self.active = False  # 초기화 시 비활성화
        self.target = target  # 추적할 목표 (보물 또는 플레이어)

    def update(self):
        if not self.active or not self.enabled:  # 괴물이 비활성화된 경우 업데이트하지 않음
            return

        # 목표를 추적하는 알고리즘
        if self.target:
            self.look_at(self.target.position)  # 목표를 바라봄
            self.position += self.forward * time.dt * self.speed  # 목표를 향해 이동

            # 목표와 충돌 처리
            if current_round == 3 and isinstance(self.target, Treasure):  # 보물을 추적하는 경우
                if self.intersects(self.target).hit:
                    end_game("The monster caught the treasure!")
            elif self.target == player:  # 플레이어를 추적하는 경우
                if self.intersects(player).hit:
                    end_game("The monster caught you!")

    def take_damage(self, damage):
        """괴물이 데미지를 받는 메서드"""
        if not self.active or not self.enabled:  # 이미 비활성화된 경우 처리하지 않음
            return

        self.hp -= damage
        if self.hp <= 0:
            print("Monster defeated!")
            self.active = False
            self.enabled = False  # 엔티티 비활성화
            destroy(self)  # 괴물 제거
            end_round()

    def reset_position(self):
        """괴물 위치를 초기화"""
        self.position = random.choice(brick_positions)

    def activate(self, target):
        """괴물을 활성화"""
        self.enabled = True
        self.hp = 100
        self.active = True
        self.target = target  # 목표 설정
        self.reset_position()

monster = Monster(position=(10, 1, 10), enabled=False)

# ----- 보물 설정 -----
class Treasure(Entity):
    def __init__(self, move=False, **kwargs):
        super().__init__(
            model='cube',
            texture='gold',
            color=color.gold,
            scale=(1, 1, 1),
            collider='box',
            **kwargs
        )
        self.direction = Vec3(random.choice([-1, 1]), 0, random.choice([-1, 1]))
        self.move = move
        self.speed = 2

    def update(self):
        if self.move:  # 보물이 움직이는 경우
            self.position += self.direction * time.dt * self.speed

            # 벽돌 근처에서만 움직이도록 제한
            nearest_brick = min(brick_positions, key=lambda pos: distance(Vec3(pos), self.position))
            if distance(Vec3(nearest_brick), self.position) > 3:
                self.direction *= -1

treasure = None

# ----- 게임 설정 -----
round_time = 30
current_round = 0  # 0라운드부터 시작
max_rounds = 3
time_left = round_time
game_active = False

# ----- 타이머 -----
timer_text = Text(text=f'Time Left: {int(time_left)}', position=(-0.5, 0.4), scale=2)

def update_timer():
    global time_left
    time_left -= time.dt
    timer_text.text = f'Time Left: {int(time_left)}'
    if time_left <= 0:
        end_game("Time's up!")

# ----- 게임 로직 -----
def start_treasure_game():
    global treasure, game_active
    print("Treasure game started!")
    treasure_position = random.choice(brick_positions)
    move = current_round > 1  # 2라운드부터 보물이 움직임
    treasure = Treasure(position=treasure_position, move=move)
    game_active = True

def start_monster_game():
    global game_active, monster, treasure
    print("Monster game started!")
    if current_round == 3:
        monster.activate(treasure)  # 3라운드에서는 보물을 추적
    else:
        monster.activate(player)  # 이전 라운드에서는 플레이어 추적
    game_active = True

def start_round():
    global treasure, monster, current_round, time_left, game_active
    if current_round > max_rounds:
        end_game("You completed all rounds!")
        return

    time_left = round_time
    print(f"Starting round {current_round}")

    # 새 맵 생성
    generate_random_map()

    # 라운드 설정
    if current_round == 0:  # 0라운드: 괴물 추적
        start_monster_game()
    elif current_round == 1:  # 첫 번째 라운드: 정적 보물
        start_treasure_game()
    elif current_round == 2:  # 두 번째 라운드: 움직이는 보물
        start_treasure_game()
    elif current_round == 3:  # 세 번째 라운드: 움직이는 보물 + 보물을 추적하는 괴물
        start_treasure_game()
        start_monster_game()

def end_round():
    global current_round, game_active
    print(f"Round {current_round} complete!")
    Text(text=f"Round {current_round} Complete!", origin=(0, 0), scale=2, color=color.gold, duration=2)
    current_round += 1
    game_active = False
    invoke(start_round, delay=2)

def end_game(reason):
    print(f"Game Over! {reason}")
    Text(text=f"Game Over! {reason}", origin=(0, 0), scale=2, color=color.red, duration=3)
    invoke(application.quit, delay=3)

# ----- 입력 처리 -----
def input(key):
    global bricks, game_active

    if key == 'left mouse down':  # 괴물 또는 보물 클릭
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            if isinstance(hit_info.entity, Monster) and game_active:
                hit_info.entity.take_damage(25)  # 괴물에게 데미지
            elif isinstance(hit_info.entity, Treasure) and game_active:
                print("Treasure collected!")
                destroy(hit_info.entity)
                end_round()
            elif hit_info.entity in bricks:  # 벽돌 제거
                bricks.remove(hit_info.entity)
                destroy(hit_info.entity)
                remove_block_sound.play()

    elif key == 'right mouse down':  # 벽돌 생성
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            position = hit_info.entity.position + hit_info.normal
            if position not in [brick.position for brick in bricks]:  # 중복 방지
                new_brick = create_brick(position, color=color.azure)
                place_block_sound.play()

# ----- 업데이트 ----- 
def update():
    global treasure, game_active

    if current_round <= max_rounds:
        update_timer()

    if treasure and game_active:
        treasure.update()

    if monster and monster.enabled and monster.active and game_active:
        monster.update()

# ----- 게임 시작 -----
start_round()

app.run()
