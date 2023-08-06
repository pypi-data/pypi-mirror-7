Open Sprinkler Lib
==================
Open Sprinkler Lib provides an api for the RPi and Beagle Bone versions of the Open Sprinkler Project.

Features
-----------------
* Auto detects supported hardware platforms.
	* RPi
	* Beagle Bone (Needs testing)
* Mocks OpenSprinkler Hardware if no supported hardware platform detected for developing code on any computer.
* json config
* Support for per station master stations.

Todo
-----------------
* Add support for Rain Sensor

Configuration json format
-----------------
>stations: array
>>sid: int - Station ID (starts at 1)  
>>name: str - Human readable name of station  
>>description: str - Human readable description of station  
>>type: str - acceptable values are "zone" and "master"  
>>master: int - optional sid of master station, only required if zone has a master station.

Example Usage
-----------------
    #!/usr/bin/env python
	 from opensprinklerlib import OpenSprinkler
	 controller = OpenSprinkler()
	 controller.load_config(open("config.json").read())
	 controller.enable_station(1)
