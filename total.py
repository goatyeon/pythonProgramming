from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# ----- 사운드 설정 -----
# 오디오 파일 경로를 맞춰주세요. 없을 경우 주석 처리하거나 기본 효과음을 대체로 설정합니다.
# place_block_sound = Audio('plac_block.wav', autoplay=False)
# remove_block_sound = Audio('block_remove.mp3', autoplay=False)

# ----- 기본 설정 -----
ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4, 4))
Sky()

# ----- 플레이어 설정 -----
class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hp_icons = []  # HP 아이콘 리스트
        self.max_hp = 5  # 최대 HP
        self.hp = self.max_hp

        # HP 아이콘 생성
        for i in range(self.max_hp):
            icon = Entity(
                parent=camera.ui,
                model='quad',
                texture='white_cube',
                color=color.red,
                scale=(0.03, 0.03),
                position=(-0.75 + i * 0.05, 0.45)
            )
            self.hp_icons.append(icon)

        # HP 텍스트 생성
        self.hp_text = Text(
            text=f"HP: {self.hp}",
            position=(-0.7, 0.35),
            scale=2,
            color=color.white
        )

    def take_damage(self):
        """플레이어가 데미지를 받는 메서드"""
        if self.hp > 0:
            self.hp -= 1
            destroy(self.hp_icons.pop())  # HP 아이콘 제거
            self.hp_text.text = f"HP: {self.hp}"  # 텍스트 업데이트
            print(f"Player HP: {self.hp}")
            if self.hp <= 0:
                end_game("You were defeated by the monster!")




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
        self.hp = 3  # 괴물의 초기 HP
        self.speed = 1  # 기본 속도
        self.active = False
        self.target = target  # 추적할 목표 (보물 또는 플레이어)
        self.attacking = False  # 플레이어 공격 중인지 상태 플래그
        self.attack_distance = 1.5  # 플레이어와의 충돌 거리 기준
        self.destroyed = False  # 삭제 상태 추적

    def update(self):
        if not self.active or not self.enabled or self.destroyed or not self.target or not self.target.enabled:
            return  # 삭제되거나 비활성화된 상태에서는 update 실행하지 않음

        if not hasattr(self.target, "position"):  # 대상이 위치 속성을 가지는지 확인
            return

        self.look_at(self.target.position)  # 목표를 바라봄
        self.position += self.forward * time.dt * self.speed  # 목표를 향해 이동

        # 거리 기반 충돌 감지
        distance_to_target = distance(self.position, self.target.position)
        if self.target and isinstance(self.target, Player) and distance_to_target <= self.attack_distance:
            self.attack_player()
        elif self.target and isinstance(self.target, Treasure) and distance_to_target <= self.attack_distance:
            print("Monster caught the treasure!")
            end_game("The monster caught the treasure!")  # 게임 종료
    
    def attack_player(self):
        """플레이어를 공격"""
        if not self.attacking:  # 이미 공격 중이 아니면 실행
            self.attacking = True
            print("Monster started attacking the player.")  # 디버깅 로그
            self.apply_damage_to_player()  # 데미지 적용 시작

    def apply_damage_to_player(self):
        """1초마다 플레이어에게 데미지를 가함"""
        if self.destroyed or not self.enabled:  # 삭제된 경우 종료
            self.attacking = False
            return

        distance_to_player = distance(self.position, player.position)
        if distance_to_player <= self.attack_distance:  # 여전히 부딪힌 상태인지 확인
            player.take_damage()  # 플레이어 HP 감소
            if player.hp > 0:  # 플레이어가 살아있다면 1초 후 다시 데미지 적용
                invoke(self.apply_damage_to_player, delay=1)
        else:
            self.attacking = False  # 부딪힘이 끝나면 공격 중단
            print("Monster stopped attacking the player.")  # 디버깅 로그

    def take_damage(self, damage):
        if self.destroyed:
            return  # 이미 삭제된 경우 처리하지 않음
        self.hp -= damage
        print(f"Monster takes {damage} damage! Remaining HP: {self.hp}")
        if self.hp <= 0:
            print("Monster defeated!")
            self.active = False
            self.enabled = False
            self.destroy_monster()  # 괴물 제거 호출

    def destroy_monster(self):
        """괴물을 제거하는 메서드"""
        self.destroyed = True  # 삭제 상태로 설정
        self.active = False
        self.enabled = False
        destroy(self)  # 실제로 엔티티 제거
        if current_round == 0:  # 첫 라운드에서 괴물이 죽었을 때
            end_round()  # 라운드 종료

    def reset_position(self):
        """괴물 위치를 초기화"""
        if not self.destroyed:
            self.position = random.choice(brick_positions)

    def activate(self, target, speed=None):
        """괴물을 활성화"""
        self.enabled = True
        self.hp = 3  # 매 라운드 초기화
        self.active = True
        self.attacking = False  # 공격 중 상태 초기화
        self.target = target
        self.speed = speed if speed is not None else 1
        self.destroyed = False  # 삭제 상태 초기화
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
        if not self.enabled:
            return

        if self.move:  # 보물이 움직이는 경우
            self.position += self.direction * time.dt * self.speed

            # 맵 경계 제한: 보물이 맵을 벗어나지 않도록 조정
            if abs(self.position.x) > 30 or abs(self.position.z) > 30:
                self.direction *= -1  # 방향 반전

            # 벽돌 근처에서만 움직이도록 제한
            nearest_brick = min(brick_positions, key=lambda pos: distance(Vec3(pos), self.position))
            if distance(Vec3(nearest_brick), self.position) > 5:  # 벽돌에서 일정 거리 이내로 제한
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

