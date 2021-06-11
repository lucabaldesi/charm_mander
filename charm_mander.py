#!/usr/bin/env python3

from __future__ import print_function
import classifier
import sys
import time


EARFCN_MAPPING = {6000: 47090, 6001: 47290, 6002: 47490, 6003: 47690}
SLEEP_INTERVAL = 1


def send_cmd(fmt, args):
    print(fmt % args)
    sys.stdout.flush()


def log(fmt, args=False):
    fmt = "%f " + str(fmt).replace(",", '').strip("{}")
    if args:
        args = (time.time(),) + args
    else:
        args = (time.time(),)
    print(fmt % args, file=sys.stderr)


class Cell(object):
    def __init__(self, cell_id, current_port):
        self.cell_id = cell_id
        self.set_frequency(current_port)

    def set_frequency(self, port):
        self.current_port = port
        send_cmd("earfcn %d %d", (self.cell_id, EARFCN_MAPPING[self.current_port]))


class CharmMander(object):
    def __init__(self, ports):
        self.current = 0
        self.ports = ports
        self.detector = classifier.Classifier(ports)
        self.inactive_cell = Cell(1, ports[0])
        self.active_cell = Cell(2, ports[0])
        self.handover(False)
        self.hide_and_seek()

    def handover(self, coexisting):
        self.active_cell.coexisting = False

        tmp = self.active_cell
        self.active_cell = self.inactive_cell
        self.inactive_cell = tmp
        send_cmd("handover %d %d", (self.inactive_cell.cell_id, self.active_cell.cell_id))
        log("handovering %d %d", (self.inactive_cell.cell_id, self.active_cell.cell_id))
        self.active_cell.coexisting = coexisting

    def hide_and_seek(self):
        while True:
            time.sleep(SLEEP_INTERVAL)
            classes = self.detector.get_mapping()
            log(classes)
            log("active: %d inactive: %d", (self.active_cell.current_port, self.inactive_cell.current_port))
            current_class = classes[self.active_cell.current_port]
            if current_class != 'clear' and current_class != 'LTE':
                policy = {'clear': 3, 'WiFi': 2, 'LTE': 1, 'other': 0}
                classes = {cl: policy[classes[cl]] for cl in classes}
                best_ch, best_value = max(classes.items(), key=lambda x: x[1])

                if self.active_cell.coexisting:
                    if best_value == 3: # there is a clear channel
                        self.inactive_cell.set_frequency(best_ch)
                        self.handover(coexisting=False)
                else:  # we detected interference
                    if best_value == 3:
                        self.inactive_cell.set_frequency(best_ch)
                        self.handover(coexisting=False)
                    elif best_value > 0:
                        self.inactive_cell.set_frequency(best_ch)
                        self.handover(coexisting=True)


if __name__ == "__main__":
    cm = CharmMander([6000, 6001, 6002, 6003])
