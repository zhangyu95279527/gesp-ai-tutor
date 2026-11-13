#!/usr/bin/env python3
"""三仓只快进同步；快照分支用于跨电脑续接，不代表发布。"""

import argparse
import json
import subprocess
from pathlib import Path

SNAPSHOT = "chore-mac-mini-handoff"


class SyncError(RuntimeError):
    pass


class Repository:
    def __init__(self, path, proxy=None):
        self.path = Path(path)
        self.prefix = ["git", "-C", str(self.path)]
        if proxy:
            self.prefix += ["-c", "http.proxy=" + proxy]

    def git(self, *args, allowed=(0,)):
        result = subprocess.run(self.prefix + list(args), text=True,
                                capture_output=True, encoding="utf-8", errors="replace")
        if result.returncode not in allowed:
            raise SyncError(f"{self.path.name}: git {args[0]} failed: {result.stderr.strip()}")
        return result

    def remote_refs(self):
        return {parts[1]: parts[0] for line in self.git("ls-remote", "--heads", "origin").stdout.splitlines()
                if len(parts := line.split()) == 2}

    def preflight(self):
        if self.git("status", "--porcelain").stdout.strip():
            raise SyncError(f"{self.path.name}: 工作区未提交，先保存代码和检查点")
        self.branch = self.git("symbolic-ref", "--short", "HEAD").stdout.strip()
        self.head = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("fetch", "origin")
        remote = self.remote_refs()
        for branch in dict.fromkeys((self.branch, SNAPSHOT)):
            sha = remote.get("refs/heads/" + branch)
            if sha and self.git("merge-base", "--is-ancestor", sha, self.head,
                                allowed=(0, 1)).returncode:
                raise SyncError(f"{self.path.name}: 远端{branch}有本机未包含的提交，停止；先拉取处理，禁止强推")
        return {"repository": self.path.name, "branch": self.branch, "commit": self.head,
                "task_synced": remote.get("refs/heads/" + self.branch) == self.head,
                "snapshot_synced": remote.get("refs/heads/" + SNAPSHOT) == self.head}

    def push(self):
        refs = [f"refs/heads/{self.branch}:refs/heads/{self.branch}"]
        if self.branch != SNAPSHOT:
            refs.append(f"HEAD:refs/heads/{SNAPSHOT}")
        # 单仓两个ref原子更新；远端变化时让Git拒绝，不传force选项。
        self.git("push", "--atomic", "origin", *refs)
        self.git("branch", "--set-upstream-to=origin/" + self.branch, self.branch)
        remote = self.remote_refs()
        for branch in (self.branch, SNAPSHOT):
            if remote.get("refs/heads/" + branch) != self.head:
                raise SyncError(f"{self.path.name}: 推送后远端SHA不一致")
        print(json.dumps({"repository": self.path.name, "branch": self.branch,
                          "commit": self.head, "remote_verified": True}, ensure_ascii=False))


def synchronize(repositories, push=False):
    # 全部仓库通过前置检查才开始推送，避免已知脏树/分叉造成部分推进。
    states = [repo.preflight() for repo in repositories]
    for state in states:
        print(json.dumps(state, ensure_ascii=False))
    if push:
        for repo in repositories:
            repo.push()
    return states


def validate_handoff(delivery, repositories):
    delivery = Path(delivery).resolve()
    try:
        manifest = json.loads((delivery / "docs/delivery/current-work.json").read_text(encoding="utf-8"))
        checkpoint = (delivery / manifest["checkpoint"]).resolve()
        if delivery not in checkpoint.parents or not checkpoint.is_file():
            raise SyncError("最新检查点不存在或超出交付仓")
        for repo in repositories:
            if repo.path.resolve() == delivery:
                continue
            expected = manifest["repositories"][repo.path.name]["commit"]
            if repo.git("rev-parse", "HEAD").stdout.strip() != expected:
                raise SyncError(f"{repo.path.name}: current-work.json未更新到本机组件提交")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SyncError("请先保存current-work.json和最新检查点") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--push", action="store_true", help="推送任务和换机分支并核验；默认仅检查")
    parser.add_argument("--proxy", help="仅本次Git命令的代理，不修改全局配置；Mac通常无需指定")
    args = parser.parse_args()
    delivery = Path(__file__).resolve().parent.parent
    repos = [Repository(delivery.parent / name, args.proxy)
             for name in ("gesp-tutor-api", "gesp-tutor-web", delivery.name)]
    try:
        validate_handoff(delivery, repos)
        synchronize(repos, args.push)
    except (SyncError, OSError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
