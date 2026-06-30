"""
Copyright 2022 Ledger SAS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Firmware C code coverage for Speculos-based functional tests.
#
# The application under test is the real ARM firmware, run by Speculos through
# `qemu-arm-static`. Unlike native unit tests (gcc `--coverage`), the firmware
# never performs a normal libc exit, so `gcov` cannot flush counters. Instead we
# trace at the *emulator* level:
#
# * QEMU honours `QEMU_LOG=in_asm` / `QEMU_LOG_FILENAME`. With `in_asm` it logs
#   the guest assembly of every *translated* basic block. A block is translated
#   the first time it is reached, so "translated" == "executed at least once" ==
#   line coverage (`exec,nochain` would log every execution -- orders of
#   magnitude bigger -- and is not needed).
# * Ledger apps are PIC: linked high (e.g. 0xc0de0000) but loaded and executed
#   by Speculos at a fixed base (0x40000000 for every Cortex-M target). We rebase
#   the executed block addresses back to link addresses.
# * We intersect those ranges with the DWARF line table of the app ELF and emit a
#   standard lcov `.info` tracefile (uploadable to Codecov, renderable with
#   `genhtml`).
#
# Limitations: line/block coverage only (no branch coverage); the app ELF must
# keep its `.debug_*` sections (a default build does; a stripped/release build
# does not); attribution is on the optimized build, so it is as approximate as
# any optimized-build coverage.
#
# Enabling tracing requires no change to Speculos or QEMU: Speculos spawns QEMU
# with `Popen` without an explicit `env`, so the `QEMU_LOG*` variables set in
# `os.environ` are inherited.
import bisect
import fnmatch
import os
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ragger.logger import get_default_logger

# Speculos maps the lowest loadable segment of the app at this fixed guest
# virtual address for every Cortex-M target (speculos src/launcher.h:
# `#define LOAD_ADDR ((void *)0x40000000)`).
LOAD_BASE = 0x40000000

logger = get_default_logger()

# Per-session registry: device name -> (elf path, trace directory). Populated by
# the Speculos backend when coverage is enabled, consumed at session end.
_REGISTRY: Dict[str, Tuple[Path, Path]] = {}


def enable(device_name: str, elf: Path, trace_dir: Path) -> None:
    """Turn on QEMU ``in_asm`` tracing for the upcoming Speculos launches.

    Sets the ``QEMU_LOG*`` environment variables (inherited by the QEMU process
    Speculos spawns) and registers the (elf, trace_dir) couple for this device
    so the traces can be converted at the end of the session. ``%d`` in the
    filename is expanded by QEMU to the process pid: the backend is usually
    class-scoped, so several QEMU instances run and each must write its own file.
    """
    trace_dir.mkdir(parents=True, exist_ok=True)
    os.environ["QEMU_LOG"] = "in_asm"
    os.environ["QEMU_LOG_FILENAME"] = str(trace_dir / "cov-%d.log")
    _REGISTRY[device_name] = (Path(elf), trace_dir)
    logger.info("[coverage] tracing enabled for %s -> %s", device_name, trace_dir)


def registered() -> Dict[str, Tuple[Path, Path]]:
    return dict(_REGISTRY)


def _run(cmd: List[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def _text_range(readelf: str, elf: Path) -> Tuple[int, int]:
    """Return (vma, size) of the .text section of the app ELF."""
    out = _run([readelf, "-S", str(elf)])
    for line in out.splitlines():
        m = re.search(r"\.text\s+\w+\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)", line)
        if m:
            return int(m.group(1), 16), int(m.group(2), 16)
    raise ValueError(f"no .text section found in {elf}")


def _parse_traces(
    trace_files: List[Path], lo: int, hi: int, delta: int
) -> List[Tuple[int, int]]:
    """Parse in_asm traces -> sorted executed link-address ranges (deduped).

    ``lo``/``hi`` bound the app .text in *runtime* addresses; ``delta`` rebases a
    runtime address to its link address.
    """
    ranges: Set[Tuple[int, int]] = set()
    block_re = re.compile(r"^(0x[0-9a-f]+):")

    def flush(addr: Optional[int], length: int) -> None:
        if addr is not None and lo <= addr < hi and length:
            ranges.add((addr + delta, addr + length + delta))

    for path in trace_files:
        cur_addr: Optional[int] = None
        cur_len = 0
        with open(path, errors="ignore") as fh:
            for line in fh:
                m = block_re.match(line)
                if m:
                    flush(cur_addr, cur_len)
                    cur_addr, cur_len = int(m.group(1), 16), 0
                elif line.startswith("OBJD-T:"):
                    cur_len += len(line.split(":", 1)[1].strip()) // 2
            flush(cur_addr, cur_len)
    return sorted(ranges)


def _line_table(
    readelf: str, elf: Path, vlo: int, vhi: int
) -> List[Tuple[int, str, int]]:
    """DWARF line table -> sorted (addr, source_path, line) statements in range."""
    out = _run([readelf, "--debug-dump=decodedline", str(elf)])
    entries: List[Tuple[int, str, int]] = []
    cur_path: Optional[str] = None
    hdr_re = re.compile(r"^(\S*\.(?:c|h|cpp|cc|cxx)):\s*$")
    ent_re = re.compile(r"^\S+\s+(\d+)\s+(0x[0-9a-f]+)")
    for line in out.splitlines():
        h = hdr_re.match(line)
        if h:
            cur_path = h.group(1)
            continue
        m = ent_re.match(line)
        if m and cur_path:
            addr, lno = int(m.group(2), 16), int(m.group(1))
            if lno and vlo <= addr < vhi:
                entries.append((addr, cur_path, lno))
    entries.sort()
    return entries


def _repo_relative(
    source_path: str, project_root: Path, cache: Dict[str, Optional[str]]
) -> Optional[str]:
    """Map a DWARF source path to a path relative to ``project_root``.

    Generic and toolchain-agnostic: strip the longest leading prefix such that
    the remainder exists as a file under ``project_root``. Drops anything not in
    the repo (SDK headers under /opt, libc under /usr, ...).
    """
    if source_path in cache:
        return cache[source_path]
    parts = Path(source_path).parts
    root = project_root.resolve()
    result: Optional[str] = None
    for i in range(len(parts)):
        candidate = Path(*parts[i:])
        # Skip absolute candidates: `root / "/opt/x"` would collapse to "/opt/x"
        # and could match a real file *outside* the repo (e.g. SDK headers).
        if candidate.is_absolute():
            continue
        full = root / candidate
        if not full.is_file():
            continue
        # Guard against `..` escaping the repo.
        try:
            full.resolve().relative_to(root)
        except ValueError:
            continue
        result = candidate.as_posix()
        break
    cache[source_path] = result
    return result


def _excluded(rel: str, patterns: List[str]) -> bool:
    """Whether a repo-relative path matches one of the exclusion patterns.

    A pattern matches if it equals the path, is a leading directory of it, or is
    an fnmatch glob matching it. So `ethereum-plugin-sdk`, `ethereum-plugin-sdk/`
    and `ethereum-plugin-sdk/*` all exclude the vendored submodule.
    """
    for pat in patterns:
        pat = pat.strip().rstrip("/")
        if not pat:
            continue
        if rel == pat or rel.startswith(pat + "/") or fnmatch.fnmatch(rel, pat):
            return True
    return False


def to_lcov(
    elf: Path,
    trace_files: List[Path],
    output: Path,
    project_root: Path,
    readelf: str = "readelf",
    load_base: int = LOAD_BASE,
    exclude: Optional[List[str]] = None,
) -> Tuple[int, int, int]:
    """Convert in_asm traces into an lcov tracefile.

    ``exclude`` is an optional list of patterns (see :func:`_excluded`) removing
    matching repo-relative source paths, e.g. vendored submodules.

    Returns (files, covered_lines, instrumented_lines). Raises ValueError if the
    ELF has no DWARF line info, or if no app code was executed.
    """
    patterns = exclude or []
    tvma, tsize = _text_range(readelf, elf)
    delta = tvma - load_base
    exec_ranges = _parse_traces(trace_files, load_base, load_base + tsize, delta)
    entries = _line_table(readelf, elf, tvma, tvma + tsize)

    if not entries:
        raise ValueError(
            f"no DWARF line info in {elf}; build with debug symbols "
            "(a default build keeps them, a stripped build does not)"
        )
    if not exec_ranges:
        raise ValueError(
            f"no app code executed in [{load_base:#x}, "
            f"{load_base + tsize:#x}); check traces and load base"
        )

    starts = [r[0] for r in exec_ranges]
    hits: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
    instr: Dict[str, Set[int]] = defaultdict(set)
    path_cache: Dict[str, Optional[str]] = {}

    for i, (addr, src, lno) in enumerate(entries):
        nxt = entries[i + 1][0] if i + 1 < len(entries) else addr + 4
        rel = _repo_relative(src, project_root, path_cache)
        if rel is None or _excluded(rel, patterns):  # not a repo source, or excluded
            continue
        instr[rel].add(lno)
        # any executed block [s, e) intersecting this statement [addr, nxt) ?
        j = bisect.bisect_right(starts, nxt) - 1
        while j >= 0 and exec_ranges[j][1] > addr:
            if exec_ranges[j][0] < nxt:
                hits[rel][lno] += 1
                break
            j -= 1

    files = cov = total = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as o:
        for rel in sorted(instr):
            o.write(f"SF:{rel}\n")
            lh = 0
            for lno in sorted(instr[rel]):
                c = hits[rel].get(lno, 0)
                o.write(f"DA:{lno},{c}\n")
                lh += 1 if c else 0
            o.write(f"LH:{lh}\nLF:{len(instr[rel])}\nend_of_record\n")
            files += 1
            cov += lh
            total += len(instr[rel])
    return files, cov, total


def to_html(info: Path, html_dir: Path, project_root: Path) -> Optional[Path]:
    """Render an lcov ``.info`` into an HTML report with ``genhtml``.

    Run from ``project_root`` so the repo-relative ``SF:`` paths resolve to their
    sources. Returns the report's ``index.html`` on success, or None (with a
    warning) if ``genhtml`` is unavailable or failed.
    """
    if shutil.which("genhtml") is None:
        logger.warning(
            "[coverage] genhtml not found, skipping HTML report "
            "(install the 'lcov' package)"
        )
        return None
    html_dir.mkdir(parents=True, exist_ok=True)
    try:
        # `source`: some sources may be absent; `unmapped`: recent genhtml is
        # strict about line-table entries it cannot map on an optimized build.
        subprocess.run(
            [
                "genhtml",
                "--quiet",
                "--ignore-errors",
                "source,unmapped",
                str(info),
                "-o",
                str(html_dir),
            ],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        logger.error("[coverage] genhtml failed: %s", exc)
        return None
    return html_dir / "index.html"


# One per-device coverage result: device, files, covered lines, total lines,
# lcov path, and HTML index (or None).
Result = Tuple[str, int, int, int, Path, Optional[Path]]


def finalize(
    project_root: Path,
    output: Path,
    readelf: str = "readelf",
    exclude: Optional[List[str]] = None,
) -> List[Result]:
    """Convert every registered device's traces into an lcov file.

    For a single device, writes ``output``. For several devices, writes one file
    per device next to ``output`` (``<stem>-<device><suffix>``). An HTML report is
    rendered next to each ``.info`` (``<stem>_html/``) whenever ``genhtml`` is
    available; otherwise only the lcov file is produced. ``exclude`` removes
    matching repo-relative source paths (e.g. vendored submodules). Returns the
    per-device results (rendering of the human-readable summary is left to the
    caller).
    """
    results: List[Result] = []
    multi = len(registered()) > 1
    for device, (elf, trace_dir) in sorted(registered().items()):
        traces = sorted(trace_dir.glob("cov-*.log"))
        if not traces:
            logger.warning("[coverage] no traces found for %s in %s", device, trace_dir)
            continue
        out = output
        if multi:
            out = output.with_name(f"{output.stem}-{device}{output.suffix}")
        try:
            files, cov, total = to_lcov(
                elf, traces, out, project_root, readelf, exclude=exclude
            )
        except ValueError as exc:
            logger.error("[coverage] %s: %s", device, exc)
            continue
        html = to_html(out, out.with_name(f"{out.stem}_html"), project_root)
        results.append((device, files, cov, total, out, html))
    return results
