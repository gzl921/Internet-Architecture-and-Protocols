import util

# Your program should send TTLs in the range [1, TRACEROUTE_MAX_TTL] inclusive.
# Technically IPv4 supports TTLs up to 255, but in practice this is excessive.
# Most traceroute implementations cap at approximately 30.  The unit tests
# assume you don't change this number.
TRACEROUTE_MAX_TTL = 30

# Cisco seems to have standardized on UDP ports [33434, 33464] for traceroute.
# While not a formal standard, it appears that some routers on the internet
# will only respond with time exceeeded ICMP messages to UDP packets send to
# those ports.  Ultimately, you can choose whatever port you like, but that
# range seems to give more interesting results.
TRACEROUTE_PORT_NUMBER = 33434  # Cisco traceroute port number.

# Sometimes packets on the internet get dropped.  PROBE_ATTEMPT_COUNT is the
# maximum number of times your traceroute function should attempt to probe a
# single router before giving up and moving on.
PROBE_ATTEMPT_COUNT = 3


class IPv4:
    # Each member below is a field from the IPv4 packet header.  They are
    # listed below in the order they appear in the packet.  All fields should
    # be stored in host byte order.
    #
    version: int
    header_len: int  # Note length in bytes, not the value in the packet.
    tos: int         # Also called DSCP and ECN bits (i.e. on wikipedia).
    length: int      # Total length of the packet.
    id: int
    flags: int
    frag_offset: int
    ttl: int
    proto: int
    cksum: int
    src: str
    dst: str

    def __init__(self, buffer: bytes):
        ...


class ICMP:
    # Each member below is a field from the ICMP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    ...

class UDP:
    # Each member below is a field from the UDP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    ...


# TODO feel free to add helper functions if you'd like
def traceroute(sendsock: util.Socket, recvsock: util.Socket, ip: str) \
        -> list[list[str]]:
    """ Run traceroute and returns the discovered path.

    Calls util.print_result() on the result of each TTL's probes to show
    progress.

    Arguments:
    sendsock -- This is a UDP socket you will use to send traceroute probes.
    recvsock -- This is the socket on which you will receive ICMP responses.
    ip -- This is the IP address of the end host you will be tracerouting.

    Returns:
    A list of lists representing the routers discovered for each ttl that was
    probed.  The ith list contains all of the routers found with TTL probe of
    i+1.   The routers discovered in the ith list can be in any order.  If no
    routers were found, the ith list can be empty.  If `ip` is discovered, it
    should be included as the final element in the list.
    """

    # TODO Add your implementation
    path = [] 
    destination_reached = False
    ip_have_seen = set()
    
    for ttl in range(1, TRACEROUTE_MAX_TTL + 1):
        sendsock.set_ttl(ttl)
        found_routers_for_this_ttl = set()

        for _ in range(PROBE_ATTEMPT_COUNT):
            sendsock.sendto(b'', (ip, TRACEROUTE_PORT_NUMBER))
            try:
                while recvsock.recv_select():
                    buf, addr = recvsock.recvfrom()
                    if len(buf) < 48:
                        continue
                    source_ip = addr[0]

                    ipv4_header = IPv4(buf)
                    if ipv4_header.proto != 1:
                        continue
                
                    icmp_header = ICMP(buf[ipv4_header.header_len:])
                
                    if icmp_header.type == 11 and icmp_header.code == 0:
                            found_routers_for_this_ttl.add(source_ip)
                
                    elif icmp_header.type == 3:
                            found_routers_for_this_ttl.add(source_ip)
                            destination_reached = True
                            break  
                    else:
                        continue
            except Exception as e:
                print(f"Error: {e}")
        
            if destination_reached:
                break
        new_ips = found_routers_for_this_ttl - ip_have_seen
        path.append(list(new_ips))
        ip_have_seen.update(new_ips)
        if destination_reached:
                break
    return path


if __name__ == '__main__':
    args = util.parse_args()
    ip_addr = util.gethostbyname(args.host)
    print(f"traceroute to {args.host} ({ip_addr})")
    traceroute(util.Socket.make_udp(), util.Socket.make_icmp(), ip_addr)
