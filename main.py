from argparse import ArgumentParser
import os
from PIL import Image

from frameworks import (StegaLCG, 
                        lsb_encrypt, 
                        lsb_decrypt,
                        lsb_capacity,
                        setup_logger,
                        log_info,
                        log_success,
                        log_warning,
                        log_error)

def import_image(image_path):
    ''' 
    Helper function for loading the image.

    Args:
        image_path (str): Path to the image

    Returns:
        image: Loaded image
    '''
    try:
        if not image_path.lower().endswith(".png"):
            raise Exception("Only .png files supported!")

        # Convert to RGB to ensure we always have 3 channels (R, G, B)
        image = Image.open(image_path).convert("RGB")
        log_success(f"Image imported successfully: {image_path}")
        return image
    except Exception as e:
        log_error(f"Error importing image: {e}")
        exit(1)

def export_image(img_obj, out_path):
    ''' 
    Helper function for exporting image.

    Args: 
        pixels (Image): Image to export
        out_path (str): Output path
    '''
    try:
        # Save the IMAGE object, not the pixels
        img_obj.save(out_path)
        log_success(f"Image exported successfully: {out_path}")
    except Exception as e:
        log_error(f"Error exporting image: {e}")
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

def message_size(string):
    return len(string) * 8 + 16

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

    parser.add_argument("-k", "--key", required=False, type = str, 
                    help="Key to use for random-path lsb")

    parser.add_argument("-v", "--verbose", default=1, required=False, type=int, 
                    help="Verbose mode (0-4, higher = more output)")
    args = parser.parse_args()

    # Initialize the logger with the specified verbose level
    setup_logger(args.verbose)

    input_image = import_image(args.input_image)

    final_image = None

    if args.encrypt or not args.decrypt:
        final_image = None

        if args.framework == "lsb":

            log_info(f"Message size: {message_size(args.message)} bits")
            log_info(f"Image capacity: {lsb_capacity(input_image, args.verbose)} bits")

            if message_size(args.message) > lsb_capacity(input_image, args.verbose):
                log_error("Message is too large for the image.")
                exit(1)
            final_image = lsb_encrypt(input_image, args.message, args.key, args.verbose)

        else:
            log_error(f"Your required framework {args.framework} is not available.")


        if final_image == None:
            log_error("Error happened during encryption")
        
        else: 
            export_image(final_image, args.output_path)
            log_success(f"Success! The message-embedded image was saved at {args.output_path}")
    
    elif args.decrypt:

        dec_msg = None

        if args.framework == "lsb":

            capacity = lsb_capacity(input_image, args.verbose)
            dec_msg = lsb_decrypt(input_image, args.key, args.verbose)

        else:
            log_error(f"Your required framework {args.framework} is not available.")

        if dec_msg != None:

            log_success(f"Decrypted message: {dec_msg}")
    


if __name__ == "__main__":
    main()