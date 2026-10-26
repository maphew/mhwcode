/**
 * Weekly repo digest for the mhwcode script collection.
 *
 * Runs at workflow scope and rolls the read-only step outputs into one durable
 * artifact: working-tree drift, recent commits touching script directories, and
 * the script syntax sweep by directory. The git steps in the workflow are
 * `ephemeral` resources, so this report is what survives the run.
 *
 * @module
 */

interface DataHandle {
  readonly name: string;
  readonly version?: number;
}

interface StepExecution {
  readonly jobName: string;
  readonly stepName: string;
  readonly modelName: string;
  readonly modelType: string;
  readonly methodName: string;
  readonly status: "succeeded" | "failed" | "skipped";
  readonly dataHandles: readonly DataHandle[];
  readonly modelId: string;
}

interface DigestContext {
  readonly scope: "workflow";
  readonly workflowName: string;
  readonly workflowRunId: string;
  readonly workflowStatus: "succeeded" | "failed";
  readonly stepExecutions: readonly StepExecution[];
  readonly dataRepository: {
    getContent(
      type: string,
      modelId: string,
      dataName: string,
      version?: number,
    ):
      | Uint8Array
      | string
      | ArrayBuffer
      | Promise<Uint8Array | string | ArrayBuffer | null>
      | null;
  };
  readonly logger: {
    warn(message: string, properties?: Record<string, unknown>): void;
  };
}

interface StatusEntry {
  status: string;
  path: string;
}

interface StatusPayload {
  entries: StatusEntry[];
  clean: boolean;
  count: number;
}

interface CommitEntry {
  sha: string;
  date: string;
  authorName?: string;
  message: string;
}

interface LogPayload {
  commits: CommitEntry[];
}

interface ScriptResult {
  path: string;
  extension: string;
  status: "ok" | "failed" | "timeout" | "skipped" | "legacy";
  message: string;
  likelyLegacyPython2: boolean;
}

interface SweepPayload {
  durationMs: number;
  scripts: ScriptResult[];
  summary: {
    total: number;
    ok: number;
    failed: number;
    timeout: number;
    skipped: number;
    legacy: number;
    legacyPython2: number;
  };
}

interface DirRollup {
  dir: string;
  total: number;
  ok: number;
  failed: number;
  timeout: number;
  skipped: number;
  legacy: number;
}

/** Normalize whatever the repository returns for content into text. */
async function contentToText(raw: unknown): Promise<string | null> {
  const value = await raw;
  if (value === null || value === undefined) return null;
  if (typeof value === "string") return value;
  if (value instanceof Uint8Array) return new TextDecoder().decode(value);
  if (value instanceof ArrayBuffer) {
    return new TextDecoder().decode(new Uint8Array(value));
  }
  if (ArrayBuffer.isView(value)) {
    return new TextDecoder().decode(
      new Uint8Array(value.buffer, value.byteOffset, value.byteLength),
    );
  }
  return null;
}

