
import random
from random import uniform
from ursina import *

app = Ursina()





#cube = Entity(model='cube', color=color.orange) 








custom_font = 'font/BMHANNAPro.ttf'  # 한글 폰트 파일 이름
Text.default_font = custom_font



# ----- 전역 변수 -----
game_state = 'menu'  # 초기 상태: 메인 메뉴
menu_entities = []  # 메인 메뉴 엔티티 리스트
game_entities = []  # 게임 화면 엔티티 리스트

# ----- 메인 메뉴 화면 -----
crosshair = None
def create_crosshair():
    """화면 중앙에 크로스헤어를 생성"""
    crosshair = Entity(
        parent=camera.ui,
        model='quad',
        color=color.red,
        scale=(0.01, 0.01),  # 크기 조정
        position=(0, 0)  # 화면 중앙에 위치
    )
    return crosshair


def setup_main_menu(round):
    """메인 메뉴 화면 생성"""
    global menu_entities

    for entity in menu_entities:
        destroy(entity)
    menu_entities = []

    # 검정 배경
    menu_background = Entity(parent=camera.ui, model='quad', scale=(2, 1), color=color.hex('#848484'), z=0)
    menu_entities.append(menu_background)

    # "게임 시작" 버튼
    
    start_button = Button(
        parent=camera.ui,
        text="게임시작",
        color=color.white,
        text_color=color.black,
        scale=(0.3, 0.1),
        position=(0, 0.1),
        on_click=lambda: set_game_state('game'),
        z=-2
    )
    menu_entities.append(start_button)

    # "게임 설명" 버튼
    instructions_button = Button(
        parent=camera.ui,
        text="게임설명",
        color=color.white,
        text_color=color.black,
        scale=(0.3, 0.1),
        position=(0, -0.1),
        on_click=show_game_instructions,
        z=-2
    )
    menu_entities.append(instructions_button)

    # "게임 종료" 버튼 추가
    quit_button = Button(
        parent=camera.ui,
        text="게임 종료",
        color=color.white,
        text_color=color.black,
        scale=(0.3, 0.1),
        position=(0, -0.3),  # 위치 조정
        on_click=exit_game,
        z=-2
    )
    menu_entities.append(quit_button)


def exit_game():
    """게임 종료 함수"""
    print("게임이 종료되었습니다.")
    application.quit()  # 게임 종료


def show_game_instructions():
    # 배경을 위한 사각형 Entity 생성
    background = Entity(
        parent=camera.ui,
        model='quad',
        scale=(1, 0.5),  # 배경 크기 조정
        color=color.hex('#69AEAD'),
        position=(0, 0),  # 텍스트와 같은 위치에 배치
        z=-3
    )
    
    # 텍스트 객체 생성
    instructions_text = Text(
        parent=camera.ui,
        text="1. W/A/S/D 키로 이동\n2. 마우스 왼쪽 클릭 시, 블럭 제거/총 쏘기 가능\n3. 제한 시간 내 목표를 달성하세요!\n\n  - 1라운드: 몬스터 죽이기\n  - 2라운드: 블럭을 제거해 보물 찾기\n  - 3라운드: 움직이는 보물 잡기\n  - 4라운드: 몬스터보다 빨리 보물 잡기",
        origin=(0, 0),
        scale=2,
        color=color.white,
        z=-4
    )


    # 5초 후에 텍스트와 배경을 삭제
    invoke(destroy, instructions_text, delay=5)
    invoke(destroy, background, delay=5)


