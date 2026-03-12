import os
import re
import glob
import math
import fitz  # PyMuPDF


def sanitize_name(text, fallback_index):
    """Converts a native PDF field name into a safe HTML name attribute while preserving case and '#'."""
    if not text:
        return f"field_{fallback_index}"

    clean = re.sub(r"[^a-zA-Z0-9#]+", "_", text).strip("_")
    return clean if clean else f"field_{fallback_index}"


def parse_pdfs(input_dir="input_pdfs", output_dir="output_forms"):
    os.makedirs(output_dir, exist_ok=True)
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in '{input_dir}'.")
        return

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        out_filename = filename.replace(".pdf", ".html")
        print(f"Parsing: {filename}...")

        with fitz.open(pdf_path) as doc:

            title = doc.metadata.get("title")
            if not title:
                title = filename

            html_content = [
                "<!DOCTYPE html>",
                "<html><head>",
                f"<title>{title}</title>",
                "<meta charset='UTF-8'>",
                "<style>",
                "  body { background-color: #525659; display: flex; flex-direction: column; align-items: center; padding: 20px; font-family: Arial, sans-serif; margin: 0; }",
                "  .form-wrapper { width: 100%; max-width: 1600px; display: flex; flex-direction: column; align-items: center; }",
                "  .page-container { position: relative; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); background: white; width: 100%; container-type: inline-size; overflow: hidden; }",
                "  .form-field { position: absolute; background: rgba(173, 216, 230, 0.4); mix-blend-mode: multiply; border: none; box-sizing: border-box; font-family: Arial, sans-serif; resize: none; pointer-events: auto; overflow: hidden !important; scrollbar-width: none; -ms-overflow-style: none; color: darkgreen; z-index: 10; }",
                "  .form-field::-webkit-scrollbar { display: none; }",
                "  .form-field:focus { outline: 2px solid #0056b3; background: rgba(255, 255, 255, 0.95); mix-blend-mode: normal; }",
                "  input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }",
                "  input[type=number] { -moz-appearance: textfield; }",
                "  .checkbox-label { position: absolute; background: rgba(173, 216, 230, 0.4); mix-blend-mode: multiply; cursor: pointer; z-index: 15; pointer-events: auto; }",
                "  .checkbox-label:hover { background: rgba(173, 216, 230, 0.7); }",
                "  .custom-checkbox { position: absolute; background: transparent; cursor: pointer; z-index: 20; pointer-events: auto; appearance: none; -webkit-appearance: none; border: none !important; margin: 0; padding: 0; display: flex; align-items: center; justify-content: center; outline: none; }",
                "  .custom-checkbox:checked { background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='darkgreen' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E\") !important; background-size: contain !important; background-position: center !important; background-repeat: no-repeat !important; }",
                "</style></head><body>",
                f"<form action='/submit-ics-form' id='{filename.replace('.pdf', '')}_form' method='POST' class='form-wrapper'>",
            ]

            global_id_counter = 1

            for page_num in range(len(doc)):
                page = doc[page_num]
                rect = page.rect
                width, height = rect.width, rect.height
                x0, y0 = rect.x0, rect.y0

                raw_paths = page.get_drawings()
                paths = []
                drawn_boxes = []

                for p in raw_paths:
                    paths.append(p)
                    for item in p["items"]:
                        if item[0] == "re":
                            r = fitz.Rect(item[1])
                            if 5 <= r.width <= 40 and 5 <= r.height <= 40:
                                if 0.5 <= r.width / r.height <= 2.0:
                                    drawn_boxes.append(r)
                    pr = fitz.Rect(p["rect"])
                    if 5 <= pr.width <= 40 and 5 <= pr.height <= 40:
                        if 0.5 <= pr.width / pr.height <= 2.0:
                            drawn_boxes.append(pr)

                text_dict = page.get_text("dict")
                char_boxes = []
                numeric_labels = []
                cb_chars = [
                    "",
                    "☐",
                    "☑",
                    "☒",
                    "\u2610",
                    "\u2611",
                    "\u2612",
                    "\u25a1",
                    "\u25a0",
                ]

                for block in text_dict.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span["text"].strip()
                            if not text:
                                continue

                            # Log the structural bounds of Table Headers indicating numeric fields
                            if len(text) < 40:
                                text_lower = text.lower()
                                if "#" in text_lower or re.search(
                                    r"\b(num|nuber|number)\b", text_lower
                                ):
                                    numeric_labels.append(fitz.Rect(span["bbox"]))

                            font_lower = span.get("font", "").lower()
                            is_wingding = (
                                "dingbat" in font_lower or "wingding" in font_lower
                            )

                            is_checkbox_char = text in cb_chars or (
                                is_wingding and len(text) == 1
                            )

                            if is_checkbox_char:
                                r = fitz.Rect(span["bbox"])
                                if r.width >= 3 and r.height >= 3:
                                    sq_size = r.height * 0.85
                                    cx = ((r.x0 + r.x1) / 2) + (r.width * 0.05)
                                    cy = (r.y0 + r.y1) / 2
                                    char_boxes.append(
                                        fitz.Rect(
                                            cx - sq_size / 2,
                                            cy - sq_size / 2,
                                            cx + sq_size / 2,
                                            cy + sq_size / 2,
                                        )
                                    )

                raw_widgets = list(page.widgets())
                checkbox_widgets = []
                textfield_widgets = []

                for w in raw_widgets:
                    is_cb = False
                    name_lower = w.field_name.lower() if w.field_name else ""

                    if w.field_type in [
                        fitz.PDF_WIDGET_TYPE_CHECKBOX,
                        fitz.PDF_WIDGET_TYPE_RADIOBUTTON,
                    ]:
                        is_cb = True
                    elif w.field_type == fitz.PDF_WIDGET_TYPE_BUTTON:
                        if (
                            "submit" not in name_lower
                            and "print" not in name_lower
                            and "reset" not in name_lower
                        ):
                            is_cb = True
                    elif w.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                        if (
                            "check" in name_lower
                            or "chk" in name_lower
                            or "radio" in name_lower
                        ):
                            is_cb = True

                    if is_cb:
                        checkbox_widgets.append(w)
                    else:
                        textfield_widgets.append(w)

                field_idx = 1
                cb_visual_rects = {}
                mapped_boxes = set()

                available_boxes = list(drawn_boxes + char_boxes)
                checkbox_widgets.sort(key=lambda w: (w.rect.y0, w.rect.x0))

                for w in checkbox_widgets:
                    w_rect = fitz.Rect(w.rect)
                    best_box = None
                    best_dist = 999999

                    for b in available_boxes:
                        if b in mapped_boxes:
                            continue

                        dx = max(0, w_rect.x0 - b.x1, b.x0 - w_rect.x1)
                        dy = max(0, w_rect.y0 - b.y1, b.y0 - w_rect.y1)
                        dist = math.hypot(dx, dy)

                        intersect = w_rect.intersect(b)
                        if intersect.is_valid and intersect.get_area() > 0:
                            dist = -(intersect.get_area() / b.get_area())

                        if dist < best_dist:
                            best_dist = dist
                            best_box = b

                    if best_box and best_dist <= 150:
                        calc_rect = best_box
                        mapped_boxes.add(best_box)
                    else:
                        if w_rect.width > w_rect.height * 1.5 and w_rect.height > 0:
                            cb_size = min(w_rect.height, 15)
                            cy = (w_rect.y0 + w_rect.y1) / 2
                            calc_rect = fitz.Rect(
                                w_rect.x0,
                                cy - cb_size / 2,
                                w_rect.x0 + cb_size,
                                cy + cb_size / 2,
                            )
                        elif w_rect.width < 5 or w_rect.height < 5:
                            w_cx = (w_rect.x0 + w_rect.x1) / 2
                            w_cy = (w_rect.y0 + w_rect.y1) / 2
                            calc_rect = fitz.Rect(
                                w_cx - 7, w_cy - 7, w_cx + 7, w_cy + 7
                            )
                        else:
                            calc_rect = w_rect

                    cb_visual_rects[w] = calc_rect

                checkbox_items = []
                for w in checkbox_widgets:
                    v_rect = cb_visual_rects[w]
                    n_rect = fitz.Rect(w.rect)

                    if n_rect.width > v_rect.width * 2.5:
                        bg_r = v_rect | n_rect
                    else:
                        bg_r = fitz.Rect(v_rect)

                    checkbox_items.append(
                        {
                            "name": sanitize_name(w.field_name, field_idx),
                            "rect": v_rect,
                            "bg_rect": bg_r,
                        }
                    )
                    field_idx += 1

                for b in char_boxes:
                    if b not in mapped_boxes:
                        checkbox_items.append(
                            {
                                "name": f"auto_checkbox_{field_idx}",
                                "rect": b,
                                "bg_rect": b,
                            }
                        )
                        field_idx += 1

                filtered_textfields = []
                for tf in textfield_widgets:
                    tf_rect = fitz.Rect(tf.rect)
                    delete_tf = False

                    if tf_rect.height <= 50 and tf_rect.width > 15:
                        for cb in checkbox_items:
                            cb_rect = cb["rect"]
                            intersect = tf_rect.intersect(cb_rect)

                            cb_cx = (cb_rect.x0 + cb_rect.x1) / 2
                            cb_cy = (cb_rect.y0 + cb_rect.y1) / 2
                            cb_center_point = fitz.Point(cb_cx, cb_cy)

                            is_contained = tf_rect.contains(cb_center_point)
                            is_high_overlap = (
                                cb_rect.get_area() > 0
                                and intersect.is_valid
                                and intersect.get_area() / cb_rect.get_area() > 0.4
                            )

                            if is_contained or is_high_overlap:
                                delete_tf = True
                                cb["bg_rect"] = cb["bg_rect"] | tf_rect
                                break

                    if not delete_tf:
                        filtered_textfields.append(tf)

                processed_widgets = []
                for cb in checkbox_items:
                    processed_widgets.append(
                        {
                            "element": "checkbox",
                            "type": "checkbox",
                            "name": cb["name"],
                            "rect": cb["rect"],
                            "bg_rect": cb["bg_rect"],
                        }
                    )

                for w in filtered_textfields:
                    field_name = sanitize_name(w.field_name, field_idx)

                    raw_name = (w.field_name or "").lower()
                    # Replace underscores and slashes to get a clean string for phrase matching
                    check_name = raw_name.replace("_", " ").replace("/", " ")

                    # Strict word boundaries ensure "update" doesn't trigger "date"
                    has_date_word = bool(re.search(r"\bdates?\b", check_name))
                    has_time_word = bool(re.search(r"\btimes?\b", check_name))

                    is_date_field = False
                    is_time_field = False

                    # Context-aware exclusions
                    if has_date_word:
                        if "to date" in check_name and "time" not in check_name:
                            is_date_field = False
                        elif "timeframe" in check_name or "time frame" in check_name:
                            is_date_field = False
                        else:
                            is_date_field = True

                    if has_time_word:
                        if any(
                            x in check_name
                            for x in [
                                "time zone",
                                "timezone",
                                "time frame",
                                "timeframe",
                            ]
                        ):
                            is_time_field = False
                        else:
                            is_time_field = True

                    is_numeric = False
                    numeric_keywords = [
                        "qty",
                        "cost",
                        "amount",
                        "total",
                        "num",
                        "number",
                        "acres",
                        "latitude",
                        "longitude",
                        "zip",
                        "phone",
                        "percent",
                        "sq_mi",
                        "personnel",
                        "resource",
                        "#",
                        "page",
                    ]
                    if any(kw in check_name for kw in numeric_keywords):
                        is_numeric = True

                    anti_numeric_keywords = ["name"]
                    if any(kw in check_name for kw in anti_numeric_keywords):
                        is_numeric = False

                    # Active Dates/Times override numeric defaults
                    if is_date_field or is_time_field:
                        is_numeric = False

                    w_rect = fitz.Rect(w.rect)

                    # Spatial Numeric Detection
                    if (
                        not is_numeric
                        and not is_date_field
                        and not is_time_field
                        and not any(kw in check_name for kw in anti_numeric_keywords)
                    ):
                        w_cx = (w_rect.x0 + w_rect.x1) / 2
                        w_cy = (w_rect.y0 + w_rect.y1) / 2

                        for l_rect in numeric_labels:
                            l_cx = (l_rect.x0 + l_rect.x1) / 2
                            l_cy = (l_rect.y0 + l_rect.y1) / 2

                            col_match = (
                                (
                                    (w_rect.x0 <= l_cx <= w_rect.x1)
                                    or (l_rect.x0 <= w_cx <= l_rect.x1)
                                )
                                and (l_rect.y0 < w_cy)
                                and (w_rect.width < width * 0.4)
                            )
                            row_match = (
                                (
                                    (w_rect.y0 <= l_cy <= w_rect.y1)
                                    or (l_rect.y0 <= w_cy <= l_rect.y1)
                                )
                                and (l_rect.x0 < w_cx)
                                and (w_rect.height < height * 0.1)
                            )

                            if col_match or row_match:
                                is_numeric = True
                                break

                    is_multiline = (w.field_flags & 4096) or (
                        w_rect.height > 26 and w_rect.width > 40
                    )

                    # Map field type correctly based on context keywords
                    html_input_type = "text"
                    if not is_multiline:
                        if is_numeric:
                            html_input_type = "number"

                    processed_widgets.append(
                        {
                            "element": "textarea" if is_multiline else "input",
                            "type": html_input_type,
                            "name": field_name,
                            "rect": w_rect,
                        }
                    )
                    field_idx += 1

                html_content.append(
                    f"<div class='page-container' style='aspect-ratio: {width} / {height};'>"
                )

                html_content.append(
                    "<div class='layer-svg' style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;'>"
                )
                html_content.append(
                    f"<svg width='100%' height='100%' viewBox='{x0} {y0} {width} {height}' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'>"
                )

                for p in paths:
                    d_str = ""
                    for item in p["items"]:
                        if item[0] == "l":
                            d_str += (
                                f"M{item[1].x} {item[1].y} L{item[2].x} {item[2].y} "
                            )
                        elif item[0] == "re":
                            r = item[1]
                            d_str += f"M{r.x0} {r.y0} L{r.x1} {r.y0} L{r.x1} {r.y1} L{r.x0} {r.y1} Z "
                        elif item[0] == "c":
                            d_str += f"M{item[1].x} {item[1].y} C{item[2].x} {item[2].y} {item[3].x} {item[3].y} {item[4].x} {item[4].y} "

                    fill = (
                        "none"
                        if not p["fill"]
                        else f"rgb({int(p['fill'][0]*255)},{int(p['fill'][1]*255)},{int(p['fill'][2]*255)})"
                    )
                    if fill == "rgb(255,255,255)":
                        fill = "none"

                    stroke = "none" if not p["color"] else "black"
                    stroke_width = p.get("width", 1) or 1
                    if d_str:
                        html_content.append(
                            f"  <path d='{d_str}' fill='{fill}' stroke='{stroke}' stroke-width='{stroke_width}'/>"
                        )

                for block in text_dict.get("blocks", []):
                    for line in block.get("lines", []):
                        dir_x, dir_y = line.get("dir", (1.0, 0.0))
                        angle = math.degrees(math.atan2(dir_y, dir_x))

                        for span in line.get("spans", []):
                            raw_text = span["text"]
                            if not raw_text.strip():
                                continue

                            text = (
                                raw_text.replace("&", "&amp;")
                                .replace("<", "&lt;")
                                .replace(">", "&gt;")
                            )

                            font_size = span["size"]
                            is_bold = bool(span["flags"] & 16) or (
                                "bold" in span.get("font", "").lower()
                            )
                            is_italic = bool(span["flags"] & 2) or (
                                "italic" in span.get("font", "").lower()
                            )
                            font_weight = "bold" if is_bold else "normal"
                            font_style = "italic" if is_italic else "normal"

                            font_name_raw = span.get("font", "Arial").lower()
                            if "times" in font_name_raw:
                                font_family = "'Times New Roman', Times, serif"
                            elif "courier" in font_name_raw:
                                font_family = "'Courier New', Courier, monospace"
                            elif (
                                "helvetica" in font_name_raw or "arial" in font_name_raw
                            ):
                                font_family = "Helvetica, Arial, sans-serif"
                            else:
                                safe_font = span.get("font", "Arial").replace("'", "")
                                font_family = (
                                    f"'{safe_font}', Helvetica, Arial, sans-serif"
                                )

                            origin_x, origin_y = span["origin"]

                            transform_attr = ""
                            if abs(angle) > 0.1:
                                transform_attr = f" transform='rotate({angle} {origin_x} {origin_y})'"

                            span_w = span["bbox"][2] - span["bbox"][0]
                            span_h = span["bbox"][3] - span["bbox"][1]

                            baseline_length = (
                                span_w if abs(dir_x) > abs(dir_y) else span_h
                            )

                            text_length_attr = ""
                            if len(raw_text.strip()) > 1 and baseline_length > 0:
                                text_length_attr = f" textLength='{baseline_length}' lengthAdjust='spacing'"

                            html_content.append(
                                f"  <text x='{origin_x}' y='{origin_y}' font-family=\"{font_family}\" font-size='{font_size}' font-weight='{font_weight}' font-style='{font_style}' fill='black' xml:space='preserve'{transform_attr}{text_length_attr}>{text}</text>"
                            )

                html_content.append("</svg></div>")

                html_content.append(
                    "<div class='layer-forms' style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;'>"
                )

                for pw in processed_widgets:
                    uid = f"field_id_{global_id_counter}"
                    global_id_counter += 1

                    if pw["element"] == "checkbox":
                        bg_r = pw["bg_rect"]
                        bg_left = ((bg_r.x0 - x0) / width) * 100
                        bg_top = ((bg_r.y0 - y0) / height) * 100
                        bg_width = (bg_r.width / width) * 100
                        bg_height = (bg_r.height / height) * 100
                        bg_style = f"left: {bg_left}%; top: {bg_top}%; width: {bg_width}%; height: {bg_height}%;"
                        html_content.append(
                            f"  <label for='{uid}' class='checkbox-label' style='{bg_style}'></label>"
                        )

                        r = pw["rect"]
                        css_left = ((r.x0 - x0) / width) * 100
                        css_top = ((r.y0 - y0) / height) * 100
                        css_width = (r.width / width) * 100
                        css_height = (r.height / height) * 100
                        style_str = f"left: {css_left}%; top: {css_top}%; width: {css_width}%; height: {css_height}%;"
                        html_content.append(
                            f"  <input type='checkbox' class='custom-checkbox' id='{uid}' name='{pw['name']}' style='{style_str}' />"
                        )

                    else:
                        r = pw["rect"]
                        is_vertical = r.height > r.width * 2.5

                        max_font_h = r.height * 0.65
                        max_font_w = r.width * 0.45
                        computed_size = min(max_font_h, max_font_w)

                        computed_size = min(computed_size, 11)
                        field_font_size = (computed_size / width) * 100

                        padding_str = (
                            "0" if (r.height < 16 or r.width < 16) else "0.2cqw"
                        )
                        text_align = "left"
                        if pw["element"] == "input" and (
                            pw["type"] == "number" or r.width < 30
                        ):
                            text_align = "center"

                        if is_vertical:
                            css_left = ((r.x0 - x0) / width) * 100
                            css_top = ((r.y1 - y0) / height) * 100
                            css_width = (r.height / width) * 100
                            css_height = (r.width / height) * 100
                            style_str = f"left: {css_left}%; top: {css_top}%; width: {css_width}%; height: {css_height}%; font-size: {field_font_size}cqw; padding: {padding_str}; text-align: {text_align}; transform-origin: 0 0; transform: rotate(-90deg);"
                        else:
                            css_left = ((r.x0 - x0) / width) * 100
                            css_top = ((r.y0 - y0) / height) * 100
                            css_width = (r.width / width) * 100
                            css_height = (r.height / height) * 100
                            style_str = f"left: {css_left}%; top: {css_top}%; width: {css_width}%; height: {css_height}%; font-size: {field_font_size}cqw; padding: {padding_str}; text-align: {text_align};"

                        if pw["element"] == "textarea":
                            html_content.append(
                                f"  <textarea class='form-field' id='{uid}' name='{pw['name']}' style='{style_str}'></textarea>"
                            )
                        else:
                            html_content.append(
                                f"  <input type='{pw['type']}' class='form-field' id='{uid}' name='{pw['name']}' style='{style_str}' />"
                            )

                html_content.append("</div></div>")

            html_content.append(
                "<button style='padding: 10px 20px; font-size: 16px; margin-top: 20px; cursor: pointer; background-color: #0056b3; color: white; border: none; border-radius: 4px;' type='submit'>Submit ICS Form</button>"
            )

            html_content.append("""
            <script>
              document.addEventListener('input', function(e) {
                if (!e.target.name) return;
                const siblings = document.querySelectorAll('[name="' + e.target.name + '"]');
                siblings.forEach(el => {
                  if (el !== e.target) {
                    if (e.target.type === 'checkbox') {
                      el.checked = e.target.checked;
                    } else {
                      el.value = e.target.value;
                    }
                  }
                });
              });
            </script>
            """)

            html_content.append("</form></body></html>")

            out_file = os.path.join(output_dir, out_filename)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write("\n".join(html_content))

        print("\nPDF parsing complete! Check the 'output_forms' directory.")


if __name__ == "__main__":
    parse_pdfs()
