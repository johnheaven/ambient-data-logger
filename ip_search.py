class ip_search():
    def __init__(self, current_ip_last_3, ip_min, ip_max, ip_template='http://192.168.2.%i/data/'):
        self.current = current_ip_last_3
        self.starting = current_ip_last_3
        # min IP to search for
        self.ip_min = ip_min
        # max IP to search for
        self.ip_max = ip_max
        # the template to insert the last 3 digits into
        self.ip_template = ip_template
        # the iteration we're on, e.g. whether we've passed ip_max and restarted from ip_min
        self.search_iter = 0
        # whether we've tried all IPs
        self.exhausted = False
    
    def get_ip(self):
        if self.exhausted:
            return False
        else:
            return self.ip_template % self.current

    def bump_sensor_ip(self):
        # try a different sensor by bumping the IP address up one
        if self.current < self.ip_max:
            self.current += 1
        elif self.search_iter == 0:
            # start from the beginning but in such a way that we stop when we hit the first one we tried.
            self.search_iter = 1
            # start again from ip_min
            self.current = self.ip_min
            # don't go any higher than the first one we tried
            self.ip_max = self.starting
        else:
            self.exhausted = True

    def get_next_ip(self):
        self.bump_sensor_ip()
        return self.get_ip()