# ----- FPS 컨트롤러 구현 -----
class CustomFPSController(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = 5  # 이동 속도
        self.rotation_speed = 40  # 회전 속도
        self.camera_pivot = Entity(parent=self, y=1.5)  # 카메라 회전 축
        camera.parent = self.camera_pivot
        camera.position = (0, 1.5, 0)
        camera.rotation = (0, 0, 0)
        mouse.locked = False  # 초기화 시 마우스 잠금 해제
        mouse.visible = True  # 초기화 시 마우스 표시
        self.disable()  # 초기화 후 비활성화

    def update(self):
        """플레이어 업데이트: 이동 및 회전"""
        if not self.enabled:
            return  # 비활성화 상태에서는 아무 동작도 하지 않음

        self.rotation_y += mouse.velocity[0] * self.rotation_speed
        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.rotation_speed
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        move = Vec3(
            self.forward * (held_keys['w'] - held_keys['s']) +
            self.right * (held_keys['d'] - held_keys['a'])
        ).normalized() * self.speed * time.dt
        self.position += move

    def enable(self):
        """플레이어 활성화"""
        super().enable()
        mouse.locked = True  # 마우스 잠금
        mouse.visible = False  # 마우스 숨기기

    def disable(self):
        """플레이어 비활성화"""
        super().disable()
        mouse.locked = False  # 마우스 잠금 해제
        mouse.visible = True  # 마우스 보이기

# ----- 게임 화면 -----
def setup_game_screen():
    """게임 화면 생성"""
    global game_entities, sky

    # 땅
    ground = Entity(
    model='plane',
    collider='box',
    scale=64,
    
    color=color.rgb(78, 52, 25)  # 어두운 갈색 (RGB 값)
)
    game_entities.append(ground)

    # 하늘
    sky = Sky(
          # 텍스처 반복 설정
    color=color.rgb(0, 0, 100)   # 어두운 남색 (RGB 값)
)       # 텍스처를 제대로 보이게 하기 위해 흰색 설정
  # 어두운 파란색 하늘
    game_entities.append(sky)

    # 조명 추가 (필요하다면)
    directional_light = Entity(
    light=DirectionalLight(),
    rotation=(45, -45, 0),
    color=color.rgb(200, 200, 200)  # 약간 밝은 조명
)
    game_entities.append(directional_light)

    # FPS 컨트롤러
    player = CustomFPSController()
    game_entities.append(player)

    crosshair = create_crosshair()
    game_entities.append(crosshair)

    for entity in game_entities:
        entity.disable()



# ----- 상태 전환 -----
def set_game_state(new_state):
    """게임 상태를 변경"""
    global game_state, player, current_round, time_left, game_active, treasure, monster

    game_state = new_state

    if game_state == 'menu':
        for entity in menu_entities:
            entity.enable()
        for entity in game_entities:
            entity.disable()

        # 카메라 UI 설정 (2D 모드)
        camera.parent = None
        camera.position = (0, 0, -10)
        camera.rotation = (0, 0, 0)
        mouse.locked = False
        mouse.visible = True

        # 크로스헤어 숨기기
        if crosshair:
            crosshair.disable()

    elif game_state == 'game':
        # 게임 초기화
        global round_time
        round_time = 30  # 각 라운드의 기본 시간
        current_round = 0
        time_left = round_time  # 타이머 리셋
        game_active = True

        # 기존 엔티티 초기화
        for entity in menu_entities:
            entity.disable()
        for entity in game_entities:
            entity.enable()

        # 플레이어 초기화
        if player:
            player.enable()
            camera.parent = player.camera_pivot
            camera.position = (0, 1.5, 0)
            camera.rotation = (0, 0, 0)

        # 크로스헤어 표시
        if crosshair:
            crosshair.enable()

        # 첫 라운드 시작
        start_round()




# # ----- 마우스 설정 -----
# def show_mouse():
#     from panda3d.core import WindowProperties
#     wp = WindowProperties()
#     wp.setCursorHidden(False)
#     wp.setMouseMode(WindowProperties.M_absolute)
#     base.win.requestProperties(wp)

# def hide_mouse():
#     from panda3d.core import WindowProperties
#     wp = WindowProperties()
#     wp.setCursorHidden(True)
#     wp.setMouseMode(WindowProperties.M_relative)
#     base.win.requestProperties(wp)


# ----- 초기화 -----
setup_main_menu(0)
setup_game_screen()
set_game_state('menu')

# ----- 업데이트 -----
def update():
    pass



bricks = []
brick_positions = []





# ----- 사운드 설정 -----
remove_block_sound = Audio('/sound/destroy_block.mp3', autoplay=False)
gun_sound = Audio('/sound/gun.mp3', autoplay=False)
died_monster_sound = Audio('/sound/destroy_monster.wav', autoplay=False)




# ----- 플레이어 설정 -----
class Player(CustomFPSController):
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

# ----- 총 엔티티 생성 -----
gun = Entity(
    model='cube',
    parent=camera,
    position=(.5, -.25, .25),
    scale=(.3, .2, 1),
    origin_z=-.5,
    color=color.red,
    on_cooldown=False
)
gun.muzzle_flash = Entity(
    parent=gun,
    z=1,
    world_scale=.5,
    model='quad',
    color=color.yellow,
    enabled=False
)

shootables_parent = Entity()  # 총알로 맞출 수 있는 대상의 부모 엔티티




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
            create_brick(pos, color=color.rgb(0, 80, 0))

def create_brick(position, color=color.rgb(0, 80, 0)):
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
            model='stone_monster/Stone(28).obj',
            scale=(0.5, 0.5, 0.5),
            collider='box',
            **kwargs
        )
        self.hp = 3
        self.speed = 1
        self.target = target
        self.active = False
        self.destroyed = False
        self.attacking = False  # 공격 중인지 상태 플래그
        self.attack_distance = 2  # 공격 거리

    

    def update(self):
        if not self.active or self.destroyed or not self.target or not self.target.enabled:
            return

        # 추적 대상 바라보기
        self.look_at(self.target.position)
        self.position += self.forward * time.dt * self.speed

        

        # 높이 제한: 괴물이 바닥 아래로 내려가지 않도록
        if self.position.y < 0:
            self.position.y = 30

        # 플레이어를 추적할 때 거리 계산
        if isinstance(self.target, Player) and distance(self.position, self.target.position) < self.attack_distance:
            self.attack_player()

        # 보석 추적
        elif isinstance(self.target, Treasure) and distance(self.position, self.target.position) < 1:
            end_game("The monster caught the treasure!")
    
    def attack_player(self):
        """플레이어에게 일정 간격으로 데미지를 입힘"""
        if not self.attacking:  # 이미 공격 중이 아니면 실행
            self.attacking = True
            self.target.take_damage()  # 플레이어 HP 감소
            invoke(self.reset_attack, delay=1)  # 1초 후 다시 공격 가능하도록 설정
    def reset_attack(self):
        """공격 쿨타임 초기화"""
        self.attacking = False

    def apply_damage_to_player(self):
        """1초마다 플레이어에게 데미지를 가함"""
        if self.destroyed or not self.enabled:  # 삭제된 경우 종료
            self.attacking = False
            return

        if distance(self.position, self.target.position) < self.attack_distance:
            self.target.take_damage()  # 플레이어 HP 감소
            if self.target.hp > 0:
                invoke(self.apply_damage_to_player, delay=1)  # 1초 후 다시 실행
        else:
            self.attacking = False  # 플레이어와의 거리가 멀어지면 공격 중단

    def take_damage(self, damage):
        """몬스터가 피해를 입음"""
        if self.destroyed:
            return

        self.hp -= damage
        print(f"Monster HP: {self.hp}")

        if self.hp <= 0:
            print("Monster defeated!")
            self.destroyed = True
            destroy(self)
            if current_round == 0:
                end_round()

    def destroy_monster(self):
        """괴물을 제거하는 메서드"""
        self.destroyed = True  # 삭제 상태로 설정
        self.active = False
        self.enabled = False
        destroy(self)  # 실제로 엔티티 제거
        if current_round == 0:  # 첫 라운드에서 괴물이 죽었을 때
            end_round()  # 라운드 종료

    def reset_position(self):
        """괴물 위치를 맵 경계 내에서 랜덤 초기화"""
        if not self.destroyed:
            # 맵 크기 기준으로 X, Z 위치를 랜덤으로 생성
            self.position = Vec3(
                uniform(0, 30),  # X 범위
                uniform(0,30),                # Y 고정 높이
                uniform(0, 30)  # Z 범위
            )

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



