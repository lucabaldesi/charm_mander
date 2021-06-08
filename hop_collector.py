#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Hop sensing
# GNU Radio version: 3.8.2.0

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time


class hop_sensing(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Hop sensing")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 20000000
        self.payload_size = payload_size = 60000
        self.dst_port = dst_port = 6000
        self.decimation = decimation = 1000
        self.cent_freq = cent_freq = 5240000000
        self.bandwidth = bandwidth = samp_rate

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(cent_freq, 0)
        self.uhd_usrp_source_0.set_gain(0, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_bandwidth(bandwidth, 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.blocks_udp_sink_0 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', dst_port, payload_size, False)
        self.blocks_udp_sink_1 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', dst_port+1, payload_size, False)
        self.blocks_udp_sink_2 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', dst_port+2, payload_size, False)
        self.blocks_udp_sink_3 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', dst_port+3, payload_size, False)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_udp_sink_3, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_bandwidth(self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_payload_size(self):
        return self.payload_size

    def set_payload_size(self, payload_size):
        self.payload_size = payload_size

    def get_dst_port(self):
        return self.dst_port

    def set_dst_port(self, dst_port):
        self.dst_port = dst_port

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation

    def get_cent_freq(self):
        return self.cent_freq

    def set_cent_freq(self, cent_freq):
        self.cent_freq = cent_freq
        self.uhd_usrp_source_0.set_center_freq(self.cent_freq, 0)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.uhd_usrp_source_0.set_bandwidth(self.bandwidth, 0)





def main():
    tb = hop_sensing()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    channels = [(5180000000, tb.blocks_udp_sink_0), (5200000000, tb.blocks_udp_sink_1), (5220000000, tb.blocks_udp_sink_2), (5240000000, tb.blocks_udp_sink_3)]
    current_port = tb.blocks_udp_sink_3
    tb.start()

    while True:
        for freq, port in channels:
            tb.lock()
            tb.disconnect((tb.uhd_usrp_source_0, 0), (current_port, 0))
            tb.set_cent_freq(freq)
            tb.unlock()
            time.sleep(0.125)

            tb.lock()
            current_port = port
            tb.connect((tb.uhd_usrp_source_0, 0), (current_port, 0))
            tb.unlock()
            time.sleep(0.125)
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
