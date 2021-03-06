
#include <OneWire.h>

String inString, remainingstring;
String myArray[5];
String commandWords[2];
byte reading, real;
int test_pin = 6; 
String SenMLdata;


enum CmdType {
  Read =0,
  Config =1,
  Actuate=2  
};


enum SensorType{
  analog=0,
  digital=1,
  spi=2,
  onewire=3
};


void setup() {
pinMode(test_pin, INPUT);  
analogReadResolution(10);    
Serial.begin(9600); //Starting serial communication
}


String obtainArray(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;
  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }
  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}


void ProcessReading(int sensortype, String param_list[5])
{
  SenMLdata = "\n";
  if (sensortype == analog)
  {
     reading = analogRead(param_list[0].toInt());
     SenMLdata= "[{\"bn\":\"ArduinoMKR1000\",\"pinType\":\""+String(sensortype)+"\",\"pinNb\":"+String(param_list[0])+",\"pinValue\":"+String(reading)+"}]\n";
     Serial.print(SenMLdata); //IMPORTANT! DO NOT PUT PRINTLN, AS THE STRING ALREADY CONTAINS \n
  } 
  else if (sensortype == digital)
  {
    //Serial.println("digital read");
    reading = digitalRead(param_list[0].toInt());
    //Serial.println(reading);
    SenMLdata= "[{\"bn\":\"ArduinoMKR1000\",\"pinType\":\""+String(sensortype)+"\",\"pinNb\":"+String(param_list[0])+",\"pinValue\":"+String(reading)+"}]\n";
    Serial.print(SenMLdata); //IMPORTANT! DO NOT PUT PRINTLN, AS THE STRING ALREADY CONTAINS \n
  }
  else if (sensortype == onewire)
  {
    float value = OneWireRead(param_list[0].toInt());
    SenMLdata= "[{\"bn\":\"ArduinoMKR1000\",\"pinType\":\""+String(sensortype)+"\",\"pinNb\":"+String(param_list[0])+",\"pinValue\":"+String(value)+"}]\n";
    Serial.print(SenMLdata); //IMPORTANT! DO NOT PUT PRINTLN, AS THE STRING ALREADY CONTAINS \n
  }
  else
    Serial.print("SPI PLACEHOLDER\n");


}

void SplitCommand(String command, String fullArray)
{
  int ctype, stype, num_param;
  ctype = command.charAt(0)- '0'; //cmdtype; extarct ASCII for zero
  stype = command.charAt(1) - '0'; //sensortype
  num_param = command.charAt(2) - '0'; //param list size
  
  remainingstring = fullArray; //the array of parameters "a, b, c]" or "a]"
  //Serial.println(cmdtype);
  //Serial.println(num_param);
  for (int i=0; i<num_param; i++)
  {
    myArray[i] = obtainArray(fullArray, ',', 0);  
    remainingstring = fullArray.substring(myArray[i].length()+2, fullArray.length());
    fullArray = remainingstring;
    //Serial.println(myArray[i]);
  }
  //sensortype = stype;
  if (ctype == Read) //read
    ProcessReading(stype, myArray); 
  
}


float OneWireRead(int one_pin){
  OneWire ds(one_pin); 
  byte data[12];
  byte addr[8];

  if ( !ds.search(addr)) {
      //no more sensors on chain, reset search
      ds.reset_search();
      return -1000;
  }

  if ( OneWire::crc8( addr, 7) != addr[7]) {
      //Serial.println("CRC is not valid!");
      return -1000;
  }

  if ( addr[0] != 0x10 && addr[0] != 0x28) {
      //Serial.print("Device is not recognized");
      return -1000;
  }

  ds.reset();
  ds.select(addr);
  ds.write(0x44,1); // start conversion, with parasite power on at the end

  byte present = ds.reset();
  ds.select(addr);
  ds.write(0xBE); // Read Scratchpad


  for (int i = 0; i < 9;  i++  ) { // we need 9 bytes
    data[i] = ds.read();
  }

  ds.reset_search();

  byte MSB = data[1];
  byte LSB = data[0];

  float Read = ((MSB << 8) | LSB); //using two's compliment
  float Sum = Read / 16;

  return Sum;
  
}
  
void loop() {


    if (Serial.available() > 0) {
      while (Serial.available() > 0){
        inString = Serial.readString();
      }     
      //Serial.println(inString);
 
      commandWords[0] = obtainArray(inString, ' ', 0); //get first word containing CmdType, SensorType, Num_param
      remainingstring = inString.substring(5, inString.length()-1); //index 0 to length-1
      commandWords[1] = obtainArray(remainingstring, ']', 0); //extract the remaining string containing the list of parameters
      SplitCommand (commandWords[0], commandWords[1]);
   }
   delay(100);

}
