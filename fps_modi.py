from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import random
import time

app = Ursina()

'''
<현재 문제점>
- 적을 처치했을 때 뜨는 메세지에 애니메이션을 주고 싶은데, 제대로 적용 안 됨
- 플레이어 체력이 0이 되었을 때, 화면이 그냥 꺼짐
- 적을 다 처치했거나, 플레이어 체력이 0이 되면 탭 키를 눌러 retry 버튼을 누르고,
다시 시작할 수 있도록 하고 싶은데 안됨.
- 버튼이 제대로 나오지 않음
- 탭 키를 다시 누르면 그냥 화면이 꺼짐


<추가해야 하는 것들>
- 3d 모델
- 효과음
'''


# 기본 설정
Entity.default_shader = lit_with_shadows_shader
ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4, 4))
Sky()

# 메시지를 표시하는 함수 (위로 올라가며 페이드 아웃)
message_list = []  # 메시지들을 저장할 리스트

def show_message(text, duration=2, color=color.white):
    # 새로운 메시지 텍스트 생성
    message = Text(text, color=color, origin=(0, 0), scale=1.5, position=(0, -0.4))
    message_list.append(message)  # 메시지 리스트에 추가

    # 메시지가 올라가고, 시간이 지나면 사라지도록 설정
    message.start_time = time.time()  # 메시지가 생성된 시간 기록
    message.duration = duration  # 메시지가 사라지는 시간 설정

def update():
    # 메시지가 위로 올라가고, 시간이 지나면 사라지도록 처리
    for message in message_list[:]:  # message_list에서 하나씩 순회
        time_elapsed = time.time() - message.start_time
        if time_elapsed < message.duration:
            # 메시지 위치 올리기 (y 축 방향으로 올라감)
            message.position = (message.position.x, message.position.y + 0.05, message.position.z)
            
            # 색상 복사 및 투명도 감소
            new_alpha = max(0, message.color.a - time.dt / message.duration)  # 투명도 점차 감소
            message.color = Color(message.color.r, message.color.g, message.color.b, new_alpha)
        else:
            # 시간이 지나면 메시지 삭제
            destroy(message)
            message_list.remove(message)  # 리스트에서 삭제

# 효과음 로드 (파일을 프로젝트에 추가해야 함)
hit_sound = Audio('hit.wav', autoplay=False)
attack_sound = Audio('attack.wav', autoplay=False)

# 플레이어 설정
class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hp = 100
        self.health_bar = Entity(parent=camera.ui, model='quad', color=color.red, scale=(0.3, 0.03), position=(-0.65, 0.45))
        self.health_text = Text(f'{self.hp} HP', position=(-0.75, 0.5), scale=1.2, color=color.white)

    def take_damage(self, damage):
        self.hp -= damage
        self.health_bar.scale_x = self.hp / 100 * 0.3
        self.health_text.text = f'{max(self.hp, 0)} HP'
        attack_sound.play()

        if self.hp <= 0:
            show_message("Game Over!", color=color.red)
            check_game_over()  # 게임 종료 후 리트라이 버튼 확인

        # 반동 효과
        self.position -= self.forward * 0.5

player = Player(model='cube', z=-10, color=color.orange, origin_y=-0.5, speed=8)

# 적 설정
class Enemy(Entity):
    def __init__(self, model='cube', **kwargs):
        super().__init__(
            model=model,
            scale=(1.5, 2, 1.5),
            collider='box',
            origin_y=-0.5,
            color=color.green,
            **kwargs
        )
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.health_text = Text(parent=self, text='100', y=1.5, x=0, color=color.white, origin=(0, 0))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance(self.position, player.position)
        if dist > 30:
            return

        self.look_at(player.position)
        if dist > 2:
            self.position += self.forward * time.dt * 2
        else:
            self.attack()

    def attack(self):
        if hasattr(self, 'last_attack_time') and time.time() - self.last_attack_time < 2:
            return
        self.last_attack_time = time.time()
        player.take_damage(10)

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        self.health_bar.world_scale_x = max(0, self.hp / self.max_hp * 1.5)
        self.health_text.text = f'{max(self.hp, 0)}'

        if self._hp <= 0:
            show_message("Enemy defeated!", color=color.yellow)
            destroy(self)
            check_game_over()  # 적이 죽을 때마다 게임 종료 여부 확인

# 적 리스트 선언
enemies = [Enemy(model='sphere', position=(5, 0, 5)), Enemy(model='sphere', position=(-5, 0, 5))]

# 총 및 발사 기능
gun = Entity(model='cube', parent=camera, position=(.5, -0.25, .25), scale=(.3, .2, 1), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

def shoot():
    if gun.on_cooldown:
        return

    # 총 발사
    gun.on_cooldown = True
    gun.muzzle_flash.enabled = True
    invoke(gun.muzzle_flash.disable, delay=0.05)
    invoke(setattr, gun, 'on_cooldown', False, delay=0.15)

    # 충돌 감지
    hit_info = raycast(camera.world_position, camera.forward, distance=50, ignore=(gun, player))
    if hit_info.hit:
        if hasattr(hit_info.entity, 'hp'):  # 적에게만 영향을 줌
            hit_info.entity.hp -= 25
            hit_info.entity.blink(color.red)
            show_message("Hit enemy!", color=color.green)

# 입력 처리
def update():
    # 총 발사
    if held_keys['left mouse']:
        shoot()

    # 마우스 시야 전환 유지
    if not mouse.locked:
        mouse.locked = True  # 항상 마우스 락 유지

    # 게임 종료 후 리트라이 버튼 체크
    check_game_over()

# 게임이 끝났을 때 리트라이 버튼을 화면에 표시
def show_retry_button():
    retry_button = Button(text="Retry", color=color.green, scale=(0.1, 0.1), position=(0, -0.2))
    retry_button.parent = camera.ui  # retry_button을 camera.ui에 배치
    retry_button.enabled = True  # 버튼 활성화
    retry_button.on_click = retry_game  # 버튼 클릭 시 게임 재시작

# 게임 종료 시 버튼을 표시하는 함수
def check_game_over():
    if len(enemies) == 0 or player.hp <= 0:  # 적이 모두 죽거나 플레이어 체력이 0일 때
        show_message("게임 종료! 리트라이를 눌러주세요.", duration=3, color=color.green)
        show_retry_button()  # 리트라이 버튼 표시

def retry_game():
    global enemies
    player.hp = 100
    player.health_bar.scale_x = 0.3
    player.health_text.text = f'{player.hp} HP'

    for enemy in enemies:
        destroy(enemy)  # 기존의 적을 모두 삭제
    enemies = [Enemy(model='sphere', position=(5, 0, 5)), Enemy(model='sphere', position=(-5, 0, 5))]  # 새로운 적 생성
    show_message("게임을 다시 시작합니다!", duration=2, color=color.blue)

# 편집 모드 전환 핸들러
editor_camera = EditorCamera(enabled=False)  # EditorCamera 정의

def pause_input(key):
    if key == 'tab':    # tab 키를 누르면 편집 모드 전환
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)  # 입력 핸들러 등록

app.run()
