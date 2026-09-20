# OptiGuard: Project Review 1 Presentation Package

> **Course:** Compiler Design Lab  
> **Milestone:** Assessment 8 — Project Review 1 (10 Marks)  
> **Date:** September 24–25, 2026  
> **Project Title:** OptiGuard: An Adaptive Compiler Optimization Framework with Degradation Detection and Safe Rollback  

---

## Part 1: Slide-by-Slide Presentation Content

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                                 SLIDE DECK OUTLINE                                ║
║  Slide 1: Title & Team Introduction                                               ║
║  Slide 2: Problem Identification (Phase-Ordering & Optimization Degradation)     ║
║  Slide 3: Literature Survey & Research Gap                                        ║
║  Slide 4: Project Objectives & Expected Outcomes                                  ║
║  Slide 5: Proposed Architecture & Transactional Rollback Flow                     ║
║  Slide 6: 25% Implementation Milestone (Lexer, Parser, TAC IR, 3 Passes)         ║
║  Slide 7: Roadmap to 75% and 100% (Adaptive Engine & Publication/Patent)          ║
║  Slide 8: Summary & Research Contribution                                         ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

---

### Slide 1: Title & Team Introduction
* **Slide Title:** OptiGuard: An Adaptive Compiler Optimization Framework with Degradation Detection and Safe Rollback
* **Subtitle:** An Intermediate-Representation (IR) Level Transactional Optimizer
* **Presented by:** Team Members (Names & Register Numbers)
* **Supervisor / Guide:** Department of Computer Science & Engineering
* **Key Visual / Teaser:**
  > *"Moving from blind, sequential optimization pipelines to verifiable, degradation-aware adaptive compilation."*

---

### Slide 2: Problem Identification (2 Marks)
* **Slide Title:** The Problem: Phase-Ordering & Optimization Degradation
* **Key Bullet Points:**
  1. **The Phase-Ordering Problem:**
     - In modern optimizing compilers (GCC, Clang/LLVM), optimization passes are applied in fixed, predetermined pipelines (e.g., `-O1`, `-O2`, `-O3`).
     - Compiler passes are non-commutative: the order in which passes execute significantly impacts execution time, register pressure, and binary size.
  2. **The Optimization Degradation Phenomenon:**
     - Individual passes applied speculatively can inadvertently degrade code quality:
       - *Aggressive Inlining* causes instruction-cache thrashing.
       - *Loop Unrolling & Common Subexpression Elimination (CSE)* inflate variable live ranges, triggering severe register spilling to RAM.
  3. **The State-Preservation Gap:**
     - Production compilers lack a fine-grained, in-situ checkpointing mechanism to detect and revert deteriorating passes during intermediate stages.

---

### Slide 3: Literature Survey & Research Gap (2 Marks)
* **Slide Title:** Literature Survey: State of the Art vs. OptiGuard
* **Comparative Table:**

| Author / Paper | Method / Technique | Critical Limitation | OptiGuard's Gap Resolution |
| :--- | :--- | :--- | :--- |
| **Cooper et al. (Rice Univ.)** | Genetic Algorithms for Phase-Ordering Search | Offline search requires hours per input program; cannot run during normal compile-time. | OptiGuard performs **lightweight, in-situ static IR analysis** without offline iterative recompilation. |
| **Kulkarni et al.** | Iterative Compilation with Fast Pruning | Relies on hardware execution profiling of compiled binaries. | OptiGuard calculates an **analytical multi-objective cost model $J(IR)$** directly on TAC IR. |
| **Milepost GCC (Fursin et al.)** | Machine Learning for Macro-Flag Selection | Black-box compiler-level flag selection; cannot inspect or revert individual micro-passes. | OptiGuard operates at the **micro-pass level**, tracking individual pass deltas. |
| **Ashouri et al. (ACM CSUR)** | Comprehensive Survey on Compiler Autotuning | Highlights that fixed heuristics fail catastrophically on atypical code structures. | OptiGuard guarantees stability using **transactional state rollback**. |

---

### Slide 4: Project Objectives (2 Marks)
* **Slide Title:** Project Objectives & Research Scope
* **Key Bullet Points:**
  1. **Modular Compiler Frontend & TAC IR Generator:**
     - Parse a procedural C-subset into an Abstract Syntax Tree (AST) and lower it into Three-Address Code (TAC).
  2. **Modular Micro-Pass Optimization Suite:**
     - Implement Constant Folding/Propagation, Algebraic Simplification, Dead-Code Elimination (DCE), and Common Subexpression Elimination (CSE).
  3. **Multi-Objective Cost Model ($J(IR)$):**
     - Quantify IR quality using a weighted metric:
       $$J(IR) = w_1 \cdot \text{InstrCount} + w_2 \cdot \text{RegPressure} + w_3 \cdot \text{ALUCycleCost}$$
  4. **Degradation Detection & Transactional Rollback:**
     - Checkpoint the IR prior to pass execution; if $\Delta J(IR) \ge 0$ (cost increases), roll back the IR to the prior stable checkpoint and ban the offending pass.
  5. **Adaptive Pass Scheduler:**
     - Dynamically select the subsequent pass based on live IR structural features.

