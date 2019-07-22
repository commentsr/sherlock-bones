import os
import json

from .member import get_member

class data:
	pass


def read_data(bot):
	data_dir = os.path.join(bot.root_dir, "data")
	for filename in os.listdir(data_dir):
		file = open(os.path.join(bot.root_dir, "data", filename), "r")

		if filename.endswith(".json"):
			contents = json.load(file)
		else:
			contents = [line.rstrip() for line in file.readlines()]
		setattr(data, os.path.splitext(filename)[0], contents)

		file.close()
	return data
