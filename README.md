# Huffman Compression CLI

A command-line file compression and decompression tool implemented from scratch in Python using Huffman coding. The tool reads a text file, builds a frequency table, constructs a Huffman tree via a min-heap, encodes the content to a bit string, packs it into bytes, and writes the result as a binary file with an embedded JSON codebook. Decompression reverses the process without any external dependencies.

## Tech stack

- Python 3 (standard library only — `heapq`, `json`, `argparse`, `collections.Counter`)

## Usage

```bash
# Compress
python main.py compress input.txt output.huff

# Decompress
python main.py decompress output.huff restored.txt
```

Example output:
```
[COMPRESS] 'input.txt' -> 'output.huff'
Original size:    45823 bytes
Compressed size:  27481 bytes (59.97% of original)
```

## File format

The `.huff` binary format is:

```
[ 4 bytes: codebook length (big-endian uint32) ]
[ N bytes: codebook as UTF-8 JSON              ]
[ remaining bytes: padded bit-packed data       ]
```

The first byte of the bit data encodes how many padding bits were added to reach a multiple of 8, allowing exact reconstruction.

## What I learned

Implementing Huffman coding end-to-end — rather than using a library — meant dealing with the details that are usually abstracted away: managing the min-heap ordering for nodes with equal frequency, handling the edge case of single-character files, and designing a self-contained binary format that embeds the codebook so no separate file is needed for decompression. Getting the bit padding and unpacking logic right (particularly the boundary between the padding-length byte and the actual data) required careful off-by-one thinking.
