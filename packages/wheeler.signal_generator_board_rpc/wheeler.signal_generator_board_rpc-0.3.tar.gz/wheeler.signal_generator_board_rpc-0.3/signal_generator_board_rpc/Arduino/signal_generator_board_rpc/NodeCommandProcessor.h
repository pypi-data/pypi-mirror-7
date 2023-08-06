
#ifndef ___COMMAND_PROCESSOR___
#define ___COMMAND_PROCESSOR___

#include "UnionMessage.h"
#include "Array.h"
#include "ArraySerialization.h"
#include "commands_pb.h"


template <typename Obj>
class CommandProcessor {
  /* # `CommandProcessor` #
   *
   * Each call to this functor processes a single command.
   *
   * All arguments are passed by reference, such that they may be used to form
   * a response.  If the integer return value of the call is zero, the call is
   * assumed to have no response required.  Otherwise, the arguments contain
   * must contain response values. */
protected:
  Obj &obj_;
#ifndef DISABLE_I2C
  buffer_with_len string_buffer_;
#endif  // #ifndef DISABLE_I2C
  uint32_t array_buffer_[10];
  union {
    Int8Array int8_t_;
    Int16Array int16_t_;
    Int32Array int32_t_;
    UInt8Array uint8_t_;
    UInt16Array uint16_t_;
    UInt32Array uint32_t_;
    FloatArray float_;
  } array_;
  union {
    Int8Array int8_t_;
    Int16Array int16_t_;
    Int32Array int32_t_;
    UInt8Array uint8_t_;
    UInt16Array uint16_t_;
    UInt32Array uint32_t_;
    FloatArray float_;
  } return_array_;
public:
  CommandProcessor(Obj &obj) : obj_(obj) {}

