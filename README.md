# Huffman Compression CLI

A command-line file compression tool built from scratch in Python using Huffman coding. No external dependencies. It builds a frequency table, constructs a Huffman tree via a min-heap, packs the encoded output into bytes, and writes a binary file with the codebook embedded as JSON so no separate dictionary is needed for decompression.

## Tech stack

- Python 3 (standard library only: `heapq`, `json`, `argparse`, `collections.Counter`)

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

The first byte of the bit data encodes how many padding bits were added to reach a multiple of 8, so decompression knows exactly where the real data ends.

## What I learned

Implementing this end-to-end rather than using a library meant dealing with the parts that are usually hidden: min-heap ordering when multiple nodes share the same frequency, handling single-character input files, and designing the binary format to be self-contained. The bit padding logic had some tricky boundary cases, particularly tracking the padding-length byte separately so decompression doesn't misread the last few bits.
