# OptiGuard: An Adaptive Compiler Optimization Framework with Degradation Detection and Safe Rollback

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/badge/Tests-6%2F6%20Passed-brightgreen.svg)]()

> **OptiGuard** is an intermediate representation (IR) level compiler optimization framework that addresses the **Phase-Ordering Problem** and prevents **Optimization Degradation**. Rather than executing a rigid, unverified sequence of passes, OptiGuard evaluates transformations using an analytical multi-objective cost function and provides **transactional state rollback** to guarantee monotonically non-degrading code generation.

---

## Key Highlights

- **Phase-Ordering Aware:** Compiler passes are non-commutative ($Pass_A \circ Pass_B \neq Pass_B \circ Pass_A$). OptiGuard tracks IR state changes per pass.
- **Optimization Degradation Detection:** Detects when a pass inadvertently inflates code size or triggers hardware register spills.
- **Transactional State Rollback:** Snapshots IR state before pass execution; if degradation occurs ($\Delta J(IR) \ge 0$), the IR is atomically reverted to the prior stable state.
- **Pure Zero-Dependency Architecture:** Clean, modular implementation in Python 3 for educational and systems research.

---

## System Architecture

```
                  ┌──────────────────────────────┐
                  │    Source Code (C-Subset)    │
                  └──────────────┬───────────────┘
                                 │ Lexer & Parser
                                 ▼
                  ┌──────────────────────────────┐
                  │  Three-Address Code (TAC/IR) │
                  └──────────────┬───────────────┘
                                 │
                   ┌─────────────▼───────────────┐
             ┌────►│    IR Feature Extractor     │◄─────────────┐
             │     └─────────────┬───────────────┘              │
             │                   │ Feature Vector               │
             │     ┌─────────────▼───────────────┐              │
             │     │   Adaptive Pass Selector    │              │
             │     └─────────────┬───────────────┘              │
             │                   │ Select Pass P_k              │
             │     ┌─────────────▼───────────────┐              │
             │     │  Checkpoint IR to Snapshot  │              │
             │     └─────────────┬───────────────┘              │
             │                   │ Apply Optimization Pass      │
             │     ┌─────────────▼───────────────┐              │
             │     │    Transformed Candidate    │              │
             │     └─────────────┬───────────────┘              │
             │                   │ Compute J(IR_new)            │
             │     ┌─────────────▼───────────────┐              │
             │     │  Degradation Detector Unit  │              │
             │     └───────┬──────────────┬──────┘              │
      Pass Accepted        │              │  Degradation Found  │
     (J_new < J_prev)      │              │  (J_new >= J_prev)  │
             │             ▼              ▼                     │
             │        [ Commit IR ]  [ ROLLBACK ] ──────────────┘
             │             │              │ Restore Snapshot &
             └─────────────┤              │ Add P_k to Tabu List
                           ▼              ▼
                   ┌──────────────────────────────┐
                   │ Convergence & Budget Check   │
                   └──────────────┬───────────────┘
                                  │ Done
                                  ▼
                   ┌──────────────────────────────┐
                   │     Optimized TAC Output     │
                   └──────────────────────────────┘
```

---

## Current Status 

The **25% prototype** is fully operational and includes:
1. **Frontend:** Lexer and Recursive Descent Parser supporting arithmetic expressions, assignments, and operator precedence.
2. **Intermediate Representation:** Three-Address Code (TAC) quadruple generation with atomic state snapshotting (`clone()`).
3. **Three Active Optimization Passes:**
   - **Constant Folding & Propagation:** Folds compile-time arithmetic ($10 \times 2 \to 20$) and propagates constants.
   - **Algebraic Simplification:** Simplifies algebraic identities ($x + 0 \to x$, $x \times 1 \to x$, $x \times 0 \to 0$, $x/1 \to x$).
   - **Dead-Code Elimination (DCE):** Backward liveness analysis pruning dead temporaries and superseded assignments.
4. **Metrics & Cost Evaluator:** Quantifies instruction count reduction, distinct variable count, and ALU cycle costs (weights: Add/Sub = 1, Mul = 3, Div = 8).

---

## Quick Start & Demo

### 1. Run the Interactive Verification Demo
```bash
python3 demo.py
```

### Sample Output:
```
######################### TEST CASE 1: Canonical Phase-Ordering Benchmark #########################

[1] INPUT SOURCE CODE:
    a = 10 * 2;
    b = a + 0;
    c = b;

[2] GENERATED RAW THREE-ADDRESS CODE (TAC / IR):
  0:  t0 = 10 * 2
  1:  a = t0
  2:  t1 = a + 0
  3:  b = t1
  4:  c = b
    -> Baseline Metrics: Instructions: 5 | Variables: 5 (Temps: 2) | Est. Cycles: 7

[3] STEP-BY-STEP OPTIMIZATION PASS EXECUTION:
  --- Pass 1: ConstantFolding [MODIFIED] ---
  --- Pass 2: AlgebraicSimplification [NO CHANGE] ---
  --- Pass 3: DeadCodeElimination [MODIFIED] ---

[4] FINAL OPTIMIZED THREE-ADDRESS CODE:
  0:  a = 20
  1:  b = 20
  2:  c = 20

[5] QUANTITATIVE EVALUATION REPORT:
    Raw Instructions Before : 5
    Raw Instructions After  : 3
    Instructions Eliminated : 2
    Code Size Reduction     : 40.0%
    ALU Cycle Cost Reduction: 57.14%
```

### 2. Run Automated Unit Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## Project Structure

```
optiguard/
├── optiguard/
│   ├── __init__.py
│   ├── frontend/
│   │   ├── __init__.py
│   │   ├── lexer.py             # Tokenizer for C-like syntax
│   │   ├── parser.py            # Recursive descent AST parser
│   │   └── ast_nodes.py         # Abstract syntax tree node definitions
│   ├── ir/
│   │   ├── __init__.py
│   │   ├── tac.py               # Three-Address Code and snapshot cloning
│   │   └── ir_generator.py      # Lowers AST to TAC
│   ├── passes/
│   │   ├── __init__.py
│   │   ├── constant_folding.py  # Constant folding & propagation
│   │   ├── algebraic_simplification.py # Arithmetic identity elimination
│   │   └── dead_code_elimination.py    # Backward liveness analysis
│   ├── metrics/
│   │   ├── __init__.py
│   │   └── cost_evaluator.py    # Analytical cost model J(IR)
│   └── pipeline.py              # Optimization orchestrator
├── docs/
│   └── REVIEW_1_PRESENTATION.md # Slide deck, script & Q&A defense
├── tests/
│   ├── __init__.py
│   └── test_optiguard.py        # 6 unit tests
├── demo.py                      # Interactive CLI demonstration
├── README.md
└── LICENSE
```

---

## Roadmap & Milestone Schedule

| Milestone | Target Date | Key Deliverables |
| :--- | :--- | :--- |
| **Review 1** | Sep 24–25, 2026  | Problem Formulation, Literature Survey, Novelty, Q&A Defense |
| **25% Prototype** | 1st Wk Oct 2026  | Lexer, Parser, AST, TAC IR, 3 Passes, Cost Evaluator, CLI Demo |
| **Review 2 (75%)** | 3rd Wk Oct 2026  | Feature Profiler, Degradation Detector, Stack Rollback, Progress Report |
| **Final Demo (100%)** | 4th Wk Oct 2026  | Adaptive Search Engine, Full Benchmarks, IEEE Paper / Patent Draft |

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
