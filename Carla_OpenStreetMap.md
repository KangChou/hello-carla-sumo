# 使用OpenStreetMap生成地图

OpenStreetMap是由贡献者开发的世界开放许可证地图。这些地图的各个部分可以导出到`.osm`OpenSreetMap格式的文件，该文件本质上是XML。CARLA可以将文件转换为OpenDRIVE格式，并使用[OpenDRIVE Standalone Mode](https://carla.readthedocs.io/en/latest/tuto_G_openstreetmap/#adv_opendrive.md)将其作为任何其他OpenDRIVE映射摄取。这个过程非常简单。

*   [**1-使用OpenStreetMap获取地图**](https://carla.readthedocs.io/en/latest/tuto_G_openstreetmap/#1-obtain-a-map-with-openstreetmap)
*   [**2-转换为OpenDRIVE格式**](https://carla.readthedocs.io/en/latest/tuto_G_openstreetmap/#2-convert-to-opendrive-format)
*   [**3-导入CARLA**](https://carla.readthedocs.io/en/latest/tuto_G_openstreetmap/#3-import-into-carla)

* * *

## 1-使用OpenStreetMap获取地图

首先要做的是使用[OpenStreetMap](https://www.openstreetmap.org/)生成包含地图信息的文件。

**1.1。转到[openstreetmap.org](https://www.openstreetmap.org/)**。如果未正确显示地图，请尝试更改righ面板中的图层。

**1.2搜索所需的位置**并放大到特定区域。 ![openstreetmap_view](https://upload-images.jianshu.io/upload_images/15863171-2d04762582fb655b.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

警告

由于虚幻引擎的限制，CARLA可以提取有限尺寸的地图（巴黎等大城市会限制引擎的使用）。此外，地图越大，转换为OpenDRIVE所需的时间就越长。

**1.3。`Export`**单击窗口左上角的。该**出口**潘内尔将打开。

**1.4。`Manually select a different area`**在“**导出”**面板中**单击**。

**1.5。**通过在视口中拖动正方形区域的角来**选择自定义区域**。

**1.6。点击`Export`按钮，**在**出口**潘内尔，并保存选定区域的地图信息`.osm`的文件。


* * *

## 2-转换为OpenDRIVE格式

CARLA可以读取由`.osm`OpenStreetMap生成的文件中的内容，并将其转换为OpenDRIVE格式，以便可以将其作为CARLA映射进行提取。可以使用PythonAPI中的以下类完成此操作。

*   **[carla.Osm2Odr](https://carla.readthedocs.io/en/latest/python_api/#carla.Osm2Odr)** –执行转换的类。它将`.osm`解析后的内容作为strind，并返回包含结果的字符串`.xodr`。
    *   `osm_file`—`.osm`解析为字符串的初始文件的内容。
    *   `settings`— [carla.Osm2OdrSettings](https://carla.readthedocs.io/en/latest/python_api/#carla.Osm2OdrSettings)对象，其中包含用于参数化转换的设置。
*   **[carla.Osm2OdrSettings](https://carla.readthedocs.io/en/latest/python_api/#carla.Osm2OdrSettings)** –包含在转换过程中使用的不同参数的Helper类。
    *   `use_offsets` *（默认值为False）* -确定应使用偏移生成地图的位置，从而根据该偏移将原点从中心移出。
    *   `offset_x` *（默认值为0.0）* — X轴上的偏移量。
    *   `offset_y` *（默认值为0.0）* -Y轴上的偏移量。
    *   `default_lane_width` *（默认4.0）* —确定在生成的XODR文件中通道应具有的宽度。
    *   `elevation_layer_height` *（默认值0.0）* —确定用于重叠元素的不同层中的高度分隔元素。阅读更多有关[图层的信息](https://wiki.openstreetmap.org/wiki/Key:layer)。

转换的输入和输出不是`.osm`和`.xodr`文件本身，而是它们的内容。出于上述原因，代码应类似于以下内容。

```
# Read the .osm data
f = open("path/to/osm/file", 'r')
osm_data = f.read()
f.close()

# Define the desired settings. In this case, default values.
settings = carla.Osm2OdrSettings()
# Convert to .xodr
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# save opendrive file
f = open("path/to/output/file", 'w')
f.write(xodr_data)
f.close()

```

结果文件包含OpenDRIVE格式的道路信息。

* * *

## 3-导入CARLA

最后，可以使用[OpenDRIVE Standalone Mode](https://carla.readthedocs.io/en/latest/tuto_G_openstreetmap/#adv_opendrive.md)在CARLA中轻松提取OpenDRIVE文件。

**a）使用您自己的脚本**-[`client.generate_opendrive_world()`](https://carla.readthedocs.io/en/latest/python_api/#carla.Client.generate_opendrive_world)通过API进行调用。这将生成新地图，并阻止模拟，直到准备就绪为止。
使用[carla.OpendriveGenerationParameters](https://carla.readthedocs.io/en/latest/python_api/#carla.OpendriveGenerationParameters)类设置网格生成的参数化。

```
vertex_distance = 2.0  # in meters
max_road_length = 500.0 # in meters
wall_height = 0.0      # in meters
extra_width = 0.6      # in meters
world = client.generate_opendrive_world(
    xodr_xml, carla.OpendriveGenerationParameters(
        vertex_distance=vertex_distance,
        max_road_length=max_road_length,
        wall_height=wall_height,
        additional_width=extra_width,
        smooth_junctions=True,
        enable_mesh_visibility=True))

```

注意

`wall_height = 0.0`强烈建议。OpenStreetMap将相反方向的车道定义为不同的道路。如果生成墙，则导致墙重叠和不希望的碰撞。

**b）使用`config.py`**-脚本可以使用新参数将OpenStreetMap文件直接加载到CARLA中。

```
python3 config.py --osm-file=/path/to/OSM/file

``` 

重要

[client.generate_opendrive_world（）](https://carla.readthedocs.io/en/latest/python_api/#carla.Client.generate_opendrive_world)要求将**OpenDRIVE文件**的**内容解析为string**，并允许参数化。相反，**`config.py`**脚本需要**文件****的路径，`.xodr`**并且始终使用默认参数。

无论哪种方式，都应在CARLA中自动提取地图，并且结果应与此类似。 ![opendrive_meshissue](https://upload-images.jianshu.io/upload_images/15863171-7274a0e081efdda8.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

*使用OpenStreetMap生成CARLA地图的结果。*

警告

生成的道路突然在地图边界终止。当车辆无法找到下一个路标时，这将导致TM崩溃。为避免这种情况，默认情况下OSM模式设置为**True**（[set_osm_mode（）](https://carla.readthedocs.io/en/latest/python_api/#carlatrafficmanager)）。这将显示警告，并在必要时销毁车辆。

* * *

这就是有关如何使用OpenStreetMap生成CARLA地图的全部知识。
