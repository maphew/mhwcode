use std::path::{Path, PathBuf};

use crate::format::Format;

/// Where to write the compressed output given a source path and target format.
/// Always appends `.<suffix>` to the full source name (like gzip).
pub fn compressed_path(src: &Path, fmt: Format) -> PathBuf {
    let mut s = src.as_os_str().to_os_string();
    s.push(".");
    s.push(fmt.suffix());
    PathBuf::from(s)
}

/// Where to write the decompressed output. If the source ends with a known
/// compression suffix, strip it; otherwise append `.out` (bash-draft behaviour
/// for misleading-or-missing-extension inputs).
pub fn decompressed_path(src: &Path) -> PathBuf {
    if let Some(name) = src.file_name().and_then(|s| s.to_str()) {
        for suf in Format::known_suffixes() {
            let dotted = format!(".{suf}");
            if name.len() > dotted.len() && name.ends_with(&dotted) {
                let stripped = &name[..name.len() - dotted.len()];
                return src.with_file_name(stripped);
            }
        }
    }
    let mut s = src.as_os_str().to_os_string();
    s.push(".out");
    PathBuf::from(s)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn compress_appends_zst() {
        assert_eq!(
            compressed_path(Path::new("notes.txt"), Format::Zstd),
            PathBuf::from("notes.txt.zst"),
        );
    }

    #[test]
    fn compress_preserves_directory() {
        assert_eq!(
            compressed_path(Path::new("/tmp/sub/notes.txt"), Format::Gzip),
            PathBuf::from("/tmp/sub/notes.txt.gz"),
        );
    }

    #[test]
    fn decompress_strips_zst() {
        assert_eq!(decompressed_path(Path::new("notes.txt.zst")), PathBuf::from("notes.txt"));
    }

    #[test]
    fn decompress_strips_zstd() {
        assert_eq!(decompressed_path(Path::new("notes.txt.zstd")), PathBuf::from("notes.txt"));
    }

    #[test]
    fn decompress_strips_gz() {
        assert_eq!(decompressed_path(Path::new("a.log.gz")), PathBuf::from("a.log"));
    }

    #[test]
    #[allow(non_snake_case)]
    fn decompress_strips_xz_bz2_lz4_Z() {
        assert_eq!(decompressed_path(Path::new("x.xz")), PathBuf::from("x"));
        assert_eq!(decompressed_path(Path::new("y.bz2")), PathBuf::from("y"));
        assert_eq!(decompressed_path(Path::new("z.lz4")), PathBuf::from("z"));
        assert_eq!(decompressed_path(Path::new("w.Z")), PathBuf::from("w"));
    }

    #[test]
    fn decompress_appends_out_when_no_known_suffix() {
        assert_eq!(decompressed_path(Path::new("blob")), PathBuf::from("blob.out"));
    }

    #[test]
    fn decompress_appends_out_when_suffix_unknown() {
        assert_eq!(decompressed_path(Path::new("blob.bin")), PathBuf::from("blob.bin.out"));
    }

    #[test]
    fn decompress_preserves_directory() {
        assert_eq!(
            decompressed_path(Path::new("/tmp/a/b.tar.zst")),
            PathBuf::from("/tmp/a/b.tar"),
        );
    }
}
