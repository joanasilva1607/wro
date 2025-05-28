
class LaneTraffic:
	Unkown = 0
	Inside = 1
	Outside = 2

class Lane():
	def __init__(self, initial = LaneTraffic.Unkown, final = LaneTraffic.Unkown):
		self.initial = initial
		self.final = final