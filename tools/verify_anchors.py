#!/usr/bin/env python3
import os
import re


def find_anchors_in_docs(docs_dir, root_dir):
    doc_anchors = set()
    contract_anchors = set()
    pattern = re.compile(r"\[@ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]")

    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file == "LLM_LINTER_GUIDE.md":
                continue
            if file.endswith(".md") or file.endswith(".html") or file.endswith(".py"):
                full_path = os.path.join(root, file)
                is_contract = False

                if "modules" in root.split(os.sep) and (
                    file.endswith(".md") or file.endswith(".py")
                ):
                    is_contract = True

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        for match in pattern.finditer(f.read()):
                            anchor = match.group(1)
                            if is_contract:
                                contract_anchors.add(anchor)
                            else:
                                doc_anchors.add(anchor)
                except UnicodeDecodeError:
                    pass

    return doc_anchors, contract_anchors


def _process_file_for_anchors(
    full_path,
    content,
    pattern,
    code_anchors,
    anchor_locations,
    tests_links,
    tests_links_set,
    verified_by_links,
    cross_references,
    duplicates,
):
    for line in content.splitlines():
        for match in pattern.finditer(line):
            anchor = match.group(1)
            prefix = line[: match.start()].strip()
            if prefix.endswith("Tests"):
                tests_links.setdefault(full_path, []).append(anchor)
                tests_links_set.add(anchor)
            elif prefix.endswith("Verified by") or prefix.endswith("Tested by"):
                verified_by_links.add(anchor)
            elif prefix.endswith("Triggers") or prefix.endswith("Triggered by"):
                cross_references.add(anchor)
            else:
                if (
                    anchor in anchor_locations
                    and not anchor.startswith("example_")
                    and anchor not in ("unique_name", "name", "feature_name")
                ):
                    duplicates.append(
                        f"'{anchor}' in {full_path} and {anchor_locations[anchor]}"
                    )
                else:
                    anchor_locations[anchor] = full_path
                    code_anchors.add(anchor)


def find_anchors_in_code(root_dir):
    code_anchors, anchor_locations = set(), {}
    tests_links, tests_links_set = {}, set()
    verified_by_links, cross_references = set(), set()
    duplicates = []
    pattern = re.compile(r"\[@ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]")
    exclude_dirs = {"docs", ".git", "venv", "__pycache__"}

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file == "LLM_LINTER_GUIDE.md":
                continue

            if file == "documentation.html":
                continue

            is_code = file.endswith((".py", ".js", ".xml", ".html"))
            is_readme = file.lower() == "readme.md"

            if is_code or is_readme:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        _process_file_for_anchors(
                            full_path,
                            f.read(),
                            pattern,
                            code_anchors,
                            anchor_locations,
                            tests_links,
                            tests_links_set,
                            verified_by_links,
                            cross_references,
                            duplicates,
                        )
                except UnicodeDecodeError:
                    pass

    return (
        code_anchors,
        anchor_locations,
        tests_links,
        tests_links_set,
        verified_by_links,
        cross_references,
        duplicates,
    )


def _report_duplicates(duplicates):
    if duplicates:
        print("\n[!] CI/CD FAILURE: Duplicate Semantic Anchors detected:")
        for dup in duplicates:
            print(f"    - {dup}")
        return True
    return False


def _report_missing_cross_refs(cross_references, code_anchors, contract_anchors):
    missing_cross_refs = set()
    for anchor in cross_references - code_anchors - contract_anchors:
        if not anchor.startswith("example_") and anchor not in (
            "unique_name",
            "name",
            "feature_name",
        ):
            missing_cross_refs.add(anchor)

    if missing_cross_refs:
        print(
            "\n[!] CI/CD FAILURE: ADR-0055 Cross-Reference Violation. The following anchors are referenced via 'Triggers' or 'Triggered by' but do not exist in the codebase or API Contracts:"
        )
        for anchor in missing_cross_refs:
            print(f"    - `{anchor}`")
        return True
    return False


def _report_missing_tests(tests_links, code_anchors, contract_anchors):
    missing_tested = set()
    for links in tests_links.values():
        for link in links:
            if (
                link not in code_anchors
                and link not in contract_anchors
                and not link.startswith("example_")
                and link not in ("unique_name", "name", "feature_name")
            ):
                missing_tested.add(link)

    if missing_tested:
        print(
            "\n[!] CI/CD FAILURE: ADR-0054 Violation. The following anchors are referenced as 'Tests' but do not exist in the codebase or API Contracts:"
        )
        for anchor in missing_tested:
            print(f"    - `{anchor}`")
        return True
    return False


