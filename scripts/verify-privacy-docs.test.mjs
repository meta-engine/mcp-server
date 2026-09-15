import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";

class PrivacyContractFixture {
  constructor(sourceRoot, scriptName) {
    this.sourceRoot = sourceRoot;
    this.scriptName = scriptName;
  }

  run(mutate) {
    const root = mkdtempSync(join(tmpdir(), "metaengine-privacy-contract-"));
    try {
      mkdirSync(join(root, "scripts"));
      writeFileSync(join(root, "scripts", "verify.mjs"), readFileSync(join(this.sourceRoot, "scripts", this.scriptName)));
      const documents = new Map(["PRIVACY.md", "README.md", "TERMS.md"].map(name => [name, readFileSync(join(this.sourceRoot, name), "utf8")]));
      mutate(documents);
      for (const [name, content] of documents) writeFileSync(join(root, name), content);
      const result = spawnSync(process.execPath, [join(root, "scripts", "verify.mjs")], { encoding: "utf8" });
      assert.ifError(result.error);
      assert.equal(result.signal, null);
      return { status: result.status, output: result.stdout + result.stderr };
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  }
}

const fixture = new PrivacyContractFixture(fileURLToPath(new URL("..", import.meta.url)), "verify-privacy-docs.mjs");

test("current privacy documentation satisfies the executable contract", () => {
  const result = fixture.run(() => {});
  assert.equal(result.status, 0, result.output);
});

const omissions = [
  ["TypeCount", /`TypeCount`/, "type-limit count"],
  ["MaxAllowed", /`MaxAllowed`/, "type-limit maximum"],
  ["native file reads", /- Reads a native specification file[^\n]*\n/, "native specification file reads"],
  ["recipe and used input file reads", /- Reads a recipe file[^\n]*\n/, "recipe and used input file reads"],
  ["native payload transmission", /It sends native generation specifications[^.]*\./, "native generation payload"],
  ["local recipe expansion", /With `generate_from_recipe`[^.]*\./, "local recipe expansion"],
  ["incorporation-only input transmission", /Only the resulting generation payload[^.]*\./, "expanded payload transmission"],
];
for (const [name, pattern, violation] of omissions) {
  test(`privacy contract rejects an omitted ${name} disclosure`, () => {
    const result = fixture.run(documents => {
      const privacy = documents.get("PRIVACY.md");
      assert.match(privacy, pattern);
      documents.set("PRIVACY.md", privacy.replace(pattern, ""));
    });
    assert.equal(result.status, 1, result.output);
    assert.ok(result.output.includes(`PRIVACY.md is missing ${violation}`), result.output);
  });
}

test("privacy contract rejects claiming every declared input file is read", () => {
  const result = fixture.run(documents => {
    const privacy = documents.get("PRIVACY.md");
    assert.ok(privacy.includes("when an instance uses them"));
    documents.set("PRIVACY.md", privacy.replaceAll("when an instance uses them", "whenever declared"));
  });
  assert.equal(result.status, 1, result.output);
  assert.match(result.output, /missing recipe and used input file reads/);
  assert.match(result.output, /missing local recipe expansion/);
});

test("privacy contract still rejects contradictory absolute logging claims", () => {
  const result = fixture.run(documents => documents.set("README.md", documents.get("README.md") + "\nRequests are not logged.\n"));
  assert.equal(result.status, 1, result.output);
  assert.match(result.output, /README.md contains contradictory absolute claim/);
});
