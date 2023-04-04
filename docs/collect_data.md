
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



```json
{
    "weather":{
        "sun_altitude_angle" : -45.0
    }
}
```