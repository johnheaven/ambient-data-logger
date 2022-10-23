class ip_search():
    def __init__(self, starting_ip_last_3, max_steps=20, ip_template='http://192.168.2.%s/data/'):
        self.current = starting_ip_last_3
        self.starting = starting_ip_last_3
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
            exhausted = True
        elif self.add_next:
            self.steps_taken += 1
            self.current = self.starting + self.steps_taken
        else:
            self.current = self.starting - self.steps_taken
        
        self.add_next = not self.add_next