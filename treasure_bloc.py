# ### 초기 블럭 형태 구현

# - 보물이 숨겨져 있는 공간
# - 보물을 어디에 숨기도록 할지 → 랜덤?
# - 전체적인 style 설정 (블록의 색상 변환, 이미지 첨가 등)
# - 떨어지는 경우 고려
# - 질감 어두운 색

# +) 블럭을 설치하거나 제거할 때 소리나 이펙트가 생기도록 추가할 수 있을까?
#round 1) 보물 상자를 찾아라
#round 2) 보물 상자가 움직임
#round 3) 잠자고 있던 해적도 나를 쫓아옴 / 보물 상자 움직임
#마지막 3초 뒤에 꺼짐

# 주의할 것 : 괴물 한테 잡아먹히면 탈락 / 시간제한 안에 못들어오면 탈락
# -> 이전 단계에 문지기 역할을 하는 괴물들을 먼저 물리쳐야 함 -> 이후에 보물찾기 게임 시작


#위의 요구사항을 거의 다 적용시킴
#아쉬운 것 -> 해적 모형을 찾기 어려움, 보물상자,, 


from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

place_block_sound = Audio('plac_block.wav', autoplay=False)
remove_block_sound = Audio('block_remove.mp3', autoplay=False)
monster_alert_sound = Audio('monster.wav', autoplay=False)

# ----- 새로운 괴물 클래스 정의 -----
class Monster(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube',  # 박스 형태
            scale=(2, 2, 2),  # 박스 크기
            collider='box',  # 콜라이더 설정
            color=color.red,
            enabled=False,  # 시작 시 비활성화
            **kwargs
        )

# ----- 게임 설정 -----
round_time = 30  # 각 라운드 제한 시간
current_round = 1  # 시작 라운드
max_rounds = 3  # 최대 라운드 수
time_left = round_time
monster_sound_played = False

# ----- 게임 오브젝트 -----
treasure_chest = None
treasure_direction = Vec3(1, 0, 0)
treasure_speed = 2
boundary_min = Vec3(0, 0, 0)
boundary_max = Vec3(7, 0, 7)

# 괴물 생성 (시작 시 비활성화)
monster = Monster(position=(5, 1, 5))

# ----- 타이머 -----
timer_text = Text(text=f'Time Left: {int(time_left)}', position=(-0.5, 0.4), scale=2)

# ----- 캐릭터 -----
player = FirstPersonController(collider='box')  # 플레이어에 콜라이더 설정
player.y = 2

# ----- 블록 생성 -----
class Voxel(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='brick',
            color=color.hsv(0, 0, random.uniform(0.9, 1.0)),
            highlight_color=color.lime,
        )

voxels = []
for z in range(8):
    for x in range(8):
        voxel = Voxel(position=(x, 0, z))
        voxels.append(voxel)

# ----- 랜덤 블록 생성 -----
block_positions = set()  # 생성된 블록의 위치를 추적하기 위해 사용
for _ in range(8):  # 한 층에 랜덤으로 8개의 블록 생성
    x, z = random.randint(0, 7), random.randint(0, 7)
    position = (x, 1, z)  # y=1 층
    if position not in block_positions:  # 중복 방지
        voxel = Voxel(position=position)
        voxels.append(voxel)
        block_positions.add(position)  # 생성된 위치 저장

# ----- 하늘과 조명 -----
sky = Sky(texture='sky_sunset')  # 어두운 스카이박스 적용
sky.color = color.rgb(50, 50, 80)

DirectionalLight(parent=scene, y=2, z=-3, shadows=True)
AmbientLight(color=color.rgba(255, 255, 255, 0.3))

# ----- 게임 로직 -----
def start_round():
    global treasure_chest, treasure_speed, treasure_direction, time_left, current_round
    if current_round > max_rounds:
        end_game("You completed all rounds!")  # 게임 종료
        return

    print(f"Starting round {current_round}")
    time_left = round_time  # 라운드 타이머 초기화
    monster_sound_played = False
    # 기존 보물 상자 제거
    if treasure_chest:
        destroy(treasure_chest)

    # 새로운 보물 상자 생성
    treasure_position = random.choice(voxels).position
    treasure_chest = Entity(
        model='cube',
        texture='gold',
        color=color.gold,
        position=treasure_position,
        scale=0.8,
        collider='box',  # 보물에 콜라이더 설정
    )

    # 속도 증가 (라운드별)
    if current_round > 1:
        treasure_speed = 2 + (current_round - 1) * 0.5

    # 3라운드에 괴물 활성화
    if current_round == 3:
        monster.enabled = True  # 괴물 활성화

        print("The monster has awakened!")

def update_timer():
    global time_left
    time_left -= time.dt
    timer_text.text = f'Time Left: {int(time_left)}'
    if time_left <= 0:
        end_game("Time's up!")

def update():
    global treasure_direction, monster_sound_played

    # 타이머 업데이트
    update_timer()

    # 보물 상자 움직임 (2라운드 이상)
    if treasure_chest and current_round > 1:
        treasure_chest.position += treasure_direction * time.dt * treasure_speed

        # 경계 충돌 감지
        if treasure_chest.x < boundary_min.x or treasure_chest.x > boundary_max.x:
            treasure_direction.x *= -1
        if treasure_chest.z < boundary_min.z or treasure_chest.z > boundary_max.z:
            treasure_direction.z *= -1

    # 괴물 추격 (3라운드)
    if monster.enabled:
        monster.look_at(player.position)  # 괴물이 플레이어를 바라봄
        monster.position += monster.forward * time.dt * 2  # 괴물 속도

        if not monster_sound_played and distance(monster.position, player.position) < 10:
            monster_sound_played = True
            monster_alert_sound.play()  # 소리 재생
            
        # 괴물이 플레이어와 충돌하면 게임 종료
        if monster.intersects(player).hit:  # 충돌 확인
            end_game("The monster caught you!")

def end_round():
    global current_round
    print(f"Round {current_round} complete!")

    # 라운드 완료 메시지
    message = Text(
        text=f"Round {current_round} Complete!",
        origin=(0, 0),
        scale=2,
        color=color.gold,
        duration=2
    )

    # 다음 라운드 시작
    current_round += 1
    invoke(start_round, delay=2)

def end_game(reason):
    print(f"Game Over! {reason}")
    message = Text(
        text=f"Game Over! {reason}",
        origin=(0, 0),
        scale=2,
        color=color.red,
        duration=3
    )
    invoke(application.quit, delay=3)  # 3초 뒤 종료

# ----- 입력 처리 -----
def input(key):
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            if hit_info.entity == treasure_chest:  # 보물 선택
                print("Treasure selected!")  # 보물 선택 시 메시지 출력
                end_round()  # 라운드 진행
            else:  # 블록 선택 시 블록 설치
                Voxel(position=hit_info.entity.position + hit_info.normal)
                place_block_sound.play()
    if key == 'right mouse down' and mouse.hovered_entity:  # 블록 제거
        if mouse.hovered_entity != treasure_chest:  # 보물 상자는 제거되지 않음
            destroy(mouse.hovered_entity)
            remove_block_sound.play()
        else:
            print("Treasure cannot be removed!")  # 보물 제거 차단 메시지 출력

# ----- 게임 시작 -----
start_round()

app.run()
