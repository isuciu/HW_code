# HW_code
Holds the code for RPI and A0


# RPI
The serial_read.py script reads the data received via serial from A0. The data respects the SenML format. The only missing information from the received data is the timestamp, which can be added in python before forwarding it to the server.

# A0
The serial_transmit.ino script reads the analog data from pin A0 and adds it, together with a fixed temperature value, to a SenML message. The message is sent via Serial1 to RPI, each 5s. No timestamp data.
