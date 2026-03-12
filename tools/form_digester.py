import fitz  # PyMuPDF
import os
import glob
import re


def get_field_label(page, widget):
    """
    Draws a spatial bounding box around the widget to grab nearby text.
    """
    rect = widget.rect

    # Adjust search area based on the type of field
    if widget.field_type in [
        fitz.PDF_WIDGET_TYPE_CHECKBOX,
        fitz.PDF_WIDGET_TYPE_RADIOBUTTON,
    ]:
        # For checkboxes/radios, text is usually to the right or left
        search_rect = fitz.Rect(rect.x0 - 50, rect.y0 - 10, rect.x1 + 150, rect.y1 + 10)
    else:
        # For text boxes, text is usually just above, or tucked inside the top-left corner
        search_rect = fitz.Rect(
            rect.x0 - 50, rect.y0 - 20, max(rect.x1, rect.x0 + 150), rect.y0 + 15
        )

    # Extract text from the calculated region
    raw_text = page.get_textbox(search_rect).strip()

    # Sanitize the text to make it a valid HTML name attribute
    clean_text = re.sub(r"[^a-zA-Z0-9\s]", " ", raw_text)  # Remove special characters
    clean_text = (
        re.sub(r"\s+", "_", clean_text).lower().strip("_")
    )  # Replace spaces with underscores

    # Truncate to a maximum of 40 characters so names don't get absurdly long
    clean_text = clean_text[:40].strip("_")

    return clean_text if clean_text else "field"


def convert_pdf_to_svg_html(pdf_path, output_dir):
    doc = fitz.open(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_html = os.path.join(output_dir, f"{base_name}.html")

    html_content = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        f"<title>{base_name}</title>",
        "<style>",
        "  body { background-color: #525659; display: flex; flex-direction: column; align-items: center; padding: 20px; font-family: Arial, sans-serif; }",
        "  .page-container { position: relative; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); background: white; }",
        "  .page-svg { display: block; width: 100%; height: 100%; pointer-events: none; }",
        "  .form-field { position: absolute; background: rgba(173, 216, 230, 0.2); border: 1px solid rgba(0, 0, 255, 0.3); box-sizing: border-box; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 13px; padding: 4px; resize: none; z-index: 10; transition: background-color 0.2s; }",
        "  .form-field:focus { outline: 2px solid #0056b3; background: rgba(255, 255, 255, 0.95); box-shadow: 0 0 5px rgba(0,86,179,0.5); }",
        "  .checkbox-field { position: absolute; cursor: pointer; z-index: 10; margin: 0; padding: 0; }",
        "  @media print { body { background: white; padding: 0; } .page-container { box-shadow: none; margin: 0; page-break-after: always; } .form-field { border: none; background: transparent; } button { display: none; } }",
        "</style>",
        "</head>",
        "<body>",
        f"<h2 style='color: white;'>{base_name}</h2>",
        f"<form method='POST' action='/submit-ics-form' id='{base_name}_form'>",
    ]

    # Dictionaries to track naming and avoid duplicate name attributes
    pdf_to_html_name_map = {}
    name_counter = {}

    for page_num in range(len(doc)):
        page = doc[page_num]

        page_width = page.rect.width
        page_height = page.rect.height

        # Extract the page as an SVG string and make it scale responsively
        svg_content = page.get_svg_image(matrix=fitz.Identity)
        svg_content = re.sub(
            r'(<svg[^>]*?)\bwidth="[^"]+"', r'\1width="100%"', svg_content, count=1
        )
        svg_content = re.sub(
            r'(<svg[^>]*?)\bheight="[^"]+"', r'\1height="100%"', svg_content, count=1
        )

        html_content.append(
            f'  <div class="page-container" style="width: {page_width}px; height: {page_height}px;">'
        )
        html_content.append(f'    <div class="page-svg">{svg_content}</div>')

        # Extract form fields and overlay them
        for widget in page.widgets():
            rect = widget.rect

            # 1. GENERATE A SMART NAME FOR THE FIELD
            # Fallback to a hash if the PDF field has literally no name string internally
            pdf_internal_name = (
                widget.field_name or f"unnamed_pdf_field_{page_num}_{hash(rect)}"
            )

            if pdf_internal_name not in pdf_to_html_name_map:
                # Grab the text physically located next to the field
                label = get_field_label(page, widget)

                # Ensure uniqueness so form data doesn't overwrite itself
                if label in name_counter:
                    name_counter[label] += 1
                    final_name = f"{label}_{name_counter[label]}"
                else:
                    name_counter[label] = 1
                    final_name = label if label != "field" else "field_1"

                pdf_to_html_name_map[pdf_internal_name] = final_name

            html_name = pdf_to_html_name_map[pdf_internal_name]
            f_value = widget.field_value or ""

            # 2. CALCULATE POSITIONS
            left = (rect.x0 / page_width) * 100
            top = (rect.y0 / page_height) * 100
            width = ((rect.x1 - rect.x0) / page_width) * 100
            height = ((rect.y1 - rect.y0) / page_height) * 100
            style = f"left: {left}%; top: {top}%; width: {width}%; height: {height}%;"

            # 3. GENERATE THE HTML ELEMENT
            if widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                checked = (
                    "checked"
                    if str(f_value).lower() in ["yes", "on", "/yes", "/on", "true"]
                    else ""
                )
                html_content.append(
                    f'    <input type="checkbox" class="checkbox-field" name="{html_name}" style="{style}" {checked}>'
                )

            elif widget.field_type == fitz.PDF_WIDGET_TYPE_RADIOBUTTON:
                html_content.append(
                    f'    <input type="radio" class="checkbox-field" name="{html_name}" value="{f_value}" style="{style}">'
                )

            elif widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                # If the box is taller than ~25 points (approx 2 lines of text), make it a textarea
                if rect.height > 25:
                    html_content.append(
                        f'    <textarea class="form-field" name="{html_name}" style="{style}">{f_value}</textarea>'
                    )
                else:
                    html_content.append(
                        f'    <input type="text" class="form-field" name="{html_name}" value="{f_value}" style="{style}">'
                    )

        html_content.append("  </div>")

    html_content.append(
        "  <button type='submit' style='padding: 10px 20px; font-size: 16px; margin-top: 20px; cursor: pointer; background-color: #0056b3; color: white; border: none; border-radius: 4px;'>Submit ICS Form</button>"
    )
    html_content.append("</form>")
    html_content.append("</body>")
    html_content.append("</html>")

    with open(output_html, "w", encoding="utf-8") as f:
        f.write("\n".join(html_content))

    print(f"Successfully created: {output_html}")


def main():
    input_directory = "./ics_pdfs"
    output_directory = "./ics_svg_forms"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    pdf_files = glob.glob(os.path.join(input_directory, "*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {input_directory}. Please add your ICS forms there.")
        return

    for pdf in pdf_files:
        print(f"Processing {pdf}...")
        convert_pdf_to_svg_html(pdf, output_directory)


if __name__ == "__main__":
    main()
