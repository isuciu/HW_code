# HW_code
Holds the code for RPI and A0


# RPI
The serial_read.py script reads the data received via serial from A0. The data respects the SenML format. The only missing information from the received data is the timestamp, which can be added in python before forwarding it to the server.

The RPi_A0_comm.py script transmits a reading command to A0 via serial. A0 triggers an interrupt on GPIO9 to announce that its answer is ready. This triggers data reception via serial.

The RPi_command_manager.py creates schedules for reading each sensor attached to Arduino. It also publishes the temperature data as thing1 of user test@xyz.com. Using 'bn'='ArduinoMKR1000' when sending SenML just merges with the 'n'='Temperature' and Grafana is not able to show it in the temperature dashboard, as name become 'ArduinoMKR1000Temperature'. For this reason, send 'bn' void, so as the dashboard can extract data for the "Temperature". 'Bn' is not needed anyway, as we assume that Thing1=ArduinoMKR1000.

# A0
The serial_transmit.ino script reads the analog data from pin A0 and adds it, together with a fixed temperature value, to a SenML message. The message is sent via Serial1 to RPI, each 5s. No timestamp data.

The serial_RPi_commands.ino file receives interrupts from RPi on D8. It also triggers interrupts to RPi using D7. After serial data reception, it processes the received command and sends an answer via serial after interrupting RPi.

The A0_command_manager.ino parses the serial commands received from RPi (one at a time)! The current version can read analog, digital and onewire sensors. Future development should deal with spi sensors. It only answers with the pintype and pinvalue, so RPi is in charge of completing the SenML by adding timestamp, name and unit. 
