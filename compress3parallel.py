# -*- coding: utf-8 -*-
"""
Created on Sat Oct 25 07:53:11 2025

@author: deepj
"""

"""
Universal File Compressor v4 - Parallel + Original Filename Restoration
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import heapq
import pickle
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from math import ceil

# ------------------------------
# Core compression utilities
# ------------------------------

class Node:
    def __init__(self, byte=None, freq=None):
        self.byte = byte
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq

def huffman_compress_bytes(data: bytes):
    if not data:
        return b'', {}
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    heap = [Node(b, f) for b, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = Node(None, n1.freq + n2.freq)
        merged.left = n1
        merged.right = n2
        heapq.heappush(heap, merged)
    root = heap[0]
    codes = {}
    def build_codes(node, code=""):
        if node.byte is not None:
            codes[node.byte] = code
            return
        build_codes(node.left, code + "0")
        build_codes(node.right, code + "1")
    build_codes(root)
    encoded_bits = ''.join(codes[b] for b in data)
    padding = (8 - len(encoded_bits) % 8) % 8
    encoded_bits += '0' * padding
    header = bytes([padding])
    compressed = bytearray(header)
    for i in range(0, len(encoded_bits), 8):
        compressed.append(int(encoded_bits[i:i + 8], 2))
    return bytes(compressed), codes

def huffman_decompress_bytes(data: bytes, codes):
    if not data or not codes:
        return b''
    rev = {v: k for k, v in codes.items()}
    padding = data[0]
    bitstring = ''.join(format(byte, '08b') for byte in data[1:])
    if padding:
        bitstring = bitstring[:-padding]
    decoded = bytearray()
    temp = ''
    for bit in bitstring:
        temp += bit
        if temp in rev:
            decoded.append(rev[temp])
            temp = ''
    return bytes(decoded)

def lz77_compress_bytes(data: bytes, window_size=256):
    i = 0
    n = len(data)
    output = []
    while i < n:
        match = (0, 0, data[i:i+1])
        start = max(0, i - window_size)
        for j in range(start, i):
            length = 0
            while i + length < n and data[j + length] == data[i + length]:
                length += 1
                if j + length >= i:
                    break
            if length > match[1]:
                next_byte = data[i + length:i + length + 1] if i + length < n else b''
                match = (i - j, length, next_byte)
        output.append(match)
        i += match[1] + 1
    return output

def lz77_decompress_triplets(triplets):
    out = bytearray()
    for dist, length, nxt in triplets:
        if dist == 0:
            out += nxt
        else:
            start = len(out) - dist
            for k in range(length):
                out.append(out[start + k])
            out += nxt
    return bytes(out)

# Worker functions
def compress_chunk_worker(chunk_bytes: bytes):
    triplets = lz77_compress_bytes(chunk_bytes)
    serialized_triplets = pickle.dumps(triplets)
    huff_bytes, codes = huffman_compress_bytes(serialized_triplets)
    return pickle.dumps((huff_bytes, codes))

def decompress_chunk_worker(serialized_chunk: bytes):
    huff_bytes, codes = pickle.loads(serialized_chunk)
    decoded = huffman_decompress_bytes(huff_bytes, codes)
    triplets = pickle.loads(decoded)
    return lz77_decompress_triplets(triplets)

# ------------------------------
# Parallel compression / decompression
# ------------------------------

def compress_file_parallel(path: str, workers: int, progress_cb=None):
    with open(path, 'rb') as f:
        data = f.read()
    total_len = len(data)
    if total_len == 0:
        raise ValueError("File is empty")
    # chunk size
    target_chunk = max(1_048_576, ceil(total_len / (workers * 2)))
    chunks = [data[i:i+target_chunk] for i in range(0, total_len, target_chunk)]
    num_chunks = len(chunks)
    results = [None] * num_chunks

    with ProcessPoolExecutor(max_workers=workers) as exe:
        futures = {exe.submit(compress_chunk_worker, chunks[i]): i for i in range(num_chunks)}
        completed = 0
        for fut in as_completed(futures):
            idx = futures[fut]
            results[idx] = fut.result()
            completed += 1
            if progress_cb:
                progress_cb((completed / num_chunks) * 90)

    # store metadata including original filename
    meta = {
        "original_size": total_len,
        "num_chunks": num_chunks,
        "workers": workers,
        "chunk_lengths": [len(c) for c in chunks],
        "version": 1,
        "original_filename": os.path.basename(path)
    }
    out_path = path + ".hybinp"
    with open(out_path, 'wb') as f:
        pickle.dump(meta, f)
        for res in results:
            f.write(pickle.dumps(res))

    compressed_size = os.path.getsize(out_path)
    ratio = 100 - ((compressed_size / total_len) * 100)
    if progress_cb:
        progress_cb(100)
    return out_path, ratio

def decompress_file_parallel(path: str, workers: int, progress_cb=None):
    with open(path, 'rb') as f:
        meta = pickle.load(f)
        chunks_serialized = []
        while True:
            try:
                blob = pickle.load(f)
                chunks_serialized.append(blob)
            except EOFError:
                break

    num_chunks = len(chunks_serialized)
    results = [None] * num_chunks

    with ProcessPoolExecutor(max_workers=workers) as exe:
        futures = {exe.submit(decompress_chunk_worker, chunks_serialized[i]): i for i in range(num_chunks)}
        completed = 0
        for fut in as_completed(futures):
            idx = futures[fut]
            results[idx] = fut.result()
            completed += 1
            if progress_cb:
                progress_cb((completed / num_chunks) * 100)

    # restore original filename
    original_name = meta.get("original_filename", "file_restored")
    out_path = os.path.join(os.path.dirname(path), original_name)
    # avoid overwrite
    base, ext = os.path.splitext(out_path)
    counter = 1
    while os.path.exists(out_path):
        out_path = f"{base}_restored{counter}{ext}"
        counter += 1

    with open(out_path, 'wb') as f:
        for chunk in results:
            f.write(chunk)
    if progress_cb:
        progress_cb(100)
    return out_path

# ------------------------------
# GUI
# ------------------------------

def make_gui():
    root = tk.Tk()
    root.title("Universal File Compressor v4 - Parallel + Restore Format")
    root.geometry("560x400")
    root.resizable(False, False)

    tk.Label(root, text="Select File:", font=("Arial", 12)).pack(pady=10)
    entry_file = tk.Entry(root, width=60)
    entry_file.pack()
    def select_file():
        p = filedialog.askopenfilename(title="Select file to compress/decompress")
        entry_file.delete(0, tk.END)
        entry_file.insert(0, p)
    tk.Button(root, text="Browse", command=select_file).pack(pady=6)

    # workers selection
    frame_workers = tk.Frame(root)
    frame_workers.pack(pady=6)
    tk.Label(frame_workers, text="Workers (processes):").pack(side=tk.LEFT)
    workers_var = tk.IntVar(value=max(1, os.cpu_count() or 1))
    tk.Spinbox(frame_workers, from_=1, to=max(1, (os.cpu_count() or 1)*2), textvariable=workers_var, width=6).pack(side=tk.LEFT, padx=8)

    # progress
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=500)
    progress_bar.pack(pady=12)

    label_status = tk.Label(root, text="", font=("Arial", 10))
    label_status.pack(pady=4)

    def safe_progress(v):
        root.after(0, progress_var.set, v)
        root.after(0, progress_bar.update_idletasks)
    def safe_status(txt):
        root.after(0, label_status.config, {"text": txt})

    def run_in_thread(fn, *args):
        thread = threading.Thread(target=fn, args=args)
        thread.daemon = True
        thread.start()

    def compress_action():
        path = entry_file.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning("Warning", "Select a valid file first.")
            return
        workers = workers_var.get()
        progress_var.set(0)
        safe_status("Compressing in parallel...")

        def proc():
            try:
                out, ratio = compress_file_parallel(path, workers, progress_cb=safe_progress)
                safe_status(f"Compression complete. Saved: {ratio:.2f}%")
                messagebox.showinfo("Success", f"Compressed:\n{out}\nSaved: {ratio:.2f}%")
            except Exception as e:
                safe_status("Compression failed")
                messagebox.showerror("Error", str(e))

        run_in_thread(proc)

    def decompress_action():
        path = entry_file.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning("Warning", "Select a valid file first.")
            return
        workers = workers_var.get()
        progress_var.set(0)
        safe_status("Decompressing in parallel...")

        def proc():
            try:
                out = decompress_file_parallel(path, workers, progress_cb=safe_progress)
                safe_status("Decompression complete.")
                messagebox.showinfo("Success", f"Decompressed:\n{out}")
            except Exception as e:
                safe_status("Decompression failed")
                messagebox.showerror("Error", str(e))

        run_in_thread(proc)

    tk.Button(root, text="Compress (Parallel)", bg="lightgreen", command=compress_action).pack(pady=8)
    tk.Button(root, text="Decompress (Parallel)", bg="lightblue", command=decompress_action).pack(pady=6)

    tk.Label(root, text="Tip: Run this script from command line for best reliability on Windows.", font=("Arial", 9, "italic")).pack(pady=10)

    return root

# ------------------------------
# Entrypoint
# ------------------------------
def main():
    root = make_gui()
    root.mainloop()

if __name__ == "__main__":
    main()
