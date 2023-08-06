==============
PyMeteostation
==============

Pymeteostation is software made for controlling meteostation built of MLAB electronic modules (http://www.mlab.cz/) and sending measurements to Open Weather Map (http://openweathermap.org/).

Currently supported sensors are:

* SHT25v01A (Sensirion SHT25)
* ALTIMET01A (MPL3115A2)

Software dependencies
=====================

* Pymlab (>= 0.2, https://pypi.python.org/pypi/pymlab/)

How to
======

1. Install PyMeteostation::
    
    pip install PyMeteostation

2. Create an account on http://openweathermap.org/

3. Run::

    pymeteostation -g

   This wil generate basic configuration file named .pymeteostation in your home directory.

4. Fill the generated config file:

   * *[Meteostation]* section:

     Requiered options: *username*, *password*, *uploadinterval* (in seconds) and *logpath* (must be absolute path)

     If you use ALTIMET01A sensor you must fill *altitude* option too. (It is used for correcting pressure to sea level altitude.)

   * *[I2C_Device]* section:

     Enter I2C configuration. (example options: *type*, *name*, *address*, *channel*, *children*...)

     Usage of *children* option::

         children = sensor1;sensor2;

     The names in *children* option are names of sections defining the children devices.

     Sensors must have *name* option filled.

     Currently supported device types: *i2chub*, *sht25*, *altimet01*

   * *[Translation_Into_POST]* section:
     
     Into option, which you want to send, fill sensor name, from which will be gathered data, and sensor measurement ID (this is because some sensors return more than one measurement).

   **Example**::
  
       [Meteostation]
       username = user
       password = XXXXXX
       uploadinterval = 120
       logpath = /home/user/PyMeteostation-logs/
       stationname = Meteostation 01
       latitude = 0.0
       longtitude = 0.0
       altitude = 0.0

       [I2C_Device]
       type = i2chub
       address = 0x72
       children = barometer;hum_temp;

       [barometer]
       name = barometer
       type = altimet01
       channel = 0

       [hum_temp]
       name = hum_temp
       type = sht25
       channel = 1

       [Translation_Into_POST]
       wind_dir = 
       wind_speed = 
       wind_gust = 
       temp = hum_temp;1;
       humidity = hum_temp;0;
       pressure = barometer;1;
       rain_1h = 
       rain_24h = 
       rain_today = 
       snow = 
       lum = 
       radiation = 
       dew_point = 
       uv = 

5. (optional) I recommend to run::

       pymetostation -n

   This will run PyMeteostation not as service, so you can check if are there any errors.

6. Run::

       pymeteostation start|stop|restart

   This will start PyMeteostation as service.