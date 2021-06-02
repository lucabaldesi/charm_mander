#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: collector
# Author: baldo
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
from gnuradio.filter import pfb


class collector(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "collector")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 80000000
        self.record_size = record_size = 20000
        self.payload_size = payload_size = 60000
        self.decimation = decimation = 2
        self.cent_freq = cent_freq = 5210000000

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
        self.uhd_usrp_source_0.set_bandwidth(samp_rate, 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.pfb_channelizer_hier_ccf_0 = pfb.channelizer_hier_ccf(
            4,
            4,
            None,
            None,
            100,
            1.0,
            0.2,
            0.1)
        self.blocks_udp_sink_0_0_0_0 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', 6002, payload_size, False)
        self.blocks_udp_sink_0_0_0 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', 6001, payload_size, False)
        self.blocks_udp_sink_0_0 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', 6003, payload_size, False)
        self.blocks_udp_sink_0 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', 6000, payload_size, False)
        self.blocks_keep_m_in_n_0_0_0_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, record_size, record_size*decimation, 0)
        self.blocks_keep_m_in_n_0_0_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, record_size, record_size*decimation, 0)
        self.blocks_keep_m_in_n_0_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, record_size, record_size*decimation, 0)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, record_size, record_size*decimation, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.blocks_udp_sink_0, 0))
        self.connect((self.blocks_keep_m_in_n_0_0, 0), (self.blocks_udp_sink_0_0, 0))
        self.connect((self.blocks_keep_m_in_n_0_0_0, 0), (self.blocks_udp_sink_0_0_0, 0))
        self.connect((self.blocks_keep_m_in_n_0_0_0_0, 0), (self.blocks_udp_sink_0_0_0_0, 0))
        self.connect((self.pfb_channelizer_hier_ccf_0, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self.pfb_channelizer_hier_ccf_0, 3), (self.blocks_keep_m_in_n_0_0, 0))
        self.connect((self.pfb_channelizer_hier_ccf_0, 1), (self.blocks_keep_m_in_n_0_0_0, 0))
        self.connect((self.pfb_channelizer_hier_ccf_0, 2), (self.blocks_keep_m_in_n_0_0_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.pfb_channelizer_hier_ccf_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 0)

    def get_record_size(self):
        return self.record_size

    def set_record_size(self, record_size):
        self.record_size = record_size
        self.blocks_keep_m_in_n_0.set_m(self.record_size)
        self.blocks_keep_m_in_n_0.set_n(self.record_size*self.decimation)
        self.blocks_keep_m_in_n_0_0.set_m(self.record_size)
        self.blocks_keep_m_in_n_0_0.set_n(self.record_size*self.decimation)
        self.blocks_keep_m_in_n_0_0_0.set_m(self.record_size)
        self.blocks_keep_m_in_n_0_0_0.set_n(self.record_size*self.decimation)
        self.blocks_keep_m_in_n_0_0_0_0.set_m(self.record_size)
        self.blocks_keep_m_in_n_0_0_0_0.set_n(self.record_size*self.decimation)

    def get_payload_size(self):
        return self.payload_size

    def set_payload_size(self, payload_size):
        self.payload_size = payload_size

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.blocks_keep_m_in_n_0.set_n(self.record_size*self.decimation)
        self.blocks_keep_m_in_n_0_0.set_n(self.record_size*self.decimation)
        self.blocks_keep_m_in_n_0_0_0.set_n(self.record_size*self.decimation)
        self.blocks_keep_m_in_n_0_0_0_0.set_n(self.record_size*self.decimation)

    def get_cent_freq(self):
        return self.cent_freq

    def set_cent_freq(self, cent_freq):
        self.cent_freq = cent_freq
        self.uhd_usrp_source_0.set_center_freq(self.cent_freq, 0)





def main(top_block_cls=collector, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
