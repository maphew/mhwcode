use std::fs;
use std::path::PathBuf;

use assert_cmd::Command;
use tempfile::tempdir;

const PAYLOAD: &[u8] = b"hello cli world\n";

fn zest_bin() -> PathBuf {
    // assert_cmd computes this for us; we use it when we need to make a copy.
    assert_cmd::cargo::cargo_bin("zest")
}

/// Copy the `zest` binary to a peer path named `unzest` (or `unzest.exe` on
/// Windows). Copy rather than symlink so the test works identically on all
/// platforms and exercises the real argv[0] dispatch path.
fn make_unzest_peer(dir: &std::path::Path) -> PathBuf {
    let src = zest_bin();
    let name = if cfg!(windows) { "unzest.exe" } else { "unzest" };
    let dst = dir.join(name);
    fs::copy(&src, &dst).unwrap();
    dst
}

#[test]
fn compress_and_decompress_via_argv0() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("payload.txt");
    fs::write(&src, PAYLOAD).unwrap();

    Command::cargo_bin("zest")
        .unwrap()
        .arg(&src)
        .assert()
        .success();

    let compressed = dir.path().join("payload.txt.zst");
    assert!(compressed.exists());
    assert!(!src.exists());

    let unzest = make_unzest_peer(dir.path());
    Command::new(&unzest).arg(&compressed).assert().success();

    assert!(!compressed.exists());
    assert_eq!(fs::read(&src).unwrap(), PAYLOAD);
}

#[test]
fn format_flag_selects_gzip() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    Command::cargo_bin("zest")
        .unwrap()
        .args(["-f", "gz"])
        .arg(&src)
        .assert()
        .success();

    let out = dir.path().join("a.txt.gz");
    assert!(out.exists(), "expected .gz output");
    // magic byte check
    let bytes = fs::read(&out).unwrap();
    assert_eq!(&bytes[..2], &[0x1F, 0x8B]);
}

#[test]
fn unknown_format_errors() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    Command::cargo_bin("zest")
        .unwrap()
        .args(["-f", "zip"])
        .arg(&src)
        .assert()
        .failure();
    assert!(src.exists(), "source must not be touched on arg error");
}

#[test]
fn no_inputs_errors() {
    Command::cargo_bin("zest").unwrap().assert().failure();
}

#[test]
fn help_flag_succeeds() {
    Command::cargo_bin("zest")
        .unwrap()
        .arg("--help")
        .assert()
        .success();
}

#[test]
fn per_file_error_does_not_abort_batch() {
    let dir = tempdir().unwrap();
    let good = dir.path().join("good.txt");
    let bad = dir.path().join("does-not-exist.txt");
    fs::write(&good, PAYLOAD).unwrap();

    Command::cargo_bin("zest")
        .unwrap()
        .arg(&bad)
        .arg(&good)
        .assert()
        .failure();

    // good still got compressed despite bad's failure
    assert!(dir.path().join("good.txt.zst").exists());
}
