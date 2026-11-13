import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "workspace_sync", Path(__file__).resolve().parents[1] / "scripts/workspace-sync.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True,
                                   stderr=subprocess.DEVNULL).strip()


class WorkspaceSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work, self.remote = self.root / "work", self.root / "remote.git"
        git(self.root, "init", "--bare", str(self.remote))
        git(self.root, "init", "-b", "task-0024-test", str(self.work))
        git(self.work, "config", "user.name", "Sync Test")
        git(self.work, "config", "user.email", "sync@example.invalid")
        git(self.work, "config", "commit.gpgsign", "false")
        git(self.work, "remote", "add", "origin", str(self.remote))
        self.commit("one")
        self.repo = MODULE.Repository(self.work)

    def commit(self, value):
        (self.work / "file.txt").write_text(value, encoding="utf-8")
        git(self.work, "add", "file.txt")
        git(self.work, "commit", "-m", value)

    def sync(self, repos=None, push=True):
        with contextlib.redirect_stdout(io.StringIO()):
            return MODULE.synchronize(repos or [self.repo], push)

    def test_push_updates_task_and_snapshot_then_verifies(self):
        self.sync()
        refs = self.repo.remote_refs()
        sha = git(self.work, "rev-parse", "HEAD")
        self.assertEqual(refs["refs/heads/task-0024-test"], sha)
        self.assertEqual(refs["refs/heads/" + MODULE.SNAPSHOT], sha)
        self.assertTrue(self.sync(push=False)[0]["snapshot_synced"])

    def test_dirty_repo_prevents_every_push(self):
        (self.work / "untracked.txt").write_text("unsaved", encoding="utf-8")
        with self.assertRaises(MODULE.SyncError):
            self.sync()
        self.assertEqual(self.repo.remote_refs(), {})

    def test_remote_newer_commit_is_not_overwritten(self):
        self.sync()
        previous = git(self.work, "rev-parse", "HEAD")
        self.commit("two")
        self.sync()
        current = git(self.work, "rev-parse", "HEAD")
        git(self.work, "reset", "--hard", previous)
        with self.assertRaises(MODULE.SyncError):
            self.sync()
        self.assertEqual(self.repo.remote_refs()["refs/heads/" + MODULE.SNAPSHOT], current)

    def test_all_preflight_checks_finish_before_first_push(self):
        class Broken:
            def preflight(self):
                raise MODULE.SyncError("another repo is dirty")
        with self.assertRaises(MODULE.SyncError):
            self.sync([self.repo, Broken()])
        self.assertEqual(self.repo.remote_refs(), {})

    def test_remote_race_rejects_both_refs_atomically(self):
        self.sync()
        previous = git(self.work, "rev-parse", "HEAD")
        self.commit("local-two")
        self.repo.preflight()
        other = self.root / "other"
        git(self.root, "clone", "--branch", MODULE.SNAPSHOT, str(self.remote), str(other))
        git(other, "config", "user.name", "Other Computer")
        git(other, "config", "user.email", "other@example.invalid")
        git(other, "config", "commit.gpgsign", "false")
        (other / "file.txt").write_text("remote-two", encoding="utf-8")
        git(other, "add", "file.txt")
        git(other, "commit", "-m", "remote-two")
        git(other, "push", "origin", "HEAD:refs/heads/" + MODULE.SNAPSHOT)
        with self.assertRaises(MODULE.SyncError):
            self.repo.push()
        refs = self.repo.remote_refs()
        self.assertEqual(refs["refs/heads/task-0024-test"], previous)
        self.assertEqual(refs["refs/heads/" + MODULE.SNAPSHOT], git(other, "rev-parse", "HEAD"))

    def handoff(self, commit):
        directory = self.root / "docs/delivery"
        directory.mkdir(parents=True, exist_ok=True)
        checkpoint = directory / "checkpoint.md"
        checkpoint.write_text("checkpoint", encoding="utf-8")
        (directory / "current-work.json").write_text(json.dumps({
            "checkpoint": "docs/delivery/checkpoint.md",
            "repositories": {self.work.name: {"commit": commit}},
        }), encoding="utf-8")
        return checkpoint

    def test_handoff_must_record_current_component_commit(self):
        sha = git(self.work, "rev-parse", "HEAD")
        self.handoff(sha)
        MODULE.validate_handoff(self.root, [self.repo])
        self.commit("two")
        with self.assertRaises(MODULE.SyncError):
            MODULE.validate_handoff(self.root, [self.repo])

    def test_missing_checkpoint_prevents_sync(self):
        checkpoint = self.handoff(git(self.work, "rev-parse", "HEAD"))
        checkpoint.unlink()
        with self.assertRaises(MODULE.SyncError):
            MODULE.validate_handoff(self.root, [self.repo])


if __name__ == "__main__":
    unittest.main()
