# AGENTS.md

## Cursor Cloud specific instructions

This is the **LLVM monorepo** (llvm-project, version 23.0.0-git). It is a C/C++ compiler infrastructure built with CMake/Ninja.

### Build system overview

| Component | Detail |
|---|---|
| Build system | CMake ≥ 3.20 + Ninja |
| Bootstrap compiler | GCC 13 (`/usr/bin/gcc`, `/usr/bin/g++`) |
| Test runner | `lit` (LLVM Integrated Tester), invoked via `build/bin/llvm-lit` or `ninja check-*` targets |
| Primary subprojects | LLVM core + Clang (configured via `-DLLVM_ENABLE_PROJECTS="clang"`) |

### CMake configuration

The build directory is `build/` at the workspace root. It is configured with:

```
cmake -S llvm -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_ENABLE_ASSERTIONS=ON \
  -DLLVM_ENABLE_PROJECTS="clang" \
  -DLLVM_TARGETS_TO_BUILD="X86" \
  -DLLVM_PARALLEL_LINK_JOBS=4 \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DCMAKE_C_COMPILER=/usr/bin/gcc \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
  -DLLVM_FORCE_VC_REPOSITORY="https://github.com/dfukalov/llvm-project"
```

### Key gotchas

- **Embedded password in git remote**: The Cloud Agent environment uses a git remote URL with an embedded token. LLVM's `VCSRevision.h` generation rejects this. You **must** pass `-DLLVM_FORCE_VC_REPOSITORY="https://github.com/dfukalov/llvm-project"` during CMake configuration, or the build will fail.
- **Default `c++` is Clang 18**: The system `c++` symlink points to Clang 18, which cannot find `<iostream>` in this environment. Use GCC explicitly: `-DCMAKE_C_COMPILER=/usr/bin/gcc -DCMAKE_CXX_COMPILER=/usr/bin/g++`.
- **X86-only target**: To keep build times reasonable (~25 min on 8 cores), build only the X86 target via `-DLLVM_TARGETS_TO_BUILD="X86"`. Building all targets is much slower.

### Common commands

| Task | Command |
|---|---|
| Incremental build | `ninja -C build` |
| Run LLVM tests | `ninja -C build check-llvm` |
| Run Clang tests | `ninja -C build check-clang` |
| Run all tests | `ninja -C build check-all` |
| Format check | `build/bin/clang-format --dry-run -Werror <file>` |
| Compile with built Clang | `build/bin/clang -O2 file.c -o output` |
| Generate LLVM IR | `build/bin/clang -S -emit-llvm file.c -o file.ll` |
| Optimize IR | `build/bin/opt -O3 file.ll -S -o file_opt.ll` |

### Adding subprojects

To add more subprojects (e.g., LLD, LLDB, MLIR), reconfigure with:
```
cmake -S llvm -B build -DLLVM_ENABLE_PROJECTS="clang;lld;mlir" <other flags>
```
Then rebuild with `ninja -C build`.
