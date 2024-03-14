import numpy as np
cimport numpy as np
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
# helper function to pack bits
cdef np.uint16_t manual_packbits_header(np.uint8_t[:] arr, int start, int end) nogil:
    cdef int i
    cdef np.uint16_t result = 0  
    for i in range(start, end):
        result = (result << 1) | arr[i]
    return result

def prefix_header(np.uint8_t[:] raw_header) -> dict:
    cdef dict header_dict = {}
    cdef np.uint8_t[:] unpacked_header = np.unpackbits(raw_header)
    cdef np.uint8_t[:] temp_array = np.empty(2, dtype=np.uint8)
    
    header_dict['sync_word1'] = manual_packbits_header(unpacked_header, 0, 12)
    header_dict['sync_word0'] = manual_packbits_header(unpacked_header, 12, 24)
    header_dict['frame_cnt'] = manual_packbits_header(unpacked_header, 24, 36)
    header_dict['shape_grp_cnt'] = manual_packbits_header(unpacked_header, 36, 48)
    header_dict['chirp_len'] = manual_packbits_header(unpacked_header, 48, 60)
    
    temp_array = np.packbits(unpacked_header[60:70])
    header_dict['sadc_val'] = ((temp_array[0] << 2) | (temp_array[1] >> 6))
    header_dict['temperature'] = 0
    header_dict['datarate'] = 0
    temp_array = np.packbits(unpacked_header[70:72])
    header_dict['cs'] = temp_array[0] >> 6
    
    return header_dict


# Predefine maximum sizes
cdef int MAX_NUM_SAMPLES = 2048
cdef int MAX_NUM_ACTIVE_RX = 4

# Static buffer allocation
cdef np.ndarray RAW_DATA_SAMPLES = np.zeros((MAX_NUM_SAMPLES, MAX_NUM_ACTIVE_RX), dtype=np.uint16)

@cython.boundscheck(False)
@cython.wraparound(False)
cdef np.uint16_t get_first_half_word(np.uint8_t first_half, np.uint8_t second_half) nogil:
    return ((<np.uint16_t>first_half << 4) & 0x0FF0) | ((<np.uint16_t>second_half >> 4) & 0x000F)

@cython.boundscheck(False)
@cython.wraparound(False)
cdef np.uint16_t get_second_half_word(np.uint8_t first_half, np.uint8_t second_half) nogil:
    return ((<np.uint16_t>first_half << 8) & 0x0F00) | (<np.uint16_t>second_half & 0x00FF)

@cython.boundscheck(False)
@cython.wraparound(False)
def extract_raw_data_cy(np.uint8_t[:] raw_data_words, int n_data_words, int active_rx):
    cdef int byte_index = 0
    cdef np.uint16_t sample_index = 0
    cdef int rx_index = 0
    
    # Loop through the data words, considering each set of 3 bytes gives 2 samples
    for i in range(n_data_words):
        if i % 2 == 0:  # First sample in the sequence
            sample = get_first_half_word(raw_data_words[byte_index], raw_data_words[byte_index + 1])
        else:  # Second sample in the sequence
            sample = get_second_half_word(raw_data_words[byte_index + 1], raw_data_words[byte_index + 2])
            byte_index += 3  # Move to the next set of bytes for the next samples
        
        # Store the sample
        RAW_DATA_SAMPLES[sample_index, rx_index] = sample
        
        # Increment and reset rx_index and sample_index as needed
        rx_index += 1
        if rx_index >= active_rx:
            rx_index = 0
            sample_index += 1
        if byte_index >= n_data_words:  # Ensure we don't go past the buffer
            break

    # Return the portion of the buffer that contains extracted data
    return RAW_DATA_SAMPLES[:sample_index, :active_rx]

