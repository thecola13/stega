from termcolor import colored
from .lcg import StegaLCG
from .helpers import vprint


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

        coords_gen = StegaLCG(input_image.size[0], input_image.size[1], key) if key else [(x, y) for x in range(input_image.size[0]) for y in range(input_image.size[1])]

        for (x, y) in coords_gen:
            if msg_index < len(binary_msg):
                rs, gs, bs = pixels[x, y]

                # Modify Red
                if msg_index < len(binary_msg):
                    r = (rs & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                # Modify Green
                if msg_index < len(binary_msg):
                    g = (gs & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                # Modify Blue
                if msg_index < len(binary_msg):
                    b = (bs & ~1) | int(binary_msg[msg_index])
                    msg_index += 1

                print(f"Modified pixel [{x}, {y}]: ({rs}, {gs}, {bs}) --> ({r}, {g}, {b})")

                pixels[x, y] = (r, g, b)
            else:
                # Message finished, return the modified image object
                vprint("Successful encryption!", "success", 2, verbose)
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

        coords = StegaLCG(input_image.size[0], input_image.size[1], key) if key else [(x, y) for x in range(input_image.size[0]) for y in range(input_image.size[1])]

        for (x, y) in coords:
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
