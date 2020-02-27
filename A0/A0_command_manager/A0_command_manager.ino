
String inString, remainingstring;
String myArray[5];
String commandWords[2];
byte reading, real;
int test_pin = 6; 
String SenMLdata;
int cmdtype,sensortype, num_param;

enum CmdType {
  Read,
  Config,
  Actuate  
};


enum SensorType{
  analog,
  digital,
  spi
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
  if (sensortype == 0)
  {
     reading = analogRead(param_list[0].toInt());
     SenMLdata= "[{\"bn\":\"ArduinoMKR1000\",\"pinType\":\""+String(sensortype)+"\",\"pinNb\":"+String(param_list[0])+",\"pinValue\":"+String(reading)+"}]\n";
     Serial.print(SenMLdata); //IMPORTANT! DO NOT PUT PRINTLN, AS THE STRING ALREADY CONTAINS \n
  } 
  else if (sensortype == 1)
  {
    //Serial.println("digital read");
    reading = digitalRead(param_list[0].toInt());
    //Serial.println(reading);
    SenMLdata= "[{\"bn\":\"ArduinoMKR1000\",\"pinType\":\""+String(sensortype)+"\",\"pinNb\":"+String(param_list[0])+",\"pinValue\":"+String(reading)+"}]\n";
    Serial.print(SenMLdata); //IMPORTANT! DO NOT PUT PRINTLN, AS THE STRING ALREADY CONTAINS \n
  }
  else
    Serial.println("SPI PLACEHOLDER");


}

void SplitCommand(String command, String fullArray)
{
  cmdtype = command.charAt(0)- '0'; //cmdtype; extarct ASCII for zero
  sensortype = command.charAt(1) - '0'; //sensortype
  num_param = command.charAt(2) - '0'; //param list size
  
  remainingstring = fullArray;
  //Serial.println(cmdtype);
  //Serial.println(num_param);
  for (int i=0; i<num_param; i++)
  {
    myArray[i] = obtainArray(fullArray, ',', 0);  
    remainingstring = fullArray.substring(myArray[i].length()+2, fullArray.length());
    fullArray = remainingstring;
    //Serial.println(myArray[i]);
  }

  if (cmdtype == 0) //read
    ProcessReading(sensortype, myArray); 
  
}
  
void loop() {


    if (Serial.available() > 0) {
      while (Serial.available() > 0){
        inString = Serial.readString();
      }     
      //Serial.println(inString);
 
      commandWords[0] = obtainArray(inString, ' ', 0); //get first word containing CmdType, SensorType, Num_param
      remainingstring = inString.substring(5, inString.length()-1);
      commandWords[1] = obtainArray(remainingstring, ']', 0); //extract the remaining string containing the list of parameters
      SplitCommand (commandWords[0], commandWords[1]);
   }
   delay(100);

}
