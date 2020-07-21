import time
import geopy


class SpatialData:
    def __init__(self):
        pass

    def near(self, other):
        raise NotImplementedError()


class GEOCoordinate(SpatialData):
    spatial_epsilon = 1

    def __init__(self, longitude, latitude):
        super().__init__()
        self.longitude = longitude
        self.latitude = latitude

    def near(self, other):
        return (
            geopy.distance.distance(
                (self.longitude, self.latitude), (other.longitude, other.latitude)
            ).meters()
            <= GEOCoordinate.spatial_epsilon
        )


class TimeStamp:
    """ one minute for example """

    temporal_epsilon = 60

    def __init__(self):
        self.time_stamp = time.time()

    def near(self, other):
        assert TimeStamp.temporal_epsilon > 0
        if abs(
                self.time_stamp -
                other.time_stamp) <= TimeStamp.temporal_epsilon:
            return True
        return False

    def strictly_before(self, other):
        return self.time_stamp < other.time_stamp - TimeStamp.temporal_epsilon

    def __lt__(self, other):
        return self.time_stamp < other.time_stamp

    def __eq__(self, other):
        return self.time_stamp == other.time_stamp


class TraceNode:
    def __init__(self, spatial_data, time_stamp):
        self.spatial_data = spatial_data
        self.time_stamp = time_stamp
        # unsure
        self.user_id = None

    def near(self, other):
        """
        in the same place at the same time
        """
        return self.spatial_data.near(
            other) and self.time_stamp.near(other.time_stamp)

    def strictly_before(self, other):
        return self.time_stamp.strictly_before(other)


class Trace:
    def __init__(self, nodes: list):
        self.nodes = nodes
        self.nodes.sort(key=lambda n: n.time_stamp)

    def intersection(self, other_trace):
        j = 0
        init_pos = 0
        for my_node in self.nodes:
            while init_pos < len(other_trace.nodes) and other_trace.nodes[
                init_pos
            ].strictly_before(my_node):
                init_pos += 1
            if init_pos > len(other_trace.nodes):
                return

            j = init_pos
            while j < len(other_trace.nodes):
                they_node = other_trace.nodes[j]
                if my_node.near(they_node):
                    yield (my_node, they_node)
                elif my_node.strictly_before(they_node):
                    break
                j += 1
