"""
Framework code for the Berkeley CS168 Distance Vector router project

"""
...

class RoutePacket(api.Packet):
    """
    A DV route advertisement

    Note that these packets have both a .dst and a .destination.
    The former is the destination address for the packet, the same as any
    packet has a destination address.
    The latter is the destination for which this is a route advertisement.
    """

    def __init__(self, destination, latency):
        super(RoutePacket, self).__init__()
        self.latency = latency
        self.destination = destination
        self.outer_color = [1, 0, 1, 1]
        self.inner_color = [1, 0, 1, 1]

    def __repr__(self):
        return "<RoutePacket to %s at cost %s>" % (self.destination, self.latency)


class Ports:
    ...


class DVRouterBase(api.Entity):
    """
    Base class for implementing a distance vector router
    """
    ... 
    def start_timer(self, interval=None):
        ...

    def handle_rx(self, packet, port):
        ...

    def handle_timer(self):
        """
        Called periodically when the router should send tables to neighbors
        """
        self.expire_routes()
        self.send_routes(force=True)

    def add_static_route(self, host, port):
        """
        Called when you should add a static route to your routing table
        """
        pass

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when this router receives a route advertisement packet
        """
        pass

    def handle_data_packet(self, packet, in_port):
        """
        Called when this router receives a data packet
        """
        pass

    def send_route(self, port, dst, latency):
        """
        Creates a control packet from dst and lat and sends it.
        """

        pkt = RoutePacket(destination=dst, latency=latency)
        self.send(pkt, port=port)

    def s_log(self, format, *args):
        ...


# TODO: Move this stuff to top of file?

# import abc
from collections import namedtuple
from numbers import Number  # Available in Python >= 2.7.
import unittest

from sim.api import HostEntity, get_name, current_time


# Used for a time ininitely in the future.
# (e.g., for routes that should never time out)
FOREVER = float("+inf")  # Denotes forever in time.
INFINITY = 100

# FIXME: Make FOREVER an internal thing and fix the way it gets formatted in __str__?
#       Instead, have expiration time = None (a default?) mean forever?  (Internally,
#       we may want to set it to +inf just because that should do the right thing?)


class _ValidatedDict(dict):
    #  __metaclass__ = abc.ABCMeta
    #
    def __init__(self, *args, **kwargs):
        super(_ValidatedDict, self).__init__(*args, **kwargs)
        for k, v in self.items():
            self.validate(k, v)

    def __setitem__(self, key, value):
        self.validate(key, value)
        return super(_ValidatedDict, self).__setitem__(key, value)

    def update(self, *args, **kwargs):
        super(_ValidatedDict, self).update(*args, **kwargs)
        for k, v in self.items():
            self.validate(k, v)

  ...
