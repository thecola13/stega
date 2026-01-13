# Python Steganography CLI Tool

This is a CLI tool for hiding messages inside .png images using steganography. Currently supports LSB (Least Significant Bit) steganography with optional randomization using a Linear Congruential Generator (LCG). 


## Installation

1.  Clone the repository or download the source code.
2.  Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the tool from the command line using `main.py`.

### Basic Usage

**Encrypt a message:**
```bash
python main.py -i input_image.png -o output_image.png -m "Secret Message"
```

**Decrypt a message:**
```bash
python main.py -i output_image.png -d
```

### Advanced Usage

**Encrypt with a text file and a secret key:**
```bash
python main.py -i cover.png -o secret.png -m secret_message.txt -k "my_secret_password"
```

**Decrypt with a key:**
```bash
python main.py -i secret.png -d -k "my_secret_password"
```

### Command Line Arguments

| Argument | Flag | Description |
| :--- | :--- | :--- |
| **Input Image** | `-i`, `--input_image` | **Required.** Path to the source .png image. |
| **Output Path** | `-o`, `--output_path` | Path for the saved image (default: `out.png`). Ignored in decryption mode. |
| **Message** | `-m`, `--message` | The string to hide OR a path to a `.txt` file containing the message. |
| **Mode** | `-e`, `--encrypt` | Encrypt mode (default). |
| **Mode** | `-d`, `--decrypt` | Decrypt mode. |
| **Key** | `-k`, `--key` | Optional password/key. If provided, it seeds the random pixel path generator. |
| **Framework** | `-f`, `--framework` | Steganography method (currently supports `lsb`). |
| **Verbose** | `-v`, `--verbose` | Output verbosity level (default: 1). |

## How it Works

### LSB (Least Significant Bit)
The tool modifies the last bit of the Red, Green, and Blue values of a pixel. 
- **Capacity**: Each pixel can store 3 bits of data.
- **Protocol**: The message is converted to binary. A 16-bit "stop sequence" (`1111111111111110`) is appended to the end. The bits are written sequentially or randomly into the image pixels.

### StegaLCG (Randomization)
If a `-k` (key) is provided, the tool allows for "Random Interval LSB". Instead of writing to pixels (0,0), (0,1), (0,2)... in order, it uses a generator to visit pixels in a pseudo-random order determined by the key.
1.  **Seed Generation**: The sum of ASCII values of the key characters is used to generate a seed.
2.  **LCG Algorithm**: A standard Linear Congruential Generator ($X_{n+1} = (aX_n + c) \mod m$) produces the sequence of coordinates. 
    - The parameters $a$ and $c$ are dynamically calculated based on the image size ($m = width \times height$) to ensure a full period (every pixel is visited exactly once).
