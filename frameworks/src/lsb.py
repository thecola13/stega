from termcolor import colored
from .lcg import StegaLCG
from .helpers import vprint
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
    try:
        pixels = input_image.load()
        msg_index = 0
        binary_msg = ''.join(format(ord(i), '08b') for i in msg) + '1111111111111110'
        
        vprint(f"Starting Encryption...", "info", 2, verbose)

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

                vprint(f"Modified pixel [{x}, {y}]: ({rs}, {gs}, {bs}) --> ({r}, {g}, {b})", "info", 4, verbose)

                pixels[x, y] = (r, g, b)
                
                if msg_index >= len(binary_msg):
                     vprint("Successful encryption!", "success", 2, verbose)
                     pbar.close()
                     return input_image
            else:
                # Message finished, return the modified image object
                vprint("Successful encryption!", "success", 2, verbose)
                pbar.close()
                return input_image 

    except Exception as e:
        vprint(f"Error encrypting message: {e}", "error", 0, verbose)
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
    try:
        pixels = input_image.load()
        binary_data = ""
        stop_sequence = "1111111111111110"
        
        vprint("Starting Decryption...", "info", 2, verbose)

        coords = StegaLCG(input_image.size, key) if key else \
                        [(x, y) for x in range(input_image.size[0]) for y in range(input_image.size[1])]

        for (x, y) in tqdm(coords, total=coords.m, desc="Decoding bits", unit="bit"):
            r, g, b = pixels[x, y]

            # Extract the LSB from each channel
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

            vprint(f"Working on pixel [{x}, {y}], extracted data {binary_data[-3:]}", "info", 4, verbose)

            # Check if the stop sequence is in our binary data
            if stop_sequence in binary_data:
                # Cut off the stop sequence
                msg_binary = binary_data[:binary_data.index(stop_sequence)]
                
                # Convert binary to characters
                # We split into 8-bit chunks and convert to int, then char
                all_bytes = [msg_binary[i:i+8] for i in range(0, len(msg_binary), 8)]
                decoded_msg = "".join(chr(int(byte, 2)) for byte in all_bytes)
                
                vprint("Successfully decrypted the message!", "success", 2, verbose)
                return decoded_msg

        vprint("No hidden message found (stop sequence never reached).", "warning", 1, verbose)
        return None

    except Exception as e:
        vprint(f"Error decrypting message: {e}", "error", 0, verbose)
        return None

def lsb_capacity(input_image, verbose = 0):
    available_bits = input_image.size[0] * input_image.size[1] * 3

    return available_bits
