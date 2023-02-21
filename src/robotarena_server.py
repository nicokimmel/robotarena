import time
import threading
import socket
import json
import random
import io
import os
import base64
import pygame

HOST = "127.0.0.1"
PORT = 5901
MAX_HANDSHAKE_SIZE = 5242880

GRID_SIZE = 20
BLOCK_SIZE = 40

WIDTH = GRID_SIZE * BLOCK_SIZE
HEIGHT = GRID_SIZE * BLOCK_SIZE

MOVE = 0
ATTACK = 1
TURN_LEFT = 2
TURN_RIGHT = 3

UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3

def recvall(client):
	try:
		data = b''
		while True:
			part = client.recv(MAX_HANDSHAKE_SIZE)
			data += part
			if len(part) < MAX_HANDSHAKE_SIZE:
				break
		return data
	except Exception as e:
		print("Error!", e)
		remove_client(client)
		return None

def cycle_turns():
	while True:
		for client in client_list:
			get_turn(client)
			if len(client_list) < 1:
				return
			time.sleep(1/len(client_list))

def get_turn(client):
	index = client_list.index(client)
	robot = robot_list[index]
	if not robot:
		return
	try:
		client.send(get_json_robot_list(robot).encode("utf-8"))
		turn = client.recv(4096).decode("utf-8")
		handle_turn(robot, json.loads(turn))
	except Exception as e:
		print("Error!", e)
		remove_client(client)

def get_json_robot_list(target):
	client_robot_list = []
	for robot in robot_list:
		if abs(robot["x"] - target["x"]) <= 3 and abs(robot["y"] - target["y"]) <= 3:
			client_robot_list.append(robot)
	return json.dumps(client_robot_list)

def get_robot(x, y):
	for robot in robot_list:
		if robot["x"] == x and robot["y"] == y:
			return robot
	return None

def remove_client(client):
	if client not in client_list:
		return
	index = client_list.index(client)
	client.close()
	client_list.remove(client)
	robot = robot_list[index]
	if not robot:
		return
	robot_list.remove(robot)

def remove_robot(robot):
	if robot not in robot_list:
		return
	index = robot_list.index(robot)
	robot_list.remove(robot)
	client = client_list[index]
	if not client:
		return
	client.close()
	client_list.remove(client)

def handle_turn(robot, turn):
	if turn == "":
		return
	if len(turn) < 0 or len(turn) > 2:
		return
	
	first_action = turn[0]
	if first_action == MOVE:
		robot_move(robot)
	elif first_action == ATTACK:
		robot_attack(robot)
	elif first_action == TURN_LEFT:
		robot_turn_left(robot)
	elif first_action == TURN_RIGHT:
		robot_turn_right(robot)
	else:
		return
	
	second_action = turn[1]
	if second_action == MOVE:
		robot_move(robot)
	elif second_action == ATTACK:
		robot_attack(robot)
	elif second_action == TURN_LEFT:
		robot_turn_left(robot)
	elif second_action == TURN_RIGHT:
		robot_turn_right(robot)
	else:
		return

def robot_move(robot):
	if robot["direction"] == UP:
		if robot["y"] > 0 and not get_robot(robot["x"], robot["y"] - 1):
			robot["y"] -= 1
	elif robot["direction"] == RIGHT:
		if robot["x"] < GRID_SIZE - 1 and not get_robot(robot["x"] + 1, robot["y"]):
			robot["x"] += 1
	elif robot["direction"] == DOWN:
		if robot["y"] < GRID_SIZE - 1 and not get_robot(robot["x"], robot["y"] + 1):
			robot["y"] += 1
	elif robot["direction"] == LEFT:
		if robot["x"] > 0 and not get_robot(robot["x"] - 1, robot["y"]):
			robot["x"] -= 1

