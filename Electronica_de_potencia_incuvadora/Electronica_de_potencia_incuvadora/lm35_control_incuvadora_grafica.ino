// -------- Pines --------
const int pinCruceCero = 2;
const int pinDisparo = 8;
const int pinLM35 = A0;

// -------- Límites REALES --------
const int RETARDO_MIN = 400;
const int RETARDO_MAX = 7500;

// -------- Control --------
float T_ref = 40.5;
float Kp = 200.0;

// -------- Variables --------
volatile bool cruceDetectado = false;
volatile int tiempoRetraso = 7500;

// -------- Tiempo --------
unsigned long lastControl = 0;
const int Ts = 100; // control

unsigned long lastPlot = 0;
const int Ts_plot = 1000; // gráfica (1 segundo)

float T_medida_global = 0;

// -------- Setup --------
void setup() {
  pinMode(pinDisparo, OUTPUT);
  digitalWrite(pinDisparo, LOW);

  pinMode(pinCruceCero, INPUT);

  attachInterrupt(digitalPinToInterrupt(pinCruceCero), ISR_cruce, RISING);

  Serial.begin(9600);
}

// -------- Loop --------
void loop() {

  // 🔹 CONTROL
  if (millis() - lastControl >= Ts) {
    lastControl = millis();

    float T_medida = leerTemperatura();
    T_medida_global = T_medida; // guardamos para graficar

    float error = T_ref - T_medida;

    float u = Kp * error;

    // Saturación
    if (u < 0) u = 0;
    if (u > (RETARDO_MAX - RETARDO_MIN)) {
      u = RETARDO_MAX - RETARDO_MIN;
    }

    tiempoRetraso = RETARDO_MAX - u;

    if (tiempoRetraso < RETARDO_MIN)
      tiempoRetraso = RETARDO_MIN;

    if (tiempoRetraso > RETARDO_MAX)
      tiempoRetraso = RETARDO_MAX;
  }

  // 🔹 DISPARO TRIAC
  if (cruceDetectado) {
    cruceDetectado = false;

    if (tiempoRetraso >= RETARDO_MAX) return;

    delayMicroseconds(tiempoRetraso);

    digitalWrite(pinDisparo, HIGH);
    delayMicroseconds(50);
    digitalWrite(pinDisparo, LOW);
  }

  // 📊 ENVÍO PARA SERIAL PLOTTER
  if (millis() - lastPlot >= Ts_plot) {
    lastPlot = millis();

    // formato limpio: referencia temperatura
    Serial.print(37);
    Serial.print(" ");
    Serial.println(T_medida_global);
  }
}

// -------- Interrupción --------
void ISR_cruce() {
  cruceDetectado = true;
}

// -------- Lectura LM35 --------
float leerTemperatura() {
  int adc = analogRead(pinLM35);
  float voltaje = adc * (5.0 / 1023.0);
  return voltaje * 100.0; // LM35
}