use std::env;
use std::ffi::OsString;
use std::fs;
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use zest::format::Format;
use zest::io::{
    compress_in_place, compress_to_writer, decompress_in_place, decompress_to_writer, test_file,
    Options,
};

const VERSION: &str = env!("CARGO_PKG_VERSION");

fn main() -> ExitCode {
    let mut args = env::args_os();
    let argv0 = args.next().unwrap_or_else(|| OsString::from("zest"));
    let rest: Vec<OsString> = args.collect();
    match run(&argv0, &rest) {
        Ok(()) => ExitCode::SUCCESS,
        Err(code) => ExitCode::from(code),
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Mode {
    Compress,
    Decompress,
}

#[derive(Debug, Default)]
struct Cli {
    mode: Option<Mode>,
    format: Option<Format>,
    level: Option<i32>,
    keep: bool,
    force: bool,
    stdout: bool,
    quiet: bool,
    verbose: bool,
    test: bool,
    recursive: bool,
    help: bool,
    version: bool,
    files: Vec<PathBuf>,
}

fn default_mode_from_argv0(argv0: &Path) -> Mode {
    let stem = argv0.file_stem().and_then(|s| s.to_str()).unwrap_or("zest");
    if stem.eq_ignore_ascii_case("unzest") { Mode::Decompress } else { Mode::Compress }
}

fn run(argv0: &OsString, args: &[OsString]) -> Result<(), u8> {
    let default_mode = default_mode_from_argv0(Path::new(argv0));
    let cli = parse_args(args)?;

    if cli.help {
        print_help(cli.mode.unwrap_or(default_mode));
        return Ok(());
    }
    if cli.version {
        println!("zest {VERSION}");
        return Ok(());
    }

    let mode = cli.mode.unwrap_or(default_mode);
    if cli.files.is_empty() {
        return Err(err("no input files"));
    }
    if cli.quiet && cli.verbose {
        return Err(err("--quiet and --verbose are mutually exclusive"));
    }
    if cli.stdout && cli.test {
        return Err(err("--stdout and --test are mutually exclusive"));
    }

    let files = if cli.recursive { expand_recursive(&cli.files) } else { cli.files.clone() };

    let mut had_error = false;
    for f in &files {
        if let Err(e) = process_one(f, mode, &cli) {
            eprintln!("{}: {}", f.display(), e);
            had_error = true;
        }
    }
    if had_error { Err(1) } else { Ok(()) }
}

fn process_one(path: &Path, mode: Mode, cli: &Cli) -> Result<(), Box<dyn std::error::Error>> {
    // -c implies -k (source never removed).
    let keep = cli.keep || cli.stdout;
    let opts = Options { keep, force: cli.force };

    match mode {
        Mode::Compress => {
            let fmt = cli.format.unwrap_or(Format::Zstd);
            if cli.test {
                return Err("--test only applies in decompress mode".into());
            }
            if cli.stdout {
                let stdout = io::stdout();
                let mut lock = stdout.lock();
                compress_to_writer(path, fmt, cli.level, &mut lock)?;
                if cli.verbose {
                    eprintln!("{} -> <stdout> [{fmt}]", path.display());
                }
            } else {
                let out = compress_in_place(path, fmt, cli.level, opts)?;
                report(cli, &format!("{} -> {}", path.display(), out.display()));
            }
        }
        Mode::Decompress => {
            if cli.test {
                let fmt = test_file(path)?;
                report(cli, &format!("{}: {} OK", path.display(), fmt));
            } else if cli.stdout {
                let stdout = io::stdout();
                let mut lock = stdout.lock();
                let fmt = decompress_to_writer(path, &mut lock)?;
                if cli.verbose {
                    eprintln!("{} [{fmt}] -> <stdout>", path.display());
                }
            } else {
                let (out, fmt) = decompress_in_place(path, opts)?;
                report(cli, &format!("{} [{fmt}] -> {}", path.display(), out.display()));
            }
        }
    }
    Ok(())
}

fn report(cli: &Cli, msg: &str) {
    if cli.quiet {
        return;
    }
    if cli.verbose {
        let _ = writeln!(io::stderr(), "{msg}");
    } else {
        // default: quiet-ish like gzip (gzip prints nothing on success). We
        // keep a single-line note on stdout so batch runs are traceable, but
        // -q silences it.
        println!("{msg}");
    }
}

fn expand_recursive(inputs: &[PathBuf]) -> Vec<PathBuf> {
    let mut out = Vec::with_capacity(inputs.len());
    for p in inputs {
        walk_into(p, &mut out);
    }
    out
}

fn walk_into(p: &Path, acc: &mut Vec<PathBuf>) {
    match fs::metadata(p) {
        Ok(m) if m.is_dir() => match fs::read_dir(p) {
            Ok(entries) => {
                let mut children: Vec<_> = entries.flatten().map(|e| e.path()).collect();
                children.sort();
                for c in children {
                    walk_into(&c, acc);
                }
            }
            Err(_) => acc.push(p.to_path_buf()),
        },
        _ => acc.push(p.to_path_buf()),
    }
}

// ---------------- argv parser ----------------

fn parse_args(args: &[OsString]) -> Result<Cli, u8> {
    let mut cli = Cli::default();
    let mut it = args.iter();
    while let Some(a) = it.next() {
        let Some(s) = a.to_str() else {
            cli.files.push(PathBuf::from(a));
            continue;
        };

        if s == "--" {
            for rest in it.by_ref() {
                cli.files.push(PathBuf::from(rest));
            }
            break;
        }

        if let Some(long) = s.strip_prefix("--") {
            parse_long(long, &mut cli, &mut it)?;
        } else if let Some(short) = s.strip_prefix('-') {
            if short.is_empty() {
                // bare `-`: treat as filename (we don't support stdin input yet).
                cli.files.push(PathBuf::from(a));
            } else {
                parse_short(short, &mut cli)?;
            }
        } else {
            cli.files.push(PathBuf::from(a));
        }
    }
    Ok(cli)
}

fn parse_long(
    long: &str,
    cli: &mut Cli,
    it: &mut std::slice::Iter<'_, OsString>,
) -> Result<(), u8> {
    let (name, attached) = match long.split_once('=') {
        Some((n, v)) => (n, Some(v)),
        None => (long, None),
    };
    match name {
        "help" => cli.help = true,
        "version" => cli.version = true,
        "keep" => cli.keep = true,
        "stdout" => cli.stdout = true,
        "force" => cli.force = true,
        "quiet" => cli.quiet = true,
        "verbose" => cli.verbose = true,
        "test" => cli.test = true,
        "recursive" => cli.recursive = true,
        "decompress" | "uncompress" => cli.mode = Some(Mode::Decompress),
        "compress" => cli.mode = Some(Mode::Compress),
        "format" => {
            let v = take_value(name, attached, it)?;
            cli.format = Some(v.parse().map_err(|_| err("unknown format (zstd|gz|xz|bz2)"))?);
        }
        "level" => {
            let v = take_value(name, attached, it)?;
            cli.level = Some(v.parse().map_err(|_| err("--level must be an integer"))?);
        }
        other => return Err(err(&format!("unknown option: --{other}"))),
    }
    Ok(())
}

fn parse_short(short: &str, cli: &mut Cli) -> Result<(), u8> {
    let mut chars = short.chars();
    while let Some(c) = chars.next() {
        match c {
            'h' => cli.help = true,
            'V' => cli.version = true,
            'k' => cli.keep = true,
            'c' => cli.stdout = true,
            'f' => cli.force = true,
            'q' => cli.quiet = true,
            'v' => cli.verbose = true,
            't' => cli.test = true,
            'r' => cli.recursive = true,
            'd' => cli.mode = Some(Mode::Decompress),
            'z' => cli.mode = Some(Mode::Compress),
            '1'..='9' => {
                cli.level = Some(c.to_digit(10).unwrap() as i32);
                // If there are trailing characters they should also be valid flags.
                // `-9kv` is accepted.
            }
            other => return Err(err(&format!("unknown option: -{other}"))),
        }
    }
    Ok(())
}

fn take_value<'a>(
    name: &str,
    attached: Option<&'a str>,
    it: &mut std::slice::Iter<'_, OsString>,
) -> Result<String, u8> {
    if let Some(v) = attached {
        return Ok(v.to_string());
    }
    match it.next() {
        Some(v) => v.to_str().map(String::from).ok_or_else(|| err("value must be UTF-8")),
        None => Err(err(&format!("--{name} requires a value"))),
    }
}

fn err(msg: &str) -> u8 {
    eprintln!("error: {msg}");
    2
}

fn print_help(mode: Mode) {
    match mode {
        Mode::Compress => println!(
            "zest {VERSION} - compress files in place (format-agnostic)\n\n\
             usage: zest [OPTIONS] FILE...\n\n\
             options:\n\
             \x20     --format {{zstd|gz|xz|bz2}}  compression format (default: zstd)\n\
             \x20     --level N                   compression level\n\
             \x20 -1 .. -9                         level shortcut\n\
             \x20 -k, --keep                       keep source file\n\
             \x20 -c, --stdout                     write to stdout, keep source\n\
             \x20 -f, --force                      overwrite existing output\n\
             \x20 -v, --verbose                    emit per-file summary on stderr\n\
             \x20 -q, --quiet                      suppress per-file summary\n\
             \x20 -r, --recursive                  descend directories\n\
             \x20 -d, --decompress                 decompress (same as unzest)\n\
             \x20 -h, --help                       show this help\n\
             \x20 -V, --version                    print version\n"
        ),
        Mode::Decompress => println!(
            "unzest {VERSION} - decompress files in place (format auto-detected)\n\n\
             usage: unzest [OPTIONS] FILE...\n\n\
             options:\n\
             \x20 -k, --keep                       keep source file\n\
             \x20 -c, --stdout                     write to stdout, keep source\n\
             \x20 -f, --force                      overwrite existing output\n\
             \x20 -t, --test                       verify integrity; never writes output\n\
             \x20 -v, --verbose                    emit per-file summary on stderr\n\
             \x20 -q, --quiet                      suppress per-file summary\n\
             \x20 -r, --recursive                  descend directories\n\
             \x20 -z, --compress                   compress (same as zest)\n\
             \x20 -h, --help                       show this help\n\
             \x20 -V, --version                    print version\n"
        ),
    }
}

