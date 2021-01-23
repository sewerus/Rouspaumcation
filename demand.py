class Demand:
    def __init__(self, iteration, source, target, bitrate, duration):
        self.a = iteration
        self.s = source
        self.t = target
        self.h = bitrate
        self.l = duration
        self.P_d = []
        self.P_d_amount = 0
        self.slices_on_edge = []
        self.slices_on_path = []
        # r=1 if demand is rejected
        self.r = 0
        # b - how long demand waits in storage
        self.b = 0
        # q=1 if demand is processing
        self.q = 0
        # m=1 if demand processing is completed
        self.m = 0

    def add_paths(self, paths, limit, all_edges):
        self.P_d = paths[:limit]
        self.P_d_amount = limit

        for p_index in range(self.P_d_amount):
            p = self.P_d[p_index]
            self.slices_on_path.append(p.slices_for_gbps(self.h))

        self.slices_on_edge = [0] * all_edges
        for e in range(all_edges):
            calculated_values = []
            for p in self.P_d:
                if not(e in p.edges):
                    continue
                calculated_values.append(p.slices_for_gbps(self.h))
            if len(calculated_values) > 0:
                self.slices_on_edge[e] = min(calculated_values)
