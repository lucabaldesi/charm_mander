#!/usr/bin/env python3


import charm_trainer.brain as brain
import charm_trainer.entropy as entropy
import multiprocessing as mp
import numpy as np
import os
import socket
import sys
import torch


DATA_UNIT = 20000
DATA_UNIT_SIZE = DATA_UNIT*2*4
SOCK_BUFF = DATA_UNIT_SIZE
BRAIN_MODEL = "brain.pt"
NORMALIZATION = (torch.tensor([-2.7671e-06, -7.3102e-07]).unsqueeze(-1), torch.tensor([0.0002, 0.0002]).unsqueeze(-1))
LABELS = {0: 'clear', 1: 'LTE', 2: 'WiFi', 3: 'other'}
MAX_PREDICTIONS = 10


class DataCruncher(mp.Process):
    def __init__(self, port, queue, id_gpu="0"):
        super(DataCruncher, self).__init__(target=self.listen_and_predict, args=())

        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"] = id_gpu
        self.port = port
        self.queue = queue

        self.device = (torch.device('cuda') if torch.cuda.is_available()
                      else torch.device('cpu'))
        self.device = torch.device('cpu')  # set computation on cpu

        self.model = brain.CharmBrain(DATA_UNIT)
        self.model.load_state_dict(torch.load(BRAIN_MODEL))
        self.model.to(self.device)
        self.model.eval()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("localhost", self.port))
        self.running = True

        self.buffer = b''

    def listen_and_predict(self):
        while self.running:
            data, _ = self.sock.recvfrom(SOCK_BUFF)
            self.buffer += data
            # print(f"{self.port}> buff size: {len(self.buffer)}")
            if len(self.buffer) >= DATA_UNIT_SIZE:
                data = self.buffer[:DATA_UNIT_SIZE]
                self.buffer = self.buffer[DATA_UNIT_SIZE:]
                data = np.frombuffer(data, dtype='<f4')
                data = data.copy()
                data = np.transpose(data.reshape((DATA_UNIT, 2)))
                data = torch.from_numpy(data)
                data = (data - NORMALIZATION[0]) / NORMALIZATION[1]

                with torch.no_grad():
                    data = data.to(self.device, non_blocking=True)
                    output = self.model(data.unsqueeze(0))
                    predicted = entropy.output2class(output, 0.666, 3)
                    predicted = predicted[0].item()
                    self.queue.put((self.port, predicted))
                    print(f"{self.port}> predicted: {predicted}", file=sys.stderr)


class Channel(object):
    def __init__(self, port):
        self.port = port
        self.predictions = []

    def label(self):
        if len(self.predictions) > 0:
            count = {}
            for pred in self.predictions:
                count[pred] = count.get(pred, 0) + 1
            m = max(count.items(), key=lambda x: x[1])
            return LABELS[m[0]]
        else:
            return LABELS[3]

    def add_prediction(self, pred):
        self.predictions.append(pred)
        if len(self.predictions) > MAX_PREDICTIONS:
            self.predictions.pop(0)


class Classifier(object):
    def __init__(self, ports):
        self.workers = []
        mp.set_start_method('spawn')
        self.queue = mp.Queue()
        self.channels = {}
        for p in ports:
            self.channels[p] = Channel(p)
            dc = DataCruncher(p, self.queue)
            self.workers.append(dc)
            dc.start()

    def join_all(self):
        for w in self.workers:
            w.join()

    def stop(self):
        for w in self.workers:
            w.running = False

    def _update_results(self):
        while not self.queue.empty():
            port, cl = self.queue.get()
            self.channels[port].add_prediction(cl)

    def get_mapping(self):
        self._update_results()
        maps = {}
        for port, ch in self.channels.items():
            maps[port] = ch.label()
        return maps


if __name__ == "__main__":
    c = Classifier([6000])
    c.join_all()