  int process_command(uint16_t request_size, uint16_t buffer_size,
                      uint8_t *buffer) {
    /* ## Call operator ##
     *
     * Arguments:
     *
     *  - `request`: Protocol buffer command request structure,
     *  - `buffer_size`: The number of bytes in the arguments buffer.
     *  - `data`: The arguments buffer. */

    union {
#ifndef DISABLE_I2C
      ForwardI2cRequestRequest forward_i2c_request;
#endif  // #ifndef DISABLE_I2C
      RamFreeRequest ram_free;
      PotValuesRequest pot_values;
      SetPotRequest set_pot;
      LoadConfigRequest load_config;
      SetI2cAddressRequest set_i2c_address;
      I2cAddressRequest i2c_address;
      SetHfAmplitudeCorrectionRequest set_hf_amplitude_correction;
      HfAmplitudeCorrectionRequest hf_amplitude_correction;
      WaveformFrequencyRequest waveform_frequency;
      SetWaveformFrequencyRequest set_waveform_frequency;
      WaveformVoltageRequest waveform_voltage;
      SetWaveformVoltageRequest set_waveform_voltage;
      VoutPkPkRequest vout_pk_pk;
      DescriptionStringRequest description_string;
    } request;

    union {
#ifndef DISABLE_I2C
      ForwardI2cRequestResponse forward_i2c_request;
#endif  // #ifndef DISABLE_I2C
      RamFreeResponse ram_free;
      PotValuesResponse pot_values;
      SetPotResponse set_pot;
      LoadConfigResponse load_config;
      SetI2cAddressResponse set_i2c_address;
      I2cAddressResponse i2c_address;
      SetHfAmplitudeCorrectionResponse set_hf_amplitude_correction;
      HfAmplitudeCorrectionResponse hf_amplitude_correction;
      WaveformFrequencyResponse waveform_frequency;
      SetWaveformFrequencyResponse set_waveform_frequency;
      WaveformVoltageResponse waveform_voltage;
      SetWaveformVoltageResponse set_waveform_voltage;
      VoutPkPkResponse vout_pk_pk;
      DescriptionStringResponse description_string;
    } response;

    pb_field_t *fields_type;
    bool status = true;
#ifndef DISABLE_I2C
    uint8_t i2c_count = 0;
#endif  // #ifndef DISABLE_I2C

    pb_istream_t istream = pb_istream_from_buffer(buffer, request_size);

    int request_type = decode_unionmessage_tag(&istream,
                                               CommandRequest_fields);

    /* Set the sub-request fields type based on the decoded message identifier
     * tag, which corresponds to a value in the `CommandType` enumerated type.
     */
    switch (request_type) {
#ifndef DISABLE_I2C
      case CommandType_FORWARD_I2C_REQUEST:
        request.forward_i2c_request.request.funcs.decode = &read_string;
        request.forward_i2c_request.request.arg = &string_buffer_;
        fields_type = (pb_field_t *)ForwardI2cRequestRequest_fields;
        break;
#endif  // #ifndef DISABLE_I2C
      case CommandType_RAM_FREE:
        fields_type = (pb_field_t *)RamFreeRequest_fields;
        break;
      case CommandType_POT_VALUES:
        fields_type = (pb_field_t *)PotValuesRequest_fields;
        break;
      case CommandType_SET_POT:
        fields_type = (pb_field_t *)SetPotRequest_fields;
        break;
      case CommandType_LOAD_CONFIG:
        fields_type = (pb_field_t *)LoadConfigRequest_fields;
        break;
      case CommandType_SET_I2C_ADDRESS:
        fields_type = (pb_field_t *)SetI2cAddressRequest_fields;
        break;
      case CommandType_I2C_ADDRESS:
        fields_type = (pb_field_t *)I2cAddressRequest_fields;
        break;
      case CommandType_SET_HF_AMPLITUDE_CORRECTION:
        fields_type = (pb_field_t *)SetHfAmplitudeCorrectionRequest_fields;
        break;
      case CommandType_HF_AMPLITUDE_CORRECTION:
        fields_type = (pb_field_t *)HfAmplitudeCorrectionRequest_fields;
        break;
      case CommandType_WAVEFORM_FREQUENCY:
        fields_type = (pb_field_t *)WaveformFrequencyRequest_fields;
        break;
      case CommandType_SET_WAVEFORM_FREQUENCY:
        fields_type = (pb_field_t *)SetWaveformFrequencyRequest_fields;
        break;
      case CommandType_WAVEFORM_VOLTAGE:
        fields_type = (pb_field_t *)WaveformVoltageRequest_fields;
        break;
      case CommandType_SET_WAVEFORM_VOLTAGE:
        fields_type = (pb_field_t *)SetWaveformVoltageRequest_fields;
        break;
      case CommandType_VOUT_PK_PK:
        fields_type = (pb_field_t *)VoutPkPkRequest_fields;
        break;
      case CommandType_DESCRIPTION_STRING:
        fields_type = (pb_field_t *)DescriptionStringRequest_fields;
        break;
      default:
        status = false;
        break;
    }

    if (!status) { return -1; }

    /* Deserialize request according to the fields type determined above. */
    decode_unionmessage_contents(&istream, fields_type, &request);

    pb_ostream_t ostream = pb_ostream_from_buffer(buffer, buffer_size);

    /* Process the request, and populate response fields as necessary. */
    switch (request_type) {
#ifndef DISABLE_I2C
      case CommandType_FORWARD_I2C_REQUEST:
        fields_type = (pb_field_t *)ForwardI2cRequestResponse_fields;
        /* Forward all bytes received on the local serial-stream to the i2c
         * bus. */
        /* Use the I2C master/slave data flow described [here][1].
         *
         *  1. Write request _(as master)_ to _slave_ device.
         *  2. Request a two-part response from the _slave_ device:
         *   a. Response length, in bytes, as an unsigned, 8-bit integer.
         *   b. Response of the length from 2(a).
         *
         * # Notes #
         *
         *  - Maximum of 32 bytes can be sent by the standard Wire library.
         *
         * ## Request data from slave ##
         *
         *  - The `Wire.requestFrom` function does not return until either the
         *    requested data is fully available, or an error occurred.
         *  - Building in a wait for `Wire.available` simply makes it possible
         *    for the code to hang forever if the data is not available.
         *
         * ## Send data from slave to master upon request ##
         *
         *  - You can only do one Wire.write in a `requestEvent` callback.
         *  - You do not do a `Wire.beginTransmission` or a
         *    `Wire.endTransmission`.
         *  - There is a limit of 32 bytes that can be returned.
         *
         * [1]: http://gammon.com.au/i2c-summary */
        Wire.beginTransmission((uint8_t)request.forward_i2c_request.address);
        Wire.write(string_buffer_.buffer, string_buffer_.length);
        response.forward_i2c_request.result = Wire.endTransmission();
        if (response.forward_i2c_request.result != 0) {
          /* Transmission failed.  Perhaps slave was not ready or not
           * connected. */
          response.forward_i2c_request.result = -1;
          break;
        }

        status = false;
        /* Request response size. */
        for (int i = 0; i < 21; i++) {
          buffer_size = Wire.requestFrom((uint8_t)request
                                         .forward_i2c_request.address,
                                         (uint8_t)1);
          if (buffer_size != 1) {
            /* Unexpected number of bytes. */
            response.forward_i2c_request.result = -2;
            status = false;
            break;
          }

          i2c_count = Wire.read();

          if (i2c_count == 0xFF) {
            /* The target is reporting that the request has not yet been
             * processed.  Try again... */
            if (i < 5) {
              /* Delay 1ms for the first 3 attempts, to allow fast requests to
               * return quickly. */
              delay(1);
            } else if (i < 10) {
              /* Delay 10ms for the first next 7 attempts. */
              delay(10);
            } else {
              /* For the last 20 attempts, double the delay each attempt, until
               * we reach 10240ms _(roughly 10 seconds)_. */
              delay(10 << (i - 10));
            }
          } else if (i2c_count > 32) {
            /* The buffer size is invalid. */
            response.forward_i2c_request.result = i2c_count;
            status = false;
            break;
          } else {
            /* The `i2c_count` should be valid. */
            request_size = i2c_count;
            response.forward_i2c_request.result = i2c_count;
            status = true;
            break;
          }
        }
        if (!status) {
          /* An error was encountered so break. */
          break;
        }

        /* Request actual response. */
        buffer_size = Wire.requestFrom((uint8_t)request
                                       .forward_i2c_request.address,
                                       (uint8_t)request_size);
        if (buffer_size != request_size) {
          /* Unexpected response size. */
          response.forward_i2c_request.result = request_size;
          break;
        }
        // Slave may send less than requested
        for (int i = 0; i < request_size; i++) {
          // receive a byte as character
          buffer[i] = Wire.read();
        }
        /* Return directly from here, since the I2C response is already
         * encoded and we wrote the encoded response directly to the
         * buffer. */
        return request_size;
#endif  // #ifndef DISABLE_I2C
      case CommandType_RAM_FREE:
        fields_type = (pb_field_t *)RamFreeResponse_fields;
        // `return_type`: uint32_t
        
        response.ram_free.result =
        obj_.ram_free();
        break;
      case CommandType_POT_VALUES:
        fields_type = (pb_field_t *)PotValuesResponse_fields;
        // `return_type`: ('uint16_t', 'array', 'UInt16Array')
        
        response.pot_values.result.funcs.encode = &write_uint_array<UInt16Array, uint16_t>;
        response.pot_values.result.arg = &return_array_.uint16_t_;
        return_array_.uint16_t_ =
        
        obj_.pot_values();
        break;
      case CommandType_SET_POT:
        fields_type = (pb_field_t *)SetPotResponse_fields;
        // `return_type`: None
        
        obj_.set_pot(
            request.set_pot.index
        , 
            request.set_pot.value
        , 
            request.set_pot.save_to_eeprom
        );
        break;
      case CommandType_LOAD_CONFIG:
        fields_type = (pb_field_t *)LoadConfigResponse_fields;
        // `return_type`: None
        
        obj_.load_config(
            request.load_config.use_defaults
        );
        break;
      case CommandType_SET_I2C_ADDRESS:
        fields_type = (pb_field_t *)SetI2cAddressResponse_fields;
        // `return_type`: None
        
        obj_.set_i2c_address(
            request.set_i2c_address.address
        );
        break;
      case CommandType_I2C_ADDRESS:
        fields_type = (pb_field_t *)I2cAddressResponse_fields;
        // `return_type`: uint8_t
        
        response.i2c_address.result =
        obj_.i2c_address();
        break;
      case CommandType_SET_HF_AMPLITUDE_CORRECTION:
        fields_type = (pb_field_t *)SetHfAmplitudeCorrectionResponse_fields;
        // `return_type`: float
        
        response.set_hf_amplitude_correction.result =
        obj_.set_hf_amplitude_correction(
            request.set_hf_amplitude_correction.correction
        );
        break;
      case CommandType_HF_AMPLITUDE_CORRECTION:
        fields_type = (pb_field_t *)HfAmplitudeCorrectionResponse_fields;
        // `return_type`: float
        
        response.hf_amplitude_correction.result =
        obj_.hf_amplitude_correction();
        break;
      case CommandType_WAVEFORM_FREQUENCY:
        fields_type = (pb_field_t *)WaveformFrequencyResponse_fields;
        // `return_type`: float
        
        response.waveform_frequency.result =
        obj_.waveform_frequency();
        break;
      case CommandType_SET_WAVEFORM_FREQUENCY:
        fields_type = (pb_field_t *)SetWaveformFrequencyResponse_fields;
        // `return_type`: float
        
        response.set_waveform_frequency.result =
        obj_.set_waveform_frequency(
            request.set_waveform_frequency.frequency
        );
        break;
      case CommandType_WAVEFORM_VOLTAGE:
        fields_type = (pb_field_t *)WaveformVoltageResponse_fields;
        // `return_type`: float
        
        response.waveform_voltage.result =
        obj_.waveform_voltage();
        break;
      case CommandType_SET_WAVEFORM_VOLTAGE:
        fields_type = (pb_field_t *)SetWaveformVoltageResponse_fields;
        // `return_type`: float
        
        response.set_waveform_voltage.result =
        obj_.set_waveform_voltage(
            request.set_waveform_voltage.vrms
        );
        break;
      case CommandType_VOUT_PK_PK:
        fields_type = (pb_field_t *)VoutPkPkResponse_fields;
        // `return_type`: float
        
        response.vout_pk_pk.result =
        obj_.vout_pk_pk();
        break;
      case CommandType_DESCRIPTION_STRING:
        fields_type = (pb_field_t *)DescriptionStringResponse_fields;
        // `return_type`: ('uint8_t', 'array', 'UInt8Array')
        
        response.description_string.result.funcs.encode = &write_byte_array;
        response.description_string.result.arg = &return_array_.uint8_t_;
        return_array_.uint8_t_ =
        
        obj_.description_string(
            request.description_string.key
        );
        break;default:
        return -1;
        break;
    }

    /* Serialize the response and write the encoded response to the buffer. */
    status = encode_unionmessage(&ostream, CommandResponse_fields, fields_type,
                                 &response);

    if (status) {
      return ostream.bytes_written;
    } else {
      return -1;
    }
  }
};

#endif  // #ifndef ___COMMAND_PROCESSOR___