monster = Monster(position=(10, 1, 10), enabled=False, parent=shootables_parent)


# ------ 총 발사 ------
def shoot():
    """총 발사 로직"""
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        gun_sound.play()  # 총소리 재생

        # 크로스헤어 위치에 있는 엔티티 감지
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            if isinstance(hit_info.entity, Monster):
                hit_info.entity.take_damage(1)  # 몬스터에게 데미지
                print("Shot the monster!")

        invoke(gun.muzzle_flash.disable, delay=0.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=0.15)





def update():
    if game_active:
        update_timer()

    if held_keys['left mouse']:
        shoot()

    if monster.active:
        monster.look_at(player.position)
        monster.position += monster.forward * time.dt * monster.speed



# ----- 보물 설정 -----
class Treasure(Entity):
    def __init__(self, move=False, **kwargs):
        super().__init__(
            model='cube',
            texture='gold.jpg',
            #color=color.gold,
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
max_rounds = 4
time_left = round_time
game_active = False

# ----- 타이머 ----- 
timer_text = Text(text=f'Time Left: {int(time_left)}', position=(-0.5, 0.4), scale=2)

def update_timer():
    global time_left, game_active

    if not game_active:
        return

    time_left -= time.dt
    timer_text.text = f"Time Left: {int(time_left)}"

    if time_left <= 0:
        end_round()


def end_round():
    """현재 라운드를 종료하고 다음 라운드로 이동"""
    global current_round, game_active

    print(f"Round {current_round + 1} complete!")  # 라운드는 0부터 시작하므로 +1
    game_active = False

    # 라운드 완료 메시지
    round_complete_text = Text(
        text=f"Round {current_round } Complete!",
        origin=(0, 0),
        scale=2,
        color=color.gold
    )

    # 메시지 삭제 후 다음 라운드로 이동
    def next_round():
        global current_round  # 전역 변수 사용
        destroy(round_complete_text)
        if current_round < max_rounds - 1:  # 3라운드(0, 1, 2)까지만
            current_round += 1
            start_round()  # 다음 라운드 시작
        else:
            end_game("Congratulations! You've completed all rounds!")  # 모든 라운드 종료

    invoke(next_round, delay=2)




def proceed_to_next_round():
    """다음 라운드로 설정"""
    global current_round, game_active

    current_round += 1

    # 모든 라운드를 완료했을 경우 게임 종료
    if current_round > max_rounds:
        end_game("Congratulations! You've completed all rounds!")
    else:
        start_round()  # 다음 라운드 시작






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
        monster.activate(treasure, speed=0.3)  # 보물을 추적
    elif current_round == 0:
        monster.activate(player, speed=1)  # 다른 라운드: 플레이어를 추적
    game_active = True

def start_round():
    """새로운 라운드 시작"""
    global current_round, treasure, monster, game_active, time_left, round_time

    print(f"Starting round {current_round}")
    game_active = True
    time_left = round_time  # 라운드 시작 시 타이머 리셋

    # 기존 보물 및 몬스터 제거
    if treasure:
        destroy(treasure)
    if monster:
        destroy(monster)

    # 새 맵 생성
    generate_random_map()

    # 라운드에 따라 설정
    if current_round == 0:
        # 라운드 0: 괴물이 플레이어를 추적
        monster = Monster(target=player, position=random.choice(brick_positions), enabled=True)
        monster.active = True
    elif current_round == 1:
        # 라운드 1: 보물이 고정된 상태
        treasure = Treasure(position=random.choice(brick_positions), move=False)
    elif current_round == 2:
        # 라운드 2: 보물이 움직이는 상태
        treasure = Treasure(position=random.choice(brick_positions), move=True)
    elif current_round == 3:
        # 라운드 3: 괴물이 보물을 추적
        treasure_pos = random.choice(brick_positions)
        treasure = Treasure(position=treasure_pos, move=True)

        # 몬스터 등장
        possible_positions = [pos for pos in brick_positions if distance(pos, treasure_pos) > 10]
        monster_pos = random.choice(possible_positions) if possible_positions else Vec3(0, 1, 0)
        monster = Monster(target=treasure, position=monster_pos, enabled=True)
        monster.active = True
        print("Monster has spawned and is targeting the treasure!")

    # 라운드 시작 메시지
    round_start_text = Text(
        text=f"Round {current_round } Start!",
        origin=(0, 0),
        scale=2,
        color=color.yellow
    )

    # 메시지 삭제
    invoke(destroy, round_start_text, delay=2)









def end_game(reason):
    print(f"Game Over! {reason}")
    Text(text=f"Game Over! {reason}", origin=(0, 0), scale=2, color=color.red, duration=3)
    invoke(application.quit, delay=3)



# ----- 입력 처리 -----
def input(key):
    global bricks, game_active

    # UI 요소를 클릭했을 때 게임 로직 무시
    if key == 'left mouse down':
        if mouse.hovered_entity and isinstance(mouse.hovered_entity, Button):
            print(f"UI Button clicked: {mouse.hovered_entity.text}")
            return  # UI 버튼을 클릭했으면 게임 로직 실행하지 않음

        # 게임 내 Raycast 로직
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        print(f"Raycast hit: {hit_info.entity}")  # 디버깅 로그
        if hit_info.hit:
            # 몬스터 클릭
            if isinstance(hit_info.entity, Monster) and game_active:
                hit_info.entity.take_damage(1)  # 괴물에게 데미지
            # 보물 클릭
            elif isinstance(hit_info.entity, Treasure) and game_active:
                print("Treasure collected!")
                destroy(hit_info.entity)
                end_round()
            # 벽돌 제거
            elif hit_info.entity in bricks:
                print("Brick destroyed!")
                remove_block_sound.play()
                bricks.remove(hit_info.entity)
                destroy(hit_info.entity)
            else:
                shoot()  # 다른 경우는 슈팅 동작

    # 벽돌 생성
    elif key == 'right mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            position = hit_info.entity.position + hit_info.normal
            if position not in [brick.position for brick in bricks]:  # 중복 방지
                new_brick = create_brick(position, color=color.azure)

    # 편집 모드 전환
    elif key == 'tab':
        pause_input(key)



def pause_input(key):
    """편집 모드 전환 및 UI 상태 제어"""
    if key == 'tab':  # tab 키를 누르면 편집 모드 전환
        editor_camera.enabled = not editor_camera.enabled  # 편집 모드 활성화 / 비활성화

        # 편집 모드에 따른 상태 변화
        player.visible_self = not editor_camera.enabled  # 편집 모드에서는 플레이어 숨기기
        mouse.enabled = not editor_camera.enabled  # 편집 모드에서는 마우스를 숨기지 않음
        mouse.locked = not editor_camera.enabled  # 편집 모드에서는 마우스 잠금 해제
        editor_camera.position = player.position  # 편집 모드에서 카메라 위치를 플레이어 위치로 설정

        # 편집 모드일 때 UI 요소를 계속 보여주기
        if editor_camera.enabled:
            setup_main_menu(current_round)  # 편집 모드에서 메인 메뉴 UI 표시

        if not editor_camera.enabled:
            mouse.locked = True  # 게임 모드로 돌아가면 마우스를 잠금


# ----- 업데이트 ----- 
def update():
    if game_active:
        if treasure and treasure.enabled:  # 보물이 활성화된 경우만 업데이트
            treasure.update()

    if monster and not monster.destroyed and monster.active:
        monster.update()  # 삭제되지 않은 상태에서만 업데이트 호출

    if current_round <= max_rounds:
        update_timer()


# ----- 게임 시작 -----

editor_camera = EditorCamera(enabled=False)  # EditorCamera 정의


app.run()