use std::fs;
use std::path::PathBuf;

use assert_cmd::Command;
use tempfile::tempdir;

const PAYLOAD: &[u8] = b"hello cli world\nhello cli world\nhello cli world\n";

fn zist_bin() -> PathBuf {
    assert_cmd::cargo::cargo_bin("zist")
}

/// Copy the binary to a peer path named `unzist` so we exercise the real
/// argv[0] dispatch on every OS (including Windows, where symlinks need perms).
fn make_unzist_peer(dir: &std::path::Path) -> PathBuf {
    let src = zist_bin();
    let name = if cfg!(windows) { "unzist.exe" } else { "unzist" };
    let dst = dir.join(name);
    fs::copy(&src, &dst).unwrap();
    dst
}

// ---- baseline round-trip ----

#[test]
fn compress_and_decompress_via_argv0() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("payload.txt");
    fs::write(&src, PAYLOAD).unwrap();

    Command::cargo_bin("zist").unwrap().arg(&src).assert().success();

    let compressed = dir.path().join("payload.txt.zst");
    assert!(compressed.exists());
    assert!(!src.exists());

    let unzist = make_unzist_peer(dir.path());
    Command::new(&unzist).arg(&compressed).assert().success();

    assert!(!compressed.exists());
    assert_eq!(fs::read(&src).unwrap(), PAYLOAD);
}

#[test]
fn format_long_flag_selects_gzip() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    Command::cargo_bin("zist")
        .unwrap()
        .args(["--format", "gz"])
        .arg(&src)
        .assert()
        .success();

    let out = dir.path().join("a.txt.gz");
    assert!(out.exists());
    assert_eq!(&fs::read(&out).unwrap()[..2], &[0x1F, 0x8B]);
}

#[test]
fn unknown_format_errors() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    Command::cargo_bin("zist")
        .unwrap()
        .args(["--format", "zip"])
        .arg(&src)
        .assert()
        .failure();
    assert!(src.exists());
}

#[test]
fn no_inputs_errors() {
    Command::cargo_bin("zist").unwrap().assert().failure();
}

#[test]
fn help_flag_succeeds() {
    Command::cargo_bin("zist").unwrap().arg("--help").assert().success();
}

#[test]
fn per_file_error_does_not_abort_batch() {
    let dir = tempdir().unwrap();
    let good = dir.path().join("good.txt");
    let bad = dir.path().join("does-not-exist.txt");
    fs::write(&good, PAYLOAD).unwrap();

    Command::cargo_bin("zist").unwrap().arg(&bad).arg(&good).assert().failure();
    assert!(dir.path().join("good.txt.zst").exists());
}

// ---- gzip-parity flags ----

#[test]
fn keep_flag_preserves_source() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    Command::cargo_bin("zist").unwrap().arg("-k").arg(&src).assert().success();
    assert!(src.exists(), "-k should keep the source");
    assert!(dir.path().join("a.txt.zst").exists());
}

#[test]
fn keep_long_flag_preserves_source() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    Command::cargo_bin("zist").unwrap().arg("--keep").arg(&src).assert().success();
    assert!(src.exists());
}

#[test]
fn stdout_flag_writes_to_stdout_and_keeps_source() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    let out = Command::cargo_bin("zist")
        .unwrap()
        .arg("-c")
        .arg(&src)
        .assert()
        .success()
        .get_output()
        .stdout
        .clone();
    assert_eq!(&out[..4], &[0x28, 0xB5, 0x2F, 0xFD], "stdout must be zstd bytes");
    assert!(src.exists(), "-c implies --keep");
    assert!(!dir.path().join("a.txt.zst").exists(), "-c must not write to disk");
}

#[test]
fn force_flag_overwrites_existing_output() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();
    fs::write(dir.path().join("a.txt.zst"), b"stale").unwrap();

    Command::cargo_bin("zist").unwrap().arg("-f").arg(&src).assert().success();
    let new_bytes = fs::read(dir.path().join("a.txt.zst")).unwrap();
    assert_ne!(new_bytes, b"stale");
    assert_eq!(&new_bytes[..4], &[0x28, 0xB5, 0x2F, 0xFD]);
}

#[test]
fn without_force_refuses_to_clobber() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();
    fs::write(dir.path().join("a.txt.zst"), b"stale").unwrap();

    Command::cargo_bin("zist").unwrap().arg(&src).assert().failure();
    assert_eq!(fs::read(dir.path().join("a.txt.zst")).unwrap(), b"stale");
    assert!(src.exists());
}

#[test]
fn test_flag_passes_valid_archive() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();
    Command::cargo_bin("zist").unwrap().arg(&src).assert().success();
    let compressed = dir.path().join("a.txt.zst");

    let unzist = make_unzist_peer(dir.path());
    Command::new(&unzist).arg("-t").arg(&compressed).assert().success();
    assert!(compressed.exists(), "-t must not remove the file");
}

