Windows10运行carla0.9.12出现下面问题的解决方法：CarlaUE4 -dx11

![c4e7746ddfa6a09f2f02b7eb9fa2d93](https://user-images.githubusercontent.com/36963108/232680473-df4dd37d-8ade-49b0-965b-3eff71d4d63c.png)


限制自车能够获取周围指定半径范围内的车辆与非车辆的信息：
```
if len(vehicles) > 1:
            self._info_text += ['Nearby vehicles:']
            distance = lambda l: math.sqrt((l.x - t.location.x)**2 + (l.y - t.location.y)**2 + (l.z - t.location.z)**2)
            vehicles = [(distance(x.get_location()), x) for x in vehicles if x.id != world.player.id]
            for d, vehicle in sorted(vehicles, key=lambda vehicles: vehicles[0]):
                if d > 200.0:
                    break
                vehicle_type = get_actor_display_name(vehicle, truncate=22)
                self._info_text.append('% 4dm %s' % (d, vehicle_type))
```
