#ifndef ___NODE__H___
#define ___NODE__H___

#include <stdint.h>
#include "Array.h"
#include "Memory.h"
#include "signal_generator_board.h"

/* # Arduino digital pins connected to shift registers #
 *
 * Note that both the _output-enable_ and _clear_ pins are _active low_,
 * meaning that setting the respective pin to logic `LOW` will trigger the
 * corresponding behavioural response.  For instance, driving the `SRCLR` pin
 * `LOW` will cause the shift register contents to be cleared, _i.e., set to
 * 0_. */
/* Output enable. */
#define OE            8
/* Clear. */
#define SRCLR         9


#ifndef DISABLE_I2C
/* Callback functions to respond to I2C communication. */
extern void i2c_receive_event(int byte_count);
extern void i2c_request_event();
#endif  // #ifndef DISABLE_I2C


class Node {
public:
  SignalGeneratorClass &board_;

  Node(SignalGeneratorClass &board) : board_(board) {}

  uint32_t ram_free() { return free_memory(); }

  /**************************************************************
   * METHODS
   **************************************************************/
  uint8_t pot(uint8_t index) const { return board_.pot(index); }
  float waveform_frequency() const { return board_.waveform_frequency(); }
  float waveform_voltage() const { return board_.waveform_voltage(); }
  uint8_t i2c_address() const { return board_.i2c_address(); }
  void set_pot(uint8_t address, uint8_t level, bool save_to_eeprom) {
    board_.set_pot(address, level, save_to_eeprom);
  }
  float set_waveform_frequency(float frequency) {
    board_.set_waveform_frequency(frequency);
    return waveform_frequency();
  }
  float set_waveform_voltage(float vrms) {
    board_.set_waveform_voltage(vrms);
    return waveform_voltage();
  }
  void set_i2c_address(uint8_t address) { board_.set_i2c_address(address); }
  void set_hf_amplitude_correction(float correction) {
    board_.set_hf_amplitude_correction(correction);
  }
  float vout_pk_pk() { return board_.vout_pk_pk(); }
  void load_config(bool use_defaults) { board_.LoadConfig(use_defaults); }
  uint16_t config_version(uint8_t position) {
    switch (position) {
      case 0:
        return board_.ConfigVersion().major;
      case 1:
        return board_.ConfigVersion().minor;
      case 2:
        return board_.ConfigVersion().micro;
      default:
        return 0xFFFF;
    }
  }
};


#endif  // #ifndef ___NODE__H___
