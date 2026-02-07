from .lcg import StegaLCG
from .helpers import get_logger, log_info, log_success, log_warning, log_error, log_debug
from tqdm import tqdm


def lsb_encrypt(input_image, msg, key = None, verbose = 0):
    ''' 
    Helper function for encrypting the message using LSB steganography.

    Args:
        input_image (Image): Input image
        msg (str): Message to hide
        key (int): Key to use for random-path lsb
        verbose (int): Verbose level

    Returns:
        image: Encrypted image
    '''
    logger = get_logger()
    
    try:
        pixels = input_image.load()
        msg_index = 0
        binary_msg = ''.join(format(ord(i), '08b') for i in msg) + '1111111111111110'
        
        log_info("Starting Encryption...")

        coords_gen = StegaLCG(input_image.size, key) if key else \
                        [(x, y) for x in range(input_image.size[0]) for y in range(input_image.size[1])]

        pbar_enabled = 1 <= verbose <= 3
        total_bits = len(binary_msg)
        pbar = tqdm(total=total_bits, disable=not pbar_enabled, desc="Encoding bits", unit="bit")  

        for (x, y) in coords_gen:
            if msg_index < len(binary_msg):
                rs, gs, bs = pixels[x, y]
                r, g, b = rs, gs, bs

                # Modify Red
                if msg_index < len(binary_msg):
                    r = (r & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                    pbar.update(1)
                # Modify Green
                if msg_index < len(binary_msg):
                    g = (g & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                    pbar.update(1)
                # Modify Blue
                if msg_index < len(binary_msg):
                    b = (b & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                    pbar.update(1)

                log_debug(f"Modified pixel [{x}, {y}]: ({rs}, {gs}, {bs}) --> ({r}, {g}, {b})")

                pixels[x, y] = (r, g, b)
                
                if msg_index >= len(binary_msg):
                     log_success("Successful encryption!")
                     pbar.close()
                     return input_image
            else:
                # Message finished, return the modified image object
                log_success("Successful encryption!")
                pbar.close()
                return input_image 

    except Exception as e:
        log_error(f"Error encrypting message: {e}")
        return None

def lsb_decrypt(input_image, key = None, verbose = 0):
    ''' 
    Helper function for decrypting a message from an image using LSB.

    Args:
        input_image (Image): The image containing the hidden message
        verbose (int): Verbose level

    Returns:
        str: The extracted message
    '''
    logger = get_logger()
    
    try:
        pixels = input_image.load()
        binary_data = ""
        stop_sequence = "1111111111111110"
        
        log_info("Starting Decryption...")

        coords = StegaLCG(input_image.size, key) if key else \
                        [(x, y) for x in range(input_image.size[0]) for y in range(input_image.size[1])]
        
        total = coords.m if hasattr(coords, 'm') else len(coords)

        for (x, y) in tqdm(coords, total=total, desc="Decoding bits", unit="bit"):
            r, g, b = pixels[x, y]

            # Extract the LSB from each channel
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

            log_debug(f"Working on pixel [{x}, {y}], extracted data {binary_data[-3:]}")

            # Check if the stop sequence is in our binary data
            if stop_sequence in binary_data:
                # Cut off the stop sequence
                msg_binary = binary_data[:binary_data.index(stop_sequence)]
                
                # Convert binary to characters
                # We split into 8-bit chunks and convert to int, then char
                all_bytes = [msg_binary[i:i+8] for i in range(0, len(msg_binary), 8)]
                decoded_msg = "".join(chr(int(byte, 2)) for byte in all_bytes)
                
                log_success("Successfully decrypted the message!")
                return decoded_msg

        log_warning("No hidden message found (stop sequence never reached).")
        return None

    except Exception as e:
        log_error(f"Error decrypting message: {e}")
        return None

def lsb_capacity(input_image, verbose = 0):
    available_bits = input_image.size[0] * input_image.size[1] * 3

    return available_bits
