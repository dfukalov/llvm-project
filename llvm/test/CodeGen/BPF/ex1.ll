; RUN: llc < %s -mtriple=bpfel -mcpu=v1 | FileCheck %s

%struct.bpf_context = type { i64, i64, i64, i64, i64, i64, i64 }
%struct.sk_buff = type { i64, i64, i64, i64, i64, i64, i64 }
%struct.net_device = type { i64, i64, i64, i64, i64, i64, i64 }

@bpf_prog1.devname = private unnamed_addr constant [3 x i8] c"lo\00", align 1
@bpf_prog1.fmt = private unnamed_addr constant [15 x i8] c"skb %x dev %x\0A\00", align 1

; Function Attrs: nounwind uwtable
define i32 @bpf_prog1(ptr nocapture %ctx) #0 section "events/net/netif_receive_skb" {
  %devname = alloca [3 x i8], align 1
  %fmt = alloca [15 x i8], align 1
  %1 = getelementptr inbounds [3 x i8], ptr %devname, i64 0, i64 0
  call void @llvm.memcpy.p0.p0.i64(ptr %1, ptr @bpf_prog1.devname, i64 3, i1 false)
  %2 = getelementptr inbounds %struct.bpf_context, ptr %ctx, i64 0, i32 0
  %3 = load i64, ptr %2, align 8
  %4 = inttoptr i64 %3 to ptr
  %5 = getelementptr inbounds %struct.sk_buff, ptr %4, i64 0, i32 2
  %6 = bitcast ptr %5 to ptr
  %7 = call ptr inttoptr (i64 4 to ptr)(ptr %6) #1
  %8 = call i32 inttoptr (i64 9 to ptr)(ptr %7, ptr %1, i32 2) #1
  %9 = icmp eq i32 %8, 0
  br i1 %9, label %10, label %13

; <label>:10                                      ; preds = %0
  %11 = getelementptr inbounds [15 x i8], ptr %fmt, i64 0, i64 0
  call void @llvm.memcpy.p0.p0.i64(ptr %11, ptr @bpf_prog1.fmt, i64 15, i1 false)
  %12 = call i32 (ptr, i32, ...) inttoptr (i64 11 to ptr)(ptr %11, i32 15, ptr %4, ptr %7) #1
; CHECK-LABEL: bpf_prog1:
; CHECK: call 4
; CHECK: call 9
; CHECK: if r0 != 0
; CHECK: r1 = 622884453
; CHECK: *(u32 *)(r10 - 16) = r1
; CHECK: r1 = 7214898703899978611 ll
; CHECK: *(u64 *)(r10 - 24) = r1
; CHECK: call 11
; CHECK: r0 = 0
; CHECK: exit
  br label %13

; <label>:13                                      ; preds = %10, %0
  ret i32 0
}

; Function Attrs: nounwind
declare void @llvm.memcpy.p0.p0.i64(ptr nocapture, ptr nocapture, i64, i1) #1
