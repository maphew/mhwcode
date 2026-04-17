use std::env;
use std::ffi::OsString;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use zest::format::Format;
use zest::io::{compress_in_place, decompress_in_place};

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

fn mode_from_argv0(argv0: &Path) -> Mode {
    let stem = argv0
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("zest");
    // Case-insensitive compare so `Unzest.exe` on Windows works.
    if stem.eq_ignore_ascii_case("unzest") {
        Mode::Decompress
    } else {
        Mode::Compress
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Mode {
    Compress,
    Decompress,
}

fn run(argv0: &OsString, args: &[OsString]) -> Result<(), u8> {
    let mode = mode_from_argv0(Path::new(argv0));
    let mut fmt = Format::Zstd;
    let mut level: Option<i32> = None;
    let mut files: Vec<PathBuf> = Vec::new();

    let mut it = args.iter();
    while let Some(a) = it.next() {
        let s = match a.to_str() {
            Some(s) => s,
            None => {
                // non-UTF-8 argument: treat as a filename.
                files.push(PathBuf::from(a));
                continue;
            }
        };
        match s {
            "-h" | "--help" => {
                print_help(mode);
                return Ok(());
            }
            "-V" | "--version" => {
                println!("zest {VERSION}");
                return Ok(());
            }
            "--" => {
                for rest in it.by_ref() {
                    files.push(PathBuf::from(rest));
                }
                break;
            }
            "-f" | "--format" if mode == Mode::Compress => {
                let v = it.next().ok_or_else(|| err("-f requires a value"))?;
                fmt = v
                    .to_str()
                    .and_then(|s| s.parse().ok())
                    .ok_or_else(|| err("unknown format (expected: zstd|gz|xz|bz2)"))?;
            }
            "-l" | "--level" if mode == Mode::Compress => {
                let v = it.next().ok_or_else(|| err("-l requires a value"))?;
                level = Some(
                    v.to_str()
                        .and_then(|s| s.parse().ok())
                        .ok_or_else(|| err("-l value must be an integer"))?,
                );
            }
            other if other.starts_with('-') && other != "-" => {
                return Err(err(&format!("unknown option: {other}")));
            }
            _ => files.push(PathBuf::from(a)),
        }
    }

    if files.is_empty() {
        return Err(err("no input files"));
    }

    let mut had_error = false;
    for f in &files {
        let result = match mode {
            Mode::Compress => compress_in_place(f, fmt, level).map(|p| {
                println!("{} -> {}", f.display(), p.display());
            }),
            Mode::Decompress => decompress_in_place(f).map(|(p, detected)| {
                println!("{} [{}] -> {}", f.display(), detected, p.display());
            }),
        };
        if let Err(e) = result {
            eprintln!("{}: {}", f.display(), e);
            had_error = true;
        }
    }
    if had_error { Err(1) } else { Ok(()) }
}

fn err(msg: &str) -> u8 {
    eprintln!("error: {msg}");
    2
}

fn print_help(mode: Mode) {
    match mode {
        Mode::Compress => {
            println!(
                "zest {VERSION} - compress files in place\n\n\
                 usage: zest [-f FMT] [-l LEVEL] FILE...\n\n\
                 options:\n\
                 \x20 -f, --format {{zstd|gz|xz|bz2}}  compression format (default: zstd)\n\
                 \x20 -l, --level  LEVEL              compression level (format-specific)\n\
                 \x20 -h, --help                      show this help\n\
                 \x20 -V, --version                   print version\n"
            );
        }
        Mode::Decompress => {
            println!(
                "unzest {VERSION} - decompress files in place (format auto-detected)\n\n\
                 usage: unzest FILE...\n"
            );
        }
    }
}