def _report_bidirectional_orphans(
    code_anchors, tests_links_set, verified_by_links, contract_anchors
):
    test_anchors = {a for a in code_anchors if a.startswith("test_")}
    source_anchors = {
        a
        for a in code_anchors
        if not a.startswith("test_")
        and not a.startswith("example_")
        and not a.startswith("UX_")
        and a not in ("unique_name", "name", "feature_name")
    }

    orphaned_source = source_anchors - tests_links_set - contract_anchors
    orphaned_tests = test_anchors - verified_by_links - contract_anchors

    has_errors = False
    if orphaned_source:
        print(
            "\n[!] CI/CD FAILURE: ADR-0054 Bidirectional Violation. Source anchors missing corresponding '# Tests [@ANCHOR: ...]' link:"
        )
        for anchor in orphaned_source:
            print(f"    - `{anchor}`")
        has_errors = True
    if orphaned_tests:
        print(
            "\n[!] CI/CD FAILURE: ADR-0054 Bidirectional Violation. Test anchors not cited by '# Verified by [@ANCHOR: ...]':"
        )
        for anchor in orphaned_tests:
            print(f"    - `{anchor}`")
        has_errors = True
    return has_errors, source_anchors


def _report_documentation_gaps(
    source_anchors, docs_anchors, code_anchors, contract_anchors
):
    undocumented = source_anchors - docs_anchors - contract_anchors
    missing_in_code = {
        a
        for a in (docs_anchors - code_anchors - contract_anchors)
        if not a.startswith("example_")
        and a not in ("unique_name", "name", "feature_name")
    }

    has_errors = False
    if undocumented:
        print(
            "\n[!] CI/CD FAILURE: ADR-0055 Bidirectional Documentation Violation. Source anchors missing from formal docs (docs/):"
        )
        for anchor in undocumented:
            print(f"    - `{anchor}`")
        has_errors = True
    if missing_in_code:
        print(
            "\n[!] CI/CD WARNING: Documentation references anchors missing from the local codebase or API Contracts (Likely external repository):"
        )
        for anchor in missing_in_code:
            print(f"    - `{anchor}`")
        # Downgraded to WARNING: Do not fail the build for multi-repo documentation overlaps
    return has_errors


def _report_missing_ux_docs(code_anchors, user_manual_anchors):
    ux_code_anchors = {a for a in code_anchors if a.startswith("UX_")}
    missing = ux_code_anchors - user_manual_anchors

    if missing:
        print(
            "\n[!] CI/CD FAILURE: The following user-facing features (UX_*) are missing from data/documentation.html:"
        )
        for m in missing:
            print(f"    - `{m}`")
        return True
    return False


def main():
    print("[*] Scanning documentation and codebase for Semantic Anchors...")
    import sys

    args = sys.argv[1:]
    if not args:
        args = ["."]

    docs_anchors = set()
    contract_anchors = set()
    code_anchors = set()
    user_manual_anchors = set()
    anchor_locations = {}
    tests_links = {}
    tests_links_set = set()
    verified_by_links = set()
    cross_references = set()
    duplicates = []

    for target_dir in args:
        docs_dir = os.path.join(target_dir, "docs")
        scan_docs_dir = docs_dir if os.path.exists(docs_dir) else target_dir

        da, ca = find_anchors_in_docs(scan_docs_dir, target_dir)
        docs_anchors.update(da)
        contract_anchors.update(ca)

        (
            c_anchors,
            a_locs,
            t_links,
            t_links_set,
            v_by_links,
            c_refs,
            dups,
        ) = find_anchors_in_code(target_dir)

        code_anchors.update(c_anchors)
        anchor_locations.update(a_locs)

        for k, v in t_links.items():
            tests_links.setdefault(k, []).extend(v)

        tests_links_set.update(t_links_set)
        verified_by_links.update(v_by_links)
        cross_references.update(c_refs)
        duplicates.extend(dups)

        for root, dirs, files in os.walk(target_dir):
            if "documentation.html" in files:
                try:
                    with open(
                        os.path.join(root, "documentation.html"), "r", encoding="utf-8"
                    ) as f:
                        for match in re.finditer(
                            r"\[@ANCHOR:\s*(UX_[a-zA-Z0-9_]+)\s*\]", f.read()
                        ):
                            user_manual_anchors.add(match.group(1))
                except Exception:
                    pass

    errs = [
        _report_duplicates(duplicates),
        _report_missing_cross_refs(cross_references, code_anchors, contract_anchors),
        _report_missing_tests(tests_links, code_anchors, contract_anchors),
        _report_missing_ux_docs(code_anchors, user_manual_anchors),
    ]

    bidi_err, source_anchors = _report_bidirectional_orphans(
        code_anchors, tests_links_set, verified_by_links, contract_anchors
    )
    errs.append(bidi_err)
    errs.append(
        _report_documentation_gaps(
            source_anchors, docs_anchors, code_anchors, contract_anchors
        )
    )

    if any(errs):
        sys.exit(1)
    else:
        print(
            f"\n[+] SUCCESS: Verified {len(code_anchors)} Semantic Anchors and {len(contract_anchors)} API Contracts."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