---

### Slide 5: System Architecture & Workflow
* **Slide Title:** OptiGuard System Architecture
* **Visual Workflow:**

```
                  ┌──────────────────────────────┐
                  │    Source Code (C-Subset)    │
                  └──────────────┬───────────────┘
                                 │ Lex & Parse
                                 ▼
                  ┌──────────────────────────────┐
                  │  Three-Address Code (TAC/IR) │
                  └──────────────┬───────────────┘
                                 │
                   ┌─────────────▼───────────────┐
             ┌────►│    IR Feature Extractor     │◄─────────────┐
             │     └─────────────┬───────────────┘              │
             │                   │ Metrics Vector               │
             │     ┌─────────────▼───────────────┐              │
             │     │   Adaptive Pass Selector    │              │
             │     └─────────────┬───────────────┘              │
             │                   │ Select Pass P_i              │
             │     ┌─────────────▼───────────────┐              │
             │     │  Save IR Snapshot (Stack)   │              │
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
             │        [ Keep IR ]    [ ROLLBACK ] ──────────────┘
             │             │              │ Revert to Snapshot &
             └─────────────┤              │ Add Pass to Tabu List
                           ▼              ▼
                   ┌──────────────────────────────┐
                   │  Convergence / Budget Check  │
                   └──────────────┬───────────────┘
                                  │ Terminated
                                  ▼
                   ┌──────────────────────────────┐
                   │     Optimized TAC Output     │
                   └──────────────────────────────┘
```

---

### Slide 6: 25% Implementation Milestone (Ready for Demo)
* **Slide Title:** Current Progress: 25% Working Prototype
* **Key Bullet Points:**
  - **Full Frontend Pipeline:** Tokenizer + Recursive Descent Parser $\to$ AST $\to$ Linear Three-Address Code (TAC).
  - **Three Active Optimization Passes:**
    1. *Constant Folding & Propagation:* Evaluates static arithmetic ($10 \times 2 \to 20$) and forward-substitutes known constants.
    2. *Algebraic Simplification:* Eliminates identity operations ($x + 0 \to x$, $x \times 1 \to x$, $x \times 0 \to 0$).
    3. *Dead Code Elimination (DCE):* Backwards def-use liveness analysis pruning dead instructions.
  - **Quantitative Metrics Engine:** Tracks before/after instruction counts and weighted CPU cycle costs.
  - **Sample Demonstration Result:**
    - Raw TAC Instructions: **8** $\to$ Optimized TAC Instructions: **4**
    - **Optimization Reduction: 50.0%** in instruction count.

---

### Slide 7: Roadmap to 75% and 100%
* **Slide Title:** Project Milestone & Timeline Alignment

| Milestone | Target Due Date | Planned Deliverables |
| :--- | :--- | :--- |
| **Review 1** | Sep 24–25, 2026 | Problem Statement, Literature Survey, Novelty, Architecture Defense. |
| **25% Demo** | 1st Week of Oct | Complete Frontend, TAC IR, 3 Passes, Metric Calculation (Ready today). |
| **Review 2 (75%)** | 3rd Week of Oct | IR Feature Profiler, Degradation Detection Unit, Stack-based Rollback, Progress Report. |
| **Final Demo (100%)** | 4th Week of Oct | Full Adaptive Engine, Benchmark Evaluation Suite, IEEE Conference Manuscript / Provisional Patent Draft. |

---

### Slide 8: Summary & Research Contribution (2 Marks)
* **Slide Title:** Summary & Expected Impact
* **Core Takeaways:**
  - **Novel Contribution:** Unifies adaptive pass scheduling with in-situ transactional rollback, preventing optimization degradation.
  - **Deterministic Safety:** Ensures generated intermediate representations are monotonically non-degrading with respect to the cost model.
  - **Project Outcome:**
    1. A modular, functional educational compiler optimizer.
    2. Empirical research manuscript benchmarked across synthetic and algorithmic test programs.

---

## Part 2: 5-Minute Presentation Script (For 1 to 3 Speakers)

