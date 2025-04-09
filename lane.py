class Lane():
	def __init__(self):
		self.initial_traffic = LaneTraffic.Unkown
		self.final_traffic = LaneTraffic.Unkown

class LaneTraffic:
	Unkown = 0
	Inside = 1
	Outside = 2