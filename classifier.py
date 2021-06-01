#!/usr/bin/env python3


import charm_trainer.brain as brain
import multiprocessing as mp
import numpy as np
import os
import socket
import torch


DATA_UNIT = 20000
DATA_UNIT_SIZE = DATA_UNIT*2*4
SOCK_BUFF = DATA_UNIT_SIZE
BRAIN_MODEL = "brain.pt"
NORMALIZATION = (torch.tensor([-2.7671e-06, -7.3102e-07]).unsqueeze(-1), torch.tensor([0.0002, 0.0002]).unsqueeze(-1))
LABELS = {0: 'clear', 1: 'LTE', 2: 'WiFi', 3: 'other'}


class DataCruncher(mp.Process):
    def __init__(self, port, queue, id_gpu="0"):
        super(DataCruncher, self).__init__(target=self.listen_and_predict, args=())

        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"] = id_gpu
        self.port = port
        self.queue = queue

        self.device = (torch.device('cuda') if torch.cuda.is_available()
                      else torch.device('cpu'))
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
            print(f"{self.port}> buff size: {len(self.buffer)}")
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
                    _, predicted = torch.max(output, dim=1)
                    predicted = predicted[0].item()
                    self.queue.push((self.port, predicted))
                    print(f"{self.port}> predicted: {predicted}")


class Classifier(object):
    def __init__(self, ports):
        self.workers = []
        mp.set_start_method('spawn')
        self.queue = mp.Queue()
        for p in ports:
            dc = DataCruncher(p, self.queue)
            self.workers.append(dc)
            dc.start()
        self.join_all()

    def join_all(self):
        for w in self.workers:
            w.join()

    def stop(self):
        for w in self.workers:
            w.running = False

    def results(self):
        res = {}
        while len(self.queue):
            port, cl = self.queue.get()
            res[port] = LABELS[cl]
        return res


if __name__ == "__main__":
    c = Classifier([6000, 6001, 6002, 6003])