#[test]
fn test_flag_fails_on_corrupted_archive() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();
    Command::cargo_bin("zist")
        .unwrap()
        .args(["--format", "gz"])
        .arg(&src)
        .assert()
        .success();
    let compressed = dir.path().join("a.txt.gz");
    // corrupt a byte past the header
    let mut bytes = fs::read(&compressed).unwrap();
    let i = 12.min(bytes.len() - 1);
    bytes[i] ^= 0xFF;
    fs::write(&compressed, &bytes).unwrap();

    let unzist = make_unzist_peer(dir.path());
    Command::new(&unzist).arg("-t").arg(&compressed).assert().failure();
}

#[test]
fn quiet_flag_suppresses_stdout() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    let out = Command::cargo_bin("zist")
        .unwrap()
        .arg("-q")
        .arg(&src)
        .assert()
        .success()
        .get_output()
        .stdout
        .clone();
    assert!(out.is_empty(), "-q must emit no stdout, got: {out:?}");
}

#[test]
fn verbose_flag_emits_summary() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    let assert = Command::cargo_bin("zist")
        .unwrap()
        .arg("-v")
        .arg(&src)
        .assert()
        .success();
    let stderr = String::from_utf8(assert.get_output().stderr.clone()).unwrap();
    assert!(
        stderr.contains("a.txt") && stderr.contains("zst"),
        "expected verbose summary on stderr, got: {stderr:?}"
    );
}

#[test]
fn level_shortcut_digit() {
    let dir = tempdir().unwrap();
    let a = dir.path().join("a.txt");
    let b = dir.path().join("b.txt");
    // 4 KiB of repeating text so level actually matters.
    let payload: Vec<u8> = b"the rain in spain\n".repeat(256);
    fs::write(&a, &payload).unwrap();
    fs::write(&b, &payload).unwrap();

    Command::cargo_bin("zist").unwrap().arg("-1").arg(&a).assert().success();
    Command::cargo_bin("zist").unwrap().arg("-9").arg(&b).assert().success();

    // Both should produce valid zstd, and -9 should not be larger than -1 on
    // repetitive data. (We don't assert strictly smaller because zstd minimums
    // can tie on tiny inputs.)
    let sz1 = fs::metadata(dir.path().join("a.txt.zst")).unwrap().len();
    let sz9 = fs::metadata(dir.path().join("b.txt.zst")).unwrap().len();
    assert!(sz9 <= sz1, "level-9 ({sz9}) should be <= level-1 ({sz1})");
}

#[test]
fn decompress_override_on_zist() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();
    Command::cargo_bin("zist")
        .unwrap()
        .args(["--format", "gz"])
        .arg(&src)
        .assert()
        .success();
    let compressed = dir.path().join("a.txt.gz");

    // `zist -d` should behave like unzist.
    Command::cargo_bin("zist").unwrap().arg("-d").arg(&compressed).assert().success();
    assert!(!compressed.exists());
    assert_eq!(fs::read(&src).unwrap(), PAYLOAD);
}

#[test]
fn compress_override_on_unzist() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    let unzist = make_unzist_peer(dir.path());
    // `unzist -z` should behave like zist.
    Command::new(&unzist).arg("-z").arg(&src).assert().success();
    assert!(dir.path().join("a.txt.zst").exists());
}

#[test]
fn bundled_short_flags() {
    let dir = tempdir().unwrap();
    let src = dir.path().join("a.txt");
    fs::write(&src, PAYLOAD).unwrap();

    // -kv = --keep --verbose
    let assert = Command::cargo_bin("zist")
        .unwrap()
        .arg("-kv")
        .arg(&src)
        .assert()
        .success();
    assert!(src.exists(), "-kv should preserve source");
    let stderr = String::from_utf8(assert.get_output().stderr.clone()).unwrap();
    assert!(stderr.contains("a.txt"), "verbose should have emitted a summary");
}

#[test]
fn recursive_flag_compresses_tree() {
    let dir = tempdir().unwrap();
    let sub = dir.path().join("sub");
    fs::create_dir(&sub).unwrap();
    fs::write(sub.join("x.txt"), PAYLOAD).unwrap();
    fs::write(sub.join("y.txt"), PAYLOAD).unwrap();
    fs::create_dir(sub.join("inner")).unwrap();
    fs::write(sub.join("inner").join("z.txt"), PAYLOAD).unwrap();

    Command::cargo_bin("zist").unwrap().arg("-r").arg(&sub).assert().success();
    assert!(sub.join("x.txt.zst").exists());
    assert!(sub.join("y.txt.zst").exists());
    assert!(sub.join("inner").join("z.txt.zst").exists());
    assert!(!sub.join("x.txt").exists());
}
