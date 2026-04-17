use std::fs::{self, File, OpenOptions};
use std::io::{self, BufReader, BufWriter, Read, Write};
use std::path::{Path, PathBuf};

use crate::format::Format;
use crate::naming::{compressed_path, decompressed_path};

#[derive(Debug)]
pub enum Error {
    Io(io::Error),
    OutputExists(PathBuf),
    UnknownFormat,
    UnsupportedFormat(Format),
}

impl From<io::Error> for Error {
    fn from(e: io::Error) -> Self {
        Error::Io(e)
    }
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Error::Io(e) => write!(f, "io: {e}"),
            Error::OutputExists(p) => write!(f, "refusing to clobber: {}", p.display()),
            Error::UnknownFormat => write!(f, "could not identify compression format"),
            Error::UnsupportedFormat(fmt) => write!(f, "no decompressor compiled in for {fmt}"),
        }
    }
}

impl std::error::Error for Error {}

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Debug, Default, Clone, Copy)]
pub struct Options {
    /// Don't remove the source file after a successful operation.
    pub keep: bool,
    /// Overwrite an existing destination instead of erroring.
    pub force: bool,
}

/// Compress `src` in place. Writes `src.<suffix>`; removes `src` unless `opts.keep`.
pub fn compress_in_place(
    src: &Path,
    fmt: Format,
    level: Option<i32>,
    opts: Options,
) -> Result<PathBuf> {
    let out_path = compressed_path(src, fmt);
    let output = open_output(&out_path, opts.force)?;
    let input = BufReader::new(File::open(src)?);
    if let Err(e) = encode(input, output, fmt, level) {
        let _ = fs::remove_file(&out_path);
        return Err(e);
    }
    if !opts.keep {
        fs::remove_file(src)?;
    }
    Ok(out_path)
}

/// Decompress `src` in place. Detects format; removes `src` unless `opts.keep`.
pub fn decompress_in_place(src: &Path, opts: Options) -> Result<(PathBuf, Format)> {
    let fmt = detect_format(src)?;
    let out_path = decompressed_path(src);
    let output = open_output(&out_path, opts.force)?;
    let input = BufReader::new(File::open(src)?);
    if let Err(e) = decode(input, output, fmt) {
        let _ = fs::remove_file(&out_path);
        return Err(e);
    }
    if !opts.keep {
        fs::remove_file(src)?;
    }
    Ok((out_path, fmt))
}

/// Stream the compressed form of `src` into `out`. Never touches the source.
pub fn compress_to_writer<W: Write>(
    src: &Path,
    fmt: Format,
    level: Option<i32>,
    out: W,
) -> Result<()> {
    let input = BufReader::new(File::open(src)?);
    encode(input, out, fmt, level)
}

/// Stream the decompressed form of `src` into `out`. Returns the detected format.
pub fn decompress_to_writer<W: Write>(src: &Path, out: W) -> Result<Format> {
    let fmt = detect_format(src)?;
    let input = BufReader::new(File::open(src)?);
    decode(input, out, fmt)?;
    Ok(fmt)
}

/// `gzip -t` equivalent: decompress `src` into a sink and report any error.
pub fn test_file(src: &Path) -> Result<Format> {
    decompress_to_writer(src, io::sink())
}

fn detect_format(src: &Path) -> Result<Format> {
    let mut head = [0u8; 6];
    let mut f = File::open(src)?;
    let n = f.read(&mut head)?;
    Format::detect(&head[..n]).ok_or(Error::UnknownFormat)
}

fn open_output(path: &Path, force: bool) -> Result<BufWriter<File>> {
    let f = if force {
        OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(true)
            .open(path)?
    } else {
        OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(path)
            .map_err(|e| match e.kind() {
                io::ErrorKind::AlreadyExists => Error::OutputExists(path.to_path_buf()),
                _ => Error::Io(e),
            })?
    };
    Ok(BufWriter::new(f))
}

