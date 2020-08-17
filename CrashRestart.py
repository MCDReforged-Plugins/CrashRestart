import json
import time
import os

CONFIG_FILE = os.path.join('config', 'CrashRestart.json')

# MAXIMUM: 3 crashes within 5min
config = {
	"MAX_COUNT": 3,
	"COUNTING_TIME": 300
}
default_config = config.copy()

counter = None
count_start_time = None


def on_server_stop(server, return_code):
	global counter, count_start_time
	if return_code == 0:
		return
	max_count = config['MAX_COUNT']
	counting_time = config['COUNTING_TIME']
	server.logger.info('Seems like a crash has happened since the return code of the server is {}'.format(return_code))
	current_time = time.time()
	if count_start_time is not None and current_time - count_start_time <= counting_time:
		counter += 1
		if counter > max_count:
			server.logger.info('No restart this time due to maximum allowed crashes ({}) in {} seconds exceeded'.format(max_count, counting_time))
			return
	else:
		count_start_time = time.time()
		counter = 1
	server.logger.info('Restarting the server, crash counter: {}/{}'.format(counter, max_count))
	server.start()


def on_load(server, old):
	global counter, count_start_time
	if old is not None:
		counter = old.counter
		count_start_time = old.count_start_time

	global config
	try:
		with open(CONFIG_FILE) as file:
			js = json.load(file)
		for key in config.keys():
			config[key] = js[key]
	except:
		server.logger.info('fail to read config file, using default value')
		config = default_config
		with open(CONFIG_FILE, 'w') as file:
			json.dump(config, file, indent=4)

	server.logger.info('Config info: {}'.format(config))