/** Decode the JSON resource behind a step's first handle of the given name. */
async function readStepData<T>(
  ctx: DigestContext,
  handleName: string,
): Promise<T | null> {
  for (const step of ctx.stepExecutions) {
    const handle = step.dataHandles.find((h) => h.name === handleName);
    if (!handle) continue;
    const text = await contentToText(
      ctx.dataRepository.getContent(
        step.modelType,
        step.modelId,
        handle.name,
        handle.version,
      ),
    );
    if (text === null) {
      ctx.logger.warn("repo-digest: no content for {name} on {step}", {
        name: handleName,
        step: step.stepName,
      });
      continue;
    }
    try {
      return JSON.parse(text) as T;
    } catch (error) {
      ctx.logger.warn("repo-digest: unparseable {name} on {step}: {error}", {
        name: handleName,
        step: step.stepName,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }
  return null;
}

/** Top-level directory of a script path, for the per-directory rollup. */
function topDir(path: string): string {
  const index = path.indexOf("/");
  return index === -1 ? "." : path.slice(0, index);
}

/** Aggregate sweep results by top-level directory. */
function rollupByDir(sweep: SweepPayload): DirRollup[] {
  const byDir = new Map<string, DirRollup>();
  for (const script of sweep.scripts) {
    const dir = topDir(script.path);
    const row = byDir.get(dir) ??
      { dir, total: 0, ok: 0, failed: 0, timeout: 0, skipped: 0, legacy: 0 };
    row.total += 1;
    row[script.status] += 1;
    byDir.set(dir, row);
  }
  return [...byDir.values()].sort((a, b) => a.dir.localeCompare(b.dir));
}

/** Shorten a commit message to its subject line. */
function subject(message: string): string {
  return message.split(/\r?\n/)[0].trim();
}

/** Markdown table from a header and rows. */
function table(headers: string[], rows: string[][]): string {
  const escape = (cell: string) => cell.replace(/\|/g, "\\|");
  return [
    `| ${headers.join(" | ")} |`,
    `| ${headers.map(() => "---").join(" | ")} |`,
    ...rows.map((row) =>
      `| ${row.map((cell) => escape(String(cell))).join(" | ")} |`
    ),
  ].join("\n");
}

/** Repo digest report — durable summary of one weekly health run. */
export const report = {
  name: "mhwcode/repo-digest",
  description:
    "Weekly digest of the mhwcode script collection: working-tree drift, recent commits touching script directories, and syntax-sweep results rolled up by directory",
  scope: "workflow" as const,
  labels: ["mhwcode", "digest", "drift", "health"],

  execute: async (ctx: DigestContext) => {
    const status = await readStepData<StatusPayload>(ctx, "status");
    const log = await readStepData<LogPayload>(ctx, "log");
    const sweep = await readStepData<SweepPayload>(ctx, "sweep");
    const generatedAt = new Date().toISOString();

    const byDir = sweep ? rollupByDir(sweep) : [];
    const legacy = sweep
      ? sweep.scripts.filter((s) => s.likelyLegacyPython2)
      : [];

    const lines: string[] = [
      `# mhwcode health digest`,
      "",
      `- Workflow: \`${ctx.workflowName}\` (${ctx.workflowStatus})`,
      `- Run: \`${ctx.workflowRunId}\``,
      `- Generated: ${generatedAt}`,
      "",
    ];

    if (status) {
      lines.push("## Working tree", "");
      lines.push(
        status.clean
          ? "Clean — nothing uncommitted."
          : `Dirty — ${status.count} change(s).`,
      );
      lines.push("");
      if (!status.clean) {
        lines.push(table(
          ["status", "path"],
          status.entries.slice(0, 40).map((e) => [e.status.trim(), e.path]),
        ));
        if (status.entries.length > 40) {
          lines.push("", `_…${status.entries.length - 40} more_`);
        }
        lines.push("");
      }
    }

    if (log && log.commits.length > 0) {
      lines.push("## Recent commits touching scripts", "");
      lines.push(table(
        ["date", "commit", "subject"],
        log.commits.map((c) => [
          c.date.slice(0, 10),
          c.sha.slice(0, 8),
          subject(c.message),
        ]),
      ));
      lines.push("");
    }

    if (sweep) {
      const s = sweep.summary;
      lines.push(
        "## Script sweep",
        "",
        `${s.total} scripts probed in ${sweep.durationMs} ms: ` +
          `${s.ok} ok, ${s.failed} failed, ${s.timeout} timeout, ${s.skipped} skipped, ` +
          `${s.legacy} known legacy Python 2. ` +
          `${s.legacyPython2} files parse as Python 2 overall.`,
        "",
      );
      if (byDir.length > 0) {
        lines.push(table(
          ["dir", "total", "ok", "failed", "timeout", "skipped", "legacy"],
          byDir.map((d) => [
            d.dir,
            String(d.total),
            String(d.ok),
            String(d.failed),
            String(d.timeout),
            String(d.skipped),
            String(d.legacy),
          ]),
        ));
        lines.push("");
      }
      const realFailures = sweep.scripts.filter((x) => x.status === "failed");
      if (realFailures.length > 0) {
        lines.push("### Failures needing a look", "");
        for (const failure of realFailures.slice(0, 25)) {
          lines.push(`- \`${failure.path}\` — ${failure.message}`);
        }
        lines.push("");
      }
      const newLegacy = legacy.filter((s) => s.status === "failed");
      if (newLegacy.length > 0) {
        lines.push(
          `### New Python 2 drift (${newLegacy.length}) — not in the baseline`,
          "",
        );
        for (const script of newLegacy) {
          lines.push(`- \`${script.path}\` — ${script.message}`);
        }
        lines.push("");
      }
      if (legacy.length > 0) {
        lines.push(`### Known legacy Python 2 (${legacy.length})`, "");
        for (const script of legacy.slice(0, 25)) {
          lines.push(`- \`${script.path}\` — ${script.message}`);
        }
        if (legacy.length > 25) {
          lines.push(`- _…${legacy.length - 25} more_`);
        }
        lines.push("");
      }
    }

    return {
      markdown: lines.join("\n"),
      json: {
        generatedAt,
        workflowName: ctx.workflowName,
        workflowRunId: ctx.workflowRunId,
        workflowStatus: ctx.workflowStatus,
        workingTree: status
          ? {
            clean: status.clean,
            count: status.count,
            entries: status.entries,
          }
          : null,
        recentCommits: log
          ? log.commits.map((c) => ({
            sha: c.sha,
            date: c.date,
            subject: subject(c.message),
          }))
          : [],
        scriptSweep: sweep
          ? {
            summary: sweep.summary,
            byDir,
            legacyPython2: legacy.map((s) => ({
              path: s.path,
              message: s.message,
            })),
            failures: sweep.scripts
              .filter((s) => s.status === "failed")
              .map((s) => ({ path: s.path, message: s.message })),
            newLegacyDrift: sweep.scripts
              .filter((s) => s.status === "failed" && s.likelyLegacyPython2)
              .map((s) => ({ path: s.path, message: s.message })),
          }
          : null,
      },
    };
  },
};