### Speaker 1: Problem & Literature (Slides 1 to 3)
> *"Good morning, respected professors and evaluation committee. Today, our team presents **OptiGuard: An Adaptive Compiler Optimization Framework with Degradation Detection and Safe Rollback**.*  
>  
> *In production compilers like GCC and LLVM, optimization passes execute in predetermined sequences, such as `-O2` or `-O3`. However, compiler research has demonstrated that pass ordering is fundamentally non-commutative. Applying passes in a rigid order leads to the **Phase-Ordering Problem**.*  
>  
> *Even worse is **Optimization Degradation**: transformations that appear beneficial—such as Loop Unrolling or Common Subexpression Elimination—can unexpectedly increase register pressure, causing cache thrashing or memory spilling. Once an industrial compiler applies a deteriorating pass, there is no in-situ mechanism to detect the degradation and revert the IR to a previous safe state.*  
>  
> *Looking at prior literature, Cooper et al. explored genetic algorithms, and Kulkarni et al. explored iterative compilation. However, these systems rely on offline searches that take hours or re-execute compiled binaries. Milepost GCC tackled flag selection, but operates as a black box. **OptiGuard bridges this gap** by performing in-situ, static IR feature profiling and transactional state rollback directly inside the optimization loop."*

### Speaker 2: Objectives & Architecture (Slides 4 & 5)
> *"Moving to our system objectives: OptiGuard designs a modular compiler pipeline that ingests a C-like language, lowers it into Three-Address Code, evaluates optimization passes against a multi-objective cost function $J(IR)$, and maintains a rollback stack.*  
>  
> *Here is how the OptiGuard architecture functions:*  
> 1. *First, the source code is parsed into Three-Address Code.*  
> 2. *Before applying an optimization pass, the system snapshots the current IR onto a rollback stack and extracts structural features.*  
> 3. *The pass is applied to create a candidate IR.*  
> 4. *Our Degradation Detection Unit re-evaluates the cost function. If the pass reduced cost, the transformation is committed.*  
> 5. *If the pass increased cost or inflated register pressure, **OptiGuard triggers a rollback**, restores the exact prior IR snapshot, and instructs the scheduler to explore an alternate pass.*  
> *This guarantees that our compiler's output never degrades."*

### Speaker 3: Implementation, Demo & Roadmap (Slides 6 to 8)
> *"We have already implemented our **25% milestone prototype** ahead of schedule. Our pipeline contains a full Lexer, Recursive Descent Parser, AST Generator, and a Three-Address Code Engine, along with three active optimization passes: Constant Folding, Algebraic Simplification, and Dead Code Elimination.*  
>  
> *In our initial test cases, OptiGuard successfully reduces code size and execution cycle cost by up to 50% on test programs.*  
>  
> *For our upcoming 75% milestone in October, we are integrating the IR feature profiler, the multi-objective cost function, and the rollback stack. Finally, for the 100% outcome milestone, we will present a complete comparative benchmark and a formal IEEE-format research manuscript with a provisional patent specification.*  
>  
> *Thank you. We are now open to questions."*

---

## Part 3: Examiner Q&A Defense Flashcards

| Question | Strongest Answer |
| :--- | :--- |
| **Q1: Why not just run GCC or LLVM `-O3`?** | `LLVM -O3` uses fixed heuristics designed for average-case code. On edge cases, `-O3` can cause register spilling and cache misses that make binaries slower than `-O2`. OptiGuard addresses this exact issue by monitoring code metrics per pass and reverting passes that degrade code quality. |
| **Q2: How do you mathematically quantify degradation?** | We define a composite cost function $J(IR) = w_1 \cdot \text{InstrCount} + w_2 \cdot \text{LiveVariables} + w_3 \cdot \text{ALUCycles}$. If after a pass $J(IR_{\text{new}}) > J(IR_{\text{prev}})$, the pass is categorized as degrading and rolled back. |
| **Q3: Does state rollback cause memory or runtime overhead?** | In our prototype, TAC instructions are represented as lightweight tuples. Deep-copying or diff-logging an instruction list takes microseconds, negligible compared to the execution runtime savings in resource-constrained or embedded environments. |
| **Q4: How do you prevent an infinite rollback loop?** | We enforce two convergence rules: (1) A maximum pass exploration budget $K$, and (2) A Tabu List that temporarily bans any pass sequence that caused degradation on the current IR state. |
| **Q5: Why build a custom TAC compiler instead of an LLVM plugin right away?** | A custom TAC compiler provides full observability over every instruction, live variable, and state snapshot without the millions of lines of boilerplate required by LLVM. Once the algorithmic rollback model is validated, the same architecture can be mapped to LLVM's `PassManager`. |
