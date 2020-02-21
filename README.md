# HW_code
Holds the code for RPI and A0


# RPI
The serial_read.py script reads the data received via serial from A0. The data respects the SenML format. The only missing information from the received data is the timestamp, which can be added in python before forwarding it to the server.

The RPi_A0_comm.py script transmits a reading command to A0 via serial. A0 triggers an interrupt on GPIO9 to announce that its answer is ready. This triggers data reception via serial.

# A0
The serial_transmit.ino script reads the analog data from pin A0 and adds it, together with a fixed temperature value, to a SenML message. The message is sent via Serial1 to RPI, each 5s. No timestamp data.

The serial_RPi_commands.ino file receives interrupts from RPi on D8. It also triggers interrupts to RPi using D7. After serial data reception, it processes the received command and sends an answer via serial after interrupting RPi.
