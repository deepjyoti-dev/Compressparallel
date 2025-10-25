🗜️ CompressParallel

Universal File Compressor v4 — Parallel + Original Filename Restoration

A high-performance file compression and decompression tool built in Python.
Features parallel processing, hybrid LZ77 + Huffman compression, and original filename restoration with an easy-to-use Tkinter GUI.

✨ Features

⚡ Hybrid Compression: LZ77 + Huffman for superior compression ratios

🖥️ Parallel Processing: Utilizes multiple CPU cores for faster compression/decompression

📄 Original Filename Restoration: Restores filenames on decompression

🧩 GUI Interface: Progress bars and status updates for user-friendly interaction

🌐 Cross-Platform: Windows, Linux, macOS (Python 3.8+)

🔧 Installation

Clone the repository:

git clone https://github.com/yourusername/universal-file-compressor.git
cd universal-file-compressor


Install dependencies:

pip install tk


Run the application:

python universal_compressor_v4.py

🛠️ Usage
Compress a File

Click Browse and select a file

Set number of worker processes (default = CPU cores)

Click Compress (Parallel)

Compressed file saved as .hybinp

Compression ratio displayed

Decompress a File

Click Browse and select .hybinp file

Set number of worker processes

Click Decompress (Parallel)

Original file restored (adds _restored if filename exists)

🧠 Technical Details

LZ77 Compression: Converts input data into triplets (distance, length, next byte)

Huffman Coding: Further compresses LZ77 triplets

Parallel Execution: Uses concurrent.futures.ProcessPoolExecutor for multiprocessing

Progress Monitoring: GUI shows real-time progress updates

⚠️ Notes

Large files benefit significantly from multiple CPU cores

On Windows, run from command line rather than IDE for reliable multiprocessing

Supports any file type — text or binary

🏷️ Tags

#python #tkinter #compression #parallelprocessing #lz77 #huffman #gui #desktopapp

🧑‍💻 Author

Deepjyoti Das
🔗 [LinkedIn](https://www.linkedin.com/in/deepjyotidas1)

💻 GitHub
