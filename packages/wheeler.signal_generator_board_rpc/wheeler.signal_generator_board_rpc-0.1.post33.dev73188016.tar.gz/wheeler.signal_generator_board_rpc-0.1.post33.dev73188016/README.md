# `signal_generator_board_rpc` #

This project provides a RPC interface for a signal-generator board design based
on the [`ATMEGA328`][1] processor _(the processor used in the Arduino
[Uno][2])_.  The RPC interface is based on the [`arduino_rpc`][3] project.


# API Example #

Below, we show an example session interacting with the signal-generator board
through a serial stream.

    >>> from signal_generator_board_rpc import SignalGeneratorBoard
    >>> s = SignalGeneratorBoard(‘/dev/ttyUSB0’)

    free memory: 191
    >>> s.
    s.config_version               s.ram_free                     s.set_waveform_voltage
    s.forward_i2c_request          s.set_hf_amplitude_correction  s.vout_pk_pk
    s.i2c_address                  s.set_i2c_address              s.waveform_frequency
    s.load_config                  s.set_pot                      s.waveform_voltage
    s.pot                          s.set_waveform_frequency
    >>> s.wave
    s.waveform_frequency  s.waveform_voltage
    >>> s.waveform_frequency()
    1000.0
    >>> s.waveform_voltage()
    0.0
    >>> s.set_waveform_frequency(frequency=1000.1010)
    <signal_generator_board_rpc.protobuf_commands.SetWaveformFrequencyResponse object at 0x7f477cb446e0>
    >>> s.waveform_frequency()
    1000.1010131835938
    >>> s.set_waveform_voltage(vrms=1.01)
    0
    >>> s.waveform_voltage()
    1.0099999904632568
    >>> hex(s.i2c_address())
    ‘0x10’
    >>> s.set_i2c_address(address=0x11)
    <signal_generator_board_rpc.protobuf_commands.SetI2cAddressResponse object at 0x7f477cb44830>
    >>> hex(s.i2c_address())
    ‘0x11’


[1]: http://www.atmel.ca/devices/ATMEGA328.aspx
[2]: http://arduino.cc/en/Main/arduinoBoardUno
[3]: https://github.com/wheeler-microfluidics/arduino_rpc
