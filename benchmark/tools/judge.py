#!/usr/bin/env python3
"""Structural judge: verify generated code matches the spec, not just compiles.

For each spec entity, find the corresponding generated file and check that the
shape matches what an "equivalent code generator" should produce. Both the
a-mcp and b-baseline variants are judged against the same criteria.

Verdict ladder (from most to least concerning):
  no_files          — output dir empty
  missing_entities  — at least one spec entity has no matching file
  structural_fail   — at least one entity's file has wrong shape (e.g. service
                      emitted as interface instead of class with method stubs)
  compile_errors    — files exist & cover the spec but don't compile
  compile_unknown   — compile gate couldn't run (compiler not installed, etc.)
  pass              — every spec entity has a structurally-correct file & compile is clean

Usage: judge.py <variant_dir> --spec <spec.json> [--language <lang>]
"""
import json, sys, re, argparse, subprocess, os, shutil, tempfile
from pathlib import Path


# ─── Per-language configuration ───────────────────────────────────────────────

LANGUAGE_CONFIG = {
    "typescript": {
        "ext": ".ts",
        "kind_dirs": {
            "aggregate":    "/aggregates/",
            "value_object": "/value-objects/",
            "enum":         "/enums/",
            "service":      "/services/",
        },
        # Each entry is a list of (regex_template, label) pairs. {name} is the entity
        # name (re.escape'd before formatting). First match wins. label is informational.
        "kind_decl": {
            "aggregate":    [(r"export\s+class\s+{name}\b",     "class")],
            "value_object": [(r"export\s+interface\s+{name}\b", "interface")],
            "enum":         [(r"export\s+enum\s+{name}\b",      "enum")],
            "service":      [(r"export\s+class\s+{name}\b",     "class")],
        },
        # Penalty patterns — if a file matches one of these instead, that's
        # a structural_fail (e.g. service emitted as interface).
        "kind_decl_alt": {
            "aggregate":    [(r"export\s+interface\s+{name}\b", "interface")],
            "service":      [(r"export\s+interface\s+{name}\b", "interface")],
        },
        "ctor_indicator":   "constructor(",
        "stub_indicator":   "throw new Error",
        "compile":          "tsc",
    },
    "java": {
        "ext": ".java",
        "kind_dirs": {
            "aggregate":    "/aggregates/",
            "value_object": "/value_objects/",
            "enum":         "/enums/",
            "service":      "/services/",
        },
        "kind_decl": {
            "aggregate":    [(r"public\s+(?:final\s+)?class\s+{name}\b",  "class"),
                             (r"public\s+(?:final\s+)?record\s+{name}\b", "record")],
            "value_object": [(r"public\s+(?:final\s+)?record\s+{name}\b", "record"),
                             (r"public\s+(?:final\s+)?class\s+{name}\b",  "class")],
            "enum":         [(r"public\s+enum\s+{name}\b",                "enum")],
            "service":      [(r"public\s+(?:final\s+)?class\s+{name}\b",  "class")],
        },
        "kind_decl_alt": {
            "aggregate":    [(r"public\s+interface\s+{name}\b", "interface")],
            "service":      [(r"public\s+interface\s+{name}\b", "interface")],
        },
        "ctor_indicator":   None,    # Java records have implicit ctors
        "stub_indicator":   "UnsupportedOperationException",
        "compile":          "javac",
    },
    "python": {
        "ext": ".py",
        "kind_dirs": {
            "aggregate":    "/aggregates/",
            "value_object": "/value_objects/",
            "enum":         "/enums/",
            "service":      "/services/",
        },
        "kind_decl": {
            # Plain class — matches `class X:` or `class X(Base):` but NOT `class X(Enum):`
            "aggregate":    [(r"class\s+{name}\s*(?:\(\s*(?!.*Enum)[^)]*\))?\s*:", "class")],
            "value_object": [(r"class\s+{name}\s*(?:\(\s*(?!.*Enum)[^)]*\))?\s*:", "class")],
            # Enum class — must inherit Enum/IntEnum/StrEnum
            "enum":         [(r"class\s+{name}\s*\([^)]*Enum[^)]*\)\s*:",         "enum-class")],
            "service":      [(r"class\s+{name}\s*(?:\(\s*(?!.*Enum)[^)]*\))?\s*:", "class")],
        },
        "kind_decl_alt": {},   # Python doesn't have an obvious "wrong" alt form
        "ctor_indicator":   None,   # could be __init__ OR @dataclass — too lenient to enforce
        "stub_indicator":   "raise NotImplementedError",
        "compile":          "py_compile",
    },
}


