高速公路检测器
本教程介绍了如何在您已经为模拟站点提供了相当不错的网络源以及使用检测器为您提供汇总计数（以及速度）的良好网络覆盖范围的情况下，主要使用netedit，dfrouter和一些python工具来设置流量场景的方法 ）在现实世界中的车辆。它不仅限于高速公路，而且前提条件在此得到更频繁地满足。重点更多地放在需求准备和校准上，而不是网络调整上。 netedit_select_highway.png

所选边（蓝色）的优先级较低，将被丢弃

网络
假设您已经熟悉从自己喜欢的映射源进行网络提取，则可以使用netedit打开网络 并将其减少到您感兴趣的领域。假设您有一个navteq文件，可以选择（然后删除）优先级小于-1的所有边，以将其缩减为公路网。之后，可以使用矩形选择（保持移位）来进一步限制所考虑的区域。您可能还想在选项对话框中启用斜坡猜测。如果网络是由较旧版本的SUMO准备的，则在以后重新计算所有连接可能是一个好主意。为此，请在选择模式下选择所有结，然后在连接模式下将它们复位。可能仍然缺少缺少的坡道和异常连接，无法自动猜测，应在设置基本方案后手动修复。

检测器数据
定位探测器
您的最终网络应该在许多可用边缘上都有感应环路的位置。如果将检测器的位置作为地理坐标，则通常需要进行一些手动操作才能在网络中定位检测器。一个起点可以是使用python sumolib将位置与网络匹配：

    sys.path.append(os.path.join(os.environ["SUMO_HOME"], 'tools'))
    import sumolib

    net = sumolib.net.readNet(<NETFILE>)
    detectors = []
    for id, lon, lat in <DETECTOR_INPUTFILE>:
        xy_pos = net.convertLonLat2XY(lon, lat)
        # look 10m around the position
        lanes = net.getNeighboringLanes(xy_pos[0], xy_pos[1], 10)
        # attention, result is unsorted
            bestLane = None
            ref_d = 9999.
        for lane, dist in lanes:
            # now process them and determine a "bestLane"
            # ...
                    if dist < ref_d:
                        ref_d = dist
                        bestLane = lane
                pos, d = bestLane.getClosestLanePosAndDist(xy_pos)
        detectors.append(sumolib.sensors.inductive_loop.InductiveLoop(id, bestLane.getID(), pos))
    sumolib.files.additional.write(<DETECTORFILE>, detectors)
默认情况下，用于数据收集的数据聚合频率为60秒。默认输出文件名设置为none。如果可用，还可以给出检测器类型（源，接收器，之间）。输出文件的示例如下所示。

<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">
<e1Detector id=""det0"" lane="262667814#2.7_0" pos="80.2550814486" freq="60" file="NUL" friendlyPos="True"/>
<e1Detector id=""det1"" lane="262667814#2.7_1" pos="90.2522181762" freq="60" file="NUL" friendlyPos="True"/>
<e1Detector id=""det2"" lane="262667814#2.7_2" pos="91.6879752087" freq="60" file="NUL" friendlyPos="True"/>
</additional>
如果使用大型网络，请注意已安装python rtree库。它将极大地加快几何查找的速度。取决于网络的质量和检测器位置数据，您可能不应该总是选择最近的车道，还应考虑车道数/速度限制是否符合您的期望。初始定位后，您可以将文件进行微调，并将其作为其他文件加载到netedit中。

处理输入数据
检测器数据的常见格式是聚合到一分钟的时隙中。该dfrouter可以处理以下格式的文件：

检测器定义
除了上述检测器定义之外，还可以应用以下定义。

<detectors xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/detectors_file.xsd">
<detectorDefinition id="MQ11Fs1" lane="ErnstRuska2O_0" pos="5.00" type="source"/>
<detectorDefinition id="MQ12Fs1" lane="ErnstRuska2W_0" pos="-5.00" type="between"/>
<detectorDefinition id="MQ13Fs1N" lane="EinsteinN_0" pos="5.00" type="sink"/>
</detectors>
流数据
必须提供有关检测器ID，时间和每种车辆类型的编号的数据，而速度数据是可选的。所有数据均以csv格式保存。

Detector_id;Time(minutes);Number_of_passenger_cars;Number_of_trucks;Average_speed_of passenger_cars;Average_speed_of_trucks
确定路线
flowrouter.py（更多信息，请参见“工具/检测器”）
该脚本基于最大流量理论，并且与dfrouter相似，进行流量路由。需要三个强制输入文件，即SUMO网络（.net.xml）和两个文件，分别指定检测器和流。检测器的类型（源，接收器，中间）可以通过脚本检测，也可以从给定的检测器文件中读取。例如，脚本可以执行为

tools/detector/flowrouter.py -n net.net.xml -d detector.det.xml -f flow.csv`
此外，还有一些选项在dfrouter中不可用 ，用于考虑不同的参数，例如速度，停车设施，流量限制，最大（转弯）流量和车辆类型，以限制路线搜索空间。

dfrouter
有不同的选项来设置路径搜索/校准条件并管理输出文件的内容。可用的选项和相应的定义可以在dfrouter上找到 。例如，执行调用是

dfrouter -n net.net.xml -d detectors.det.xml -f flows.csv -o routes.rou.xml`
此外，还可以使用XML模式定义（dfrouterConfiguration.xsd）来设置配置文件。

比较检测到的流量和估计的流量
根据上述方法，可以使用给定的检测器数据估算/生成路线，然后将其用于仿真中以估算边沿流量。可以使用两个脚本在多个时间间隔内检查估计的流量与检测到的流量相对应的程度。

flowFromEdgeData.py
该脚本用于比较检测到的边缘流和模拟的边缘流。后者基于SUMO的汇总输出。该脚本可以按以下方式执行：

tools/detector/flowFromEdgeData.py -d detectors.det.xml -e edgeData.xml -f detector_flows.xml -c flow_column`
，其中detectors.det.xml主要定义检测器和边缘之间的关系；edgeData.xml是SUMO的聚合输出；detector_flows.xml定义了检测到的流数据；flow_column是该列，其中包含给定检测器流文件中的流数据。也可以指定分析间隔和不带数据的检测器的考虑因素。除每个间隔基于边缘的相对误差外，平均路线流量，平均检测流量，平均流量偏差，RMSE和RMSPE也作为输出计算。

flowFromRoutes.py
该脚本用于根据预定义的发射流和路由比较检测到的流和路由流。基本执行调用如下：

tools/detector/flowFromRoutes.py -d detectors.det.xml -e emitters.flows.xml -f detector_flows.txt -r routes.rou.xml`
，其中generators.flows.xml定义路线流；detector_flows.txt定义了检测到的流量数据；route.rou.xml定义每条路线的边缘组成。有一些选项可以定义分析间隔。除了flowFromEdgeData.py中的上述输出外，还可以使用相应的选项--geh和--geh-treshold获得GEH统计信息。
