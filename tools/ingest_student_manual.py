#!/usr/bin/env python3
"""
ingest_student_manual.py
Parses FEMA ICS Student Manual PDFs using PyMuPDF.
Chunks the document by 'Visual' or 'Slide' boundaries, and utilizes the
Gemini LLM with Structured Outputs to synthesize comprehensible HTML training.
Maintains a continuous story state to provide narrative continuity across lessons.
Maintains a Global Glossary Context Engine to cross-reference acronyms and
concepts seamlessly across multiple courses.
"""

import os
import sys
import re
import csv
import json
import time
import argparse
import hashlib
import fitz  # PyMuPDF
from typing import Optional

try:
    from google import genai
    from google.genai import types
    from pydantic import BaseModel, Field
except ImportError:
    print("[!] ERROR: Required libraries are missing.")
    print("    Please run: pip install google-genai pydantic pymupdf")
    sys.exit(1)


# --- Pydantic Schemas for Strict JSON Enforcement ---
class ChoiceSchema(BaseModel):
    text: str = Field(description="The text of the multiple choice answer.")
    is_correct: bool = Field(
        description="True if this is the correct answer, False otherwise."
    )


class QuestionSchema(BaseModel):
    text: str = Field(description="The question text formatted as safe HTML.")
    explanation: str = Field(
        description="HTML explanation detailing exactly why the correct answer is right AND explicitly explaining why EACH and EVERY distractor is wrong."
    )
    choices: list[ChoiceSchema]


class GlossarySchema(BaseModel):
    term: str = Field(description="The acronym or key concept name.")
    definition: str = Field(
        default="",
        description="The concise definition of the term. Leave blank if providing an alias.",
    )
    alias_for: str = Field(
        default="",
        description="If this term is an abbreviation (e.g., 'IC'), provide the exact full term it stands for here (e.g., 'Incident Commander').",
    )


class LessonSchema(BaseModel):
    lesson_html: str = Field(
        description="The synthesized training lesson formatted as safe HTML paragraphs and lists. Must include the continuing story narrative seamlessly integrating the technical concepts."
    )
    story_arc_summary: str = Field(
        description="The top-level narrative tracking the overall plot. MUST be structured using the Pixar Story Spine framework (Once upon a time..., Every day..., One day..., Because of that..., Until finally...). Compress older 'Because of that' beats to keep this under 500 words. MUST include the strict roster of active characters, their titles, and dynamic bios that explicitly track their Character Arcs (their initial flaws/beliefs, how the crisis challenges them, and how applying ICS principles causes them to grow). MUST be plain text, NO HTML TAGS."
    )
    incident_status_log: str = Field(
        default="",
        description="A strict, bulleted running log of all tactical decisions made, ICS roles activated (even if filled by unnamed characters), and resources deployed. Update this continuously to act as the story's factual memory, preventing continuity errors (e.g., forgetting a role was already activated).",
    )
    video_title: Optional[str] = Field(
        default=None,
        description="If a video is referenced in the text, extract its exact title here.",
    )
    questions: list[QuestionSchema] = Field(default_factory=list)
    glossary_terms: list[GlossarySchema] = Field(default_factory=list)
    new_character_names: list[str] = Field(
        default_factory=list,
        description="List of the first and last names of any characters used in this story, to prevent reuse in future courses.",
    )
    new_scenario_description: str = Field(
        default="",
        description="If this chunk establishes the initial disaster scenario, provide a brief 1-sentence summary of the disaster to ban it from being reused in future courses.",
    )


# ----------------------------------------------------


# Regex patterns for filtering out boilerplate PDF headers and footers
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
HEADER_RE = re.compile(rf"^({MONTHS})\s+\d{{4}}$", re.IGNORECASE)
COURSE_RE = re.compile(r"^(?:IS|ICS|E|L|G)[\s\-]?\d+[a-zA-Z.]*:.*", re.IGNORECASE)
PAGE_RE = re.compile(r"^(?:SM|Page)[\s\-]?\d+$", re.IGNORECASE)

# Regex patterns for structural boundaries
UNIT_RE = re.compile(
    r"^(?:Lesson|Unit|Module)\s+([A-Za-z0-9.-]+)(?:[\s:\-]+(.*))?$", re.IGNORECASE
)
VISUAL_RE = re.compile(
    r"^(?:Visual|Slide)\s+([A-Za-z0-9.-]+)(?:[\s:\-]+(.*))?$", re.IGNORECASE
)

