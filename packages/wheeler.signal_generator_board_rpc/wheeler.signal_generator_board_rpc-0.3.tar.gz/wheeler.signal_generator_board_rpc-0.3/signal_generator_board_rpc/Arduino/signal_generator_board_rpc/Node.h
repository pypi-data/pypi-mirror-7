#ifndef ___NODE__H___
#define ___NODE__H___

#include <stdint.h>
#include "Array.h"
#include "Memory.h"
#include "signal_generator_board.h"
#include "custom_pb.h"

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
  UInt16Array pot_values() {
    UInt16Array result;
    result.data = reinterpret_cast<uint16_t *>(&board_.buffer_[0]);
    for(int i = 0; i < board_.POT_COUNT; i++) {
      result.data[i] = board_.pot(i);
    }
    result.length = board_.POT_COUNT;
    return result;
  }
  void set_pot(uint8_t index, uint8_t value, bool save_to_eeprom) {
    board_.set_pot(index, value, save_to_eeprom);
  }
  void load_config(bool use_defaults) { board_.LoadConfig(use_defaults); }
  void set_i2c_address(uint8_t address) { board_.set_i2c_address(address); }
  uint8_t i2c_address() const { return board_.i2c_address(); }
  float set_hf_amplitude_correction(float correction) {
    board_.set_hf_amplitude_correction(correction);
    return board_.hf_amplitude_correction();
  }
  float hf_amplitude_correction() const {
    return board_.hf_amplitude_correction();
  }

  float waveform_frequency() const { return board_.waveform_frequency(); }
  float set_waveform_frequency(float frequency) {
    board_.set_waveform_frequency(frequency);
    return waveform_frequency();
  }
  float waveform_voltage() const { return board_.waveform_voltage(); }
  float set_waveform_voltage(float vrms) {
    board_.set_waveform_voltage(vrms);
    return waveform_voltage();
  }
  float vout_pk_pk() { return board_.vout_pk_pk(); }

  UInt8Array description_string(uint8_t key) {
    UInt8Array result;

    result.data = reinterpret_cast<uint8_t *>(&board_.buffer_[0]);
    switch (key) {
      case DescriptionStrings_NAME:
        result.length = strlen(board_.name());
        break;
      case DescriptionStrings_HARDWARE_VERSION:
        result.length = strlen(board_.hardware_version());
        break;
      case DescriptionStrings_URL:
        result.length = strlen(board_.url());
        break;
      case DescriptionStrings_SOFTWARE_VERSION:
        result.length = strlen(board_.software_version());
        break;
      case DescriptionStrings_PROTOCOL_NAME:
        result.length = strlen(board_.protocol_name());
        break;
      case DescriptionStrings_PROTOCOL_VERSION:
        result.length = strlen(board_.protocol_version());
        break;
      case DescriptionStrings_MANUFACTURER:
        result.length = strlen(board_.manufacturer());
        break;
      default:
        result.data[0] = '\0';
        result.length = 0;
        break;
    }
    return result;
  }
};

#endif  // #ifndef ___NODE__H___
