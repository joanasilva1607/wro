import json
import logging
from time import sleep
from flask import Flask, Response, request
from flask_cors import CORS

from camera import Camera
from config import Config

app = Flask(__name__)
CORS(app)
log = logging.getLogger('werkzeug')
log.disabled = True


def feed(color=None):
	while True:
		sleep(1/20)

		yield (b'--frame\r\n'
			b'Content-Type: image/jpeg\r\n\r\n' +
			  ( Camera.get_frame(Camera.colors[color]["mask"]) if color is not None  else Camera.get_frame(Camera.im)) +
			b'\r\n')


@app.route('/video_feed')
def video_feed():
	color = request.args.get('color')
	if color is None:
		return Response(feed(), mimetype='multipart/x-mixed-replace; boundary=frame')
	else:
		return Response(feed(color=color), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/hsv')
def get_hsv():
	color = request.args.get('color')
	return json.dumps({
		'status': True,
		'hsv': Config.config["camera"]["colors"][color]
	})

@app.route('/hsv', methods=['POST'])
def set_hsv():
	color = request.args.get('color')
	data = request.json

	Config.config["camera"]["colors"][color] = {
		"lower": [data["h_min"], data["s_min"], data["v_min"]],
		"upper": [data["h_max"], data["s_max"], data["v_max"]]
	}

	return json.dumps({
		'status': True
	})


@app.route('/test')
def test():
	return "Hello World!"


@app.route('/reload')
def reset():
	Config.load_config()
	return json.dumps({
		'status': True,
	})

@app.route('/save')
def save():
	Config.save_config()
	return json.dumps({
		'status': True,
	})

def start_flask():
	app.run(host='0.0.0.0', port=5000)