# ─── Compile gates ────────────────────────────────────────────────────────────

TSCONFIG_DEFAULT = """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "isolatedModules": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["**/*.ts"]
}
"""


def run_tsc_compile(out_dir: Path, log_path: Path) -> int:
    if not out_dir.exists() or not list(out_dir.rglob("*.ts")):
        return -1
    tsconfig = out_dir / "tsconfig.json"
    if not tsconfig.exists():
        tsconfig.write_text(TSCONFIG_DEFAULT)
    try:
        r = subprocess.run(
            ["npx", "--yes", "-p", "typescript@5.5",
             "tsc", "--noEmit", "-p", "tsconfig.json"],
            cwd=str(out_dir),
            capture_output=True, text=True, timeout=300,
        )
        log_path.write_text((r.stdout or "") + (r.stderr or ""))
        return len(re.findall(r"error TS\d+", (r.stdout or "") + (r.stderr or "")))
    except Exception as e:
        log_path.write_text(f"tsc invocation failed: {e}")
        return -2


def run_javac_compile(out_dir: Path, log_path: Path) -> int:
    if not out_dir.exists():
        return -1
    files = [str(f) for f in out_dir.rglob("*.java")]
    if not files:
        return -1
    if not shutil.which("javac"):
        log_path.write_text("javac not found in PATH — skipping compile gate")
        return -2
    classes_out = tempfile.mkdtemp(prefix="javac-out-")
    try:
        r = subprocess.run(
            ["javac", "--release", "17", "-d", classes_out, "-encoding", "UTF-8"] + files,
            cwd=str(out_dir),
            capture_output=True, text=True, timeout=300,
        )
        log_path.write_text((r.stdout or "") + (r.stderr or ""))
        # javac error lines look like "Foo.java:5: error: ..."
        return len(re.findall(r":\s*error:", (r.stdout or "") + (r.stderr or "")))
    except Exception as e:
        log_path.write_text(f"javac invocation failed: {e}")
        return -2
    finally:
        shutil.rmtree(classes_out, ignore_errors=True)


def run_pycompile_compile(out_dir: Path, log_path: Path) -> int:
    """Use python -m py_compile to syntax-check each .py file. Note: this is a
    syntax-only gate — it doesn't validate cross-file imports or types. Weaker
    than tsc/javac. Documented limitation."""
    if not out_dir.exists():
        return -1
    files = list(out_dir.rglob("*.py"))
    if not files:
        return -1
    if not shutil.which("python3"):
        log_path.write_text("python3 not found in PATH — skipping compile gate")
        return -2
    errors = 0
    log_lines = []
    for f in files:
        try:
            r = subprocess.run(
                ["python3", "-m", "py_compile", str(f)],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode != 0:
                errors += 1
                log_lines.append(f"--- {f.relative_to(out_dir)} ---")
                log_lines.append(r.stderr or r.stdout or "(no output)")
        except Exception as e:
            errors += 1
            log_lines.append(f"--- {f.relative_to(out_dir)} ---\npy_compile invocation failed: {e}")
    log_path.write_text("\n".join(log_lines) if log_lines else "all files passed py_compile\n")
    return errors


COMPILE_FNS = {
    "tsc":        run_tsc_compile,
    "javac":      run_javac_compile,
    "py_compile": run_pycompile_compile,
}


# ─── Entity finding & checking ────────────────────────────────────────────────

def _search_files(out_dir: Path, ext: str, dir_sub: str, decl_pairs, name: str):
    """Iterate (regex_template, label) pairs; return (file, label) for first match."""
    if not out_dir.exists():
        return None, None
    name_esc = re.escape(name)
    compiled = [(re.compile(tpl.format(name=name_esc)), label) for tpl, label in decl_pairs]
    for f in out_dir.rglob(f"*{ext}"):
        if dir_sub not in str(f):
            continue
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        for pat, label in compiled:
            if pat.search(text):
                return f, label
    return None, None


def find_entity_file(out_dir: Path, cfg: dict, kind: str, name: str):
    """Acceptable shapes (returns (file, label) or (None, None))."""
    return _search_files(out_dir, cfg["ext"], cfg["kind_dirs"][kind],
                         cfg["kind_decl"][kind], name)


def find_with_alt(out_dir: Path, cfg: dict, kind: str, name: str):
    """Penalty shapes — emitted form is structurally wrong for this kind."""
    pairs = cfg.get("kind_decl_alt", {}).get(kind)
    if not pairs:
        return None, None
    return _search_files(out_dir, cfg["ext"], cfg["kind_dirs"][kind], pairs, name)


def check_aggregate(out_dir, cfg, entity):
    name = entity["name"]
    f, label = find_entity_file(out_dir, cfg, "aggregate", name)
    if not f:
        alt_f, alt_label = find_with_alt(out_dir, cfg, "aggregate", name)
        if alt_f:
            return "structural_fail", alt_f, [f"emitted as `{alt_label}` instead of class/record (aggregate must encapsulate fields)"]
        accepted = "/".join(l for _, l in cfg["kind_decl"]["aggregate"])
        return "missing", None, [f"no aggregate `{name}` ({accepted}) under any aggregates/ dir"]
    text = f.read_text(errors="ignore")
    issues = []
    # Records have implicit ctors; only check ctor for class declarations
    if cfg["ctor_indicator"] and label == "class" and cfg["ctor_indicator"] not in text:
        issues.append("class has no constructor (aggregate root expected to encapsulate ctor params)")
    return ("pass" if not issues else "structural_fail"), f, issues


def check_value_object(out_dir, cfg, entity):
    name = entity["name"]
    f, _ = find_entity_file(out_dir, cfg, "value_object", name)
    if not f:
        return "missing", None, [f"no value_object `{name}` under any value-objects/ dir"]
    return "pass", f, []


def _enum_member_name_variants(name: str):
    """Yield plausible spellings of an enum member name across language idioms.
    Spec uses PascalCase; engines may transform to ALL_CAPS / SCREAMING_SNAKE / snake_case."""
    yield name
    # PascalCase → snake_case (insert underscore before each uppercase except first)
    snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name)
    yield snake.upper()    # SCREAMING_SNAKE (Java enum convention)
    yield snake.lower()    # snake_case
    yield name.upper()     # plain ALL_CAPS (single-word case)


