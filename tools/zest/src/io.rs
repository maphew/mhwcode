use std::fs::{self, File};
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

/// Compress `src` in place. Writes `src.<suffix>` and removes `src` on success.
pub fn compress_in_place(src: &Path, fmt: Format, level: Option<i32>) -> Result<PathBuf> {
    let out_path = compressed_path(src, fmt);
    if out_path.exists() {
        return Err(Error::OutputExists(out_path));
    }
    let input = BufReader::new(File::open(src)?);
    let output = BufWriter::new(File::create(&out_path)?);
    let result = encode(input, output, fmt, level);
    if let Err(e) = result {
        // best-effort cleanup so we don't leave a half-written output.
        let _ = fs::remove_file(&out_path);
        return Err(e);
    }
    fs::remove_file(src)?;
    Ok(out_path)
}

/// Decompress `src` in place. Detects the format and removes `src` on success.
pub fn decompress_in_place(src: &Path) -> Result<(PathBuf, Format)> {
    let mut head = [0u8; 6];
    let mut f = File::open(src)?;
    let n = f.read(&mut head)?;
    let fmt = Format::detect(&head[..n]).ok_or(Error::UnknownFormat)?;
    drop(f);

    let out_path = decompressed_path(src);
    if out_path.exists() {
        return Err(Error::OutputExists(out_path));
    }
    let input = BufReader::new(File::open(src)?);
    let output = BufWriter::new(File::create(&out_path)?);
    let result = decode(input, output, fmt);
    if let Err(e) = result {
        let _ = fs::remove_file(&out_path);
        return Err(e);
    }
    fs::remove_file(src)?;
    Ok((out_path, fmt))
}

fn encode<R: Read, W: Write>(
    mut input: R,
    output: W,
    fmt: Format,
    level: Option<i32>,
) -> Result<()> {
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

        let compressed = compress_in_place(&src, fmt, None).unwrap();
        assert!(compressed.exists(), "compressed output missing for {fmt}");
        assert!(!src.exists(), "source not removed after compress for {fmt}");
        assert_eq!(compressed.extension().unwrap(), fmt.suffix());

        let (restored, detected) = decompress_in_place(&compressed).unwrap();
        assert_eq!(detected, fmt);
        assert!(!compressed.exists(), "compressed not removed after decompress for {fmt}");
        assert_eq!(restored, src, "restored path mismatch for {fmt}");
        assert_eq!(fs::read(&restored).unwrap(), PAYLOAD, "payload mismatch for {fmt}");
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
        let compressed = compress_in_place(&gz_src, Format::Gzip, None).unwrap();

        let lying = dir.path().join("lying.xz");
        fs::rename(&compressed, &lying).unwrap();

        let (restored, detected) = decompress_in_place(&lying).unwrap();
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

        match compress_in_place(&src, Format::Zstd, None) {
            Err(Error::OutputExists(_)) => {}
            other => panic!("expected OutputExists, got {other:?}"),
        }
        assert!(src.exists(), "source should not be removed when clobber refused");
    }

    #[test]
    fn decompress_unknown_format_errors() {
        let dir = tempdir().unwrap();
        let src = dir.path().join("plain.bin");
        fs::write(&src, b"not a compressed file at all, nope").unwrap();
        match decompress_in_place(&src) {
            Err(Error::UnknownFormat) => {}
            other => panic!("expected UnknownFormat, got {other:?}"),
        }
        assert!(src.exists(), "source should not be removed on detection failure");
    }
}
