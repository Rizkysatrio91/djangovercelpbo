import sys

# Nama file input yang rusak dan file output yang akan kita buat
file_input = 'databackup_benar.json'
file_output = 'databackup_final.json'

print(f"Membaca file '{file_input}'...")

try:
    # Buka file input dengan encoding 'utf-8-sig' yang secara otomatis akan menangani dan menghapus BOM
    with open(file_input, 'r', encoding='utf-8-sig') as f_in:
        data = f_in.read()
    
    # Tulis ulang data ke file output baru dengan encoding 'utf-8' murni (tanpa BOM)
    with open(file_output, 'w', encoding='utf-8') as f_out:
        f_out.write(data)

    print(f"Berhasil! File bersih telah disimpan sebagai '{file_output}'.")
    print("\nSilakan jalankan 'loaddata' dengan file baru ini.")

except FileNotFoundError:
    print(f"ERROR: File '{file_input}' tidak ditemukan. Pastikan namanya sudah benar.")
except Exception as e:
    print(f"Terjadi error tak terduga: {e}")