import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 1. PENGATURAN KLIEN
# ----------------------------------------------------
# Memuat environment variable (OPENAI_API_KEY) dari file .env
load_dotenv()

# Inisialisasi klien OpenAI
# Klien akan secara otomatis membaca OPENAI_API_KEY dari environment
try:
    client = OpenAI()
except Exception as e:
    print(f"Error: Tidak dapat menginisialisasi klien OpenAI.")
    print("Pastikan Anda sudah mengatur OPENAI_API_KEY di file .env")
    exit()

# ----------------------------------------------------
# 2. FUNGSI ANALISIS (CORE LLM)
# ----------------------------------------------------
def analyze_complaint_with_llm(user_text: str) -> dict | None:
    """
    Mengirim teks komplain ke LLM dan meminta output JSON terstruktur.
    """
    
    # Ini adalah "otak" dari sistem Anda.
    # Prompt ini menginstruksikan LLM cara berperilaku dan format output.
    system_prompt = """
Anda adalah AI Customer Service yang bertugas menganalisis komplain.
Tugas Anda adalah mengubah teks komplain yang tidak terstruktur menjadi 
data JSON yang terstruktur.

Kategori Produk yang valid: [`Pulsa`, `Paket Data`, `Listrik PLN`, `E-Wallet`, `Lainnya`]
Kategori Masalah yang valid: [`Produk Belum Diterima`, `Salah Nomor Tujuan`, `Transaksi Gagal`, `Minta Refund`, `Lainnya`]

Analisis teks komplain berikut dan berikan output HANYA dalam format JSON.
Format JSON harus seperti ini:
{
  "kategori_produk": "...",
  "kategori_masalah": "...",
  "entities": {
    "nominal": (angka dalam integer, 100rb=100000, jika tidak ada = null),
    "nomor_salah": (string, jika tidak ada = null),
    "nomor_baru": (string, jika tidak ada = null),
    "trx_id": (string, jika tidak ada = null)
  }
}
"""

    print(f"\n💬 Menganalisis Teks: '{user_text}'")
    try:
        # Menggunakan 'gpt-4o' untuk kemampuan pemahaman yang tinggi
        # Menggunakan 'response_format' untuk menjamin output JSON yang valid
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
        )
        
        response_content = response.choices[0].message.content
        
        # Mengubah string JSON dari LLM menjadi dictionary Python
        structured_data = json.loads(response_content)
        return structured_data

    except Exception as e:
        print(f"Error saat memanggil OpenAI API: {e}")
        return None

# ----------------------------------------------------
# 3. FUNGSI LOGIKA BISNIS (SIMULASI)
# ----------------------------------------------------
def handle_automation(data: dict):
    """
    Menerima data JSON terstruktur dan memutuskan tindakan apa yang harus diambil.
    """
    
    print("\n--- 🤖 Menerima Output LLM ---")
    # Mencetak JSON dengan format yang rapi
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("--- 🚀 Menjalankan Logika Bisnis ---")
    
    try:
        masalah = data.get("kategori_masalah")
        entities = data.get("entities", {})

        # Skenario 1: Salah Nomor Tujuan
        if masalah == "Salah Nomor Tujuan":
            nomor_baru = entities.get("nomor_baru")
            nominal = entities.get("nominal")
            produk = data.get("kategori_produk")
            
            if nomor_baru and nominal and produk:
                print(f"[LOGIC]: Mendeteksi 'Salah Nomor Tujuan'.")
                print(f"[ACTION]: MEMANGGIL API TRANSAKSI ULANG untuk produk '{produk}' senilai {nominal} ke nomor '{nomor_baru}'.")
                print("[REPLY]: Siap, transaksi sedang kami proses ulang ke nomor baru {nomor_baru}.")
            else:
                print(f"[LOGIC]: 'Salah Nomor Tujuan' terdeteksi, tapi data tidak lengkap.")
                print("[REPLY]: Baik, Anda ingin kirim ulang ke nomor berapa ya? (Eskalasi data tidak lengkap)")

        # Skenario 2: Minta Refund
        elif masalah == "Minta Refund":
            trx_id = entities.get("trx_id")
            if trx_id:
                print(f"[LOGIC]: Mendeteksi 'Minta Refund' untuk TRX ID: {trx_id}.")
                print(f"[ACTION]: MEMANGGIL API REFUND untuk transaksi {trx_id}.")
                print("[REPLY]: Baik, permintaan refund untuk transaksi {trx_id} sedang kami proses.")
            else:
                print(f"[LOGIC]: 'Minta Refund' terdeteksi, tapi TRX ID tidak ada.")
                print("[REPLY]: Mohon info nomor transaksi (TRX ID) yang ingin di-refund. (Eskalasi data tidak lengkap)")
        
        # Skenario 3: Produk Belum Diterima
        elif masalah == "Produk Belum Diterima":
            trx_id = entities.get("trx_id")
            print(f"[LOGIC]: Mendeteksi 'Produk Belum Diterima' (TRX ID: {trx_id or 'N/A'}).")
            print(f"[ACTION]: MEMANGGIL API CEK STATUS untuk transaksi {trx_id or 'N/A'}.")
            print("[REPLY]: Mohon ditunggu, sedang kami cek status transaksinya ya.")
        
        # Skenario Lainnya
        else:
            print(f"[LOGIC]: Kategori tidak terdefinisi ('{masalah}').")
            print("[ACTION]: Eskalasi ke agen CS.")
            print("[REPLY]: Mohon ditunggu, tim CS kami akan segera membantu Anda.")
            
    except Exception as e:
        print(f"Error pada logika bisnis: {e}")
        print("[ACTION]: Eskalasi ke agen CS karena error sistem.")

# ----------------------------------------------------
# 4. CONTOH EKSEKUSI
# ----------------------------------------------------
if __name__ == "__main__":
    
    # --- Contoh 1: Komplain salah nomor (lengkap) ---
    print("========================================")
    print("Contoh 1: Komplain Salah Nomor (Lengkap)")
    complaint_1 = "Kak, sy salah kirim pulsa 100rb ke 0812111. Harusnya ke 081999. ID transaksinya T5566. Bisa dibantu?"
    
    data_1 = analyze_complaint_with_llm(complaint_1)
    if data_1:
        handle_automation(data_1)

    # --- Contoh 2: Komplain refund (data kurang) ---
    print("\n========================================")
    print("Contoh 2: Komplain Refund (Data Kurang)")
    complaint_2 = "plsa 50rb saya gagal, tolong refund aja."
    
    data_2 = analyze_complaint_with_llm(complaint_2)
    if data_2:
        handle_automation(data_2)

    # --- Contoh 3: Komplain produk belum masuk (typo) ---
    print("\n========================================")
    print("Contoh 3: Produk Belum Diterima (Typo)")
    complaint_3 = "mas, token listrik 20k sy kok blm msk ya? ID: L9987"
    
    data_3 = analyze_complaint_with_llm(complaint_3)
    if data_3:
        handle_automation(data_3)