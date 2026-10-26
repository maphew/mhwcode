/**
 * Script health sweep for a utility-script repository.
 *
 * Walks the script directories once and probes every script in a single
 * fan-out run, so a whole collection gets a health verdict without one
 * behavior call per file.
 *
 * @module
 */
import { z } from "npm:zod@4.6.7";

/** Directories of the mhwcode tree that hold runnable scripts. */
const DEFAULT_DIRS = [
  "tools",
  "gis",
  "other",
  "video",
  "arcplus",
  "register-python",
  "Lib",
];

const DEFAULT_EXCLUDES = [
  ".git",
  ".venv",
  "venv",
  "__pycache__",
  "node_modules",
  "samples",
  "assets",
];

/** Probe kinds: `syntax` parses only (no imports, no side effects). */
const ProbeSchema = z.enum(["syntax", "help", "none"]);
type Probe = z.infer<typeof ProbeSchema>;

const StatusSchema = z.enum(["ok", "failed", "timeout", "skipped"]);
type Status = z.infer<typeof StatusSchema>;

const GlobalArgsSchema = z.object({
  rootPath: z.string().default(".").describe(
    "Repository root the script directories resolve against",
  ),
  dirs: z.array(z.string()).default(DEFAULT_DIRS).describe(
    "Script directories to scan, relative to rootPath",
  ),
  extensions: z.array(z.string()).default([
    ".py",
    ".ps1",
    ".bat",
    ".cmd",
    ".sh",
  ])
    .describe("File extensions treated as scripts"),
  probe: ProbeSchema.default("syntax").describe(
    "Default probe: syntax parses without executing, help runs --help, none only lists",
  ),
  timeoutMs: z.number().int().positive().default(20000).describe(
    "Per-script probe timeout in milliseconds",
  ),
  concurrency: z.number().int().positive().max(16).default(4).describe(
    "Number of probes to run in parallel",
  ),
  excludes: z.array(z.string()).default(DEFAULT_EXCLUDES).describe(
    "Directory names skipped while walking",
  ),
});

type GlobalArgs = z.infer<typeof GlobalArgsSchema>;

const CheckArgsSchema = z.object({
  dirs: z.array(z.string()).optional().describe(
    "Override the scanned directories",
  ),
  paths: z.array(z.string()).optional().describe(
    "Explicit script paths (relative to rootPath) to check instead of a directory walk",
  ),
  probe: ProbeSchema.optional().describe(
    "Override the probe kind for this run",
  ),
  timeoutMs: z.number().int().positive().optional().describe(
    "Override the per-script timeout",
  ),
  concurrency: z.number().int().positive().max(16).optional().describe(
    "Override the parallelism",
  ),
});

const ScriptResultSchema = z.object({
  path: z.string().describe("Script path relative to rootPath"),
  extension: z.string(),
  probe: z.string(),
  status: StatusSchema,
  exitCode: z.number().int().nullable(),
  durationMs: z.number().int(),
  message: z.string().describe(
    "Line number and error, when the probe reported one",
  ),
  likelyLegacyPython2: z.boolean().describe(
    "Python file that fails Python 3 parsing but carries Python 2 constructs",
  ),
});

const SweepResultSchema = z.object({
  rootPath: z.string(),
  probe: z.string(),
  dirs: z.array(z.string()),
  startedAt: z.string(),
  durationMs: z.number().int(),
  scripts: z.array(ScriptResultSchema),
  failed: z.array(z.string()).describe("Scripts that failed or timed out"),
  summary: z.object({
    total: z.number().int(),
    ok: z.number().int(),
    failed: z.number().int(),
    timeout: z.number().int(),
    skipped: z.number().int(),
    legacyPython2: z.number().int().describe(
      "Failed scripts that look like unconverted Python 2",
    ),
  }),
});

interface ExecOutcome {
  readonly status: Status;
  readonly exitCode: number | null;
  readonly message: string;
}

interface ProbeContext {
  readonly globalArgs: GlobalArgs;
  readonly logger: {
    info(message: string, properties?: Record<string, unknown>): void;
    warn(message: string, properties?: Record<string, unknown>): void;
  };
  readonly signal?: AbortSignal;
}

/** First non-empty line of command output, trimmed and length-capped. */
function firstLine(text: string, cap = 240): string {
  const line = text.split(/\r?\n/).map((l) => l.trim()).find((l) =>
    l.length > 0
  );
  if (!line) return "";
  return line.length > cap ? `${line.slice(0, cap)}…` : line;
}

/**
 * Pull the diagnostic out of command output: the last `…Error:` line, with a
 * source line number when the tool reported one, instead of a traceback header.
 */