def end_round():
    """현재 라운드를 종료하고 다음 라운드로 이동"""
    global current_round, game_active
    print(f"Round {current_round} complete!")
    Text(
        text=f"Round {current_round} Complete!",
        origin=(0, 0),
        scale=2,
        color=color.gold,
        duration=2
    )

    current_round += 1
    game_active = False

    # 다음 라운드 시작을 지연 호출
    if current_round <= max_rounds:
        invoke(start_round, delay=2)  # 2초 후 다음 라운드 시작
    else:
        end_game("You completed all rounds!")


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
    if not monster or not monster.enabled:
        monster = Monster(position=(10, 1, 10), enabled=True)

    # 라운드별 설정
    if current_round == 3:  # 마지막 라운드
        monster.activate(treasure, speed=0.5)  # 보물을 추적
    else:
        monster.activate(player, speed=1)  # 다른 라운드: 플레이어를 추적
    game_active = True

def start_round():
    global treasure, monster, current_round, time_left, game_active
    print(f"Starting round {current_round}")  # 디버깅 로그

    if current_round > max_rounds:
        end_game("You completed all rounds!")
        return

    time_left = round_time  # 라운드 시간 초기화

    # 새 맵 생성
    generate_random_map()

    # 라운드 설정
    if current_round == 0:  # 0라운드: 괴물이 플레이어를 추적
        start_monster_game()
    elif current_round == 1:  # 첫 번째 라운드: 정적 보물
        start_treasure_game()
    elif current_round == 2:  # 두 번째 라운드: 움직이는 보물
        start_treasure_game()
    elif current_round == 3:  # 세 번째 라운드: 움직이는 보물 + 보물을 추적하는 괴물
        start_treasure_game()
        start_monster_game()


def end_game(reason):
    print(f"Game Over! {reason}")
    Text(text=f"Game Over! {reason}", origin=(0, 0), scale=2, color=color.red, duration=3)
    invoke(application.quit, delay=3)

# ----- 입력 처리 -----
def input(key):
    global bricks, game_active

    if key == 'left mouse down':  # 괴물, 보물, 또는 벽돌 클릭
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        print(f"Raycast hit: {hit_info.entity}")  # 디버깅 로그
        if hit_info.hit:
            if isinstance(hit_info.entity, Monster) and game_active:
                hit_info.entity.take_damage(1)  # 괴물에게 데미지
            elif isinstance(hit_info.entity, Treasure) and game_active:
                print("Treasure collected!")
                destroy(hit_info.entity)
                end_round()
            elif hit_info.entity in bricks:  # 벽돌 제거
                print("Brick destroyed!")
                bricks.remove(hit_info.entity)
                destroy(hit_info.entity)

    elif key == 'right mouse down':  # 벽돌 생성
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            position = hit_info.entity.position + hit_info.normal
            if position not in [brick.position for brick in bricks]:  # 중복 방지
                new_brick = create_brick(position, color=color.azure)
                # place_block_sound.play()

# ----- 업데이트 ----- 
def update():
    if game_active and treasure:
        treasure.update()

    if monster and not monster.destroyed and monster.active:
        monster.update()  # 삭제되지 않은 상태에서만 업데이트 호출

    if current_round <= max_rounds:
        update_timer()

# ----- 게임 시작 -----
start_round()

editor_camera = EditorCamera(enabled=False)  # EditorCamera 정의

def pause_input(key):
    if key == 'tab':  # tab 키를 누르면 편집 모드 전환
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position  # 편집 모드에서 카메라 위치 조정

        if not editor_camera.enabled:
            mouse.locked = True  # 게임 모드로 돌아가면 마우스가 잠김

app.run()
