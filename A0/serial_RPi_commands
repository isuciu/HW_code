
const byte interruptPin = 8;
volatile bool listening_state = 0;
String inString;
int x;
String words[3];
int i;
int maxWords = 3;
byte reading, real;
int test_pin = 6; 
int triggerRPIpin=7;
int counter = 0;
String some_answer;

void setup() {
pinMode(test_pin, INPUT);  
pinMode(triggerRPIpin, OUTPUT);
analogReadResolution(10);  
pinMode(interruptPin, INPUT_PULLUP); 
attachInterrupt(digitalPinToInterrupt(interruptPin), IncomingCmd, RISING);  
Serial1.begin(9600);   
Serial.begin(9600); //Starting serial communication
}

void IncomingCmd(){
  Serial.println ("an interrupt happened");
  listening_state = 1;
  
}

String getWords(String data, char separator, int index)
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


void Process(String cmd1, String cmd2, String cmd3)
{
  Serial.println("Processing command");
  if (cmd2 == "Analog" || cmd2 == "analog" || cmd2 == "ANALOG")
  {
     Serial.println("analog read");
     reading = analogRead(cmd3.toInt());
     Serial.println(reading);
  } 
  else if (cmd2 == "Digital" || cmd2 == "digital" || cmd2 == "DIGITAL")
  {
    Serial.println("digital read");
    reading = digitalRead(cmd3.toInt());
    Serial.println(reading);
    
  }
  Serial.println("OUTPUT 1 on pin 7");
  digitalWrite(triggerRPIpin, 1);
  some_answer = "Read value counter =" + String(counter) + "\n";
  Serial.println(some_answer);
  Serial1.print(some_answer); //IMPORTANT! DO NOT PUT PRINTLN, AS THE STRING ALREADY CONTAINS \n
  counter = counter + 1;
}

  
void loop() {


    if (Serial1.available() > 0) {
      Serial.println("OUTPUT 0 on pin 7");
      digitalWrite(triggerRPIpin, 0);
      while (Serial1.available() > 0){
        inString = Serial1.readString();
      }
      Serial.println(inString);
      for (i=0; i<=maxWords-1; i++) {
          words[i] = getWords(inString, ' ', i);
          Serial.println(words[i]);
      }
      Process(words[0], words[1], words[2]);
   }


}
