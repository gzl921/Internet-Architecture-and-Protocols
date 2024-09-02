"""
Your awesome Distance Vector router for CS 168

Based on skeleton code by:
  MurphyMc, zhangwen0411, lab352
"""

import sim.api as api
from cs168.dv import (
    RoutePacket,
    Table,
    TableEntry,
    DVRouterBase,
    Ports,
    FOREVER,
    INFINITY,
)


class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = False
    POISON_REVERSE = False
    # -----------------------------------------------

    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (
            self.SPLIT_HORIZON and self.POISON_REVERSE
        ), "Split horizon and poison reverse can't both be on"

        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()

        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self

        self.route_history = {}

    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.
        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."

        # TODO: fill this in!
        port_latency = self.ports.get_latency(port)
        self.table[host] = TableEntry(dst=host, port=port, latency=port_latency, expire_time=FOREVER)

    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.
        """
        # TODO: fill this in!
        #If no route exists for a packet’s destination, 
        #do nothing.   if there exists:
        if packet.dst in self.table:
            route_entry = self.table[packet.dst]
            if route_entry.latency < INFINITY:
                self.send(packet, port=route_entry.port)


    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.
        """
        # TODO: fill this in!
        #Get all ports to send
        if single_port is not None:
            ports_to_send = [single_port]
        else:
            ports_to_send = self.ports.get_all_ports()

        for port in ports_to_send:
            for route in self.table.values():
                # broadcast
                if (force or route in self.changed_routes or self.if_route_changed(route, port)) and (not self.SPLIT_HORIZON or port != route.port):
                    if self.POISON_REVERSE and route.port == port:  
                        self.send_route(port, route.dst, INFINITY) 
                    else:
                        self.send_route(port, route.dst, route.latency)
                    self.route_history[(route.dst, port)] = route

    def if_route_changed(self, route, port):
        """
        Check if a route has changed since the last advertisement on a specific port.
        the route & port to check.
        """
        key = (route.dst, port)
        if key in self.route_history:
            last_route, last_time = self.route_history[key]
            return route != last_route
        return True
    
    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        # TODO: fill this in!
        expired_routes = []
        for dst, entry in self.table.items():
            if entry.has_expired:
                expired_routes.append(dst)
    
        for dst in expired_routes:
            if self.POISON_EXPIRED:
                route = self.table[dst]
                self.table[dst] = TableEntry(route.dst, route.port, INFINITY, route.expire_time)
            else:
                del self.table[dst]

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        # TODO: fill this in!
        total_latency = route_latency + self.ports.get_latency(port)
        if route_dst in self.table:
            current_entry = self.table[route_dst]
             #poisoned route
            if route_latency == INFINITY:
                self.table[route_dst] = TableEntry(route_dst, port, INFINITY, FOREVER)
            elif (total_latency < current_entry.latency or
             (total_latency == current_entry.latency and current_entry.expire_time < api.current_time())) or current_entry.port == port:
                self.table[route_dst] = TableEntry( route_dst, port, total_latency, api.current_time() + self.ROUTE_TTL,)
        else:
            self.table[route_dst] = TableEntry(route_dst, port, total_latency, api.current_time() + self.ROUTE_TTL,)


    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)

        # TODO: fill in the rest!
        if self.SEND_ON_LINK_UP:
            self.send_routes(port)

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router goes down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        self.ports.remove_port(port)

        # TODO: fill this in!
        # Invalidate and poison routes using the link that went down
        # Checking if the current route's next port is the one that went down
        invalidated_routes = []
        for dst, entry in self.table.items():
            if entry.port == port:
                invalidated_routes.append(dst)

        for dst in invalidated_routes:
            if self.POISON_ON_LINK_DOWN:
                self.table[dst] = TableEntry(dst, port, INFINITY, api.current_time() + self.ROUTE_TTL)
                self.send_route(port, dst, INFINITY)
            else:
                del self.table[dst]
