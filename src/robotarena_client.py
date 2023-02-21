import socket
import json
import base64
import os
import traceback

MAX_FILE_SIZE = 5242880

MOVE = 0
ATTACK = 1
TURN_LEFT = 2
TURN_RIGHT = 3

UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3

def json_to_grid(json_grid, grid_size):
	grid = [[None] * grid_size] * grid_size
	for robot in json.loads(json_grid):
		grid[robot["x"]][robot["y"]] = robot
	return grid

class Robot:
	
	def __init__(self, name):
		self.name = name
		self.grid_size = None
		self.client = None
		self.turn_callback = None
		self.image = None
	
	def get_name(self):
		return self.name
	
	def get_grid_size(self):
		return self.grid_size
	
	def set_turn(self, callback):
		self.turn_callback = callback
	
	def set_image(self, image_path):
		try:
			if os.path.getsize(image_path) > MAX_FILE_SIZE:
				print("Image file too big, using default image.\nMax file size is", MAX_FILE_SIZE, "bytes.")
				return
			with open(image_path, "rb") as image_file:
				self.image = base64.b64encode(image_file.read()).decode("utf-8")
		except Exception as e:
			print("Error while loading image!", e)
			self.client.close()
	
	def connect(self, ip, port):
		if self.client != None:
			print("Client already connected")
			return
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect((ip, port))
	
	def start(self):
		if self.client == None:
			print("Client is not connected")
			return
		if self.turn_callback == None:
			print("Turn callback is not set")
			return
		
		self.grid_size = int(self.client.recv(4096).decode("utf-8"))
		
		handshake_data = {
			"name": self.name,
			"image": self.image
		}
		
		self.client.send(json.dumps(handshake_data).encode("utf-8"))
		
		while True:
			try:
				grid = self.client.recv(4096).decode("utf-8")
				turn = self.turn_callback(json_to_grid(grid, self.grid_size))
				self.client.send(json.dumps(turn).encode("utf-8"))
			except Exception as e:
				traceback.print_exc()
				print("Connection lost!")
				self.client.close()
				break
	
	