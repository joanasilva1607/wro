
# The Team

## Joana Silva

Age: 18
High School: Madeira Torres, Torres Vedras, Lisboa, Portugal
Description: Hi, I'm Joana from Portugal and this is my fourth season of WRO. I've participated in this category before, but as I find it extremely challenging, there's always something to improve on. I've enjoyed challenges ever since I was little and this is another one that connects what I love: programming and robotics.


## Simão Freire

Age: 20
University: Instituito Superior de Engenharia de Lisboa, Lisboa, Portugal
Description: Hi! My name is Simão and ever since I was a kid, I've been interested in computers and how they work, that led me to the path of wanting to learn more about programming and so I joined the robotics club of my school. This will be my third season in WRO and I'm really looking forward to it!


## Rafael Teodoro

Age: 16
High School: Henriques Nogueira, Torres Vedras, Lisboa, Portugal
Description: Hi, my name is Rafael, I took part in WRO last year and I'm very excited to do it again. This category challenges us by making us think further to solve the obstacles to the final result.


## Tiago Severino (Coach)

Role: Coach
Description: I’m hardworking, goal-oriented young man. Challenges captivate me and the harder they are, the better. Overcoming limits gives me a special taste, realizing how far I can go. I’ve already taken part in robotics competitions and now I’m leading a team with the aim of teaching what I’ve learned from my experience. I believe that the only way to get where you want to go is to never stop trying and never give until up you reach the end goal.


[Team photo]

# The Challenge
The WRO 2025 Future Engineers - Self-Driving Cars challenge invites teams to plan, build and program a robotic vehicle capable of driving autonomously on a track that changes dynamically with each round, having to be prepared for any option. The competition consists of two races: the first “Open Challenge” where the objective is to complete three laps in the direction decided before the race and stop where it started and the second “Obstacle Challenge” where the vehicle must complete 3 laps while overcoming random obstacles depending on their color and successfully perform a precise parallel parking maneuver. Teams must integrate advanced robotics concepts such as computer vision, sensor fusion and kinematics, focusing on innovation and reliability.

This challenge puts all aspects of the engineering process into practice, including:
* Mobility management: Developing efficient mechanisms for moving vehicles.
* Obstacle handling: Defining strategies to detect and navigate traffic signs (red and green markers) within specified rules.
* Parking: Creating parallel parking strategies to meet all the requirements.
* Documentation: Present engineering progress, design decisions and open source collaboration via a public GitHub repository.
Points are awarded based on performance in the challenge rounds, the quality of the engineering documentation and the ability to create an innovative and robust solution. The aim is to inspire learning through real-world applications of robotics and teamwork to create creative problem-solving.


# Our Robot
![Robot Image](./v-photos/TheRobot.jpeg)

Our vídeo of the robot on youtube (hiperligação)


## Strategy
Our strategy for the WRO 2025 Future Engineers challenge is to strike a balance between speed and precision. For the Open Challenge, we rely on sonar sensors to detect the outer walls and a compass to maintain a stable trajectory and assist with turning corners accurately.

For the Obstacle Challenge, we use a combination of a camera, sonars, and the compass to detect traffic signs and obstacles, allowing the robot to navigate the course effectively. During the **first lap**, the robot will take a **slower, strategic turn** at the corners to give the camera time to identify upcoming obstacles. If an obstacle is detected early, it likely indicates a double-obstacle lane, else, it means the lane only has one obstacle. In the first case, the robot will bypass the first obstacle and perform an additional obstacle check in the middle of the lane to avoid collisions. In the second case, it will move forward until it leaves the corner section and then check for obstacles.

Once the robot completes the lane, it stores the obstacle positions in memory. This allows it to navigate more efficiently on the remaining laps, avoiding previously detected obstacles without needing to reprocess them.

For the parking maneuver, the robot uses the camera to detect the designated parking space and the compass to ensure accurate alignment. It is programmed to perform a precise parallel parking maneuver, meeting all the required criteria—stopping in the correct position and orientation.


## Components List

<table border="1" cellspacing="0" cellpadding="8">
  <thead>
    <tr>
      <th>Component</th><th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Raspberry Pi 5</td> <td>89.99€</td>
    </tr>
    <tr>
      <td>Raspberry Pi Pico</td> <td>4.99€</td>
    </tr>
    <tr>
      <td>Camera Module</td><td>35.99€</td>
    </tr>
    <tr>
      <td>Servo Motor</td><td>5.66€</td>
    </tr>
    <tr>
      <td>Sonar Sensor (x3)</td><td>0.50€ (each)</td>
    </tr>
    <tr>
      <td>Compass Module</td><td>39.99€</td>
    </tr>
    <tr>
      <td>Testing Board and components</td><td>10.00€</td>
    </tr>
    <tr>
      <td>Motor Driver</td><td>2.00€</td>
    </tr>
    <tr>
      <td>Battery Pack (Old laptop batteries)</td><td>$0.00</td>
    </tr>
    <tr>
      <td>Battery level sensor</td><td>$8.00</td>
    </tr>
    <tr>
      <td>3D Filament</td><td>20.00€</td>
    </tr>
</table>






## Mobility Management
The robot's mobility is managed by a combination of components, including  the powertrain (motor + drivetrain), steering system, and chassis. The size of the robot chassis was designed for optimal maneuverability, allowing it to make sharp turns and navigate tight spaces effectively. 


### Drivetrain

Our drivetrain consists of a diferential system that allows for the motor generated torque to be distributed to the wheels, enabling the wheels to rotate at different speeds for smoother cornering and the axles, which deliver power directly to the wheels

#### Motor

<table>
  <tr>
    <td width="50%" style="text-align: left;">
      <img src="./other/readme-images/drive-motor.jpg" alt="DC Motor" width="100%">
    </td>
    <td width="50%" style="text-align: left; vertical-align: top;">
      <h3>Specifications:</h3>
      <li>Voltage: 12V</li>
      <li>Gear Ratio: </li>
      <li>Speed: </li>
      <li>Torque: </li>
      <li>Weight: </li>
      </li>
    </td>
  </tr>
</table>

Where to find the motor: [Link](https://www.example.com)


### Steering Mechanism

For our steering system, we opted for a servo-actuated linkage steering system, similar to a simplified Ackermann steering setup. The two front wheels are mechanically linked via a connecting rod, and a servo motor controls their angle through a steering handle. This system allows precise and synchronized wheel steering, essential for stable turns during navigation and parking maneuvers.


add images of 3d file steering mechanism







