#!/usr/bin/env python3
import os
import sys
import csv
import json
import time
from PyPDF2 import PdfReader
from google import genai
from google.genai import types

# Map known PDF filenames to the pre-existing course XML IDs
COURSE_MAP = {
    "IS0100c_SM.pdf": "course_is100",
    "IS0200c-SM.pdf": "course_is200",
    "ICS-300-Student-Manual.pdf": "course_ics300",
    "smis0700b.pdf": "course_is700",
    "ICS-700-100-200-800-Overview-Training_4.11.23.pdf": "course_is700",
    "IS-800 B NRF Final Exam Questions.pdf": "course_is800",
}

SYS_PROMPT_LESSONS = """
You are an expert NIMS/ICS instructor.
Convert the following raw PDF text from a Student Manual into structured lessons.
Output valid JSON only. The JSON must be an array of objects.
Each object must have two keys:
1. 'title': A short, descriptive string.
2. 'content_html': A well-formatted HTML string using <p>, <ul>, <li>, and <strong> tags.
Do not include any markdown wrappers like ```json.
"""

SYS_PROMPT_EXAMS = """
You are an expert NIMS/ICS examiner.
Extract multiple-choice questions from the following raw PDF text.
You MUST provide an explanation that explicitly debunks the incorrect distractors based on NIMS doctrine.
Output valid JSON only. The JSON must be an array of objects.
Each object must have:
1. 'text': The question text (HTML string).
2. 'explanation': The debunking explanation (HTML string).
3. 'choices': An array of objects, each with 'text' (string) and 'is_correct' (boolean).
Do not include any markdown wrappers like ```json.
"""


def extract_text_from_pdf(filepath):
    """Extracts text from a PDF, chunked by every 10 pages to avoid token limits."""
    print(f"[*] Extracting text from {filepath}...")
    reader = PdfReader(filepath)

    # Government PDFs often use AES encryption with an empty password to restrict editing.
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as e:
            print(f"[!] Warning: Could not decrypt {filepath} with empty password: {e}")
            return []

    chunks = []
    current_chunk = ""

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            current_chunk += text + "\n\n"

        if (i + 1) % 10 == 0:
            chunks.append(current_chunk)
            current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def call_gemini(client, text_chunk, system_instruction):
    """Calls the Gemini API with structured JSON enforcement."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=text_chunk,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"[!] Gemini API Error: {e}")
        return []


def write_lessons_csv(lessons_data):
    dest = "ham_auxcomm_training/data/ham.auxcomm.lesson.csv"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    file_exists = os.path.exists(dest)

    with open(dest, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            writer.writerow(["id", "course_id:id", "sequence", "title", "content_html"])

        for row in lessons_data:
            writer.writerow(
                [
                    row["id"],
                    row["course_id"],
                    row["sequence"],
                    row["title"],
                    row["content_html"],
                ]
            )


def write_questions_csv(questions_data, choices_data):
    q_dest = "ham_auxcomm_training/data/ham.auxcomm.question.csv"
    c_dest = "ham_auxcomm_training/data/ham.auxcomm.choice.csv"

    q_exists = os.path.exists(q_dest)
    c_exists = os.path.exists(c_dest)

    with open(q_dest, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if not q_exists:
            writer.writerow(["id", "lesson_id:id", "text", "explanation"])
        for row in questions_data:
            writer.writerow(
                [row["id"], row["lesson_id"], row["text"], row["explanation"]]
            )

        with open(c_dest, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            if not c_exists:
                writer.writerow(["id", "question_id:id", "text", "is_correct"])
            for row in choices_data:
                writer.writerow(
                    [row["id"], row["question_id"], row["text"], row["is_correct"]]
                )


def process_pdfs(source_dir):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    global_lesson_seq = 10

    for filename in os.listdir(source_dir):
        if not filename.lower().endswith(".pdf"):
            continue

        course_id = COURSE_MAP.get(filename)
        if not course_id:
            print(f"[!] Warning: {filename} not found in COURSE_MAP. Skipping.")
            continue

        filepath = os.path.join(source_dir, filename)
        is_exam = "Exam" in filename or "Questions" in filename
        system_prompt = SYS_PROMPT_EXAMS if is_exam else SYS_PROMPT_LESSONS

        chunks = extract_text_from_pdf(filepath)

        for chunk_idx, chunk in enumerate(chunks):
            print(
                f"[*] Sending chunk {chunk_idx + 1}/{len(chunks)} of {filename} to Gemini..."
            )
            parsed_json = call_gemini(client, chunk, system_prompt)

            if not parsed_json:
                continue

            if is_exam:
                q_csv_data = []
                c_csv_data = []
                for q_idx, q in enumerate(parsed_json):
                    q_id = f"q_{course_id.split('_')[1]}_{chunk_idx}_{q_idx}"
                    # Attach to the first lesson of the course as a generic fallback anchor
                    lesson_id = f"lesson_{course_id.split('_')[1]}_01"

                    q_csv_data.append(
                        {
                            "id": q_id,
                            "lesson_id": lesson_id,
                            "text": q.get("text", ""),
                            "explanation": q.get("explanation", ""),
                        }
                    )

                    for c_idx, c in enumerate(q.get("choices", [])):
                        c_id = f"c_{q_id}_{c_idx}"
                        c_csv_data.append(
                            {
                                "id": c_id,
                                "question_id": q_id,
                                "text": c.get("text", ""),
                                "is_correct": c.get("is_correct", False),
                            }
                        )
                write_questions_csv(q_csv_data, c_csv_data)
            else:
                lesson_csv_data = []
                for l_idx, l in enumerate(parsed_json):
                    l_id = f"lesson_{course_id.split('_')[1]}_{chunk_idx}_{l_idx}"
                    lesson_csv_data.append(
                        {
                            "id": l_id,
                            "course_id": course_id,
                            "sequence": global_lesson_seq,
                            "title": l.get("title", "Extracted Lesson"),
                            "content_html": l.get("content_html", ""),
                        }
                    )
                    global_lesson_seq += 10
                write_lessons_csv(lesson_csv_data)

            # Anti-rate-limit jitter
            time.sleep(2)

    print("[+] PDF Ingestion and CSV Generation Complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ingest_auxcomm_pdfs.py <path_to_pdf_directory>")
        sys.exit(1)

    process_pdfs(sys.argv[1])
