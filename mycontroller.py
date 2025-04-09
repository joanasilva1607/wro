from pyPS4Controller.controller import Controller
from cmps12 import CMPS12

from motor import Motor
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

        m1.on()
        m2.off()
        m_pwm.value = value

    def on_triangle_press(self):
        self.angle_offset = CMPS12.bearing3599() + 270
                       
        max_offset = 40
        diff = SERVO.center - SERVO.min
        margin = 0.5

        Motor.forward(0.5)

        while True:
            current_bearing = self.GetAngle()

            if current_bearing > (180 - margin) and current_bearing < (180 + margin):
                Motor.stop()
                SERVO.set_angle(SERVO.center)
                break

            if current_bearing < 180:
                offset = 180 - current_bearing

                if offset > max_offset:
                    offset = max_offset

                angle = int(SERVO.center + (offset / max_offset) * diff)
                
                SERVO.set_angle(angle)
                
            if current_bearing > 180:
                offset = current_bearing - 180


                angle = int(SERVO.center - (offset / max_offset) * diff)
                SERVO.set_angle(angle)

        print("Angle: ", self.GetAngle())
        
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