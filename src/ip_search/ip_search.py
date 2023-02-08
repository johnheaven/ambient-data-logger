import ipaddress
class ip_search():
    def __init__(self, sensor_id, starting_ip: str='192.168.2.118', max_steps=100, ip_mask='192.168.2.0/24', uri_template='http://%s/data', cached=True):

        # get all possible IPs
        self.network_ips = list(ipaddress.ip_network(ip_mask).hosts())

        self.uri_template = uri_template

        # maximum number of steps to take in either direction
        self.max_steps = max_steps
        # the iteration we're on, e.g. whether we've passed ip_max and restarted from ip_min
        self.search_iter = 0
        # whether we've tried all IPs
        self.exhausted = False
        # whether  to add or subtract to find next IP
        self.add_next = True
        # number of steps taken so far
        self.steps_taken = 0
    
        self.sensor_id = sensor_id

        if not any((starting_ip, cached)):
            raise ValueError('Either starting_ip must be set or cached must be `True`')

        if cached:
            try:
                with open(f'cache/best-ip-cache__{sensor_id}.json', 'r') as f:
                    cached_ip = f.readline()
                    if not cached_ip:
                        if starting_ip:
                            cached_ip = starting_ip
                        else:
                            raise RuntimeError('Couldn\'t find cached value and no starting IP specified.')
                
            except (FileNotFoundError, ValueError) as e:
                cached_ip = starting_ip
            
            finally:
                self.current = self.starting \
                    = self.network_ips.index(ipaddress.ip_address(cached_ip))
                
        else:
            self.current = self.starting = self.network_ips.index(ipaddress.ip_address(starting_ip))

    def get_uri(self):
        if self.exhausted:
            return False
        else:
            return self.uri_template % self.network_ips[self.current]

    def get_current(self):
        return self.network_ips[self.current]

    def bump_sensor_ip(self):
        # try a different IP by bumping up or down - it 'radiates' out from initial
        if self.steps_taken >= self.max_steps or self.current == 1 or (self.current + 1) == len(self.network_ips):
            self.exhausted = True
        elif self.add_next:
            self.steps_taken += 1
            self.current = self.starting + self.steps_taken
        else:
            self.current = self.starting - self.steps_taken
        
        self.add_next = not self.add_next
        
        return self.exhausted
        
    def write_cache(self):
        with open(f'cache/best-ip-cache__{ self.sensor_id }.json', 'w') as f:
            f.write(str(self.get_current()))