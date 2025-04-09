from pyPS4Controller.controller import Controller
from cmps12 import CMPS12

from motor import Motor
from robot import Robot
from servo import SERVO

speed = 0.7

class MyController(Controller):
    def GetAngle(self):
        bear = CMPS12.bearing3599()

        bear -= self.angle_offset % 360.0

        if bear >= 360.0:
            bear -= 360.0
        elif bear <= 0:
            bear += 360.0

        print("Bear: ", bear)
        print("Offset: ", self.angle_offset)

        return bear

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

        self.angle_offset = CMPS12.bearing3599() + 180

    def on_x_press(self):
       Motor.forward(speed)

    def on_x_release(self):
        Motor.stop()

    def on_circle_press(self):
        Motor.backward(speed)

    def on_circle_release(self):
        Motor.stop()

    def on_left_arrow_press(self):
        SERVO.set_angle(SERVO.min)

    def on_right_arrow_press(self):
        SERVO.set_angle(SERVO.max)

    def on_left_right_arrow_release(self):
        SERVO.set_angle(SERVO.center)

    def on_R2_press(self, value):
        # Convert value from -30000 to 30000 to 0 to 1
        value = (value + 30000) / 60000

        if value < 0:
            value = 0

        if value > 1:
            value = 1

        Motor.forward(value)

    def on_R2_release(self):
        Motor.stop()

    def on_triangle_press(self):
        Robot.RotateAngle(90, reverse=True)


    def on_up_arrow_press(self):
        self.up = True

        self.angle_offset = CMPS12.bearing3599() + 270

        max_offset = 40
        diff = SERVO.center - SERVO.min

        Motor.forward(0.5)

        while self.up:
            current_bearing = self.GetAngle()

            offset = current_bearing - 180

            # Clamp the offset
            if abs(offset) > max_offset:
                offset = max_offset if offset > 0 else -max_offset

            angle_adjustment = (offset / max_offset) * diff
            angle = int(SERVO.center - angle_adjustment)
            SERVO.set_angle(angle)
    
    def on_up_down_arrow_release(self):
        Motor.stop()
        self.up = False  
    
    def on_R3_left(self, value):
        return
    
    def on_R3_up(self, value):
        return

    def on_R3_down(self, value):
        return

    def on_R3_left(self, value):
        return

    def on_R3_right(self, value):
        return

    def on_R3_y_at_rest(self):
        """R3 joystick is at rest after the joystick was moved and let go off"""
        return

    def on_R3_x_at_rest(self):
        """R3 joystick is at rest after the joystick was moved and let go off"""
        return

    def on_R3_press(self):
        """R3 joystick is clicked. This event is only detected when connecting without ds4drv"""
        return

    def on_R3_release(self):
        """R3 joystick is released after the click. This event is only detected when connecting without ds4drv"""
        return

    def on_L3_left(self, value):
        return
    
    def on_L3_up(self, value):
        return

    def on_L3_down(self, value):
        return

    def on_L3_left(self, value):
        return

    def on_L3_right(self, value):
        return

    def on_L3_y_at_rest(self):
        """R3 joystick is at rest after the joystick was moved and let go off"""
        return

    def on_L3_x_at_rest(self):
        """R3 joystick is at rest after the joystick was moved and let go off"""
        return

    def on_L3_press(self):
        """R3 joystick is clicked. This event is only detected when connecting without ds4drv"""
        return

    def on_L3_release(self):
        """R3 joystick is released after the click. This event is only detected when connecting without ds4drv"""
        return

def init_my_controller():
    controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
    # you can start listening before controller is paired, as long as you pair it within the timeout window
    controller.listen(timeout=60)