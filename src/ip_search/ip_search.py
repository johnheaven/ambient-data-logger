import json
class ip_search():
    def __init__(self, sensor_id, starting_ip_last_3=None, max_steps=100, ip_template='http://192.168.2.%s/data', cached=True):
        # maximum number of steps to take in either direction
        self.max_steps = max_steps
        # the template to insert the last 3 digits into
        self.ip_template = ip_template
        # the iteration we're on, e.g. whether we've passed ip_max and restarted from ip_min
        self.search_iter = 0
        # whether we've tried all IPs
        self.exhausted = False
        # whether  to add or subtract to find next IP
        self.add_next = True
        # number of steps taken so far
        self.steps_taken = 0
    
        self.sensor_id = sensor_id

        if not any((starting_ip_last_3, cached)):
            raise ValueError('Either starting_ip_last_3 must be set or cached must be `True`')

        if cached:
            # try to get a cached value, otherwise set to 145
            try:
                self.current = self.starting \
                    = json.load(open(f'cache/best-ip-cache__{sensor_id}.json', 'r'))
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(e)
                starting_ip_last_3 = 145

        self.current = starting_ip_last_3
        self.starting = starting_ip_last_3

    def get_uri(self):
        if self.exhausted:
            return False
        else:
            return self.ip_template % self.current

    def get_current(self):
        return self.current

    def bump_sensor_ip(self):
        # try a different IP by bumping up or down - it 'radiates' out from initial
        if self.steps_taken >= self.max_steps:
            self.exhausted = True
        elif self.add_next:
            self.steps_taken += 1
            self.current = self.starting + self.steps_taken
        else:
            self.current = self.starting - self.steps_taken
        
        self.add_next = not self.add_next
        
        return self.exhausted
        
    def write_cache(self):
        json.dump(self.get_current(), open(f'cache/best-ip-cache__{ self.sensor_id }.json', 'w'))