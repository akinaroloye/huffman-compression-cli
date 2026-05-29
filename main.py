import argparse
import heapq
import json
import os
from collections import Counter

# -------------------- Huffman Tree Node --------------------
class Node:
    def __init__(self, char, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):  # needed for heapq
        return self.freq < other.freq

# -------------------- Huffman Functions --------------------
def build_frequency_table(text):
    return Counter(text)

def build_huffman_tree(freq_table):
    heap = [Node(char, freq, None, None) for char, freq in freq_table.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)

    return heap[0] if heap else None

def build_codes(tree):
    codes = {}

    def _generate_codes(node, current_code):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = current_code
            return
        _generate_codes(node.left, current_code + "0")
        _generate_codes(node.right, current_code + "1")

    _generate_codes(tree, "")
    return codes

def encode_text(text, codes):
    return ''.join(codes[char] for char in text)

def decode_text(encoded_text, tree):
    decoded = []
    node = tree
    for bit in encoded_text:
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            decoded.append(node.char)
            node = tree
    return ''.join(decoded)

def rebuild_tree_from_codes(codes):
    root = Node(None)
    for char, code in codes.items():
        node = root
        for bit in code:
            if bit == '0':
                if not node.left:
                    node.left = Node(None)
                node = node.left
            else:
                if not node.right:
                    node.right = Node(None)
                node = node.right
        node.char = char
    return root

# -------------------- Bit Handling --------------------
def pad_encoded_text(encoded_text):
    """Pad encoded text to be multiple of 8 bits"""
    extra_padding = 8 - len(encoded_text) % 8
    for i in range(extra_padding):
        encoded_text += "0"
    padded_info = "{0:08b}".format(extra_padding)
    return padded_info + encoded_text

def remove_padding(padded_encoded_text):
    padded_info = padded_encoded_text[:8]
    extra_padding = int(padded_info, 2)
    encoded_text = padded_encoded_text[8:]  
    return encoded_text[:-extra_padding]

def get_byte_array(padded_encoded_text):
    b = bytearray()
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i+8]
        b.append(int(byte, 2))
    return b

# -------------------- Compression/Decompression --------------------
def compress_file(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"[ERROR] Input file '{input_path}' not found.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = build_codes(tree)
    encoded_text = encode_text(text, codes)

    padded_encoded_text = pad_encoded_text(encoded_text)
    b = get_byte_array(padded_encoded_text)

    with open(output_path, "wb") as f:
        # store codes as JSON first, then delimiter, then binary data
        codes_json = json.dumps(codes).encode("utf-8")
        f.write(len(codes_json).to_bytes(4, "big"))  # store length of codes section
        f.write(codes_json)
        f.write(bytes(b))

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)
    ratio = compressed_size / original_size * 100

    print(f"[COMPRESS] '{input_path}' -> '{output_path}'")
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes ({ratio:.2f}% of original)")

def decompress_file(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"[ERROR] Input file '{input_path}' not found.")
        return

    with open(input_path, "rb") as f:
        codes_len = int.from_bytes(f.read(4), "big")
        codes_json = f.read(codes_len).decode("utf-8")
        codes = json.loads(codes_json)
        bit_data = f.read()

    bit_string = ""
    for byte in bit_data:
        bit_string += f"{byte:08b}"

    encoded_text = remove_padding(bit_string)
    tree = rebuild_tree_from_codes(codes)
    decoded_text = decode_text(encoded_text, tree)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(decoded_text)

    compressed_size = os.path.getsize(input_path)
    decompressed_size = os.path.getsize(output_path)
    print(f"[DECOMPRESS] '{input_path}' -> '{output_path}'")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Decompressed size: {decompressed_size} bytes")

# -------------------- CLI Interface --------------------
def main():
    parser = argparse.ArgumentParser(description="Huffman Compression Tool")
    parser.add_argument("mode", choices=["compress", "decompress"], help="Operation mode")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", help="Output file path")
    args = parser.parse_args()

    if args.mode == "compress":
        compress_file(args.input, args.output)
    else:
        decompress_file(args.input, args.output)

# -------------------- Entry Point --------------------
if __name__ == "__main__":
    main()
