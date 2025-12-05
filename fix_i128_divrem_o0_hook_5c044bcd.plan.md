---
name: Fix i128 DivRem O0 Hook
overview: Add a TargetLowering hook that allows targets like AMDGPU to request IR-level expansion of power-of-2 divisions, fixing the i128 div/rem crash at -O0 when DAG combines are disabled.
todos:
  - id: add-hook-header
    content: Add shouldExpandPowerOf2DivRem to TargetLowering.h
    status: completed
  - id: modify-expand-pass
    content: Query hook in ExpandLargeDivRem.cpp
    status: completed
  - id: amdgpu-override
    content: Implement override in AMDGPUISelLowering
    status: completed
  - id: verify-tests
    content: Verify div_i128.ll and rem_i128.ll pass
    status: in_progress
---

# Fix i128 Div/Rem at -O0 via TargetLowering Hook

## Problem

`ExpandLargeDivRem` skips power-of-2 divisions expecting DAG combiner to convert them to shifts. With DAG combines disabled at -O0 for AMDGPU, this causes `LLVM ERROR: unsupported library call operation`.

## Solution

Add a TargetLowering hook that targets can override to request expansion of power-of-2 divisions.

## Files to Modify

### 1. Add Hook to TargetLowering

[`llvm/include/llvm/CodeGen/TargetLowering.h`](llvm/include/llvm/CodeGen/TargetLowering.h)

Add virtual method:
```cpp
/// Return true if the target wants ExpandLargeDivRem to expand div/rem
/// by power-of-2 constants, rather than leaving them for DAG combines.
/// Default is false (current behavior - skip power-of-2 cases).
virtual bool shouldExpandPowerOf2DivRem(EVT VT) const { return false; }
```

### 2. Query Hook in ExpandLargeDivRem

[`llvm/lib/CodeGen/ExpandLargeDivRem.cpp`](llvm/lib/CodeGen/ExpandLargeDivRem.cpp)

Modify the power-of-2 skip logic (around line 105-108):
```cpp
// The backend has peephole optimizations for powers of two,
// unless the target explicitly requests expansion.
Type *Ty = I.getType()->getScalarType();
if (isConstantPowerOfTwo(I.getOperand(1), isSigned(I.getOpcode())) &&
    !TLI.shouldExpandPowerOf2DivRem(TLI.getValueType(DL, Ty)))
  continue;
```

### 3. Override in AMDGPU

[`llvm/lib/Target/AMDGPU/AMDGPUISelLowering.h`](llvm/lib/Target/AMDGPU/AMDGPUISelLowering.h)

Declare override:
```cpp
bool shouldExpandPowerOf2DivRem(EVT VT) const override;
```

[`llvm/lib/Target/AMDGPU/AMDGPUISelLowering.cpp`](llvm/lib/Target/AMDGPU/AMDGPUISelLowering.cpp)

Implement:
```cpp
bool AMDGPUTargetLowering::shouldExpandPowerOf2DivRem(EVT VT) const {
  // At -O0 we disable DAG combines, so power-of-2 div/rem won't be
  // converted to shifts. Request IR expansion for large types.
  return getTargetMachine().getOptLevel() == CodeGenOptLevel::None &&
         VT.getScalarSizeInBits() > 64;
}
```

### 4. Verify Tests Pass

- `llvm/test/CodeGen/AMDGPU/div_i128.ll` - should now work at -O0
- `llvm/test/CodeGen/AMDGPU/rem_i128.ll` - should now work at -O0

## Testing

1. Rebuild `llc` with changes
2. Run `llvm-lit llvm/test/CodeGen/AMDGPU/div_i128.ll llvm/test/CodeGen/AMDGPU/rem_i128.ll`
3. Run full AMDGPU test suite to ensure no regressions