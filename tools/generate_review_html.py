#!/usr/bin/env python3
"""
generate_review_html.py
Reads the extracted lesson CSV and generates a styled HTML file for browser review.
Includes an index of courses, built-in CSS (95% width, 20pt font), and a bulletproof
vanilla JS engine to make <dfn> tooltips functional on hover with strict edge-clamping.
"""

import os
import csv
import argparse


def generate_html_review(csv_path, output_path, course_filter=None):
    if not os.path.exists(csv_path):
        print(f"[!] Error: Could not find {csv_path}")
        return

    # Attempt to load the course definitions to get the short and long titles
    course_csv_path = csv_path.replace("lesson.csv", "course.csv")
    courses_info = {}
    if os.path.exists(course_csv_path):
        print(f"[*] Reading course definitions from {course_csv_path}...")
        with open(course_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                courses_info[row.get("id")] = {
                    "code": row.get("code", "").upper(),
                    "name": row.get("name", "Unknown Title"),
                }
    else:
        print(
            f"[~] Warning: Could not find {course_csv_path}. Titles may be incomplete."
        )

    print(f"[*] Reading lessons from {csv_path}...")
    lessons = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if course_filter:
                # Normalize the course code for matching (e.g., "ICS100" -> "course_ics100")
                filter_id = f"course_{course_filter.replace('-', '').lower()}"
                if row.get("course_id:id", "").lower() != filter_id:
                    continue
            lessons.append(row)

    if not lessons:
        print("[!] No lessons found matching criteria.")
        return

    # Sort lessons by course, then by sequence number to ensure chronological order
    lessons.sort(key=lambda x: (x.get("course_id:id", ""), int(x.get("sequence", 0))))

    # Extract unique courses present in the filtered lessons to build the index
    unique_course_ids = []
    for lesson in lessons:
        c_id = lesson.get("course_id:id")
        if c_id not in unique_course_ids:
            unique_course_ids.append(c_id)

    # Basic HTML skeleton with custom CSS (95% width, 20pt font)
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Content Review</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 95%;
            font-size: 20pt;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f2f5;
        }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 40px; }
        .course-index {
            background: #fff;
            padding: 20px 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 40px;
            border-top: 5px solid #2c3e50;
        }
        .course-index h2 {
            margin-top: 0;
            color: #2c3e50;
        }
        .course-index ul {
            list-style-type: none;
            padding: 0;
        }
        .course-index li {
            margin-bottom: 10px;
        }
        .course-index a {
            text-decoration: none;
            color: #3498db;
            font-weight: bold;
        }
        .course-index a:hover {
            text-decoration: underline;
            color: #2980b9;
        }
        .course-header {
            background: #2c3e50;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-top: 50px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .lesson-card {
            background: #fff;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-left: 5px solid #3498db;
        }
        .lesson-card h2 {
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
            margin-top: 0;
            font-size: 1.5em;
        }
        .seq-badge {
            background-color: #e74c3c;
            color: white;
            font-size: 0.5em;
            padding: 4px 8px;
            border-radius: 12px;
            vertical-align: middle;
            margin-left: 10px;
        }
        /* Base styling for the highlighted terms */
        dfn {
            cursor: help;
            border-bottom: 2px dotted #2980b9;
            color: #2980b9;
            font-style: normal;
            font-weight: bold;
        }
        /* Styling for the dynamic JS tooltip container */
        .custom-tooltip {
            position: fixed;
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px 20px;
            border-radius: 8px;
            font-size: 20pt;
            max-width: 600px;
            white-space: pre-wrap;
            pointer-events: none;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.15s ease-in-out;
            z-index: 9999;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            box-sizing: border-box;
        }
        .custom-tooltip.visible {
            opacity: 1;
            visibility: visible;
        }
        .video-container {
            background: #000;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>Course Narrative Review</h1>
"""

    # Build the Index HTML
    html_content += (
        '    <div class="course-index">\n        <h2>Course Index</h2>\n        <ul>\n'
    )
    for c_id in unique_course_ids:
        # Fallback if the course CSV is missing the record
        fallback_code = c_id.replace("course_", "").upper()
        info = courses_info.get(c_id, {"code": fallback_code, "name": "Unknown Title"})
        html_content += f'            <li><a href="#{c_id}">{info["code"]} - {info["name"]}</a></li>\n'
    html_content += "        </ul>\n    </div>\n"

    current_course = None
    for lesson in lessons:
        course = lesson.get("course_id:id", "Unknown Course")
        if course != current_course:
            fallback_code = course.replace("course_", "").upper()
            info = courses_info.get(
                course, {"code": fallback_code, "name": "Unknown Title"}
            )
            display_course = f"{info['code']}: {info['name']}"

            # Inject the ID tag here so the index links can anchor to it
            html_content += (
                f'    <h2 id="{course}" class="course-header">{display_course}</h2>\n'
            )
            current_course = course

        title = lesson.get("title", "Untitled")
        seq = lesson.get("sequence", "N/A")

        # Replace the old 'title' attribute with 'data-tooltip' to kill the browser's native popup
        raw_html = lesson.get("content_html", "<p>No content generated.</p>")
        clean_html = raw_html.replace(' title="', ' data-tooltip="')

        html_content += f"""
    <div class="lesson-card">
        <h2>{title} <span class="seq-badge">Seq: {seq}</span></h2>
        <div class="lesson-content">
            {clean_html}
        </div>
    </div>
"""

    # Inject the robust vanilla JS tooltip engine right before closing the body
    html_content += """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Create the single global tooltip element
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            document.body.appendChild(tooltip);

            const dfns = document.querySelectorAll('dfn');

            function positionTooltip(e) {
                const padding = 15;
                let posX = e.clientX + padding;
                let posY = e.clientY + padding;

                // Force browser to calculate true layout dimensions
                const tWidth = tooltip.offsetWidth;
                const tHeight = tooltip.offsetHeight;
                const winWidth = window.innerWidth;
                const winHeight = window.innerHeight;

                // Right edge collision
                if (posX + tWidth > winWidth - padding) {
                    posX = e.clientX - tWidth - padding;
                    // Left edge clamp fallback if flipping pushes it off the left side
                    if (posX < padding) posX = padding;
                }

                // Bottom edge collision
                if (posY + tHeight > winHeight - padding) {
                    posY = e.clientY - tHeight - padding;
                    // Top edge clamp fallback if flipping pushes it off the top side
                    if (posY < padding) posY = padding;
                }

                tooltip.style.left = posX + 'px';
                tooltip.style.top = posY + 'px';
            }

            dfns.forEach(function(el) {
                el.addEventListener('mouseenter', function(e) {
                    // Grab from the hidden data attribute
                    tooltip.textContent = el.getAttribute('data-tooltip');
                    // Position it BEFORE making it visible to prevent layout jumps
                    positionTooltip(e);
                    tooltip.classList.add('visible');
                });

                el.addEventListener('mousemove', positionTooltip);

                el.addEventListener('mouseleave', function() {
                    tooltip.classList.remove('visible');
                });
            });
        });
    </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] Successfully generated review file: {output_path}")
    print(f"    -> Open {output_path} in your web browser to read the narrative.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate an HTML review file from the lesson CSV."
    )
    parser.add_argument(
        "--input",
        default="ham_auxcomm_training/data/ham.auxcomm.lesson.csv",
        help="Path to the lesson CSV",
    )
    parser.add_argument(
        "--output", default="course_review.html", help="Output HTML file path"
    )
    parser.add_argument(
        "--course",
        help="Optional: Filter by specific course code (e.g., ics100 or ics700)",
    )

    args = parser.parse_args()
    generate_html_review(args.input, args.output, args.course)