fn encode<R: Read, W: Write>(mut input: R, output: W, fmt: Format, level: Option<i32>) -> Result<()> {
    match fmt {
        Format::Zstd => {
            let lvl = level.unwrap_or(3);
            let mut enc = zstd::stream::write::Encoder::new(output, lvl)?;
            io::copy(&mut input, &mut enc)?;
            let mut out = enc.finish()?;
            out.flush()?;
        }
        Format::Gzip => {
            let lvl = level.map(|l| l.clamp(0, 9) as u32).unwrap_or(6);
            let mut enc = flate2::write::GzEncoder::new(output, flate2::Compression::new(lvl));
            io::copy(&mut input, &mut enc)?;
            let mut out = enc.finish()?;
            out.flush()?;
        }
        Format::Xz => {
            let lvl = level.map(|l| l.clamp(0, 9) as u32).unwrap_or(6);
            let mut enc = xz2::write::XzEncoder::new(output, lvl);
            io::copy(&mut input, &mut enc)?;
            let mut out = enc.finish()?;
            out.flush()?;
        }
        Format::Bzip2 => {
            let lvl = match level {
                Some(l) => bzip2::Compression::new(l.clamp(1, 9) as u32),
                None => bzip2::Compression::default(),
            };
            let mut enc = bzip2::write::BzEncoder::new(output, lvl);
            io::copy(&mut input, &mut enc)?;
            let mut out = enc.finish()?;
            out.flush()?;
        }
        other => return Err(Error::UnsupportedFormat(other)),
    }
    Ok(())
}

