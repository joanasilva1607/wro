import time
from pyPS4Controller.controller import Controller
from camera import Camera
from cmps12 import CMPS12

from motor import Motor
from robot import Robot
from servo import SERVO
from ultis import start_thread

speed = 0.7

class MyController(Controller):
    up = None

    def GetAngle(self):
        bear = CMPS12.bearing3599()

        bear -= self.angle_offset % 360.0

        if bear >= 360.0:
            bear -= 360.0
        elif bear <= 0:
            bear += 360.0

        return bear

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

        self.angle_offset = CMPS12.bearing3599() + 180

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

    def on_square_press(self):
        Robot.RotateAngle(-90)

    def on_x_press(self):
        Robot.RotateAngle(-90, reverse=True)

    def on_circle_press(self):
        Robot.RotateAngle(90)

    def on_triangle_press(self):
        Robot.RotateAngle(90, reverse=True)

    def on_square_release(self):
        return
    
    def on_x_release(self):
        return

    def on_circle_release(self):
        return
    
    def on_triangle_release(self):
        return
    

    def on_up_arrow_press(self):
        self.up = True
        start_thread(self.straight_move)

    def on_down_arrow_press(self):
        self.up = True
        start_thread(self.straight_move, args=[True] )

    def straight_move(self, reverse=False):
        self.angle_offset = CMPS12.bearing3599() + 180

        max_offset = 40
        diff = SERVO.center - SERVO.min

        if reverse:
            Motor.backward(0.5)
        else:
            Motor.forward(0.5)

        while self.up is not None:
            current_bearing = self.GetAngle()

            offset = current_bearing - 180

            # Clamp the offset
            if abs(offset) > max_offset:
                offset = max_offset if offset > 0 else -max_offset

            angle_adjustment = (offset / max_offset) * diff

            if reverse:
                angle_adjustment = -angle_adjustment

            angle = int(SERVO.center - angle_adjustment)
            SERVO.set_angle(angle)

            time.sleep(1/60)

    def on_L1_press(self):
        while True:
            Motor.forward(0.4)
            left_angle = Camera.left_wall[4] if Camera.left_wall is not None else 0
            right_angle = Camera.right_wall[4] if Camera.right_wall is not None else 0

            angle = 0

            if Camera.left_wall is not None and Camera.right_wall is not None:
                angle = -(left_angle + right_angle)
            else:
                if Camera.left_wall is not None:
                    angle = -((left_angle + 12))   
                elif Camera.right_wall is not None:
                    angle = -((right_angle - 12))
                else:
                    Motor.stop()
                    break

            SERVO.set_angle(SERVO.center + int(angle * 3))
            print(angle*3)

            time.sleep(1/120)
    
    def on_up_down_arrow_release(self):
        Motor.stop()
        self.up = None
        SERVO.set_angle(SERVO.center)
    
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