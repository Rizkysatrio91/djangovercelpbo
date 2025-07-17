import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY tidak ditemukan di .env file.")

genai.configure(api_key=API_KEY)

# Inisialisasi model Gemini 
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def generate_response(prompt_text, chat_history=None, safety_settings=None, generation_config=None):
    """
    Menghasilkan respons dari Gemini berdasarkan prompt dan konteks.
    """
    try:
        # Jika ada history chat, gunakan untuk memulai sesi chat
        if chat_history:
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(
                prompt_text,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            return response.text, chat.history # Kembalikan teks dan history baru
        else:
            # Jika tidak ada history, kirim prompt tunggal
            response = model.generate_content(
                prompt_text,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            # Untuk kasus non-chat, history sederhana bisa dibuat manual jika diperlukan
            # atau cukup kembalikan teksnya saja.
            # Untuk konsistensi, kita bisa buat format history sederhana:
            new_history = [
                {'role': 'user', 'parts': [prompt_text]},
                {'role': 'model', 'parts': [response.text]}
            ]
            return response.text, new_history

    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        return "Maaf, terjadi kesalahan dalam memproses permintaan Anda.", []

def construct_prompt_with_rules_and_kb(user_input, rules, knowledge_base_entries):
    """
    Membangun prompt yang lebih kompleks dengan menyertakan aturan dan basis pengetahuan.
    """
    system_instructions = "Anda adalah chatbot yang membantu."

    # Tambahkan aturan ke instruksi sistem
    if rules:
        system_instructions += "\n\nPatuhi aturan berikut dengan ketat:\n"
        for rule in rules:
            system_instructions += f"- {rule.description}\n"
            if rule.allowed:
                system_instructions += f"  Anda BOLEH membahas topik terkait: {rule.topic}.\n"
            else:
                system_instructions += f"  Anda TIDAK BOLEH membahas topik terkait: {rule.topic}. Jika ditanya tentang ini, katakan Anda tidak bisa membahasnya.\n"

    relevant_kb = []
    if knowledge_base_entries:
        system_instructions += "\n\nGunakan informasi berikut sebagai basis pengetahuan Anda:\n"
        for entry in knowledge_base_entries:
            # Contoh sederhana: jika kata kunci ada di input pengguna
            if entry.keyword.lower() in user_input.lower():
                system_instructions += f"- Informasi terkait '{entry.keyword}': {entry.information}\n"
                relevant_kb.append(entry)
        if not relevant_kb and knowledge_base_entries: # Jika tidak ada yang cocok, berikan beberapa info umum
             system_instructions += "- Berikut adalah beberapa informasi umum yang mungkin berguna:\n"
             for i, entry in enumerate(knowledge_base_entries):
                 if i < 3: # Batasi jumlah info umum yang ditampilkan
                     system_instructions += f"  - {entry.keyword}: {entry.information}\n"


    final_prompt = f"{system_instructions}\n\nPertanyaan Pengguna: {user_input}"
    return final_prompt