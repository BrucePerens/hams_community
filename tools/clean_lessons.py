import csv
import os


def separate_interactive_lessons():
    input_file = "ham.auxcomm.lesson.csv"
    interactive_file = "ham.auxcomm.interactive.csv"
    temp_clean_file = "ham.auxcomm.lesson_temp.csv"

    # The complete list of lesson IDs that require in-person interaction
    interactive_ids = {
        # IS-100
        "lesson_is100_0_3",
        "lesson_is100_0_4",
        "lesson_is100_0_6",
        "lesson_is100_1_6",
        "lesson_is100_2_1",
        "lesson_is100_2_2",
        "lesson_is100_4_6",
        "lesson_is100_5_2",
        "lesson_is100_5_4",
        "lesson_is100_5_7",
        "lesson_is100_6_0",
        "lesson_is100_6_2",
        "lesson_is100_6_9",
        "lesson_is100_7_1",
        "lesson_is100_8_4",
        "lesson_is100_10_2",
        "lesson_is100_13_1",
        "lesson_is100_14_1",
        "lesson_is100_14_3",
        "lesson_is100_14_5",
        "lesson_is100_14_6",
        "lesson_is100_15_1",
        "lesson_is100_15_3",
        # IS-200
        "lesson_is200_0_2",
        "lesson_is200_0_3",
        "lesson_is200_0_4",
        "lesson_is200_0_6",
        "lesson_is200_2_2",
        "lesson_is200_3_8",
        "lesson_is200_4_4",
        "lesson_is200_4_5",
        "lesson_is200_5_0",
        "lesson_is200_5_2",
        "lesson_is200_5_6",
        "lesson_is200_7_1",
        "lesson_is200_7_5",
        "lesson_is200_8_1",
        "lesson_is200_8_4",
        "lesson_is200_8_5",
        "lesson_is200_9_3",
        "lesson_is200_9_8",
        "lesson_is200_10_6",
        "lesson_is200_12_0",
        "lesson_is200_13_1",
        "lesson_is200_14_4",
        "lesson_is200_14_9",
        "lesson_is200_17_1",
        "lesson_is200_17_6",
        "lesson_is200_18_2",
        "lesson_is200_18_9",
        "lesson_is200_19_3",
        "lesson_is200_19_8",
        "lesson_is200_20_8",
        "lesson_is200_22_0",
        "lesson_is200_22_3",
        "lesson_is200_24_1",
        "lesson_is200_24_6",
        "lesson_is200_25_0",
        "lesson_is200_25_2",
        "lesson_is200_25_4",
        "lesson_is200_25_5",
        "lesson_is200_25_7",
        "lesson_is200_26_2",
        "lesson_is200_26_9",
        "lesson_is200_27_1",
        # ICS-300
        "lesson_ics300_0_1",
        "lesson_ics300_1_2",
        "lesson_ics300_3_11",
        "lesson_ics300_8_6",
        "lesson_ics300_9_5",
        "lesson_ics300_15_1",
        # IS-700
        "lesson_is700_0_2",
        "lesson_is700_0_3",
        "lesson_is700_0_4",
        "lesson_is700_0_6",
        "lesson_is700_2_0",
        "lesson_is700_2_6",
        "lesson_is700_3_4",
        "lesson_is700_3_6",
        "lesson_is700_4_3",
        "lesson_is700_5_3",
        "lesson_is700_5_4",
        "lesson_is700_6_1",
        "lesson_is700_8_1",
        "lesson_is700_9_4",
        "lesson_is700_10_7",
        "lesson_is700_11_0",
        "lesson_is700_12_2",
        "lesson_is700_12_5",
        "lesson_is700_13_2",
        "lesson_is700_14_3",
        "lesson_is700_14_7",
        "lesson_is700_16_1",
        "lesson_is700_16_8",
        "lesson_is700_17_3",
    }

    try:
        with open(input_file, mode="r", encoding="utf-8") as infile, open(
            temp_clean_file, mode="w", encoding="utf-8", newline=""
        ) as clean_out, open(
            interactive_file, mode="w", encoding="utf-8", newline=""
        ) as interactive_out:

            reader = csv.DictReader(infile)

            # Ensure the output files use the same headers as the input
            fieldnames = reader.fieldnames

            clean_writer = csv.DictWriter(clean_out, fieldnames=fieldnames)
            interactive_writer = csv.DictWriter(interactive_out, fieldnames=fieldnames)

            clean_writer.writeheader()
            interactive_writer.writeheader()

            interactive_count = 0
            clean_count = 0

            # Route rows to the appropriate CSV
            for row in reader:
                if row["id"] in interactive_ids:
                    interactive_writer.writerow(row)
                    interactive_count += 1
                else:
                    clean_writer.writerow(row)
                    clean_count += 1

        # Replace the original file with the cleaned version
        os.replace(temp_clean_file, input_file)

        print(f"Success! Processed {interactive_count + clean_count} total lessons.")
        print(
            f" -> Removed {interactive_count} interactive lessons and saved them to '{interactive_file}'."
        )
        print(f" -> Retained {clean_count} online-ready lessons in '{input_file}'.")

    except FileNotFoundError:
        print(
            f"Error: The file '{input_file}' was not found. Please ensure it is in the same directory as this script."
        )
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    separate_interactive_lessons()
