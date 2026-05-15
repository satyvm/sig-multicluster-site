#!/usr/bin/env python3
# Copyright The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generate per-version conformance comparison pages from submitted YAML report files.

Scans all project directories under the implementations root for a reports/
subdirectory containing reports as YAML files. Generates comparison Markdown pages
under each project's directory.

Expected layout:
site-src/
    implementations/
        mcs-implementations/
            reports/
                v0.4.1/submariner/v0.23.0.yaml    (submitted)
                v0.4.1/gke/2026-01-01.yaml        (submitted)
                v0.4.1/gke/2026-07-01.yaml        (submitted)
            conformance-matrix.md                 (generated)
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Any

import yaml

REPO_URL = "https://github.com/kubernetes-sigs/sig-multicluster-site"
IMPLEMENTATIONS_DIR = "site-src/implementations"


@dataclass
class ReportData:
    organization: str
    project: str
    version: str
    url: str
    passed: int
    total: int
    required_passed: int
    required_total: int
    report_path: str


def compute_required_counts(groups: list[dict[str, Any]]) -> tuple[int, int]:
    """Compute required test counts from the groups field in a report.

    Iterates through test groups and counts passed/total for
    required tests (group name == "Required").
    Returns: (required_passed, required_total)
    """
    required_passed = 0
    required_total = 0

    for group in groups:
        if group.get("name") != "Required":
            continue
        for test in group.get("tests", []):
            required_total += 1
            if test.get("passed", False):
                required_passed += 1

    return required_passed, required_total


def parse_report(report_file: pathlib.Path) -> ReportData:
    """Parse a single report.yaml file and return a ReportData instance."""
    with open(report_file) as f:
        data: dict[str, Any] = yaml.safe_load(f)

    impl: dict[str, Any] = data.get("implementation", {})
    required_passed, required_total = compute_required_counts(data.get("groups", []))

    return ReportData(
        organization=impl.get("organization", ""),
        project=impl.get("project", ""),
        version=impl.get("version", ""),
        url=impl.get("url", ""),
        passed=data.get("passed", "Not found"),
        total=data.get("total", "Not found"),
        required_passed=required_passed,
        required_total=required_total,
        report_path=str(report_file),
    )


def generate_version_section(version: str, reports: list[ReportData]) -> str:
    """Generate Markdown table for a single API version."""
    lines = [
        f"## {version}",
        "| Organization | Project | Version | Required Tests | Total Tests | Report |",
        "|---|---|---|---|---|---|",
    ]

    for r in reports:
        project = r.project
        if r.url:
            project = f"[{r.project}]({r.url})"

        report_name = pathlib.Path(r.report_path).name
        report_link = f"[{report_name}]({REPO_URL}/blob/main/{r.report_path})"

        # for green ticks to appear if all required tests passed/ if all tests passed
        req_check = " :white_check_mark:" if r.required_passed == r.required_total else ""
        total_check = " :white_check_mark:" if r.passed == r.total else ""

        lines.append(
            f"| {r.organization} | {project} | {r.version} "
            f"| {r.required_passed}/{r.required_total}{req_check} "
            f"| {r.passed}/{r.total}{total_check} | {report_link} |"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    implementations_dir = pathlib.Path(IMPLEMENTATIONS_DIR)

    for project_dir in sorted(d for d in implementations_dir.iterdir() if d.is_dir()):
        reports_dir = pathlib.Path.joinpath(project_dir, "reports")

        reports_by_version: dict[str, list[ReportData]] = {}
        for report_file in sorted(reports_dir.glob("*/*/*.yaml")):
            api_version = report_file.parent.parent.name
            reports_by_version.setdefault(api_version, []).append(parse_report(report_file))

        output_file = pathlib.Path.joinpath(project_dir, "conformance-matrix.md")

        # Sort implementations alphabetically by organization then project
        for api_version in reports_by_version:
            reports_by_version[api_version].sort(
                key=lambda r: (r.organization.lower(), r.project.lower())
            )

        versions = sorted(reports_by_version.keys(), reverse=True) # versions in descending order
        sections = [generate_version_section(v, reports_by_version[v]) for v in versions]
        output_file.write_text("\n".join(sections))
        print(f"Generated {output_file}")


if __name__ == "__main__":
    main()
