#!/usr/bin/env python3

from __future__ import print_function
import classifier
import sys
import time


EARFCN_MAPPING = {6000: 47090, 6001: 47290, 6002: 47490, 6003: 47690}
SLEEP_INTERVAL = 1


class Cell(object):
    def __init__(self, cell_id, current_port):
        self.cell_id = cell_id
        self.set_frequency(current_port)

    def set_frequency(self, port):
        self.current_port = port
        print("earfcn %d %d" % (self.cell_id, EARFCN_MAPPING[self.current_port]))


class CharmMander(object):
    def __init__(self, ports):
        self.current = 0
        self.ports = ports
        self.detector = classifier.Classifier(ports)
        self.inactive_cell = Cell(1, ports[0])
        self.active_cell = Cell(2, ports[0])
        self.handover()
        self.hide_and_seek()

    def handover(self):
        tmp = self.active_cell
        self.active_cell = self.inactive_cell
        self.inactive_cell = tmp
        print("handover %d %d" % (self.inactive_cell.cell_id, self.active_cell.cell_id))

    def hide_and_seek(self):
        while True:
            time.sleep(SLEEP_INTERVAL)
            classes = self.detector.get_mapping()
            print(classes, file=sys.stderr)
            policy = {'clear': 3, 'WiFi': 2, 'LTE': 1, 'other': 0}
            classes = {cl: policy[classes[cl]] for cl in classes}
            best_ch, best_value = max(classes.items(), key=lambda x: x[1])
            if best_value > classes[self.active_cell.current_port]:
                self.inactive_cell.set_frequency(best_ch)
                self.handover()


if __name__ == "__main__":
    cm = CharmMander([6000, 6001, 6002, 6003])
