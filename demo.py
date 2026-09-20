#!/usr/bin/env python3
"""OptiGuard - 25% Implementation Live Verification Demo
Run this script directly in the terminal to demonstrate:
1. C-Subset Lexing & Parsing
2. Three-Address Code (TAC) Generation
3. Pass 1: Constant Folding & Propagation
4. Pass 2: Algebraic Simplification
5. Pass 3: Dead Code Elimination
6. Quantitative Improvement Metrics & Cost Evaluation
"""

import sys
from optiguard.pipeline import OptiGuardPipeline

def print_separator(title="", ch="="):
    if title:
        print(f"\n{ch * 25} {title} {ch * 25}")
    else:
        print(ch * 65)

def run_case(pipeline: OptiGuardPipeline, case_number: int, description: str, source_code: str):
    print_separator(f"TEST CASE {case_number}: {description}", "#")
    print("\n[1] INPUT SOURCE CODE:")
    for line in source_code.strip().split('\n'):
        print(f"    {line}")

    result = pipeline.optimize(source_code)

    print("\n[2] GENERATED RAW THREE-ADDRESS CODE (TAC / IR):")
    print(result.initial_tac.dump())
    print(f"    -> Baseline Metrics: {result.initial_metrics}")

    print("\n[3] STEP-BY-STEP OPTIMIZATION PASS EXECUTION:")
    for idx, step in enumerate(result.steps, 1):
        status = "MODIFIED" if step.modified else "NO CHANGE"
        print(f"\n  --- Pass {idx}: {step.pass_name} [{status}] ---")
        print(step.tac_snapshot.dump())
        print(f"      Metrics: {step.metrics_after}")

    print("\n[4] FINAL OPTIMIZED THREE-ADDRESS CODE:")
    print(result.final_tac.dump())

    print("\n[5] QUANTITATIVE EVALUATION REPORT:")
    summary = result.improvement_summary
    print(f"    Raw Instructions Before : {result.initial_metrics.instruction_count}")
    print(f"    Raw Instructions After  : {result.final_metrics.instruction_count}")
    print(f"    Instructions Eliminated : {summary['instructions_saved']}")
    print(f"    Code Size Reduction     : {summary['instruction_reduction_pct']}%")
    print(f"    ALU Cycle Cost Before   : {result.initial_metrics.estimated_cycle_cost} cycles")
    print(f"    ALU Cycle Cost After    : {result.final_metrics.estimated_cycle_cost} cycles")
    print(f"    Cycle Cost Reduction    : {summary['cycle_reduction_pct']}%")

    print_separator()

def main():
    print(r"""
===================================================================
   ___       _   _  ____                     _ 
  / _ \ _ __ | |_(_)/ ___|_   _  __ _ _ __ __| |
 | | | | '_ \| __| | |  _| | | |/ _` | '__/ _` |
 | |_| | |_) | |_| | |_| | |_| | (_| | | | (_| |
  \___/| .__/ \__|_|\____|\__,_|\__,_|_|  \__,_|
       |_|   Adaptive Compiler Pass Optimizer (25% Milestone)
===================================================================
""")
    pipeline = OptiGuardPipeline()

    # Case 1: Canonical 25% Example from Project Specification
    case1_code = """
a = 10 * 2;
b = a + 0;
c = b;
"""
    run_case(pipeline, 1, "Canonical Phase-Ordering Benchmark", case1_code)

    # Case 2: Multi-pass with Dead Code and Multiple Identities
    case2_code = """
x = 10 + 5;
dead_val = 99 * 4;
y = x * 1;
z = y + 0;
final_res = z * 2;
"""
    run_case(pipeline, 2, "Dead Code Elimination & Identity Reduction", case2_code)

    # Case 3: Symbolic Algebraic Simplification (Variables without static constants)
    case3_code = """
temp_a = input_val * 1;
temp_b = temp_a + 0;
res = temp_b;
"""
    run_case(pipeline, 3, "Symbolic Algebraic Simplification (Identity Elimination)", case3_code)

if __name__ == "__main__":
    main()
