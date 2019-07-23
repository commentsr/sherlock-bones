import os
import json

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


def read_logs(bot):
	logs_dir = os.path.join(bot.root_dir, "logs")
	logs = {}
	for filename in os.listdir(logs_dir):
		logs[filename] = []
		file = open(os.path.join(bot.root_dir, "logs", filename), "r")
		for line in file.readlines():
			logs[filename].append(json.loads(line))
	return logs
