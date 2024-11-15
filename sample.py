import turtle

# Set up the screen
screen = turtle.Screen()
screen.bgcolor("white")
screen.title("Interactive Network Drawing")

# Create a turtle for drawing
drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)

# Store nodes as a list of (x, y) coordinates
nodes = []

# Function to handle user clicks for placing nodes
def place_node(x, y):
    drawer.penup()
    drawer.goto(x, y)
    drawer.pendown()
    drawer.dot(10, "black")  # Draw a node as a dot
    nodes.append((x, y))
    print(f"Node placed at ({x}, {y})")

# Function to draw edges between nodes (connects the last two nodes added)
def draw_edge(x, y):
    if len(nodes) >= 2:
        drawer.penup()
        drawer.goto(nodes[-2])
        drawer.pendown()
        drawer.goto(nodes[-1])
        print(f"Edge drawn from {nodes[-2]} to {nodes[-1]}")

# Bind mouse click to place nodes and draw edges
screen.onclick(place_node)  # Left click places a node
screen.onclick(draw_edge, btn=3)  # Right click connects the last two nodes with an edge

# Close the window when clicked
screen.mainloop()
