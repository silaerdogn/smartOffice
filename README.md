# Smart Office Security and Monitoring System
Hello there! We are a group of passionate engineers and developers who embarked on a journey to create an intelligent system that enhances the security and productivity of office spaces. That's how our "Smart Office Security and Monitoring System" project was born.

# Project Overview
The primary goal of our project is to ensure the safety of the office environment, improve employee comfort, and provide real-time insights to managers about the office. To achieve this, we utilized a Raspberry Pi as the central control unit and integrated various sensors, database connectivity, and cloud services to create a comprehensive solution.

# Project Components
Our system covers different areas and functions within the office:

# 1. Main Entrance Control
To gain access to the office, employees are required to enter a password using a keypad. The entered password is validated against the Amazon RDS database. If the password is correct, a green LED lights up, and a message "Welcome @name" is displayed on the LCD screen. If the password is incorrect, a red LED provides a visual alert. Upon successful authentication, the attendance tracking system is automatically triggered.

The code for the main entrance control can be found in the giris.py file. It handles the keypad input, database validation, and LCD display management. The db_operations.py file contains the necessary functions for database connectivity and operations.

# 2. Manager's Office Control
Access to the manager's office is controlled using facial recognition technology. When the face of the manager, which is registered in the database, is detected, a servo motor unlocks the door. This ensures that only authorized individuals can enter the manager's office.

The mudur_yonetimi.py file contains the code for the manager's office control. It handles the facial recognition system and servo motor control. The facial recognition model is trained using the images stored in the manager_images directory.

# 3. Main Hall Monitoring
The temperature and humidity levels in the office environment are continuously monitored using a temperature/humidity sensor. The measured values are displayed on the LCD screen in real-time, ensuring optimal working conditions for employees.

The code for the main hall monitoring can be found in the salon.py file. It reads the data from the temperature/humidity sensor and displays it on the LCD screen. The dht11.py file provides the necessary functions for interacting with the DHT11 sensor.

# 4. Kitchen Safety
To detect potential gas leaks in the kitchen, an MQ2 gas sensor is utilized. When a dangerous level of gas is detected, an audible alarm is triggered using a buzzer. This early warning system helps prevent accidents and ensures the safety of the office.

The mutfak.py file contains the code for kitchen safety. It reads the data from the MQ2 gas sensor and activates the buzzer when a threshold is exceeded. The mq2.py file provides the necessary functions for interacting with the MQ2 sensor.

# 5. Restroom Occupancy
The occupancy status of the restroom is determined using a motion sensor. When the restroom door is opened, the sensor detects the movement, and an LED illuminates. Additionally, the restroom status is displayed on the LCD screen as "Restroom Occupied/Vacant." This feature prevents unnecessary waiting and optimizes office traffic.

The code for the restroom occupancy can be found in the lavabo.py file. It reads the data from the motion sensor, controls the LED, and updates the LCD display accordingly. The pir.py file provides the necessary functions for interacting with the PIR motion sensor.

# 6. Meeting Room
The meeting room is also equipped with a motion sensor. When motion is detected in the room, an LED light turns on, indicating that the room is occupied. This allows employees to track the usage of the meeting room and plan accordingly.

The toplantiodasi.py file contains the code for the meeting room control. It reads the data from the motion sensor and controls the LED based on the occupancy status. The pir.py file is used for interacting with the PIR motion sensor.

# Technologies Used
In our project, we utilized a range of hardware components and software technologies:

# Raspberry Pi: Acts as the central control unit.
Various sensors: Motion, temperature/humidity, gas sensors, etc.
LCD screens: Used for displaying information.
LEDs and buzzer: Provide visual and auditory feedback.
Servo motor: Used for door control.
Amazon RDS: Used for database management.
AWS IoT Core: Used for cloud-based data processing and analytics.
Python programming language: Used for software development of the system.
Installation and Usage
Setting up and using our system is quite straightforward. Step-by-step installation instructions and comprehensive documentation are available in our GitHub repository. Prepare your Raspberry Pi, connect the necessary components, install the software, and configure the system. Once you start the system, your office environment will be intelligently monitored and controlled.

# Smart Office Monitoring Dashboard
One of the most exciting features of our project is the web-based monitoring dashboard. You can access the dashboard by visiting akilliofisin.com . The dashboard provides real-time data and insights to office managers and authorized personnel.

Through the dashboard, you can view:

Who is currently present in the office
Gas sensor status and alerts
Occupancy status of the meeting room
Recent activities in the office
Total number of people in the office
This information helps you optimize office management, utilize resources efficiently, and quickly identify potential issues.

Our website also features a contact page. If you have any questions, feedback, or need support, you can reach out to us at akilliofisin.com/iletisim . Our team will be happy to assist you.

# Conclusion
Our "Smart Office Security and Monitoring System" project is a comprehensive solution designed to meet the needs of modern offices. It enhances security, improves productivity, and simplifies office management. By combining the power of Raspberry Pi, various sensors, cloud services, and our custom-developed software, we are transforming offices into smart and connected spaces.

Our project is open-source and available on GitHub. We invite you to contribute, provide feedback, and adapt the project to suit your specific requirements.

Bring your offices into the future with the "Smart Office Security and Monitoring System." Visit our website akilliofisin.com for more information and join us on this exciting journey!

# Contact:

Website: akilliofisin.com
Contact: akilliofisin.com/iletisim
GitHub: github.com/ahmetmertkabak/smartOffice
Join us in creating smarter offices for a better future!