def robot_attack(robot):
	if robot["direction"] == UP:
		target = get_robot(robot["x"], robot["y"] - 1)
		if target:
			remove_robot(target)
			print(robot["name"], "has been destroyed!")
	elif robot["direction"] == RIGHT:
		target = get_robot(robot["x"] + 1, robot["y"])
		if target:
			remove_robot(target)
			print(robot["name"], "has been destroyed!")
	elif robot["direction"] == DOWN:
		target = get_robot(robot["x"], robot["y"] + 1)
		if target:
			remove_robot(target)
			print(robot["name"], "has been destroyed!")
	elif robot["direction"] == LEFT:
		target = get_robot(robot["x"] - 1, robot["y"])
		if target:
			remove_robot(target)
			print(robot["name"], "has been destroyed!")

def robot_turn_left(robot):
	robot["direction"] = (robot["direction"] + 1) % 4

def robot_turn_right(robot):
	robot["direction"] = (robot["direction"] - 1) % 4

def load_random_image():
	surface = pygame.image.load(os.path.join("images", "robot" + str(random.randint(2, 15)) + ".png"))
	scaled_surface = pygame.transform.scale(surface, (BLOCK_SIZE, BLOCK_SIZE))
	return scaled_surface

def load_image_from_base64(base64_string):
	image = base64.b64decode(base64_string)
	surface = pygame.image.load(io.BytesIO(image))
	scaled_surface = pygame.transform.scale(surface, (BLOCK_SIZE, BLOCK_SIZE))
	return scaled_surface

def start_server():
	while not running:
		print("Server is running and listening ...")
		
		try:
			client, address = server.accept()
			print("connection is established with", str(address))
			client.send(str(GRID_SIZE).encode("utf-8"))
			handshake_data = json.loads(recvall(client).decode("utf-8"))
		except Exception as e:
			print("Error! Could not shake hands with client.", e)
			client.close()
			continue
		
		if not "name" in handshake_data or handshake_data["name"] == "":
			client.close()
			continue
		
		double_name = False
		for robot in robot_list:
			if handshake_data["name"] == robot["name"]:
				double_name = True
				break
		if double_name:
			client.close()
			print("Robot", handshake_data["name"], "already on server!")
			continue
		
		robot = {
			"name": handshake_data["name"],
			"direction": random.randint(0, 3),
			"x": random.randint(0, GRID_SIZE - 1),
			"y": random.randint(0, GRID_SIZE - 1),
		}
		
		if not "image" in handshake_data or not handshake_data["image"]:
			image_list[robot["name"]] = load_random_image()
		else:
			image_list[robot["name"]] = load_image_from_base64(handshake_data["image"])
		
		robot_list.append(robot)
		client_list.append(client)
		
		print("The name of this robot is", robot["name"])

def draw():
	pygame.init()
	pygame.display.set_caption("RobotArena Server")
	pygame.display.set_icon(load_random_image())
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	clock = pygame.time.Clock()
	
	font_15 = pygame.font.SysFont("Arial", 15)
	robotwars_surface = font_15.render("RobotArena Server", True, (255, 255, 255))
	font_30 = pygame.font.SysFont("Arial", 30)
	start_surface = font_30.render("START", True, (255, 255, 255))
	
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				os._exit(0)
			if event.type == pygame.MOUSEBUTTONDOWN:
				global running
				if not running:
					running = True
					threading.Thread(target=cycle_turns).start()
		
		screen.fill((0, 0, 0))
		
		screen.blit(robotwars_surface, (10, 10))
		for robot in robot_list:
			if robot["name"] not in image_list:
				image_list[robot["name"]] = load_random_image()
			rotated_image = pygame.transform.rotate(image_list[robot["name"]], robot["direction"] * 90)
			screen.blit(rotated_image, (robot["x"] * BLOCK_SIZE, robot["y"] * BLOCK_SIZE))
		if not running:
			screen.blit(start_surface, (WIDTH/2 - start_surface.get_width()/2, HEIGHT/2 - start_surface.get_height()/2))
		
		pygame.display.flip()
		clock.tick(60)

running = False

client_list = []
robot_list = []
image_list = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

threading.Thread(target=start_server).start()

draw()