def check_enum(out_dir, cfg, entity):
    name = entity["name"]
    f, _ = find_entity_file(out_dir, cfg, "enum", name)
    if not f:
        return "missing", None, [f"no enum `{name}` under any enums/ dir"]
    text = f.read_text(errors="ignore")
    issues = []
    for m in entity.get("members", []):
        mname = m["name"]
        mvalue = m["value"]
        # Accept various member-name spellings (PascalCase, ALL_CAPS, SCREAMING_SNAKE_CASE,
        # snake_case) and either numeric or string-quoted values, across languages:
        #   TS:     Draft = 0,
        #   Java:   DRAFT(0) or IN_TRANSIT(1)
        #   Python: Draft = 0
        match_found = False
        for variant in _enum_member_name_variants(mname):
            numeric_pat = rf"\b{re.escape(variant)}\s*[=(]\s*{re.escape(str(mvalue))}\b"
            string_pat  = rf"\b{re.escape(variant)}\s*[=(]\s*[\"']{re.escape(str(mvalue))}[\"']"
            if re.search(numeric_pat, text) or re.search(string_pat, text):
                match_found = True
                break
        if not match_found:
            issues.append(f"member '{mname}' with value {mvalue!r} not found in expected form")
    return ("pass" if not issues else "structural_fail"), f, issues


def _method_name_variants(name: str):
    """Yield plausible spellings of a method name across language idioms.
    Spec uses camelCase; engines may transform to snake_case (Python) or keep camelCase (TS/Java)."""
    yield name
    # camelCase → snake_case
    snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    yield snake


def check_service(out_dir, cfg, entity):
    name = entity["name"]
    f, _ = find_entity_file(out_dir, cfg, "service", name)
    if not f:
        alt_f, alt_label = find_with_alt(out_dir, cfg, "service", name)
        if alt_f:
            return "structural_fail", alt_f, [f"emitted as `{alt_label}` instead of class with method stub bodies"]
        return "missing", None, [f"no service class `{name}` under any services/ dir"]
    text = f.read_text(errors="ignore")
    issues = []
    for m in entity.get("methods", []):
        mname = m["name"]
        # Try camelCase (spec literal) and snake_case (Python idiomatic transformation).
        match_found = False
        for variant in _method_name_variants(mname):
            if re.search(rf"\b{re.escape(variant)}\s*\(", text):
                match_found = True
                break
        if not match_found:
            issues.append(f"missing method '{mname}'")
    if cfg["stub_indicator"] and cfg["stub_indicator"] not in text:
        issues.append(f"method bodies missing — expected stub indicator `{cfg['stub_indicator']}`")
    return ("pass" if not issues else "structural_fail"), f, issues


