# ChARM Mander

The goal of ChARM Mander is to intelligently optimize the wireless spectrum usage, avoiding interference and exploiting the available unused bandwidth.
Specifically, ChARM Mander is an AI-enabled driver for a modified version of srsRAN [1].
srsRAN is a 3GPP protocol stack, implementing a 3GPP mobile base station.
The modified version [1] adds to the base station the API for cell frequency change and user handovering.
Please, refer to [3] for an in-depth description of its internals and working.

ChARM Mander is made up of two components:
 - hop_collector.py: it connects to a Software Defined Radio (SDR) to collect I/Q sample on four (configurable) frequencies; it later sends the four streams to four different TCP/IP sockets.
 - charm_mander.py: it reads from the TCP/IP ports the four collected streams, and it runs the ChARM machine learning classifier [2]. ChARM Mander implements a policy to avoid interference and exploit unused channels, and it drives the srsRAN base station accordingly (e.g., changing the base station operating frequencies if an interference with a WiFi device is detected).

## How to run

To start the I/Q sample collection:

```
./hop_collector.py
```

To start the smart reacting base station:

```
nc -l -p 8000 | ./srsenb <conf args>
/charm_mander.py | nc 127.0.0.1 8000
```


## ChARM work

ChARM Mander stems from a research project at the Northeastern University [1], if you use this code, please cite our work:

```
@inproceedings{Baldesi2022Charm,
  author = {Baldesi, Luca and Restuccia, Francesco and Melodia, Tommaso},
  booktitle = {{IEEE INFOCOM 2022 - IEEE Conference on Computer Communications}},
  title = {{ChARM: NextG Spectrum Sharing Through Data-Driven Real-Time O-RAN Dynamic Control}},
  year = {2022},
  month = may 
}
```

## ChARM dataset

ChARM Mander has been released with a dataset for training, validation, and testing [4].
The dataset was collected using Xilinx and USRP SDRs running the [OpenWiFi](https://github.com/open-sdr/openwifi) and [srsRAN](https://github.com/srsran/srsRAN) software stacks.

## References

1. https://github.com/lucabaldesi/srsRAN/tree/charm_api
2. https://github.com/lucabaldesi/charm_trainer
3. L. Baldesi, F. Restuccia and T. Melodia. "ChARM: NextG Spectrum Sharing Through Data-Driven Real-Time O-RAN Dynamic Control", IEEE INFOCOM 2022 - IEEE Conference on Computer Communications, May 2022.
4. http://hdl.handle.net/2047/D20423481
