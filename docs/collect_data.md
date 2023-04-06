
# Collect Raw Data

This document will guide you through the process of using this project to collect raw data, including scene setup, sensor configuration, and data collection steps.

# 1 Overview

The ***sensor_config.json*** and ***scene_config.json*** are respectively the configuration files for sensor settings and scene settings. The sensor configuration file is mainly used to set camera models, camera resolution, image types, camera position, and other information. The scene configuration file sets NPC, map, weather, and other information. It can be considered that when these two files are determined, and the random seed of the program is determined, the data collected by the program is the same.

![WorkFlowImage](./images/WorkFlow.jpg#pic_center)

# 2 Recommended Directory Structure

Create a folder named "output" at the root directory of the project, and create a subfolder for each scene inside the "output" folder. Each scene folder should contain both "***scene_config.json***" and "***sensor_config.json***" files, following the directory structure shown in the figure below. The naming convention for the scene folders should be "***[version_name]_[scene_name]***". 

```txt
WARNINGS: This directory structure will be used in the subsequent steps.
```

```txt
version="demo"
scene_name="parkingtest"

D:\HETEROGENENOUS-DATA-CARLA-MAIN
├─output
│  ├─demo_parkingtest
│  │  └─configs
│  │          scene_config.json
│  │          sensor_config.json
```

# 3 Scene Config

## 3.1 Map Config

The key field 'map' is used to indicate which map the scene uses. Generally, these map names are consistent with the maps in the official Carla document. For information on Carla maps, please refer to [carla map](https://carla.readthedocs.io/en/latest/core_map/)

```json
{
    "map" : "Town05"
}
```

* WARNINGS
    >When the map in the Carla emulator is not consistent with the map indicated in the json file, the program switches the map.
    >However, this may cause timeout in the Carla emulator, which can be solved by setting the timeout in the emulator.
    >It is still recommended that the map be manually switched before collection.

## 3.2 Weather Config

The keyword 'weather' can control the weather of the scene, and the fields contained in it are consistent with the objects contained in the 'WeatherParameter' in the official Carla document. Please refer to [carla weather](https://carla.readthedocs.io/en/latest/python_api/#carlaweatherparameters) for details.


```json
{
    "weather":{
        "sun_altitude_angle" : -45.0
    }
}
```

## 3.3 Vehicle Config

The vehicles in the scene are controlled by the "vehicle_manager", and before the next frame of world operation in the simulator, the "vehicle_manager" will control the vehicle operation according to the settings in the "JSON" configuration file. 

* "role_name" 
  * Each vehicle has a unique name, and the sensor is usually set on the "hero" vehicle.
* "blueprint"
  * The definition is consistent with that in the official Carla document([carla blueprint](https://carla.readthedocs.io/en/latest/bp_library/#vehicle)).
* "spawn_point"
  * The generated position of the vehicle in the map.
  * [carla.location.x, carla.location.y, carla.location.z, carla.rotation.pitch, carla.rotation.yaw, carla.rotation.roll]
  * Refer to [carla transform](https://carla.readthedocs.io/en/latest/python_api/#carlatransform)
* "drive_type"
  * 0(static) represents that the vehicle is not moving and is in a stationary state.
  * 1(autopilot) represents the vehicle being controlled by 'traffic_manager', please refer to [carla traffic manager](https://carla.readthedocs.io/en/latest/ts_traffic_simulation_overview/#traffic-manager)
  * 2(ctrl_by_file_wheel)

* WARNINGS
    >The 'vehicle. audit. invisible' in the document is our own definition and is not provided in the official document. 
    >This blueprint sets 'vehicle.audi.tt 'as a transparent material. If you do not have this blueprint, please use another blueprint instead.

```json
"vehicles": [
    {
      "role_name": "hero",
      "blueprint": "vehicle.audi.invisiable",
      "spawn_point": [17.30, -40.20, 0.5, 0.0, -20.0, 0.0],
      "drive_type" : 2,
      "drive_file": "output/huawei_demo_parking/configs/drive_flies/ctrl_tt0.npy",
      "constant_velocity" : [-0.3, 0.0, 0.0]
    },
    {
      "role_name": "file_control_steer",
      "blueprint": "vehicle.mercedes.coupe_2020",
      "spawn_point": [-1.90, -34.20, 0.5, 0.0, 150.0, 0.0],
      "drive_type" : 2,
      "drive_file": "output/huawei_demo_parking/configs/drive_flies/ctrl_mercedes_coupe0.npy",
      "constant_velocity" : [-0.3, 0.0, 0.0]
    },
    {
      "role_name": "static",
      "blueprint": "vehicle.dodge.charger_police",
      "spawn_point": [3.50, -41.20, 0.5, 0.0, -180.0, 0.0],
      "drive_type" : 0
    }
  ]
```