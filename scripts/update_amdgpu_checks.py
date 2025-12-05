#!/usr/bin/env python3

"""Utility to refresh FileCheck annotations for the failing AMDGPU tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LLC_BIN = REPO_ROOT / "build_dbg" / "bin" / "llc"
UPDATE_LLC = REPO_ROOT / "llvm" / "utils" / "update_llc_test_checks.py"
UPDATE_MIR = REPO_ROOT / "llvm" / "utils" / "update_mir_test_checks.py"
TEST_ROOT = REPO_ROOT / "llvm" / "test" / "CodeGen" / "AMDGPU"

# Tests that crash llc at -O0 due to missing i128 lowering; skip for now.
SKIP_TESTS = {
    "div_i128.ll",
    "rem_i128.ll",
}

LLC_TESTS = [
    "atomicrmw-expand.ll",
    "cf-loop-on-constant.ll",
    "collapse-endcf.ll",
    # "div_i128.ll",  # skipped: i128 lowering issue
    "indirect-addressing-si.ll",
    "insert-delay-alu-bug.ll",
    "kernel-vgpr-spill-mubuf-with-voffset.ll",
    "llvm.amdgcn.update.dpp.ll",
    "load-global-invariant.ll",
    "memory-legalizer-flat-agent.ll",
    "memory-legalizer-flat-cluster.ll",
    "memory-legalizer-flat-lastuse.ll",
    "memory-legalizer-flat-nontemporal.ll",
    "memory-legalizer-flat-singlethread.ll",
    "memory-legalizer-flat-system.ll",
    "memory-legalizer-flat-volatile.ll",
    "memory-legalizer-flat-wavefront.ll",
    "memory-legalizer-flat-workgroup.ll",
    "memory-legalizer-global-agent.ll",
    "memory-legalizer-global-cluster.ll",
    "memory-legalizer-global-lastuse.ll",
    "memory-legalizer-global-nontemporal.ll",
    "memory-legalizer-global-singlethread.ll",
    "memory-legalizer-global-system.ll",
    "memory-legalizer-global-volatile.ll",
    "memory-legalizer-global-wavefront.ll",
    "memory-legalizer-global-workgroup.ll",
    "memory-legalizer-local-agent.ll",
    "memory-legalizer-local-cluster.ll",
    "memory-legalizer-local-nontemporal.ll",
    "memory-legalizer-local-singlethread.ll",
    "memory-legalizer-local-system.ll",
    "memory-legalizer-local-volatile.ll",
    "memory-legalizer-local-wavefront.ll",
    "memory-legalizer-local-workgroup.ll",
    "memory-legalizer-private-agent.ll",
    "memory-legalizer-private-cluster.ll",
    "memory-legalizer-private-lastuse.ll",
    "memory-legalizer-private-nontemporal.ll",
    "memory-legalizer-private-singlethread.ll",
    "memory-legalizer-private-system.ll",
    "memory-legalizer-private-volatile.ll",
    "memory-legalizer-private-wavefront.ll",
    "memory-legalizer-private-workgroup.ll",
    "partial-sgpr-to-vgpr-spills.ll",
    # "rem_i128.ll",  # skipped: i128 lowering issue
    "rewrite-vgpr-mfma-to-agpr.ll",
    "select-phi-s16-fp.ll",
    "sgpr-spill-no-vgprs.ll",
    "sgpr-spills-split-regalloc.ll",
    "smfmac_alloc_failure_no_agpr_O0.ll",
    "spill-vgpr-to-agpr-update-regscavenger.ll",
    "stacksave_stackrestore.ll",
    "trap-abis.ll",
    "vgpr-spill-placement-issue61083.ll",
    "vgpr_constant_to_sgpr.ll",
    "wwm-reserved-spill.ll",
    "wwm-reserved.ll",
]

MIR_TESTS = [
    "bb-prolog-spill-during-regalloc.ll",
    "dagcombine-lshr-and-cmp.ll",
    "indirect-addressing-term.ll",
    "llvm.amdgcn.ds.gws.barrier-fastregalloc.ll",
]


def run(cmd: list[str]) -> None:
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    if not LLC_BIN.exists():
        raise SystemExit(f"Missing llc binary at {LLC_BIN}")

    for rel in LLC_TESTS:
        path = TEST_ROOT / rel
        run([sys.executable, str(UPDATE_LLC), "--llc-binary", str(LLC_BIN), str(path)])

    for rel in MIR_TESTS:
        path = TEST_ROOT / rel
        run([sys.executable, str(UPDATE_MIR), "--llc-binary", str(LLC_BIN), str(path)])


if __name__ == "__main__":
    main()

