import heapq
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


# ---------------- Huffman Node ----------------
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # For heapq (min-heap)
    def __lt__(self, other):
        return self.freq < other.freq


# ---------------- Huffman Coding Class ----------------
class HuffmanCoding:
    def __init__(self):
        self.codes = {}
        self.reverse_mapping = {}

    # Build frequency dictionary
    def make_frequency_dict(self, text):
        frequency = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        return frequency

    # Build Huffman Tree
    def build_heap(self, frequency):
        heap = []
        for char, freq in frequency.items():
            node = Node(char, freq)
            heapq.heappush(heap, node)
        return heap

    def merge_nodes(self, heap):
        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            merged = Node(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(heap, merged)
        return heap

    def make_codes_helper(self, root, current_code):
        if root is None:
            return
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self, heap):
        root = heapq.heappop(heap)
        self.make_codes_helper(root, "")

    def get_encoded_text(self, text):
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for _ in range(extra_padding):
            encoded_text += "0"
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            messagebox.showerror("Error", "Encoded text not padded properly.")
            return None
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b

    # ---------------- Compression ----------------
    def compress(self, text):
        frequency = self.make_frequency_dict(text)
        heap = self.build_heap(frequency)
        heap = self.merge_nodes(heap)
        self.make_codes(heap)
        encoded_text = self.get_encoded_text(text)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        byte_array = self.get_byte_array(padded_encoded_text)
        return byte_array

    # ---------------- Decompression ----------------
    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-1 * extra_padding]
        return encoded_text

    def decode_text(self, encoded_text):
        current_code = ""
        decoded_text = ""
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                decoded_text += self.reverse_mapping[current_code]
                current_code = ""
        return decoded_text

    def decompress(self, bit_string):
        encoded_text = self.remove_padding(bit_string)
        decompressed_text = self.decode_text(encoded_text)
        return decompressed_text


# ---------------- GUI ----------------
class HuffmanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Huffman Coding Compression Tool")
        self.root.geometry("700x600")
        self.huffman = HuffmanCoding()

        tk.Label(root, text="Huffman Coding Compression Tool", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
        self.text_area.pack(pady=10)

        tk.Button(root, text="Compress", command=self.compress_text, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(root, text="Decompress", command=self.decompress_text, bg="#2196F3", fg="white").pack(pady=5)

        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=10)
        self.output_area.pack(pady=10)

    def compress_text(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text.")
            return
        byte_array = self.huffman.compress(text)
        compressed_bits = ''.join(format(byte, '08b') for byte in byte_array)
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, f"Compressed Binary Data:\n{compressed_bits}")

    def decompress_text(self):
        compressed_bits = self.output_area.get("1.0", tk.END).strip()
        if not compressed_bits:
            messagebox.showwarning("Warning", "No compressed data found.")
            return
        decompressed = self.huffman.decompress(compressed_bits)
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, f"Decompressed Text:\n{decompressed}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanApp(root)
    root.mainloop()