CHECKERS = {
    "aggregate":    check_aggregate,
    "value_object": check_value_object,
    "enum":         check_enum,
    "service":      check_service,
}


def collect_expected_ddd(spec):
    """DDD shape: spec.domains[].types[] + spec.domains[].services[]."""
    expected = []
    for d in spec.get("domains", []):
        dname = d["name"]
        for t in d.get("types", []):
            entity = {"kind": t["kind"], "name": t["name"], "domain": dname}
            if "fields" in t: entity["fields"] = t["fields"]
            if "members" in t: entity["members"] = t["members"]
            expected.append(entity)
        for s in d.get("services", []):
            expected.append({
                "kind": "service",
                "name": s["name"],
                "domain": dname,
                "methods": s.get("methods", []),
            })
    return expected


def collect_expected_monolith(spec):
    """Modular-monolith shape: spec.modules[].types[] + spec.modules[].services[],
    plus spec.orchestrators.services[] at the top level. The `domain` field on
    the entity dict carries the module path (or "orchestrators") for issue logging."""
    expected = []
    for m in spec.get("modules", []):
        mpath = m.get("path", m.get("name"))
        for t in m.get("types", []):
            entity = {"kind": t["kind"], "name": t["name"], "domain": mpath}
            if "fields" in t: entity["fields"] = t["fields"]
            if "members" in t: entity["members"] = t["members"]
            expected.append(entity)
        for s in m.get("services", []):
            expected.append({
                "kind": "service",
                "name": s["name"],
                "domain": mpath,
                "methods": s.get("methods", []),
            })
    orch = spec.get("orchestrators") or {}
    for s in orch.get("services", []):
        expected.append({
            "kind": "service",
            "name": s["name"],
            "domain": "orchestrators",
            "methods": s.get("methods", []),
        })
    return expected


def collect_expected(spec):
    """Dispatch on spec.shape; default DDD for backward compatibility."""
    if spec.get("shape") == "modular-monolith":
        return collect_expected_monolith(spec)
    return collect_expected_ddd(spec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant_dir")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--language", default=os.environ.get("LANGUAGE", "typescript"))
    args = ap.parse_args()

    cfg = LANGUAGE_CONFIG.get(args.language)
    if not cfg:
        sys.stderr.write(f"unknown language: {args.language}; known: {list(LANGUAGE_CONFIG)}\n")
        sys.exit(2)

    vdir = Path(args.variant_dir)
    out_dir = vdir / "output"
    spec = json.load(open(args.spec))
    expected = collect_expected(spec)

    counts = {"pass": 0, "structural_fail": 0, "missing": 0}
    issues_log = []
    for entity in expected:
        checker = CHECKERS.get(entity["kind"])
        if not checker:
            continue
        status, file, issues = checker(out_dir, cfg, entity)
        counts[status] = counts.get(status, 0) + 1
        if status != "pass":
            issues_log.append({
                "kind":   entity["kind"],
                "name":   entity["name"],
                "domain": entity["domain"],
                "status": status,
                "file":   str(file.relative_to(out_dir)) if file else None,
                "issues": issues,
            })

    files = list(out_dir.rglob(f"*{cfg['ext']}")) if out_dir.exists() else []
    compile_fn = COMPILE_FNS.get(cfg["compile"])
    compile_errors = compile_fn(out_dir, vdir / "compile.log") if compile_fn else -2

    # Verdict ladder
    if not files:
        verdict = "no_files"
    elif counts["missing"] > 0:
        verdict = "missing_entities"
    elif counts["structural_fail"] > 0:
        verdict = "structural_fail"
    elif compile_errors > 0:
        verdict = "compile_errors"
    elif compile_errors < 0:
        verdict = "compile_unknown"
    else:
        verdict = "pass"

    out = {
        "verdict": verdict,
        "language": args.language,
        "ts_file_count": len(files),  # historical name; counts files in target language ext
        "expected_total": len(expected),
        "tsc_errors": compile_errors,  # historical name; counts compile errors in target compiler
        "structural_counts": counts,
        "issues_per_entity": issues_log[:30],
    }
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
