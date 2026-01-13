from argparse import ArgumentParser
from termcolor import colored
import os
from PIL import Image

def vprint(msg, type = "info", level = 1, verbose = 1):
    ''' 
    Helper function to print messages. Different colors for different types.

    Args:
        msg (str): Message to print
        type (str): Type of message (info, success, warning, error)
        level (int): Level of message 
        verbose (int): Verbose level
    
    '''
    colors = {
        "info": "blue",
        "success": "green",
        "warning": "yellow",
        "error": "red"
    }
    if verbose >= level:
        print(colored(f"[{type}] {msg}", colors[type]))

def import_image(image_path, verbose):
    ''' 
    Helper function for loading the image.

    Args:
        image_path (str): Path to the image
        verbose (int): Verbose level

    Returns:
        image: Loaded image
    '''
    try:
        if not image_path.lower().endswith(".png"):
            raise Exception("Only .png files supported!")

        # Convert to RGB to ensure we always have 3 channels (R, G, B)
        image = Image.open(image_path).convert("RGB")
        vprint(f"Image imported successfully: {image_path}", "success", 2, verbose)
        return image
    except Exception as e:
        vprint(f"Error importing image: {e}", "error", 0, verbose)
        exit(1)

def export_image(img_obj, out_path, verbose):
    ''' 
    Helper function for exporting image.

    Args: 
        pixels (Image): Image to export
        out_path (str): Output path
        verbose (int): Verbose level
    '''
    try:
        # Save the IMAGE object, not the pixels
        img_obj.save(out_path)
        vprint(f"Image exported successfully: {out_path}", "success", 2, verbose)
    except Exception as e:
        vprint(f"Error exporting image: {e}", "error", 0, verbose)
        exit(1)

def message_type(string):
    '''
    Helper function to determine if the message is a string or a path

    Args:
        string (str): Message to hide

    Returns:
        str: Message
    '''
    if os.path.isfile(string):
        with open(string, 'r', encoding='utf-8') as f:
            return f.read()
    return string


def lsb_encrypt(input_image, msg, verbose):
    ''' 
    Helper function for encrypting the message using LSB steganography.

    Args:
        input_image (Image): Input image
        msg (str): Message to hide
        output_path (str): Output path
        verbose (int): Verbose level

    Returns:
        image: Encrypted image
    '''
    try:
        pixels = input_image.load()
        msg_index = 0
        binary_msg = ''.join(format(ord(i), '08b') for i in msg) + '1111111111111110'
        
        vprint(f"Starting Encryption...", "info", 2, verbose)

        for y in range(input_image.size[1]):
            for x in range(input_image.size[0]):
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

def lsb_decrypt(input_image, verbose):
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

        for y in range(input_image.size[1]):
            for x in range(input_image.size[0]):
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


def main():
    parser = ArgumentParser(description="Steganography tool in Python")
    parser.add_argument("-i", "--input_image", required=True, 
                    help="Input image path (only .png files supported)")
    parser.add_argument("-o", "--output_path", default = "out.png", required=False, 
                    help="Output path (if in decrypt mode, this will be ignored)")
    parser.add_argument("-m", "--message", required=False, type=message_type, 
                    help="Message to hide OR path to a .txt file containing the message")
    parser.add_argument("-e", "--encrypt", required=False, action="store_true", 
                    help="Encrypt mode (default)")
    parser.add_argument("-d", "--decrypt", required=False, action="store_true", 
                    help="Decrypt mode")

    parser.add_argument("-f", "--framework", default="lsb", choices=["lsb", "dct"], required=False, 
                    help="Steganography framework to use (default: lsb)")

    parser.add_argument("-v", "--verbose", default=1, required=False, type=int, 
                    help="Verbose mode")
    args = parser.parse_args()

    input_image = import_image(args.input_image, args.verbose)

    final_image = None

    if args.encrypt or not args.decrypt:
        final_image = None

        if args.framework == "lsb":
            final_image = lsb_encrypt(input_image, args.message, args.verbose)

        else:
            vprint(f"Your required framework {args.framework} is not available.", "error", 0, args.verbose)


        if final_image == None:
            vprint("Error happened during encryption", "error", 0, args.verbose)
        
        else: 
            export_image(final_image, args.output_path, args.verbose)
            vprint(f"Success! The message-embedded image was saved at {args.output_path}", "success", 1, args.verbose)
    
    elif args.decrypt:

        dec_msg = None

        if args.framework == "lsb":
            dec_msg = lsb_decrypt(input_image, args.verbose)

        else:
            vprint(f"Your required framework {args.framework} is not available.", "error", 0, args.verbose)

        if dec_msg != None:

            vprint(f"Decrypted message: {dec_msg}", "success", 0, args.verbose)
    
    

if __name__ == "__main__":
    main()