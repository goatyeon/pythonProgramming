*거북이 여러 마리 키우는 방법

=> 지금까지는 import turtle as t 를 통해 한마리의 거북이만 조작했었는데요,

      변수명 = t.Turtle() 함수를 통해 원하는 만큼 거북이를 늘릴 수 있습니다. 

      이번 게임에서는 ts (악당거북이) , t (주인공거북이), te(먹이) 총 세마리의 거북이가 등장하게 되고요.

​

*타이머 사용하기

=> 거북이 그래픽에는 일정 시간이 흐른 후에 정해진 함수를 실행하는 타이머 기능이 있으며,

      t.ontimer( 실행할 함수 , 정해진 시간 ) 을 통해 구현할 수 있습니다. 

      타이머는 일회성으로, 계속 함수를 수행토록 구현하기 위해선 반복문을 사용해야 합니다. 

      또한 시간의 단위가 1 / 1000초 이기 때문에, 1000으로 설정해야 1초가 됩니다.

​

*악당 거북이가 주인공 거북이를 쫒도록 설정하기

- 1.악당 거북이를 기준으로 주인공 거북이로 향하는 각도를 구합니다

   => ang = ts.towards(t.pos())    # 특정 방향으로 향하는 각도를 구하기 원할경우 towards 함수 사용.

   2.구한 각도에 맞춰 악당 거북이의 머리를 돌립니다

   => ts.setheading(ang)

   3. 악당 거북이를 앞으로 이동시킵니다.

​

1.등장인물을 만듭니다 (악당거북이, 주인공 거북이, 먹이) 

2.turn_으로 시작하는 함수작성하여 사용자가 키보드의 방향키를 눌렀을 때 원하는 방향으로 돌립니다.

3.play() 함수를 작성합니다. 주인공 거북이가 앞으로 이동하며, 악당 거북이가 주인공을 쫒아가고, 주인공 

   거북이가 악당/ 먹이에 닿았을 때의 처리를 모두 이 함수에서 처리.

4.playing변수, start() 함수. playing변수를 통해 게임이 실행 중인지, 대기중인지 구분하며 (True / False)

    start() 함수를 통해 사용자가 space 를 누르면 게임이 시작되도록 합니다. 

​

<소스>
```python
import turtle as t

import random

​

score = 0

playing = False

​

ts = t.Turtle()

ts.shape("turtle")

ts.color("red")

ts.speed(9)    # 악당 거북이의 속도를 9로 설정합니다    

ts.up()

ts.goto(0,200)

​

te = t.Turtle() 

te.shape("circle")

te.color("green")

te.speed(9)

te.up()

te.goto(0,-200)

​

def turn_right():

    t.setheading(0)

def turn_up():

    t.setheading(90)

def turn_left():

    t.setheading(180)

def turn_down():

    t.setheading(270)

​

def start():

    global playing    # playing 변수를 play()함수 밖에서도 사용할 수 있도록 global 지정해줌

    if playing == False:    # 게임이 대기중(False)인 상태이면 

        playing == True

        t.clear()    # 화면상의 메시지를 지웁니다

        play()    # t.play() -> 오류가 발생하여 play()로 수정 (2019.10.18)

​

def play():

    global score

    global playing

    t.forward(10)

    if random.randint(1,5) == 3:    # 악당 거북이가 항상 주인공을 따라오는 것이 아니라 20%의 확률로 따라옴

        ang = ts.towards(t.pos())     

        ts.setheading(ang)

    speed = score + 5   # 점수에 5를 더해서 속도를 올립니다. (점수가 높아질 수록 빨라짐)

    

    if speed > 15:

        speed = 15    # speed가 15를 넘지는 않도록 설정합니다.

    ts.forward(speed)

​

    if t.distance(ts) < 12:    # 주인공과 악당 사이의 거리가 12보다 작으면 게임을 종료합니다

        text =  "Score: " + str(score)

        message("Game Over",text)

        playing = False    # 게임을 종료할 수 있도록 playing = False 설정

        score = 0

    if t.distance(te) < 12:     # 주인공과 먹이 사이의 거리가 12보다 작으면 

        score = score + 1

        t.write(score)      # 점수를 화면에 표시합니다

        star_x = random randint(-230,230)    

        star_y = random randint(-230,230)

        te.goto(star_x,star_y)    # 먹이를 임의생성된 위치로 보냅니다

​

    ''' score = 5일 때 악당 거북이 한 마리를 추가합니다 ''' 

    if score == 5:

        ts2 = t.Turtle()

        ts2.shape("turtle")

        ts2.color("blue")

        ts2.speed(9)    # 악당 거북이의 속도를 9로 설정합니다    

        ts2.down()

        ts2.goto(0,100)

    

    if playing:     # if playing == True 와 같은 의미. 게임을 계속 이어갈 수 있게 해주는 중요한 if절

        t.ontimer(play,100)    # 게임 플레이 중이면 0.1초 후 play함수를 실행합니다. 

​

 

def message(m1,m2):

    t.clear()

    t.goto(0,100)

    t.write(m1,False,"center",("",20))

    t.goto(0,-100)

    t.write(m2,False,"center",("",15))

    t.home()

​

t.title("Turtle Run")

t.setup(50,50)    # 창의 크기를 50 x 50 으로 설정 (?)

t.bgcolor("black")

t.shape("turtle")

t.speed(9)

t.up()

t.color("white")

​

t.onkeypress(turn_right,"Right")

t.onkeypress(turn_up,"Up")

t.onkeypress(turn_left,"Left")

t.onkeypress(turn_down,"Down")

t.onkeypress(start,"space")    # space키는 소문자!

t.listen()
```
​

message("Turtle Run","[Space]")
[출처] 08.파이썬 프로젝트04 - 터틀런 게임 -|작성자 오리
