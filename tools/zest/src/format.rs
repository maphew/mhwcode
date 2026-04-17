use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Format {
    Zstd,
    Gzip,
    Xz,
    Bzip2,
    Lz4,
    Lzip,
    Compress,
}

impl Format {
    /// Canonical suffix we append when compressing (without leading dot).
    pub fn suffix(self) -> &'static str {
        match self {
            Format::Zstd => "zst",
            Format::Gzip => "gz",
            Format::Xz => "xz",
            Format::Bzip2 => "bz2",
            Format::Lz4 => "lz4",
            Format::Lzip => "lz",
            Format::Compress => "Z",
        }
    }

    /// Every suffix we'll strip when deriving an output name for decompression.
    pub fn known_suffixes() -> &'static [&'static str] {
        &["zst", "zstd", "gz", "xz", "bz2", "bzip2", "lz4", "lz", "Z"]
    }

    /// Identify a compressed stream by its leading bytes. Needs at least 6.
    pub fn detect(head: &[u8]) -> Option<Format> {
        if head.len() < 6 {
            return None;
        }
        match head {
            [0x28, 0xB5, 0x2F, 0xFD, ..] => Some(Format::Zstd),
            [0x1F, 0x8B, ..] => Some(Format::Gzip),
            [0xFD, 0x37, 0x7A, 0x58, 0x5A, 0x00, ..] => Some(Format::Xz),
            [b'B', b'Z', b'h', ..] => Some(Format::Bzip2),
            [0x04, 0x22, 0x4D, 0x18, ..] => Some(Format::Lz4),
            [b'L', b'Z', b'I', b'P', ..] => Some(Format::Lzip),
            [0x1F, 0x9D, ..] => Some(Format::Compress),
            _ => None,
        }
    }
}

impl fmt::Display for Format {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Format::Zstd => "zstd",
            Format::Gzip => "gzip",
            Format::Xz => "xz",
            Format::Bzip2 => "bzip2",
            Format::Lz4 => "lz4",
            Format::Lzip => "lzip",
            Format::Compress => "compress",
        })
    }
}

impl std::str::FromStr for Format {
    type Err = String;
    fn from_str(s: &str) -> Result<Format, String> {
        match s {
            "zstd" | "zst" => Ok(Format::Zstd),
            "gz" | "gzip" => Ok(Format::Gzip),
            "xz" => Ok(Format::Xz),
            "bz2" | "bzip2" => Ok(Format::Bzip2),
            other => Err(format!("unsupported format: {other}")),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn detects_zstd() {
        assert_eq!(Format::detect(&[0x28, 0xB5, 0x2F, 0xFD, 0, 0]), Some(Format::Zstd));
    }

    #[test]
    fn detects_gzip() {
        assert_eq!(Format::detect(&[0x1F, 0x8B, 0x08, 0, 0, 0]), Some(Format::Gzip));
    }

    #[test]
    fn detects_xz() {
        // Full magic: FD 37 7A 58 5A 00. Bug-history: the bash draft dropped 0x58.
        assert_eq!(Format::detect(&[0xFD, 0x37, 0x7A, 0x58, 0x5A, 0x00]), Some(Format::Xz));
    }

    #[test]
    fn rejects_xz_missing_0x58() {
        assert_ne!(Format::detect(&[0xFD, 0x37, 0x7A, 0x5A, 0x00, 0x00]), Some(Format::Xz));
    }

    #[test]
    fn detects_bzip2() {
        assert_eq!(Format::detect(b"BZh91AY"), Some(Format::Bzip2));
    }

    #[test]
    fn detects_lz4() {
        assert_eq!(Format::detect(&[0x04, 0x22, 0x4D, 0x18, 0, 0]), Some(Format::Lz4));
    }

    #[test]
    fn detects_lzip() {
        assert_eq!(Format::detect(b"LZIP\x01\x00"), Some(Format::Lzip));
    }

    #[test]
    fn detects_compress() {
        assert_eq!(Format::detect(&[0x1F, 0x9D, 0x90, 0, 0, 0]), Some(Format::Compress));
    }

    #[test]
    fn unknown_returns_none() {
        assert_eq!(Format::detect(b"hello!"), None);
    }

    #[test]
    fn too_short_returns_none() {
        assert_eq!(Format::detect(&[0x28, 0xB5]), None);
    }
}
