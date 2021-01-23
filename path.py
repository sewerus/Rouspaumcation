class Path:
    def __init__(self, source, target, edges_bin, path_spec):
        self.source = source
        self.target = target
        self.edges_bin = edges_bin
        self.edges = []
        self.slices_amounts = path_spec
        for i in range(len(edges_bin)):
            if edges_bin[i] == 1:
                self.edges.append(i)

    def slices_for_gbps(self, gbps):
        index = gbps // 50
        if index >= len(self.slices_amounts):
            return self.slices_amounts[-1]
        if index < 0:
            return self.slices_amounts[0]
        else:
            return self.slices_amounts[gbps // 50]