# Global sequence tracker initialized dynamically to prevent collisions
GLOBAL_SEQUENCE = 10


def setup_ai():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[!] ERROR: GEMINI_API_KEY environment variable is not set.")
        print("    Please export your key before running this script:")
        print("    export GEMINI_API_KEY='your_api_key_here'")
        sys.exit(1)

    return genai.Client(api_key=api_key)


def get_starting_sequence(output_dir):
    lesson_csv = os.path.join(output_dir, "ham.auxcomm.lesson.csv")
    max_seq = 0
    if os.path.exists(lesson_csv):
        with open(lesson_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    seq = int(row.get("sequence", 0))
                    if seq > max_seq:
                        max_seq = seq
                except ValueError:
                    pass
    return max_seq + 10


def load_global_glossary(output_dir):
    """Loads the master cross-course glossary to pass to the AI context."""
    glossary_csv = os.path.join(output_dir, "ham.auxcomm.glossary.csv")
    gmap = {}
    if os.path.exists(glossary_csv):
        with open(glossary_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name", "").strip()
                if name:
                    gmap[name.lower()] = row
    return gmap


def save_global_glossary(output_dir, gmap):
    """Saves the entire cross-course glossary back to the CSV."""
    glossary_csv = os.path.join(output_dir, "ham.auxcomm.glossary.csv")
    os.makedirs(output_dir, exist_ok=True)
    with open(glossary_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "course_id:id", "name", "definition", "alias_for"]
        )
        writer.writeheader()
        # Sort alphabetically for consistency
        for key in sorted(gmap.keys()):
            if "alias_for" not in gmap[key]:
                gmap[key]["alias_for"] = ""
            writer.writerow(gmap[key])


def load_banned_names(output_dir):
    """Loads previously used character names to prevent reuse across courses."""
    banned_csv = os.path.join(output_dir, "ham.auxcomm.banned_names.csv")
    # Base list of AI clichés and previously flagged names
    names = {
        "Miller",
        "Eva",
        "Rostova",
        "Javi",
        "Davis",
        "Carter",
        "Petrova",
        "Alex",
        "Emma",
        "Sarah",
        "Ben",
    }
    if os.path.exists(banned_csv):
        with open(banned_csv, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                if row:
                    names.add(row[0].strip())
    return list(names)


def save_banned_names(output_dir, names):
    """Saves accumulated character names to prevent reuse across courses."""
    banned_csv = os.path.join(output_dir, "ham.auxcomm.banned_names.csv")
    os.makedirs(output_dir, exist_ok=True)
    with open(banned_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for name in sorted(set(names)):
            writer.writerow([name])


def load_banned_scenarios(output_dir):
    """Loads previously used scenarios to prevent reuse across courses."""
    banned_csv = os.path.join(output_dir, "ham.auxcomm.banned_scenarios.csv")
    scenarios = set()
    if os.path.exists(banned_csv):
        with open(banned_csv, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                if row:
                    scenarios.add(row[0].strip())
    return list(scenarios)


def save_banned_scenarios(output_dir, scenarios):
    """Saves accumulated scenarios to prevent reuse across courses."""
    banned_csv = os.path.join(output_dir, "ham.auxcomm.banned_scenarios.csv")
    os.makedirs(output_dir, exist_ok=True)
    with open(banned_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for scenario in sorted(set(scenarios)):
            writer.writerow([scenario])


def load_video_map(output_dir):
    video_csv = os.path.join(output_dir, "video_links.csv")
    vmap = {}
    if os.path.exists(video_csv):
        with open(video_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    vmap[row[0].strip()] = row[1].strip()
    return vmap


def save_video_map(output_dir, vmap):
    video_csv = os.path.join(output_dir, "video_links.csv")
    os.makedirs(output_dir, exist_ok=True)
    with open(video_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["video_title", "youtube_embed_url"])
        for title in sorted(vmap.keys()):
            writer.writerow([title, vmap[title]])


def upsert_course_record(output_dir, raw_course_code, course_title):
    course_csv = os.path.join(output_dir, "ham.auxcomm.course.csv")
    sanitized_code = re.sub(r"[^a-zA-Z0-9]", "", raw_course_code).lower()
    course_id = f"course_{sanitized_code}"

    fieldnames = ["id", "code", "name", "sequence"]
    existing_courses = []
    max_seq = 0
    found = False

    if os.path.exists(course_csv):
        with open(course_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames if reader.fieldnames else fieldnames
            for row in reader:
                existing_courses.append(row)
                if row.get("id") == course_id:
                    found = True
                try:
                    seq = int(row.get("sequence", 0))
                    if seq > max_seq:
                        max_seq = seq
                except ValueError:
                    pass

    if not found:
        new_course = {
            "id": course_id,
            "code": raw_course_code.upper(),
            "name": (
                course_title if course_title else f"{raw_course_code.upper()} Course"
            ),
            "sequence": max_seq + 10,
        }
        for f in fieldnames:
            if f not in new_course:
                new_course[f] = ""

        existing_courses.append(new_course)

        os.makedirs(output_dir, exist_ok=True)
        with open(course_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_courses)
        print(f"[*] Auto-provisioned parent course record: {course_id}")


def sanitize_text(text):
    """
    Removes weird PDF control characters (like backspaces, null bytes, vertical tabs)
    that confuse the LLM or cause it to output invalid JSON strings.
    Keeps legitimate whitespaces like \n, \r, and \t.
    """
    if not text:
        return ""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)


def synthesize_section_with_ai(
    client,
    model_name,
    title,
    raw_text,
    global_glossary,
    running_story_context,
    banned_names,
    banned_scenarios,
    debug=False,
):
    # Compact the global glossary for the prompt context window, handling aliases explicitly
    glossary_context = {}
    for v in global_glossary.values():
        if v.get("alias_for"):
            glossary_context[v["name"]] = f"Acronym/Alias for: {v['alias_for']}"
        else:
            glossary_context[v["name"]] = v.get("definition", "")

    glossary_json_str = json.dumps(glossary_context, indent=2)

    # Only apply the banned names and scenarios list if this is the very first chunk of a new course
    is_new_story = "No previous story state" in running_story_context
    if is_new_story:
        banned_names_str = (
            ", ".join(set(banned_names))
            if banned_names
            else "Miller, Eva, Rostova, Javi, Davis"
        )
        banned_scenarios_str = (
            " | ".join(set(banned_scenarios)) if banned_scenarios else "None"
        )

        naming_instruction = f"- CHARACTER NAMING: Use a mix of 50% diverse/uncommon names and 50% common names. You are STRICTLY FORBIDDEN from using these previously used or cliché names: {banned_names_str}. You must invent a completely new roster of names for this course."
        scenario_instruction = f"- REALISTIC BUT UNIQUE SCENARIOS: You MUST invent a realistic disaster scenario that ICS responders actually face in the real world. You are STRICTLY FORBIDDEN from using these previously used scenarios: {banned_scenarios_str}. Ensure the community name is completely new."
    else:
        naming_instruction = "- CHARACTER NAMING: Continue using the exact same characters established in the Previous Story State. Do not alter their names, titles, or professions. You MAY introduce new characters seamlessly if the incident expands and requires new roles."
        scenario_instruction = "- SCENARIO CONTINUITY: Continue the exact same disaster scenario established in the Previous Story State. Do not invent a new disaster."

    system_prompt = f"""
    You are an expert instructional designer and narrative non-fiction writer for emergency management (NIMS/ICS).
    Your target audience is a FIRST-TIME TRAINEE who has never taken an ICS course before.

    1. Continuous Narrative Transformation (NO CLASSROOMS):
       - Create a compelling, vivid, and emotionally resonant story that continues through the entire course.
       - NEVER break the fourth wall. NEVER place the characters in a classroom, a tabletop exercise, or a training simulation. They are real responders dealing with a live, unfolding crisis.
       {scenario_instruction}
       - HEMINGWAY-STYLE SETTING: Fully develop the setting using sensory details (sight, sound, smell, weather, physical textures) rather than directly describing emotions. Show, don't tell. Clearly establish the 1) Physical Location, 2) Time Period, 3) Culture/Society, and 4) Climate/Environment.
       - SPATIAL CONTINUITY: Avoid abrupt location transitions. If a character moves to a new location, narrate the movement. If an object (like a whiteboard, radio, or ICS form) is used, narrate exactly how it got there. Objects and locations must not magically 'pop up'.
       {naming_instruction}
       - STRUCTURE THE NARRATIVE USING PIXAR'S STORY SPINE: The overarching plot must follow: "Once upon a time... Every day... One day... Because of that... Because of that... Until finally... And ever since then...". Compress older 'Because of that' beats to keep this under 500 words.
       - The story thread MUST continue organically. Build out the story details, describing the sights, sounds, and evolving challenges of the active incident scene.
       - DO NOT "wave off" narrative or summarize dialogue (e.g., do not write "The chief asked for their answers and they responded"). Write the actual dialogue. Show, don't just tell.
       - MULTI-DIMENSIONAL CHARACTERS & ARCS: You MUST dynamically evolve their bios in the arc summary. Avoid flat stereotypes by giving them complex motivations, internal conflicts, and psychological vulnerabilities. Use contradictions (e.g., a stern leader showing unexpected kindness) and unique, memorable quirks. Make them ACTIVE decision-makers who drive the plot, interacting differently with various peers. Show, don't tell, their traits through behavior. Show how the stress of the incident and their application of ICS concepts forces them to learn, adapt, and grow. They are not static sock-puppets.
       - PLAIN TEXT MEMORY: Your `story_arc_summary` MUST be strictly plain text. Do NOT use HTML tags (like <dfn>) or markdown formatting in the summary.
       - INCIDENT STATUS LOG: You must maintain a strict, bulleted 'incident_status_log' tracking every tactical decision, ICS role activated (even if filled by unnamed 'red shirt'), and resource deployed. This acts as your factual memory to prevent continuity errors.

    2. Plain Language & Clean HTML:
       - Translate dense bureaucratic FEMA jargon into simple, accessible English.
       - Keep paragraphs short and use bold text (`<strong>`) for key terms.
       - Format as safe, modern HTML (using <p>, <ul>, <li>). Do NOT wrap it in <html> or <body> tags.
       - Remove references to "Instructor Notes" or "refer to your Student Manual."
       - NO CONTROL CHARACTERS: You are strictly forbidden from emitting raw escaped control characters like `\\b` (backspace). Only emit clean, valid text.

    3. Mentorship & Field Integration (NO EXTRACTION):
       - Do NOT extract tabletop exercises or activities. Integrate them directly into the story narrative (`lesson_html`).
       - If the raw text contains a classroom exercise, group activity, or form-filling (e.g., ICS forms), you MUST narrate the mentor character leading the junior responders through it step-by-step in the field.
       - Explicitly state the exact name and number of any ICS forms (e.g., "ICS Form 201") and narrate them completing it together, explaining the details.

    4. Exhaustive Testing (Questions):
       - You MUST create a multiple-choice question about EVERY new role and concept introduced in this section. Do not leave any concept untested.
       - STRICTLY ACADEMIC: Questions MUST test the technical ICS/NIMS concepts ONLY. DO NOT ask questions about the fictional narrative, the characters, or the specific events of the story. The questions must be universally applicable and usable in a standalone final exam or flashcard deck.
       - In the explanation field, you MUST explain why the correct choice is right AND explicitly explain why EACH AND EVERY distractor is wrong.

    5. Cross-Course Glossary Engine (NO HTML WRAPPING):
       - We maintain a global dictionary of terms across all courses. Here is the current index:
       {glossary_json_str}
       - DO NOT WRAP TERMS IN `<dfn>` TAGS in the `lesson_html`. The system will do this automatically later.
       - If the current text provides a SIGNIFICANTLY BETTER definition for an existing term, include it in your `glossary_terms` output to permanently upgrade the dictionary.
       - Extract any NEW key concepts to `glossary_terms`.
       - HANDLING ABBREVIATIONS/ACRONYMS: Do not duplicate definitions. If a term is an acronym (e.g., "IC"), extract it as a separate entry, leave its `definition` blank, and put the full term (e.g., "Incident Commander") in the `alias_for` field. The system will automatically link them.

    6. Video Integration: If the raw text references a specific FEMA video, extract its exact title into the `video_title` field. Do NOT generate HTML placeholders for it yourself.
    """

    user_prompt = f"Previous Story State (Continue from here):\n{running_story_context}\n\nSection Title: {title}\nRaw Text:\n{raw_text}"

    if debug:
        print("\n" + "=" * 70)
        print(f"--- DEBUG: AI INPUT FOR '{title}' ---")
        print(">>> SYSTEM PROMPT:")
        print(system_prompt)
        print("-" * 35)
        print(">>> USER PROMPT:")
        print(user_prompt)
        print("=" * 70 + "\n")

    # Retry up to 5 times for intermittent LLM failures or bad JSON formatting
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=LessonSchema,
                    temperature=0.8,
                ),
            )

            if debug:
                print("\n" + "=" * 70)
                print(f"--- DEBUG: AI OUTPUT FOR '{title}' (Attempt {attempt+1}) ---")
                print(response.text)
                print("=" * 70 + "\n")

            # Clean the LLM output before parsing to catch any hallucinations of raw control bytes
            clean_llm_output = sanitize_text(response.text)

            # strict=False protects against the LLM inserting unescaped newlines inside strings
            return json.loads(clean_llm_output, strict=False)

        except json.JSONDecodeError as json_err:
            print(f"      [~] JSON Parsing Error on attempt {attempt+1}: {json_err}")
            if attempt == 4:
                raise Exception(f"Invalid JSON returned after 5 attempts: {json_err}")

            print(
                "      [~] Detected malformed LLM output (control characters/bad JSON). Re-sending input..."
            )
            time.sleep(2)  # Fast retry since it's just a formatting hallucination

        except Exception as e:
            print(f"      [~] API Error on attempt {attempt+1}: {e}")
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt == 4:
                    raise Exception(f"Fatal Quota Exhaustion: {e}")
                time.sleep(4**attempt)  # Exponential backoff for strict rate limiting
            else:
                if attempt == 4:
                    raise Exception(f"Fatal API Error: {e}")
                time.sleep(2)

    raise Exception(f"Failed to synthesize section: {title} after 5 retries.")


def process_visual_chunk(
    client,
    model_name,
    course_code,
    unit,
    visual_range,
    title,
    combined_text,
    lessons_out,
    questions_out,
    choices_out,
    global_glossary,
    video_map,
    running_story_context,
    banned_names,
    new_names_this_course,
    banned_scenarios,
    new_scenarios_this_course,
    debug=False,
):
    global GLOBAL_SEQUENCE

    if (
        "knowledge check" in title.lower()
        or "review" in title.lower()
        and "course" not in title.lower()
    ):
        pass

    print(
        f"    -> AI Synthesizing: Unit {unit} | Visuals {visual_range} | {title[:50]}..."
    )

    ai_data = synthesize_section_with_ai(
        client,
        model_name,
        title,
        combined_text,
        global_glossary,
        running_story_context,
        banned_names,
        banned_scenarios,
        debug,
    )

    lesson_html = ai_data.get("lesson_html", "<p>Content missing.</p>")
    v_title = ai_data.get("video_title")

    # 1. Update Global Glossary Dictionary First (so new acronyms from this chunk are available for wrapping)
    for g_data in ai_data.get("glossary_terms", []):
        term = g_data.get("term", "").strip()
        definition = g_data.get("definition", "").strip()
        alias_for = g_data.get("alias_for", "").strip()
        if term and (definition or alias_for):
            term_key = term.lower()
            if term_key in global_glossary:
                if definition:
                    global_glossary[term_key]["definition"] = definition
                if alias_for:
                    global_glossary[term_key]["alias_for"] = alias_for
            else:
                sanitized_term = re.sub(r"[^a-z0-9]", "", term_key)[:25]
                term_hash = hashlib.md5(term_key.encode("utf-8")).hexdigest()[:6]
                g_id = f"glossary_{course_code}_{sanitized_term}_{term_hash}"
                global_glossary[term_key] = {
                    "id": g_id,
                    "course_id:id": f"course_{course_code}",
                    "name": term,
                    "definition": definition,
                    "alias_for": alias_for,
                }

    # 2. Programmatic HTML Wrap for Glossary Terms & Abbreviations
    # Sort terms by length descending ("Incident Commander" gets wrapped before "Command" or "IC")
    sorted_terms = sorted(
        global_glossary.values(), key=lambda x: len(x["name"]), reverse=True
    )

    # Split HTML into text nodes and tag nodes to avoid breaking existing HTML attributes (like <strong>)
    html_parts = re.split(r"(<[^>]+>)", lesson_html)
    replacements = {}

    for term_data in sorted_terms:
        term_name = term_data["name"]

        # Resolve alias if present
        alias = term_data.get("alias_for", "").strip()
        if alias and alias.lower() in global_glossary:
            target_def = global_glossary[alias.lower()].get("definition", "")
            term_def = f"{alias}: {target_def}".replace('"', "&quot;")
        else:
            term_def = term_data.get("definition", "").replace('"', "&quot;")

        # Skip empty definitions to prevent empty tooltips
        if not term_def:
            continue

        # Word boundary regex, case-insensitive
        if term_name.isupper() and len(term_name) <= 5:
            # For acronyms, enforce case sensitivity to avoid mismatching regular words
            pattern = re.compile(rf"\b({re.escape(term_name)})\b")
        else:
            pattern = re.compile(rf"\b({re.escape(term_name)})\b", re.IGNORECASE)

        def repl(match):
            token = f"@@GLOSSARY_{len(replacements)}@@"
            replacements[token] = (
                f'<dfn title="{term_def}" class="text-primary border-bottom border-primary" data-bs-toggle="tooltip" style="cursor:help;">{match.group(1)}</dfn>'
            )
            return token

        for i in range(
            0, len(html_parts), 2
        ):  # Even indices are pure text outside of tags
            if html_parts[i]:
                html_parts[i] = pattern.sub(repl, html_parts[i])

    lesson_html = "".join(html_parts)

    # Restore the tooltip placeholders to prevent nested <dfn> tags
    for token, html_str in replacements.items():
        lesson_html = lesson_html.replace(token, html_str)

    if v_title:
        existing_url = video_map.get(v_title, "").strip()
        if existing_url:
            iframe_html = f'<div class="video-container" style="text-align:center; margin-bottom:20px;"><iframe width="560" height="315" src="{existing_url}" frameborder="0" allowfullscreen></iframe></div>'
            lesson_html = iframe_html + lesson_html
        else:
            video_map[v_title] = ""
            placeholder = f'<div style="padding:20px; background-color:#ffcccc; border: 2px dashed red; text-align:center; margin-bottom:15px;"><strong>Missing Video Link</strong><br>Please add the YouTube embed URL for <em>"{v_title}"</em> to <strong>video_links.csv</strong> and re-run the ingestion script.</div>'
            lesson_html = placeholder + lesson_html

    lesson_id = f"lesson_{course_code}_{GLOBAL_SEQUENCE}"

    lessons_out.append(
        {
            "id": lesson_id,
            "course_id:id": f"course_{course_code}",
            "sequence": GLOBAL_SEQUENCE,
            "title": title.strip(),
            "content_html": lesson_html,
        }
    )

    for q_idx, q_data in enumerate(ai_data.get("questions", [])):
        q_id = f"q_{course_code}_{GLOBAL_SEQUENCE}_{q_idx+1}"
        questions_out.append(
            {
                "id": q_id,
                "lesson_id:id": lesson_id,
                "text": q_data.get("text", ""),
                "explanation": q_data.get("explanation", ""),
            }
        )

        for c_idx, c_data in enumerate(q_data.get("choices", [])):
            c_id = f"c_{course_code}_{GLOBAL_SEQUENCE}_{q_idx+1}_{c_idx+1}"
            choices_out.append(
                {
                    "id": c_id,
                    "question_id:id": q_id,
                    "text": c_data.get("text", ""),
                    "is_correct": "True" if c_data.get("is_correct") else "False",
                }
            )

    # Collect new names for this course so they aren't banned mid-story
    for name in ai_data.get("new_character_names", []):
        if name not in new_names_this_course:
            new_names_this_course.append(name)

    # Collect new scenario description so it isn't banned mid-story
    scenario_desc = ai_data.get("new_scenario_description", "").strip()
    if scenario_desc and scenario_desc not in new_scenarios_this_course:
        new_scenarios_this_course.append(scenario_desc)

    GLOBAL_SEQUENCE += 10

    # Return the updated story state to be fed into the next chunk
    arc_raw = ai_data.get("story_arc_summary", "")
    arc_clean = re.sub(r"<[^>]+>", " ", arc_raw)
    arc_clean = re.sub(r"\s+", " ", arc_clean).strip()

    log_raw = ai_data.get("incident_status_log", "")
    log_clean = re.sub(r"<[^>]+>", " ", log_raw)
    log_clean = re.sub(r"\s+", " ", log_clean).strip()

    # Extract the pure text from the lesson HTML to use as the scene memory
    raw_html = ai_data.get("lesson_html", "")
    pure_text_scene = re.sub(r"<[^>]+>", " ", raw_html)
    pure_text_scene = re.sub(r"\s+", " ", pure_text_scene).strip()

    if not arc_clean and not pure_text_scene:
        return running_story_context

    return f"--- OVERARCHING STORY ARC ---\n{arc_clean}\n\n--- INCIDENT STATUS LOG ---\n{log_clean}\n\n--- FULL NARRATIVE OF PREVIOUS SCENE ---\n{pure_text_scene}"


def merge_and_write_csv(filepath, new_data, fieldnames, course_code):
    retained_data = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (
                    f"_{course_code}_" not in row.get("id", "")
                    and row.get("course_id:id", "") != f"course_{course_code}"
                ):
                    retained_data.append(row)

    final_data = retained_data + new_data
    if not final_data:
        return

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)


def parse_manual(
    pdf_path,
    raw_course_code,
    course_title,
    output_dir,
    model_name,
    batch_size,
    debug=False,
):
    global GLOBAL_SEQUENCE
    course_code = re.sub(r"[^a-zA-Z0-9]", "", raw_course_code).lower()

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"[!] Failed to open PDF: {e}")
        sys.exit(1)

    if not course_title:
        for page in doc[:3]:
            for b in page.get_text("blocks"):
                t = sanitize_text(b[4].strip())
                if COURSE_RE.match(t):
                    course_title = t.replace("\n", " ")
                    break
            if course_title:
                break

    print(f"[*] Parsing {pdf_path} for Course: {raw_course_code.upper()}")
    print(
        f"[*] Using Model: {model_name} | Batch Size: {batch_size} slides per request"
    )

    upsert_course_record(output_dir, raw_course_code, course_title)
    client = setup_ai()

    GLOBAL_SEQUENCE = get_starting_sequence(output_dir)
    global_glossary = load_global_glossary(output_dir)
    video_map = load_video_map(output_dir)

    # Load previously banned names and scenarios to pass to the AI
    banned_names = load_banned_names(output_dir)
    banned_scenarios = load_banned_scenarios(output_dir)

    # Track new items invented during THIS course to save later
    new_names_this_course = []
    new_scenarios_this_course = []

    lessons = []
    questions = []
    choices = []

    current_unit = "0"
    current_visual = "0"
    current_title = ""
    current_blocks = []
    expecting_title = False

    # State tracking
    running_story_context = "No previous story state. This is the first module of a NEW course. Establish a realistic but unique disaster setting that ICS responders actually face, using the beginning of the Pixar Story Spine ('Once upon a time there was... Every day they... One day, [disaster strikes]...'). Establish a BRAND NEW roster of characters with diverse names (with explicit job titles/roles and rich bios detailing their starting flaws/inexperience for their character arc), and a vivid, unfolding live scenario. DO NOT put them in a classroom. They are on the ground responding to a real crisis.\n\n--- INCIDENT STATUS LOG ---\nNone."
    current_batch = []

    def flush_batch():
        nonlocal running_story_context
        if not current_batch:
            return

        start_unit = current_batch[0]["unit"]
        start_vis = current_batch[0]["visual"]
        end_vis = current_batch[-1]["visual"]
        visual_range = f"{start_vis}-{end_vis}" if start_vis != end_vis else start_vis

        title_texts = [b["title"] for b in current_batch]
        batch_title = " | ".join(title_texts)
        if len(batch_title) > 60:
            batch_title = f"{title_texts[0][:25]}... to {title_texts[-1][:25]}..."

        combined_text = ""
        for b in current_batch:
            combined_text += (
                f"\n\n--- Visual {b['visual']}: {b['title']} ---\n{b['text']}"
            )

        running_story_context = process_visual_chunk(
            client,
            model_name,
            course_code,
            start_unit,
            visual_range,
            batch_title,
            combined_text,
            lessons,
            questions,
            choices,
            global_glossary,
            video_map,
            running_story_context,
            banned_names,
            new_names_this_course,
            banned_scenarios,
            new_scenarios_this_course,
            debug,
        )
        current_batch.clear()

    try:
        for page in doc:
            blocks = page.get_text("blocks")
            for b in blocks:
                text = b[4].strip()
                # Sanitize the raw PDF text to prevent control character injection to the LLM
                text = sanitize_text(text)

                if not text:
                    continue

                if (
                    HEADER_RE.match(text)
                    or COURSE_RE.match(text)
                    or PAGE_RE.match(text)
                    or text == "Contents"
                ):
                    continue

                if expecting_title:
                    current_title = text.replace("\n", " ").strip()
                    expecting_title = False
                    continue

                unit_match = UNIT_RE.match(text.replace("\n", " "))
                if unit_match:
                    current_unit = (
                        unit_match.group(1).replace("-", "_").replace(".", "_")
                    )
                    continue

                visual_match = VISUAL_RE.match(text.replace("\n", " "))
                if visual_match:
                    if current_title and len(" ".join(current_blocks)) > 50:
                        current_batch.append(
                            {
                                "unit": current_unit,
                                "visual": current_visual,
                                "title": current_title,
                                "text": "\n".join(current_blocks),
                            }
                        )
                        if len(current_batch) >= batch_size:
                            flush_batch()

                    current_visual = (
                        visual_match.group(1).replace("-", "_").replace(".", "_")
                    )
                    title_part = visual_match.group(2)

                    if title_part and title_part.strip():
                        current_title = title_part.strip()
                    else:
                        expecting_title = True
                        current_title = f"Visual {current_visual}"

                    current_blocks = []
                    continue

                if current_title and not expecting_title:
                    current_blocks.append(text)

        # Flush any remaining blocks at the end of the document
        if current_title and len(" ".join(current_blocks)) > 50:
            current_batch.append(
                {
                    "unit": current_unit,
                    "visual": current_visual,
                    "title": current_title,
                    "text": "\n".join(current_blocks),
                }
            )
        flush_batch()
        print("\n[*] PDF fully parsed successfully.")

    except (Exception, KeyboardInterrupt) as e:
        print(f"\n[!] Parsing interrupted or failed: {e}")
        print(
            "[*] Catching exception... Saving partial progress to CSVs to prevent data loss."
        )

    if len(lessons) == 0:
        print("\n[!] WARNING: Zero lessons were extracted. Nothing to save.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    lesson_csv = os.path.join(output_dir, "ham.auxcomm.lesson.csv")
    merge_and_write_csv(
        lesson_csv,
        lessons,
        ["id", "course_id:id", "sequence", "title", "content_html"],
        course_code,
    )

    question_csv = os.path.join(output_dir, "ham.auxcomm.question.csv")
    merge_and_write_csv(
        question_csv,
        questions,
        ["id", "lesson_id:id", "text", "explanation"],
        course_code,
    )

    choice_csv = os.path.join(output_dir, "ham.auxcomm.choice.csv")
    merge_and_write_csv(
        choice_csv, choices, ["id", "question_id:id", "text", "is_correct"], course_code
    )

    save_global_glossary(output_dir, global_glossary)
    save_video_map(output_dir, video_map)

    # Save the newly invented characters and scenarios to the permanent ban lists
    banned_names.extend(new_names_this_course)
    save_banned_names(output_dir, banned_names)

    banned_scenarios.extend(new_scenarios_this_course)
    save_banned_scenarios(output_dir, banned_scenarios)

    print(
        f"\n[*] Extracted: {len(lessons)} Batched Lessons, {len(questions)} Questions."
    )
    print("[+] Database seeding files updated successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest FEMA ICS Student Manual PDFs using AI synthesis."
    )
    parser.add_argument("input_pdf", help="Path to the FEMA Student Manual PDF")
    parser.add_argument(
        "--course",
        required=True,
        help="Course code prefix (e.g., is100, is200, ics300)",
    )
    parser.add_argument(
        "--title",
        help="Human readable course title (e.g., 'IS-100: Introduction to ICS')",
    )
    parser.add_argument(
        "--outdir",
        default="ham_auxcomm_training/data",
        help="Output directory for the CSVs",
    )
    parser.add_argument(
        "--model",
        default="gemini-3.1-pro-preview",
        help="Gemini model to use (default: gemini-3.1-pro-preview). Use gemini-2.5-pro if you are rate-limited.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Number of slides to batch into a single AI prompt to save quota (default: 4).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print exact AI prompts and responses to the console for debugging.",
    )

    args = parser.parse_args()
    parse_manual(
        args.input_pdf,
        args.course,
        args.title,
        args.outdir,
        args.model,
        args.batch_size,
        args.debug,
    )