fn decode<R: Read, W: Write>(input: R, mut output: W, fmt: Format) -> Result<()> {
    match fmt {
        Format::Zstd => {
            let mut dec = zstd::stream::read::Decoder::new(input)?;
            io::copy(&mut dec, &mut output)?;
        }
        Format::Gzip => {
            let mut dec = flate2::read::GzDecoder::new(input);
            io::copy(&mut dec, &mut output)?;
        }
        Format::Xz => {
            let mut dec = xz2::read::XzDecoder::new(input);
            io::copy(&mut dec, &mut output)?;
        }
        Format::Bzip2 => {
            let mut dec = bzip2::read::BzDecoder::new(input);
            io::copy(&mut dec, &mut output)?;
        }
        other => return Err(Error::UnsupportedFormat(other)),
    }
    output.flush()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::tempdir;

    const PAYLOAD: &[u8] = b"the quick brown fox jumps over the lazy dog\n\
        the rain in spain falls mainly on the plain\n\
        pack my box with five dozen liquor jugs\n";

    fn roundtrip(fmt: Format) {
        let dir = tempdir().unwrap();
        let src = dir.path().join("sample.txt");
        fs::write(&src, PAYLOAD).unwrap();

        let compressed = compress_in_place(&src, fmt, None, Options::default()).unwrap();
        assert!(compressed.exists());
        assert!(!src.exists());
        assert_eq!(compressed.extension().unwrap(), fmt.suffix());

        let (restored, detected) = decompress_in_place(&compressed, Options::default()).unwrap();
        assert_eq!(detected, fmt);
        assert!(!compressed.exists());
        assert_eq!(restored, src);
        assert_eq!(fs::read(&restored).unwrap(), PAYLOAD);
    }

    #[test]
    fn roundtrip_zstd() { roundtrip(Format::Zstd); }
    #[test]
    fn roundtrip_gzip() { roundtrip(Format::Gzip); }
    #[test]
    fn roundtrip_xz() { roundtrip(Format::Xz); }
    #[test]
    fn roundtrip_bzip2() { roundtrip(Format::Bzip2); }

    #[test]
    fn decompress_with_misleading_extension() {
        let dir = tempdir().unwrap();
        let gz_src = dir.path().join("real.txt");
        fs::write(&gz_src, PAYLOAD).unwrap();
        let compressed = compress_in_place(&gz_src, Format::Gzip, None, Options::default()).unwrap();

        let lying = dir.path().join("lying.xz");
        fs::rename(&compressed, &lying).unwrap();

        let (restored, detected) = decompress_in_place(&lying, Options::default()).unwrap();
        assert_eq!(detected, Format::Gzip);
        assert_eq!(restored, dir.path().join("lying"));
        assert_eq!(fs::read(&restored).unwrap(), PAYLOAD);
    }

    #[test]
    fn compress_refuses_to_clobber() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("a.txt");
        fs::write(&src, PAYLOAD).unwrap();
        fs::write(dir.path().join("a.txt.zst"), b"existing").unwrap();

        match compress_in_place(&src, Format::Zstd, None, Options::default()) {
            Err(Error::OutputExists(_)) => {}
            other => panic!("expected OutputExists, got {other:?}"),
        }
        assert!(src.exists());
    }

    #[test]
    fn decompress_unknown_format_errors() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("plain.bin");
        fs::write(&src, b"not a compressed file at all, nope").unwrap();
        match decompress_in_place(&src, Options::default()) {
            Err(Error::UnknownFormat) => {}
            other => panic!("expected UnknownFormat, got {other:?}"),
        }
        assert!(src.exists());
    }

    // ---- new: Options (keep, force) ----

    #[test]
    fn keep_preserves_source_on_compress() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("a.txt");
        fs::write(&src, PAYLOAD).unwrap();

        let opts = Options { keep: true, ..Options::default() };
        let out = compress_in_place(&src, Format::Zstd, None, opts).unwrap();
        assert!(src.exists(), "keep=true must preserve source");
        assert!(out.exists());
    }

    #[test]
    fn keep_preserves_source_on_decompress() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("a.txt");
        fs::write(&src, PAYLOAD).unwrap();
        let compressed =
            compress_in_place(&src, Format::Gzip, None, Options::default()).unwrap();

        let opts = Options { keep: true, ..Options::default() };
        let (restored, _) = decompress_in_place(&compressed, opts).unwrap();
        assert!(compressed.exists(), "keep=true must preserve compressed source");
        assert!(restored.exists());
    }

    #[test]
    fn force_overwrites_existing_output_on_compress() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("a.txt");
        fs::write(&src, PAYLOAD).unwrap();
        let stale = dir.path().join("a.txt.zst");
        fs::write(&stale, b"stale contents").unwrap();

        let opts = Options { force: true, ..Options::default() };
        compress_in_place(&src, Format::Zstd, None, opts).unwrap();
        assert!(stale.exists());
        // output must have been truncated & rewritten, not left as "stale contents"
        assert_ne!(fs::read(&stale).unwrap(), b"stale contents");
    }

    #[test]
    fn force_overwrites_existing_output_on_decompress() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("a.txt");
        fs::write(&src, PAYLOAD).unwrap();
        let compressed =
            compress_in_place(&src, Format::Xz, None, Options::default()).unwrap();
        // simulate a stale `a.txt` in the way
        fs::write(dir.path().join("a.txt"), b"stale").unwrap();

        let opts = Options { force: true, ..Options::default() };
        decompress_in_place(&compressed, opts).unwrap();
        assert_eq!(fs::read(dir.path().join("a.txt")).unwrap(), PAYLOAD);
    }

    // ---- new: streaming ----

    #[test]
    fn compress_to_writer_then_decompress_to_writer() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("a.txt");
        fs::write(&src, PAYLOAD).unwrap();

        let mut buf: Vec<u8> = Vec::new();
        compress_to_writer(&src, Format::Zstd, None, &mut buf).unwrap();
        assert_eq!(&buf[..4], &[0x28, 0xB5, 0x2F, 0xFD]);
        assert!(src.exists(), "streaming must never touch source");

        let staged = dir.path().join("staged.zst");
        fs::write(&staged, &buf).unwrap();
        let mut plain = Vec::new();
        let fmt = decompress_to_writer(&staged, &mut plain).unwrap();
        assert_eq!(fmt, Format::Zstd);
        assert_eq!(plain, PAYLOAD);
    }

    // ---- new: test mode ----

    #[test]
    fn test_file_passes_valid_archive() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("a.txt");
        fs::write(&src, PAYLOAD).unwrap();
        let compressed =
            compress_in_place(&src, Format::Bzip2, None, Options::default()).unwrap();
        assert_eq!(test_file(&compressed).unwrap(), Format::Bzip2);
    }

    #[test]
    fn test_file_fails_on_corruption() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("a.txt");
        fs::write(&src, PAYLOAD).unwrap();
        let compressed =
            compress_in_place(&src, Format::Gzip, None, Options::default()).unwrap();

        // Flip a byte in the deflate stream (skip the 10-byte gzip header).
        let mut bytes = fs::read(&compressed).unwrap();
        let i = 12.min(bytes.len() - 1);
        bytes[i] ^= 0xFF;
        fs::write(&compressed, &bytes).unwrap();

        assert!(test_file(&compressed).is_err(), "corrupted archive must fail test");
    }
}
