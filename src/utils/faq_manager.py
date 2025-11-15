FAQ_MAP = {
    "Product Not Received": [
        "Apakah transaksi sudah lebih dari 10 menit?",
        "Apakah nomor tujuan sudah benar?",
        "Apakah kamu ingin kami cek status transaksi?"
    ],
    "Wrong Destination Number": [
        "Apakah kamu ingin kirim ulang ke nomor yang benar?",
        "Apakah kamu ingin refund saja?"
    ],
    "Request Refund": [
        "Apakah kamu ingin refund ke e-wallet atau rekening bank?",
        "Apakah kamu sudah punya ID transaksi?"
    ]
}

def get_faq_for_issue(issue_category: str) -> list[str]:
    return FAQ_MAP.get(issue_category, ["Mohon tunggu, kami sedang memproses laporanmu."])