function errorSummary(text: string, cap = 240): string {
  const lines = text.split(/\r?\n/).map((l) => l.trim()).filter((l) =>
    l.length > 0
  );
  const diagnostic = [...lines].reverse().find((l) => /error/i.test(l)) ??
    lines[lines.length - 1] ?? "";
  const lineMatches = [...text.matchAll(/line (\d+)/g)];
  const lineNumber = lineMatches.length > 0
    ? lineMatches[lineMatches.length - 1][1]
    : undefined;
  const message = lineNumber && !/^line \d+/.test(diagnostic)
    ? `line ${lineNumber}: ${diagnostic}`
    : diagnostic;
  return message.length > cap ? `${message.slice(0, cap)}…` : message;
}

/** Python 2 constructs that a Python 3 parser rejects. */
const PY2_MARKERS = [
  /^\s*print\s+(?!\()/m,
  /^\s*except\s+[\w.]+\s*,\s*\w+\s*:/m,
  /\braw_input\s*\(/,
  /\b(iteritems|itervalues|iterkeys|has_key)\s*\(/,
  /`[^`]+`/,
  /<>/,
];

/** True when a Python file carries constructs that only Python 2 accepts. */
async function looksLikePython2(absPath: string): Promise<boolean> {
  try {
    const source = await Deno.readTextFile(absPath);
    return PY2_MARKERS.some((marker) => marker.test(source));
  } catch {
    return false;
  }
}

/** Quote a path for a single-quoted PowerShell string literal. */
function psQuote(path: string): string {
  return path.replace(/'/g, "''");
}

/**
 * Build the argv for one script, or a skip reason when the extension has no
 * safe probe under the requested kind.
 */
function probeCommand(
  absPath: string,
  extension: string,
  probe: Probe,
): string[] | { skip: string } {
  if (probe === "none") return { skip: "probe none: listing only" };

  if (extension === ".py") {
    if (probe === "help") return ["python", absPath, "--help"];
    return [
      "python",
      "-c",
      "import ast,sys;ast.parse(open(sys.argv[1],'rb').read(),sys.argv[1])",
      absPath,
    ];
  }

  if (extension === ".ps1") {
    if (probe === "help") {
      return { skip: "no safe help probe for PowerShell scripts" };
    }
    const script =
      "$e=$null;[void][System.Management.Automation.Language.Parser]" +
      `::ParseFile('${psQuote(absPath)}',[ref]$null,[ref]$e);` +
      "if($e){$e|%{$_.Message};exit 1}";
    return ["powershell", "-NoProfile", "-NonInteractive", "-Command", script];
  }

  return {
    skip: `no ${probe} probe for ${extension} scripts`,
  };
}

/** Run one probe with a timeout, mapping abort/failure to a status. */
async function runProbe(
  argv: string[],
  cwd: string,
  timeoutMs: number,
  outerSignal?: AbortSignal,
): Promise<ExecOutcome> {
  const controller = new AbortController();
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);
  const forward = () => controller.abort();
  outerSignal?.addEventListener("abort", forward, { once: true });

  try {
    const command = new Deno.Command(argv[0], {
      args: argv.slice(1),
      cwd,
      stdout: "piped",
      stderr: "piped",
      signal: controller.signal,
    });
    const output = await command.output();
    const decoder = new TextDecoder();
    const stderr = decoder.decode(output.stderr).trim();
    const stdout = decoder.decode(output.stdout).trim();
    if (output.code === 0) {
      return { status: "ok", exitCode: 0, message: "" };
    }
    return {
      status: "failed",
      exitCode: output.code,
      message: errorSummary(stderr || stdout) || `exit ${output.code}`,
    };
  } catch (error) {
    if (timedOut) {
      return {
        status: "timeout",
        exitCode: null,
        message: `exceeded ${timeoutMs}ms`,
      };
    }
    if (outerSignal?.aborted) throw error;
    const message = error instanceof Error ? error.message : String(error);
    if (message.includes("NotFound") || message.includes("No such file")) {
      return {
        status: "skipped",
        exitCode: null,
        message: `${argv[0]} not found on PATH`,
      };
    }
    return { status: "failed", exitCode: null, message: firstLine(message) };
  } finally {
    clearTimeout(timer);
    outerSignal?.removeEventListener("abort", forward);
  }
}

/** Recursively collect script paths under one directory, honouring excludes. */
async function walk(
  absDir: string,
  dirName: string,
  extensions: readonly string[],
  excludes: readonly string[],
  out: string[],
): Promise<void> {
  let entries: Deno.DirEntry[];
  try {
    entries = [];
    for await (const entry of Deno.readDir(absDir)) entries.push(entry);
  } catch {
    return;
  }
  for (const entry of entries) {
    if (entry.isDirectory) {
      if (excludes.includes(entry.name) || entry.name.startsWith(".")) continue;
      await walk(
        `${absDir}/${entry.name}`,
        `${dirName}/${entry.name}`,
        extensions,
        excludes,
        out,
      );
      continue;
    }
    if (!entry.isFile) continue;
    const lower = entry.name.toLowerCase();
    if (extensions.some((ext) => lower.endsWith(ext.toLowerCase()))) {
      out.push(`${dirName}/${entry.name}`);
    }
  }
}

/** Run `worker` over `items` with a bounded number in flight. */
async function pool<T>(
  items: readonly T[],
  concurrency: number,
  worker: (item: T) => Promise<void>,
): Promise<void> {
  let next = 0;
  const runners = Array.from(
    { length: Math.min(concurrency, Math.max(items.length, 1)) },
    async () => {
      while (next < items.length) {
        const index = next++;
        await worker(items[index]);
      }
    },
  );
  await Promise.all(runners);
}

/** Script health behavior — one fan-out sweep per run. */
export const behavior = {
  type: "mhwcode/script-health",
  version: "2026.10.26.1",

  globalArguments: GlobalArgsSchema,

  resources: {
    sweepResult: {
      description:
        "Per-script probe verdicts for one sweep: status, exit code, duration, failure line, and totals",
      schema: SweepResultSchema,
      lifetime: "ephemeral" as const,
      garbageCollection: 10,
    },
  },

  methods: {
    check: {
      description:
        "Probe every script in the configured directories once and report ok/failed/timeout/skipped per script",
      arguments: CheckArgsSchema,
      execute: async (
        args: z.input<typeof CheckArgsSchema>,
        ctx: ProbeContext & {
          writeResource: (
            specName: string,
            name: string,
            data: Record<string, unknown>,
            overrides?: { tags?: Record<string, string> },
          ) => Promise<{ name: string }>;
        },
      ) => {
        const globalArgs = GlobalArgsSchema.parse(ctx.globalArgs);
        const parsed = CheckArgsSchema.parse(args);
        const rootPath = globalArgs.rootPath === "."
          ? Deno.cwd()
          : globalArgs.rootPath.replace(/\\/g, "/").replace(/\/$/, "");
        const dirs = parsed.dirs ?? globalArgs.dirs;
        const probe = parsed.probe ?? globalArgs.probe;
        const timeoutMs = parsed.timeoutMs ?? globalArgs.timeoutMs;
        const concurrency = parsed.concurrency ?? globalArgs.concurrency;
        const startedAt = new Date();
        const start = performance.now();

        // Collect the script list: explicit paths win, else walk each directory.
        let candidates: string[];
        if (parsed.paths && parsed.paths.length > 0) {
          candidates = [...parsed.paths];
        } else {
          candidates = [];
          for (const dir of dirs) {
            const abs = `${rootPath}/${dir}`.replace(/\/+$/, "");
            await walk(
              abs,
              dir,
              globalArgs.extensions,
              globalArgs.excludes,
              candidates,
            );
          }
        }
        candidates = [...new Set(candidates)].sort();
        ctx.logger.info("script-health: {count} scripts under {root}", {
          count: candidates.length,
          root: rootPath,
        });

        const results: z.infer<typeof ScriptResultSchema>[] = [];

        await pool(candidates, concurrency, async (relPath) => {
          const absPath = `${rootPath}/${relPath}`;
          const extension = (relPath.match(/\.[^.\\/]+$/)?.[0] ?? "")
            .toLowerCase();
          const built = probeCommand(absPath, extension, probe);
          const scriptStart = performance.now();

          if ("skip" in built) {
            results.push({
              path: relPath,
              extension,
              probe: "none",
              status: "skipped",
              exitCode: null,
              durationMs: 0,
              message: built.skip,
              likelyLegacyPython2: false,
            });
            return;
          }

          const outcome = await runProbe(
            built,
            rootPath,
            timeoutMs,
            ctx.signal,
          );
          if (outcome.status !== "ok") {
            ctx.logger.warn("script-health: {path} {status}: {message}", {
              path: relPath,
              status: outcome.status,
              message: outcome.message,
            });
          }
          const legacy = extension === ".py" && outcome.status === "failed" &&
            /syntax/i.test(outcome.message) &&
            await looksLikePython2(absPath);

          results.push({
            path: relPath,
            extension,
            probe,
            status: outcome.status,
            exitCode: outcome.exitCode,
            durationMs: Math.round(performance.now() - scriptStart),
            message: outcome.message,
            likelyLegacyPython2: legacy,
          });
        });

        results.sort((a, b) => a.path.localeCompare(b.path));
        const count = (status: Status) =>
          results.filter((r) => r.status === status).length;

        const handle = await ctx.writeResource("sweepResult", "sweep", {
          rootPath,
          probe,
          dirs,
          startedAt: startedAt.toISOString(),
          durationMs: Math.round(performance.now() - start),
          scripts: results,
          failed: results
            .filter((r) => r.status === "failed" || r.status === "timeout")
            .map((r) => r.path),
          summary: {
            total: results.length,
            ok: count("ok"),
            failed: count("failed"),
            timeout: count("timeout"),
            skipped: count("skipped"),
            legacyPython2: results.filter((r) => r.likelyLegacyPython2).length,
          },
        }, {
          tags: {
            method: "check",
            probe,
            failed: String(count("failed") + count("timeout")),
          },
        });

        return { dataHandles: [handle] };
      },
    },
  },
};
