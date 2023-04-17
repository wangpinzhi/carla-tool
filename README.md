# heterogenenous-data-carla

 Scripts for Collecting Heterogeneous data in carla

# origin_manual_control.py说明

基于manual_contorol更改

ctrl+Backspace：切换车辆并保留原车，可在restart函数（暂位于290行处）中更改车型及出生点

ctrl+R：开启录制，生成记录车辆id和初始位置的json文件，生成以车辆id命名的npy记录文件（目前基于vehicleControl数据记录和基于车辆transform记录各会保存一份）
，再次摁下停止录制。

ctrl+T：切换回放模式（以vehicleControl数据回放或以transform数据回放）

ctrl+P：开启回放，回放场景中所有已记录id车辆的数据，再次摁下停止回放
，开启后可以使用ctrl+R进行边回放边录制
。已经处于录制模式（ctrl+R）时摁下则会取消录制并不保存录制结果。

R：对当前camera进行单次截图并将图片rgb数据以json形式存储，如果是深度相机（2号相机）则会额外保存一个记录各像素点深度值的json，数据单位为米
此功能在雷达相机下使用可能会报错

ctrl++/ctrl+-因功能更改原先功能不可用

在cameraManager下if not self._parent.type_id.startswith("walker.pedestrian")处可更改相机参数，
如相机位置等，已将第四个位置改成一个较高角度由前向后的视角
