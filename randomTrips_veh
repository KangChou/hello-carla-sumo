randomTrips.py:https://sumo.dlr.de/docs/Tools/Trip.html#edge_probabilities
“ randomTrips.py”为给定的网络（选项-n）生成一组随机行程。通过随机选择均匀分布的源边缘和目标边缘，或采用如下所述的修改分布来做到这一点。生成的行程存储在适用于duarouter的XML文件（选项-o，默认trips.trips.xml）中，如果给出了选项（带有生成的路由文件的文件名），则会自动调用该文件。行程以秒为单位，以开始（选项-b，默认值为0）和结束时间（选项-e，默认值为3600）定义的间隔均匀分布。行程次数由重复率定义（选项-p，默认为1）（以秒为单位）。每次旅行都有一个ID，该ID由前缀（选项--prefix，默认为“”）和运行编号组成。示例调用：

<SUMO_HOME>/tools/randomTrips.py -n input_net.net.xml -e 50
该脚本不会检查是否可以从源到达选定的目的地。该任务由路由器执行。如果网络未完全连接，则某些行程可能会被丢弃。

选项--min-distance <FLOAT>确保行程的起点和终点之间的最小直线距离（以米为单位）。该脚本将继续从边缘分布中采样，直到找到足够距离的足够行程。

随机化
当使用相同的参数两次运行randomTrips.py时，由于随机性，将创建不同的输出文件。选项--seed <INT>可用于获取可重复的伪随机性。

边缘概率
选项--fringe-factor <FLOAT>增加了跳闸在网络边缘开始/结束的可能性。如果给定值10，则没有后继或前任的边将被选择为行程的起点或终点的可能性要高10倍。在对在模拟区域外部开始和结束的交通进行建模时，这很有用。

选择边缘的概率也可以通过以下方式加权

边长（选项-l），
按车道数（选项-L）
边缘速度（以指数形式，通过选项--speed-exponent）
通用边缘参数（选项--edge-param）
行进方向（选项--angle-factor和--angle）
有关影响边缘概率的其他方法，请致电

<SUMO_HOME>/tools/randomTrips.py --help
到达率
到达率由选项--period <FLOAT>（默认值1）控制。默认情况下，生成的车辆具有恒定的时间段和到达速率（每秒（1 /周期））。通过使用低于1的值，可以实现每秒多次到达。

当添加选项--binomial <INT>时，将使用二项分布将到达随机化，其中--binomial的参数给出n（同时到达的最大数量），并且预期到达率为1 /周期 （此选项为在版本0.23.0中尚不可用）。

例
要让n辆车在时间t0和t1之间出发，请设置选项

-b t0 -e t1 -p ((t1 - t0) / n)
注意

如果道路通行能力不足以容纳该数量的车辆，或者网络未完全连接（在这种情况下，某些生成的行程将是无效的），则实际的出发次数可能会更少。

经过验证的路线和行程
使用--route-file选项时，将生成带有有效车辆路线的输出文件。这是通过在后台自动调用 duarouter将随机行程转换为路线并自动丢弃断开的行程来实现的。可能有必要增加生成的随机行程的数量，以解决一部分断开，丢弃的行程。

警告

使用选项--vehicle-class时，应为选项--edge-permission设置相同的值

有时，希望获得经过验证的行程而不是路线（即，使用一次性路线分配。在这种情况下，可以使用附加选项--validate来生成经过验证的行程（首先生成有效路线，然后将其转换回去）旅行）。

生成具有其他参数的车辆
使用选项--trip-attributes <STRING>，可以为生成的车辆提供其他参数（请注意引号字符的用法）。

<SUMO_HOME>/tools/randomTrips.py -n input_net.net.xml 
  --trip-attributes="departLane=\"best\" departSpeed=\"max\" departPos=\"random\""
这将使随机车辆在其起始边缘随机分布，并在合理的车道上高速插入。

警告

在Linux上引用旅行属性必须使用样式--trip-attributes'departLane =“ best” departSpeed =“ max” departPos =“ random”'

从外部文件设置车辆类型
如果生成的车辆应具有特定的车辆类型，则需要准备一个附加文件：

