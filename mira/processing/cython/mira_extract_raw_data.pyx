cimport cython
import numpy as np
cimport numpy as np
from numpy cimport uint8_t, uint16_t, uint32_t

@cython.cdivision(True)
@cython.nonecheck(False)
@cython.wraparound(False)
@cython.boundscheck(False)
cdef uint16_t manual_packbits_header(uint8_t[:] arr, uint16_t start, uint16_t end) nogil:
    cdef uint16_t i
    cdef uint16_t result = 0  
    for i in range(start, end):
        result = (result << 1) | arr[i]
    return <uint16_t> result

@cython.cdivision(True)
@cython.nonecheck(False)
@cython.wraparound(False)
@cython.boundscheck(False)
cpdef uint32_t[:] prefix_header_cy(uint8_t[:] raw_header):
    cdef uint16_t i
    cdef uint8_t[:] unpacked_header = np.unpackbits(raw_header)
    cdef uint32_t[:] header_values = np.zeros(9, np.uint32)
    cdef uint16_t temp_value

    # Example for 'sync_word1' and 'sync_word0'
    header_values[0] = manual_packbits_header(raw_header, 0, 12)
    header_values[1] = manual_packbits_header(raw_header, 12, 24)
    header_values[2] = manual_packbits_header(unpacked_header, 24, 36)
    header_values[3] = manual_packbits_header(unpacked_header, 36, 48)
    header_values[4] = manual_packbits_header(unpacked_header, 48, 60)
    
    temp_array = np.packbits(unpacked_header[60:70])
    header_values[5] = ((temp_array[0] << 2) | (temp_array[1] >> 6))
    temp_array = np.packbits(unpacked_header[70:72])
    header_values[6] = temp_array[0] >> 6
    header_values[7] = 0
    header_values[8] = 0

    return header_values

# Assuming MAX_NUM_SAMPLES and MAX_NUM_ACTIVE_RX are predefined constants
cdef uint16_t MAX_NUM_SAMPLES = 2048
cdef uint8_t MAX_NUM_ACTIVE_RX = 4

# Static buffer allocation
cdef uint16_t[:, :] RAW_DATA_SAMPLES = np.zeros((MAX_NUM_SAMPLES, MAX_NUM_ACTIVE_RX), dtype=np.uint16)

@cython.cdivision(True)
@cython.nonecheck(False)
@cython.wraparound(False)
@cython.boundscheck(False)
cdef uint16_t get_first_half_word(uint8_t first_half, uint8_t second_half) nogil:
    return <uint16_t>((<uint16_t>first_half << 4) & 0x0FF0) | ((<uint16_t>second_half >> 4) & 0x000F)

@cython.cdivision(True)
@cython.nonecheck(False)
@cython.wraparound(False)
@cython.boundscheck(False)
cdef uint16_t get_second_half_word(uint8_t first_half, uint8_t second_half) nogil:
    return <uint16_t>((<uint16_t>first_half << 8) & 0x0F00) | (<uint16_t>second_half & 0x00FF)

@cython.cdivision(True)
@cython.nonecheck(False)
@cython.wraparound(False)
@cython.boundscheck(False)
cpdef uint16_t[:,:] extract_raw_data_cy(uint8_t[:] raw_data_words, uint32_t n_data_words, uint16_t active_rx):
    cdef uint32_t byte_index = 0
    cdef uint32_t sample_index = 0
    cdef uint32_t rx_index = 0

    for i in range(n_data_words):
        if i % 2 == 0:
            RAW_DATA_SAMPLES[sample_index, rx_index] = \
                get_first_half_word(raw_data_words[byte_index], raw_data_words[byte_index + 1])
        else:
            RAW_DATA_SAMPLES[sample_index, rx_index] = \
                get_second_half_word(raw_data_words[byte_index + 1], raw_data_words[byte_index + 2])
            byte_index += 3  # This assumes sequential processing and may need adjustment for parallelization
        
        rx_index += 1
        if rx_index >= active_rx:
            rx_index = 0
            sample_index += 1
        if byte_index >= n_data_words:
            break

    return np.asarray(RAW_DATA_SAMPLES[:sample_index, :active_rx], np.uint16)

