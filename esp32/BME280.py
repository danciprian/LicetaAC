from machine import Pin, I2C
import time


class BME280Sensor:
  """
    Clasa folosita pentru comunicarea cu senzorul BME280
    
    Implementeaza metode pentru scrierea si citirea temperaturii,
    presiunii si a umiditatii de la senzor
    
    Metodele folosite pentru a obtine aceste valori finale sunt:
    - temperature_celsius_degrees
    - read_pressure_hpa
    - read_humidity_percent
  """
  # pinii folositi pentru I2C
  I2C_SCL_PIN = Pin(22)
  I2C_SDA_PIN = Pin(21)
  # frecventa folosita pentru magistrala I2C
  I2C_FREQ = 100000
  
  # BME280 adresa I2C
  BME280_I2C_ADDR = 0x77

  # Registrii interni
  BME280_ID_REGISTR         = 0xD0
  BME280_RESET_REGISTR      = 0xE0
  BME280_HUM_REGISTER       = 0xF2
  BME280_STATUS_REGISTER    = 0xF3
  BME280_CTRL_MEAS_REGISTER = 0xF4
  BME280_CFG_REGISTER       = 0xF5
  BME280_TEMP_MSB           = 0xFA
  BME280_TEMP_LSB           = 0xFB
  BME280_TEMP_XLSB          = 0xFC
  BME280_PRES_MSB           = 0xF7
  BME280_PRES_LSB           = 0xF8
  BME280_PRES_XLSB          = 0xF9
  
  # Registrii de oversampling
  BME280_OSAMPLE_1  = 1
  BME280_OSAMPLE_2  = 2
  BME280_OSAMPLE_4  = 3
  BME280_OSAMPLE_8  = 4
  BME280_OSAMPLE_16 = 5
  
  # Parametrii de compensare stocati in senzor
  BME280_DIG_T1_REGISTER = 0x88
  BME280_DIG_T2_REGISTER = 0x8A
  BME280_DIG_T3_REGISTER = 0x8C
  
  BME280_REGISTER_DIG_P1 = 0x8E
  BME280_REGISTER_DIG_P2 = 0x90
  BME280_REGISTER_DIG_P3 = 0x92
  BME280_REGISTER_DIG_P4 = 0x94
  BME280_REGISTER_DIG_P5 = 0x96
  BME280_REGISTER_DIG_P6 = 0x98
  BME280_REGISTER_DIG_P7 = 0x9A
  BME280_REGISTER_DIG_P8 = 0x9C
  BME280_REGISTER_DIG_P9 = 0x9E
  
  BME280_REGISTER_DIG_H1 = 0xA1
  BME280_REGISTER_DIG_H2 = 0xE1
  BME280_REGISTER_DIG_H3 = 0xE3
  BME280_REGISTER_DIG_H4 = 0xE4
  BME280_REGISTER_DIG_H5 = 0xE5
  BME280_REGISTER_DIG_H6 = 0xE6
  BME280_REGISTER_DIG_H7 = 0xE7
  
  
  def __init__(self):
    """
      Creaza o instanta a obiectului pentru comunicarea cu senzorul
      BME280 si citeste coeficientii de compensare din senzor
    """
    self._i2c_bus = I2C(1, scl=(self.I2C_SCL_PIN), sda=(self.I2C_SDA_PIN), freq=self.I2C_FREQ)
    self._i2c_bus.scan()
    # parametrii pentru compensarea temperaturii
    self.dig_T1 = self.i2c_read_16b(self.BME280_DIG_T1_REGISTER)
    self.dig_T2 = self.i2c_read_16b(self.BME280_DIG_T2_REGISTER)
    self.dig_T3 = self.i2c_read_16b(self.BME280_DIG_T3_REGISTER)
    # parametrii pentru compensarea presiunii
    self.dig_P1 = self.i2c_read_16b(self.BME280_REGISTER_DIG_P1)
    self.dig_P2 = self.i2c_read_16b(self.BME280_REGISTER_DIG_P2)
    self.dig_P3 = self.i2c_read_16b(self.BME280_REGISTER_DIG_P3)
    self.dig_P4 = self.i2c_read_16b(self.BME280_REGISTER_DIG_P4)
    self.dig_P5 = self.i2c_read_16b(self.BME280_REGISTER_DIG_P5)
    self.dig_P6 = self.i2c_read_16b(self.BME280_REGISTER_DIG_P6)
    self.dig_P7 = self.i2c_read_16b(self.BME280_REGISTER_DIG_P7)
    self.dig_P8 = self.i2c_read_16b(self.BME280_REGISTER_DIG_P8)
    self.dig_P9 = self.i2c_read_16b(self.BME280_REGISTER_DIG_P9)
    # parametrii pentru compensarea umiditatii
    self.dig_H1 = self.i2c_read_byte(self.BME280_REGISTER_DIG_H1)
    self.dig_H2 = self.i2c_read_16b(self.BME280_REGISTER_DIG_H2)
    self.dig_H3 = self.i2c_read_byte(self.BME280_REGISTER_DIG_H3)
    self.dig_H6 = self.i2c_read_byte(self.BME280_REGISTER_DIG_H7)
    
    h4 = self.i2c_read_byte(self.BME280_REGISTER_DIG_H4)
    h4 = (h4 << 24) >> 20
    self.dig_H4 = h4 | (self.i2c_read_byte(self.BME280_REGISTER_DIG_H5) & 0x0F)

    h5 = self.i2c_read_byte(self.BME280_REGISTER_DIG_H6)
    h5 = (h5 << 24) >> 20
    self.dig_H5 = h5 | (self.i2c_read_byte(self.BME280_REGISTER_DIG_H5) >> 4 & 0x0F)
    
    self.t_fine = 0
    print("Construted")
 
 
  def i2c_write(self, i2c_addr, register, value):
    """
      Metoda scrie 1 byte pe magistrala I2C la adresa specificata
    """
    data_byte = bytearray(1)
    data_byte[0] = value & 0xFF
    self._i2c_bus.writeto_mem(i2c_addr, register, data_byte)


  def i2c_read_byte(self, register):
    """
      Metoda citeste 1 byte din registrul specifical in parametrul ei, de la 
      sensorul BME280 sireturneaza acest byte citit
    """
    return int.from_bytes(self._i2c_bus.readfrom_mem(self.BME280_I2C_ADDR, register, 1),'little') & 0xFF
   
  
  def i2c_read_16b(self, register):
    """
      Metoda citeste 2 bytes de la registrul specificat in parametrul ei
    """
    return int.from_bytes(self._i2c_bus.readfrom_mem(self.BME280_I2C_ADDR, register, 2),'little') & 0xFFFF 
  
  
  def read_temperature_raw(self):
    """
      Aceasta metoda citeste temperatura in format necompensat si returneaza valoarea
      (1) - Configurarea registrului de umiditate al senzorului cu valoarea standard
      (2) - Configurarea registrului de control  al senzorului cu valoarea pentru citirea temperaturii
      (3) - citirea bitului cel mai semnificativ al valorii temperaturii
      (4) - citirea bitului cel mai putin semnificativ al valorii temperaturii
      (5) - citirea bitului cel mai putin semnificativ al valorii temperaturii, este afectat de 
            rezolutia presiunii
      (6) - valoarea finala a temperaturii
    """
    self.i2c_write(self.BME280_I2C_ADDR, self.BME280_HUM_REGISTER, 0x01)        #(1)
    time.sleep_ms(150) 
    self.i2c_write(self.BME280_I2C_ADDR, self.BME280_CTRL_MEAS_REGISTER, 0x37)  #(2) 
    time.sleep_ms(150) 
    msb = self.i2c_read_byte(self.BME280_TEMP_MSB)                              #(3)
    lsb = self.i2c_read_byte(self.BME280_TEMP_LSB)                              #(4)
    xlsb = self.i2c_read_byte(self.BME280_TEMP_XLSB)                            #(5)
    temp = ((msb << 16) | (lsb << 8) | xlsb) >> 4                               #(6)
    return temp 
    
    
  def read_raw_pressure(self):
    """
      Aceasta metoda citeste presiunea in format necompensat si returneaza valoarea
      (1) - Configurarea registrului de umiditate al senzorului cu valoarea standard
      (3) - citirea bitului cel mai semnificativ al valorii presiunii
      (4) - citirea bitului cel mai putin semnificativ al valorii presiunii
      (5) - citirea bitului cel mai putin semnificativ al valorii presiunii, este afectat de 
            rezolutia presiunii
      (6) - valoarea finala a temperaturii
    """
    self.i2c_write(self.BME280_I2C_ADDR, self.BME280_CTRL_MEAS_REGISTER, 0x13) #(1) 
    time.sleep_ms(150) 
    msb = self.i2c_read_byte(self.BME280_PRES_MSB)                             #(2)
    lsb = self.i2c_read_byte(self.BME280_PRES_LSB)                             #(3)
    xlsb = self.i2c_read_byte(self.BME280_PRES_XLSB)                           #(4)
    press = ((msb << 16) | (lsb << 8) | xlsb) >> 4                             #(5)
    return press 
    
    
  def read_raw_humidity(self):
    """
      Aceasta metoda citeste umiditatea in format necompensat si returneaza valoarea
      (3) - citirea bitului cel mai semnificativ al valorii umiditatii
      (4) - citirea bitului cel mai putin semnificativ al valorii umiditatii
      (6) - valoarea finala a umiditatii
    """
    msb = self.i2c_read_byte(self.BME280_TEMP_MSB)                             #(1)
    lsb = self.i2c_read_byte(self.BME280_TEMP_LSB)                             #(2)
    return (msb << 8) | lsb 
  
 
  def read_temperature_compensated(self):
    """
      Aceasta metoda returneaza temperatura calculata cu compensare
      
      Compensarea se obtine din registrii interni de configurare a compensarii 
      cititi in constructor
      
      Formula de calcul este obtinuta din datasheet-ul senzorului
    """
    adc = self.read_temperature_raw()
    var1 = ((adc >> 3) - (self.dig_T1 << 1)) * (self.dig_T2 >> 11)
    var2 = (((((adc >> 4) - self.dig_T1) * ((adc >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
    self.t_fine = var1 + var2
    return (self.t_fine * 5 + 128) >> 8
  
   
  def read_pressure_compensated(self):
    """
      Aceasta metoda returneaza presiunea calculata cu compensare
      
      Compensarea se obtine din registrii interni de configurare a compensarii 
      cititi in constructor
      
      Formula de calcul este obtinuta din datasheet-ul senzorului
    """
    adc = self.read_raw_pressure()
    var1 = self.t_fine - 128000
    var2 = var1 * var1 * self.dig_P6
    var2 = var2 + ((var1 * self.dig_P5) << 17)
    var2 = var2 + (self.dig_P4 << 35)
    var1 = (((var1 * var1 * self.dig_P3) >> 8) +
            ((var1 * self.dig_P2) >> 12))
    var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
    if var1 == 0:
      return 0
    p = 1048576 - adc
    p = (((p << 31) - var2) * 3125) // var1
    var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
    var2 = (self.dig_P8 * p) >> 19
    return ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
  

  def read_humidity_compensated(self):
    """
      Aceasta metoda returneaza umiditatea calculata cu compensare
      
      Compensarea se obtine din registrii interni de configurare a compensarii 
      cititi in constructor
      
      Formula de calcul este obtinuta din datasheet-ul senzorului
    """
    adc = self.read_raw_humidity()
    h = self.t_fine - 76800
    h = (((((adc << 14) - (self.dig_H4 << 20) - (self.dig_H5 * h)) +
         16384) >> 15) * (((((((h * self.dig_H6) >> 10) * (((h *
                          self.dig_H3) >> 11) + 32768)) >> 10) + 2097152) *
                          self.dig_H2 + 8192) >> 14))
    h = h - (((((h >> 15) * (h >> 15)) >> 7) * self.dig_H1) >> 4)
    h = 0 if h < 0 else h
    h = 419430400 if h > 419430400 else h
    return h >> 12
    
  
  def read_temperature_celsius_degrees(self):
    """
      Aceasta metoda returneaza temperatura calculata cu compensare in hecto pascali
    """
    t = self.read_temperature_compensated()
    ti = t // 100
    td = t - ti * 100
    return "{}.{:02d}C".format(ti, td)
  

  def read_pressure_hpa(self):
    """
      Aceasta metoda returneaza presiunea calculata cu compensare in hecto pascali
    """
    p = self.read_pressure_compensated() // 256
    pi = p // 100
    pd = p - pi * 100
    return "{}.{:02d}hPa".format(pi, pd)


  def read_humidity_percent(self):
    """
      Aceasta metoda returneaza umiditatea calculata cu compensare in procente
    """
    h = self.read_humidity_compensated()
    hi = h // 1024
    hd = h * 100 // 1024 - hi * 100
    return "{}.{:02d}%".format(hi, hd)

  