<additional>
  <vType id="myType" maxSpeed="27" vClass="passenger"/>
</additional>
然后使用选项--additional-file加载此文件（假定将其保存为type.add.xml）。

<SUMO_HOME>/tools/randomTrips.py -n input_net.net.xml --trip-attributes="type=\"myType\"" --additional-file type.add.xml
   --edge-permission passenger
注意使用选项--edge-permission（不建议使用别名：-- vclass），该选项可确保随机的起始边缘和到达边缘允许特定的车辆类别。

为了产生随机的行人交通而不是车辆交通，可以使用--pederrians选项。建议将此选项与--max-distance选项结合使用 ，以免走得太长。有关行人模拟的更多信息，请参见 模拟/行人。

请注意，-vehicle-class选项仅应用作为给定车辆类别的标准类型生成行程的快速速记，因为它在生成的行程文件中放置了标准vType定义。

自动生成车辆类型
通过设置选项--vehicle-class，可以将指定车辆类别的车辆类型定义添加到输出文件中。即

randomTrips.py --vehicle-class bus ...
将添加

<vType id="bus" vClass="bus"/>
适用于车辆类型而非车辆的任何--trip属性将自动放置在生成的vType定义中：

randomTrips.py --vehicle-class bus --trip-attributes="maxSpeed=\"27.8\""
将添加

<vType id="bus" vClass="bus" maxSpeed="random"/>
或者，在randomTrips.py完成之后，<vType>可以编辑创建的-element以指定其他参数。手动编辑的缺点是，再次运行randomTrips.py时必须重复进行。

产生不同的交通方式
使用选项-行人将产生行人而不是车辆。
使用--persontrips选项将生成具有<persontrip>定义的人员。这样可以指定可用的交通方式，从而使用 IntermodalRouting决定他们是否使用公共交通工具，私家车还是步行。
步行或公共交通工具：-- trip-attributes“ modes = \” public \“”
步行，公共交通工具或汽车-旅行归因于“ modes = \” public car \“”
警告

在Linux上引用旅行属性必须使用--trip-attributes'modes =“ public”'样式

中级航路点
为了在网络内生成更长的行程，可以使用选项--intermediate <INT>生成中间航路点。这会将给定数量的 通孔边缘添加 到行程定义中。

定制重量
保存
使用选项weights-output-prefix <STRING>将导致生成具有给定前缀的三个权重文件（<prefix> .src.xml，<prefix> .dst.xml，<prefix> .via.xml），其中包含使用的边缘概率。

.src.xml包含选择为from-edge的边的概率
.dst.xml包含被选择为to-edge的边的概率
.via.xml包含将边缘选择为via-edge的概率（仅在设置选项--intermediate时使用）。
可视化
这些文件中的任何一个都可以在sumo-gui中加载以进行可视化

载入中
通过使用带有前缀值作为参数的--weights-prefix <STRING>选项，可以使用这种格式的文件来设置自定义权重以生成随机行程。randomTrips脚本将尝试加载所有边缘和所有三个文件扩展名（.src.xml，.dst.xml，.via.xml）的权重，但是如果缺少相同值，将使用以下默认值：

如果加载的权重文件未包含所有边缘，则缺失边缘的概率为0
如果文件丢失，则在采样该类型的边缘时使用根据常规选项的概率（即，丢失的 <prefix> .dst.xml将导致如#Edge_Probabilities部分中所述的概率，在对目标边缘进行采样时将使用）
注意

从权重文件加载的概率会自动归一化。因此，将概率指定为分数还是百分比值都没有关系。

使用范例
要获得从两个特定位置（边a和b）到随机目的地的旅行，请使用

randomTrips.py --weights-prefix example  ...<other options>...
并仅定义文件example.src.xml，如下所示：

<edgedata>
  <interval begin="0" end="10"/>
    <edge id="a" value="0.5"/>
    <edge id="b" value="0.5"/>
  </interval>
</edgedata>
route2trips.py
该脚本通过剥离除起点和终点之外的所有路线信息，从路线文件生成行程文件。它只有一个参数，即路线文件，并将行程文件打印到stdout。例：

<SUMO_HOME>/tools/route2trips.py input_routes.rou.xml
