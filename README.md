# Compressparallel
# Universal File Compressor v4 - Parallel + Original Filename Restoration

A high-performance file compression and decompression tool in Python, featuring parallel processing, Huffman + LZ77 hybrid compression, and original filename restoration. Built with a user-friendly GUI using Tkinter.

---

## Features

- **Hybrid Compression:** Combines LZ77 and Huffman encoding for better compression ratios.
- **Parallel Processing:** Utilizes multiple CPU cores for faster compression and decompression.
- **Original Filename Restoration:** Keeps track of the original filename when decompressing.
- **GUI Interface:** Easy-to-use interface with progress bars and status updates.
- **Cross-Platform:** Works on Windows, Linux, and macOS (requires Python 3.8+).

---

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/universal-file-compressor.git
    cd universal-file-compressor
    ```

2. Install dependencies:
    ```bash
    pip install tk
    ```

3. Run the application:
    ```bash
    python universal_compressor_v4.py
    ```

---

## Usage

### Compress a File
1. Click **Browse** to select a file to compress.
2. Set the number of worker processes (default = number of CPU cores).
3. Click **Compress (Parallel)**.
4. The compressed file will be saved with a `.hybinp` extension.
5. Compression ratio is displayed as a percentage of space saved.

### Decompress a File
1. Click **Browse** to select a `.hybinp` compressed file.
2. Set the number of worker processes.
3. Click **Decompress (Parallel)**.
4. The original file will be restored in the same directory (with filename restored and `_restored` added if a file exists).

---

## Technical Details

- **LZ77 Compression:** Converts input data to triplets (distance, length, next byte) for efficient encoding of repeated patterns.
- **Huffman Coding:** Further compresses serialized LZ77 triplets.
- **Parallel Execution:** Uses Python’s `concurrent.futures.ProcessPoolExecutor` for multi-process compression/decompression.
- **Progress Monitoring:** GUI shows real-time progress updates for each stage.

---

## Notes

- Large files benefit significantly from multiple CPU cores.
- Avoid running the GUI from an IDE on Windows due to potential multiprocessing issues; use the command line for best reliability.
- Supports any type of file (binary or text).

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Screenshots

*(Add GUI screenshots here to showcase the interface and progress bar)*

---

## Acknowledgments

- Python `tkinter` for GUI.
- Python `concurrent.futures` for parallel processing.
- Inspired by universal compression and hybrid algorithm techniques.

