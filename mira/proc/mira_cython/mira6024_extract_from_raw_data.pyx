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
    cdef np.uint8_t[:] unpacked_header = np.unpackbits(raw_header)
    cdef np.uint8_t[:] temp_array = np.empty(2, dtype=np.uint8)
    
    cdef dict header_dict = {}
    
    header_dict['sync_word1'] = manual_packbits_header(unpacked_header, 0, 12)
    header_dict['sync_word0'] = manual_packbits_header(unpacked_header, 12, 24)
    header_dict['frame_cnt'] = manual_packbits_header(unpacked_header, 24, 36)
    header_dict['shape_grp_cnt'] = manual_packbits_header(unpacked_header, 36, 48)
    header_dict['chirp_len'] = manual_packbits_header(unpacked_header, 48, 60)
    
    temp_array = np.packbits(unpacked_header[60:70])
    header_dict['sadc_val'] = ((temp_array[0] << 2) | (temp_array[1] >> 6))
    header_dict['temperature'] = 0
    temp_array = np.packbits(unpacked_header[70:72])
    header_dict['cs'] = temp_array[0] >> 6
    
    return header_dict


@cython.cfunc
cdef np.uint8_t manual_packbits(np.uint8_t[:] bits) nogil:
    cdef int i
    cdef np.uint8_t result = 0
    for i in range(8):
        result |= bits[i] << (7 - i)
    return result

@cython.cfunc
cdef np.uint8_t manual_packbits_padded(np.uint8_t[:] bits) nogil:
    cdef int i
    cdef np.uint8_t result = 0
    # The loop runs for 4 bits as the array length is 4 in this case
    for i in range(len(bits)):
        result |= bits[i] << (3 - i)
    return result

@cython.boundscheck(False)
@cython.wraparound(False)
def extract_channels_cy(np.uint8_t[:] raw_data) -> np.ndarray:
    cdef int n_rows = raw_data.shape[0] // 6  # Each row after unpacking will have 6 uint8 elements (48 bits)
    cdef np.ndarray raw_data_np = np.array(raw_data, dtype=np.uint8)
    cdef np.uint8_t[:, :] data_block = np.unpackbits(raw_data_np.reshape(-1, 3), axis=1)
    cdef np.uint16_t[:, :] ch_data = np.zeros((n_rows, 4), dtype=np.uint16)
    
    cdef int j
    cdef np.uint8_t ch1_first, ch1_second, ch2_first, ch2_second
    cdef np.uint8_t ch3_first, ch3_second, ch4_first, ch4_second

    for j in range(n_rows):
        # Channel 1
        ch1_first = manual_packbits(data_block[j * 2, :8])
        ch1_second = manual_packbits_padded(data_block[j * 2, 8:12])
        ch_data[j, 0] = (ch1_first << 4) | ch1_second

        # Channel 2
        ch2_first = manual_packbits(data_block[j * 2, 12:20])
        ch2_second = manual_packbits_padded(data_block[j * 2, 20:])
        ch_data[j, 1] = (ch2_first << 4) | ch2_second

        # Channel 3
        ch3_first = manual_packbits(data_block[j * 2 + 1, :8])
        ch3_second = manual_packbits_padded(data_block[j * 2 + 1, 8:12])
        ch_data[j, 2] = (ch3_first << 4) | ch3_second

        # Channel 4
        ch4_first = manual_packbits(data_block[j * 2 + 1, 12:20])
        ch4_second = manual_packbits_padded(data_block[j * 2 + 1, 20:])
        ch_data[j, 3] = (ch4_first << 4) | ch4_second

    return np.asarray(ch_data, dtype=np.uint16)



@cython.boundscheck(False)
@cython.wraparound(False)
def rx_mode_3_cy(np.uint8_t[:, :] data_block, int n_rows) -> np.ndarray:
    cdef np.uint16_t[:, :] ch_data = np.zeros((n_rows, 4), dtype=np.uint16)
    cdef int i, row = 0, ch_counter = 0
    cdef np.uint8_t ch_x1_first, ch_x1_second

    for i in range(data_block.shape[0]):
        # First half of the row
        ch_x1_first = manual_packbits(data_block[i, :8])
        ch_x1_second = manual_packbits_padded(data_block[i, 8:12])
        ch_data[row, ch_counter] = (ch_x1_first << 4) | (ch_x1_second >> 4)
        ch_counter += 1

        if ch_counter >= 3:
            row += 1
            ch_counter = 0

        # Second half of the row
        ch_x1_first = manual_packbits(data_block[i, 12:20])
        ch_x1_second = manual_packbits_padded(data_block[i, 20:])
        ch_data[row, ch_counter] = (ch_x1_first << 4) | (ch_x1_second >> 4)
        ch_counter += 1

        if ch_counter >= 3:
            row += 1
            ch_counter = 0

    return np.asarray(ch_data, dtype=np.uint16)


@cython.boundscheck(False)
@cython.wraparound(False)
def rx_mode_2_cy(np.uint8_t[:, :] data_block, int n_rows) -> np.ndarray:
    cdef np.uint16_t[:, :] ch_data = np.zeros((n_rows, 4), dtype=np.uint16)
    cdef int j, row = 0, ch_counter = 0
    cdef np.uint8_t ch1_first, ch1_second

    for j in range(data_block.shape[0]):
        # First half of the row
        ch1_first = manual_packbits(data_block[j, :8])
        ch1_second = manual_packbits_padded(data_block[j, 8:12])
        ch_data[row, ch_counter] = (ch1_first << 4) | (ch1_second >> 4)
        ch_counter += 1

        if ch_counter >= 2:
            row += 1
            ch_counter = 0

        # Second half of the row
        ch1_first = manual_packbits(data_block[j, 12:20])
        ch1_second = manual_packbits_padded(data_block[j, 20:])
        ch_data[row, ch_counter] = (ch1_first << 4) | (ch1_second >> 4)
        ch_counter += 1

        if ch_counter >= 2:
            row += 1
            ch_counter = 0

    return np.asarray(ch_data, dtype=np.uint16)

@cython.boundscheck(False)
@cython.wraparound(False)
def rx_mode_1_cy(np.uint8_t[:, :] data_block, int n_rows) -> np.ndarray:
    cdef np.uint16_t[:, :] ch_data = np.zeros((n_rows, 4), dtype=np.uint16)
    cdef int j, row = 0
    cdef np.uint8_t ch1_first, ch1_second

    for j in range(data_block.shape[0]):
        # First half of the row
        ch1_first = manual_packbits(data_block[j, :8])
        ch1_second = manual_packbits_padded(data_block[j, 8:12])
        ch_data[row, 0] = (ch1_first << 4) | (ch1_second >> 4)
        row += 1

        # Second half of the row
        ch1_first = manual_packbits(data_block[j, 12:20])
        ch1_second = manual_packbits_padded(data_block[j, 20:])
        ch_data[row, 0] = (ch1_first << 4) | (ch1_second >> 4)
        row += 1

    return np.asarray(ch_data, dtype=np.uint16)



