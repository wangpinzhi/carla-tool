
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
  * **0(static)** represents that the vehicle is not moving and is in a stationary state.
  * **1(autopilot)** represents the vehicle being controlled by 'traffic_manager', please refer to [carla traffic manager](https://carla.readthedocs.io/en/latest/ts_traffic_simulation_overview/#traffic-manager).
  * **2(ctrl_by_file_wheel)** represents that the operating status of the vehicle is controlled by the vehicle operation matrix, which reads' VehicleControlParameters' every frame. However, before each frame operation, the simulator only reads the "steel" parameters, which means that this matrix only affects the vehicle's steering wheel. For information on the vehicle control matrix, please refer to the [carla vehicle control](https://carla.readthedocs.io/en/latest/python_api/#carlavehiclecontrol).
  * **3(ctrl_by_file_all)** represents that the operating status of the vehicle is fully taken over by the vehicle control matrix, and each frame of the simulator will use all parameters in the vehicle control matrix.
* "drive_file"
  * Path relative to 'scene_config. json'
  * It is only valid when the value of **drive_type** is 2 or 3.
* "constant_velocity"
  * When selecting "2" to control the vehicle's operating status, it is necessary to give the vehicle a speed.
  * The same as [carla.Actor.enable_constant_velocity](https://carla.readthedocs.io/en/latest/python_api/#methods).

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
      "drive_file": "drive_flies/ctrl_tt0.npy",
      "constant_velocity" : [-0.3, 0.0, 0.0]
    },
    {
      "role_name": "file_control_steer",
      "blueprint": "vehicle.mercedes.coupe_2020",
      "spawn_point": [-1.90, -34.20, 0.5, 0.0, 150.0, 0.0],
      "drive_type" : 1,
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

## 3.4 Spectator Config

The relevant status of this parameter is currently under development, please set it as follows.

```json
"spectator":{
    "control_type": 0
}
```

# 4 Sensor Config

## 4.1 save setting

This keyword can control the start and end positions of the collection frame count.
Skip Frames [0, "frame_start")

```json
"save_setting": {
    "frame_start": 0,
    "frame_end": 199
  }
```

## 4.2 sensor setting

The sensors in the scene are controlled by the "sensor_manager", and before the next frame of world operation in the simulator, the "sensor_manager" will collect raw data according to the settings in the "JSON" configuration file. The collected cubemap images can be converted into pinhole, fisheye, ERP projection images, etc. in the post-processing step, or pinhole images can be directly collected, and all cameras can collect depth images.

```json
```

* name_id
  * sensor_name: {cm/ph}_{rgb/depth}{number_id} (cm->cubemap, ph->pinhole)
* attacth_type

  ```python
  class EnumAttachType(IntEnum):
      SPECTATOR = 0
      VEHICLE = 1 # Use this often
      WALKER = 2 # not implement yet
  ```

* attach_name
  * Valid only when **attach_type==EnumAttachType.VEHICLE**, corresponding to [**role_name in 3.3**](#33-vehicle-config)

* transform
  * A coordinate system (left-handed coordinate system) originating from the object being attached.
  * Refer to [carla transform](https://carla.readthedocs.io/en/latest/python_api/#carlatransform).

* image_size
  * When using a cubemap camera, the width and height of the image must be the same, and the FOV must be 90°.

* post_process
  * This field is only valid in cubemap cameras, refer to [post-process_data.md](./post-process_data.md).

```json
"sensors": [
    {
      "name_id" : "cm_depth0",
      "attach_type": 1,
      "attach_name": "hero",
      "transform": [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
      "image_size": {"width": "2560", "height": "2560"},
      "post_process":{
        "cam_model":2, "width":5120, "height":2560, "fov":360, "type":0
      }
    },
    {
      "name_id" : "cm_rgb0",
      "attach_type": 1,
      "attach_name": "hero",
      "transform": [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
      "image_size": {"width": "2560", "height": "2560"},
      "post_process":{
        "cam_model":2, "width":5120, "height":2560, "fov":360, "type":1
      }
    },
    {
      "name_id": "ph_rgb0",
      "attach_type": 1,
      "attach_name": "hero",
      "transform": [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
      "image_size": {"width": "1920", "height": "1080"},
      "fov": "60"
    }
  ]
```
