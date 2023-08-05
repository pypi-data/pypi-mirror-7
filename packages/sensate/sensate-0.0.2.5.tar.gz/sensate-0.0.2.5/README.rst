***************************************
Sensate: sensaphone interaction library
***************************************

Sensate provides a pythonic interaction layer for Sensaphone hubs
and sensors

Currently only the WSG30 is supported (the model we use at Invitae).

If you'd like to help develop Sensate for use with other Sensaphone 
models, the infrastructure of this library has been designed with 
modularity in mind.  


As most open source libraries, changes should be submitted via
diff or pull request, and you should formally accept the terms of
the packaged license (in this case, the MIT license).


Purpose
-------

The Sensaphone family of equipment communicates over the SNMP protocol,
a protocol generally considered to be bothersome for humans to work with.

Even python libraries for SNMP tend to be a pain.

This library allows you to work with "SensorHub" and "SensorCheck" objects
in a much more programmatically natural way.



Setup
-----

To start playing with sensate, it's recommended (though not required) to
use a virtual environment:



Next you can run a "build install", which will pull in all the dependencies
it needs. There aren't many dependencies, so it shouldn't take long.

python setup.py build install

That's it!

Test your installation by...


Usage
-----

In most cases, the following code should work for you. Set HOSTNAME to a 
reachable hostname on your network or over the internet::

    from sensate.sensorhub import SensorHub
    hub = SensorHub(HOSTNAME)
    print hub.checks

That's it.  `hub.checks` then contains a list of SensorCheck objects with 
as many addressable attributes as the hub will provide.  For example::

   SensorCheck for Sensor 1 at sensaphone1.458.locusdev.net
   { 'lastalarm': '2/27/2014 1:08:57pm', 
     'checktime': datetime.datetime(2014, 3, 7, 23, 23, 1, 90909), 
     'hostname': 'sensaphone1.458.locusdev.net', 
     'name': 'LM2068 CLIA Reagent Freezer Sens', 
     'idx': 1, 
     'measurement': -19.2, 
     'units': 'C', 
     'alarmlow': -25.0, 
     'alarmhigh': -15.0, 
     'battery_status': 'OK',
     'measurement_type': 'Temp 2.8k C' }

The `idx` attribute represents the numerical index of the sensor on the hub.

You'll also notice the `checktime` attribute, which will be set by sensate
at `datetime.utcnow()`.

All "checked" attributes can be easily dumped to a dictionary via the to_dict()
method.


Tips and Tricks
---------------

You may not want to connect to the hub immediately upon establishing the SensorHub
object. That's fine -- just supply `auto=False` as a keyword argument to SensorHub.

Then when you want to perform the checks, use the `SensorHub.reload()` method.

You can get even more granular about your data retrieval: `reload()` is just a
convenience interface to the following two methods::

  SensorHub.discover()
  SensorHub.check()

The first method (discover) populates a dictionary called sensors_by_idx which you
can access as an attribute of the SensorHub object. `discover` performs one poll
per possible index point (0 to MAX_SENSORS_PER_HUB) to see if there's a 'name' 
attribute for this index point. Only indexes with names are added to sensors_by_idx

Also, if you supply match='foo' to SensorHub instantiation, only those sensors
whose name matches 'foo' will be collected. This is useful when trying to ignore
Battery and Power level on the hubs, or when collecting logically grouped sensors.

The second method (check) uses the sensors_by_idx dictionary to construct SensorCheck
objects, which in turn perform the work of collecting values and statuses.

