# 2027 Intelligent Handling Robot

> **The 10th Chinese University Student Engineering Practice and Innovation Competition (2027)**
> Intelligent+ Engineering Innovation Track · **Intelligent Handling** Event
> Three-person team preparation repository

[中文文档](README.md)　|　[Repository Handbook (中文)](仓库管理手册.md)　|　[Contributing](CONTRIBUTING.md)　|　[Changelog](CHANGELOG.md)

---

## 1. About This Repository

This is the engineering repository for our team's entry in the **Intelligent Handling** event of the 10th Chinese University Student Engineering Practice and Innovation Competition (2027). It centralizes:

- **Rules & Compliance** — official problem statements, rule interpretation, compliance self-check (what may be purchased vs. must be self-manufactured)
- **Interface Contracts** — mechanical/electrical/software integration agreements (coordinate frames, communication protocol, dimensional interfaces)
- **Mechanical & Hardware** — CAD models, circuit design, BOM, manufacturing drawings, procurement compliance ledger
- **Embedded & Control** — main controller firmware, communication protocol implementation
- **Vision & Algorithms** — camera calibration, recognition, localization, path planning, task scheduling
- **Testing & Acceptance** — bench tests, field tests, self-scoring against official criteria
- **Decisions & Project Management** — architecture decision records, milestones, risk register, open questions

> **Single principle**: discussion may happen anywhere, but **conclusions must land back in this repository**.

---

## 2. Key Event Constraints (Quick Reference)

> Full interpretation: **[docs/00-规则与命题/规则解读.md](docs/00-规则与命题/规则解读.md)** (Chinese).

### 2.1 Hard Limits (violation ⇒ disqualification or void result)

| # | Constraint | Value / Requirement |
|---|---|---|
| 1 | **No purchased finished products or kit assembly** | Except standard parts, all non-standard parts must be self-designed and manufactured |
| 2 | **Robot footprint** | Vertical projection ≤ **300 × 300 mm**, height ≤ **400 mm** (including all flexible wiring) |
| 3 | **Foldable arm allowed** | May self-deploy after start; **deployed size unrestricted** |
| 4 | **Power** | Exactly **one** internal power source; **cannot be replaced** during the competition (including setup) |
| 5 | **No remote control** | Any form of teleoperation prohibited; the laptop may not be touched while running |
| 6 | **Lighting** | Field must not be occluded; **only vertical downward fill light** is permitted |
| 7 | **Task-code display** | Prominent upper position, illuminated, unobstructed, **glyph height ≥ 12 mm**, shows task code and completion statistics |
| 8 | **One-button start** | Exactly **one** clearly labelled START button |
| 9 | **Document anonymity** | School name / personal name / team name / phone / special symbols ⇒ **0 points**; **template headings must not be modified** |

### 2.2 Field and Materials

| Item | Parameter |
|---|---|
| Field | **2400 × 2400 mm** square |
| Lanes | Gray; central cross lane width **400 mm**; four symmetric pale-yellow zones **450 × 450 mm** |
| Lane rule | After leaving the start/stop zone the robot may travel **only on gray lanes**; vertical projection crossing the boundary (arm excepted) ⇒ round over |
| Obstacles | Black φ50 × 100 mm; quantity and position **randomly drawn** |
| Start/stop zone | Blue, **2 locations**, 300 × 300 mm |
| Raw-material zone | **φ300 mm powered turntable**, total height 80–100 mm, 3 workpieces at **120°**, rotation **6–10 s/rev**, direction random |
| Buffer / rough-machining zones | 580 × 150 mm, with precision measuring rings, **line width 1.5 mm** |
| Workpieces | 3D printed **ABS/PLA**, size ≤ **80 mm**, mass ≤ **100 g** |
| Workpiece colors | Red 1, Yellow 2, Blue 3, Green 4, Black 5, Light Blue 6 (RBGYB = ABS, light blue = PLA), **2 of each** |
| QR board | A4 landscape, QR **80 × 80 mm** (incl. border), randomly positioned |

### 2.3 Placement Accuracy Scoring (non-linear — decisive)

| Ring | 1 | 2 | 3 | 4 | 5 | 6 | Outside 6 / toppled |
|---|---|---|---|---|---|---|---|
| **Score** | **15** | 10 | 7 | 5 | 3 | 1 | 0 |

- Criterion: **if the workpiece underside reveals the edge of a ring, the workpiece is inside that ring**
- ⚠️ **Once the workpiece underside contacts the ground it counts as placed; moving it again ⇒ round over** (no "fine-tuning")

### 2.4 Task Code Format

**4 groups of three digits joined by `+`**:

```
  1 5 6  +  1 2 3  +  5 1 6  +  2 3 1
  └─┬─┘    └─┬─┘    └─┬─┘    └─┬─┘
 batch-1 color order   batch-1 positions   batch-2 color order   batch-2 positions
```

- **Colors**: Red 1, Yellow 2, Blue 3, Green 4, Black 5, Light Blue 6
- **Positions**: rings 1–6
- Example `156+123+516+231`: batch 1 picked in order red → black → light blue and placed on rough-machining rings 1, 2, 3; batch 2 picked black → red → light blue and placed on rings 2, 3, 1.

See **[docs/10-接口契约/任务码定义.md](docs/10-接口契约/任务码定义.md)**

### 2.5 Timing Budget (tightest constraint)

| Phase | Time |
|---|---|
| Setup per round | **3 minutes** |
| 3 min remaining | Task drawn by lot |
| 30 s remaining | Robot stops, returned to start position; judge places QR board, randomizes workpieces, starts turntable |
| Run per round | **3 minutes** |
| Idle tolerance after start | **15 seconds** (the allowance for turntable rotation is increased by 8 s) ⇒ exceeding it ends the round |
| Start method | **One-button start, one attempt only** |
| Attempts | **2 runs** per team, best score counts |

### 2.6 Score Composition

```
Preliminary total = Task document 20% + Creative design 10% + On-site preliminary 70%
Final total       = Innovation practice 30% + On-site final 70%
```

**On-site preliminary scoring items**:

| Item | Score |
|---|---|
| Correctly read QR and display task code | 1 |
| Each correctly grasped workpiece (placed onto robot) | 2 each |
| Placement accuracy in rough-machining + buffer zones | 15/10/7/5/3/1/0 per workpiece ← **largest weight** |
| Stacking in buffer zone (batch 2, matching color, no fall) | same as placement score |
| Return to the drawn start/stop zone in time | 2 |
| Correctly display grasp count + placement count | 2 each |

**Creative design (100)**: innovation 40 / aesthetics 30 / rationality 30
> Scoring presupposes the **internal structure is clearly observable** — the exterior should *expose* internals.

### 2.7 Timeline

| Date | Milestone |
|---|---|
| 2026-09-30 | School-level pre-registration deadline |
| **Early Oct 2026** | **Deliverable submission** (design report, design data, defense slides) |
| Late Oct 2026 | School-level review (on-site defense + material review) |
| Jul–Aug 2027 | National finals |

---

## 3. Team and Division of Work

> Work is divided by **deliverable interface**, not by job title.
> See **[.github/CODEOWNERS](.github/CODEOWNERS)** for the role → directory → permission mapping.

| Role | Primary responsibility | Primary directories |
|---|---|---|
| **A · System integration & PM** | Technical roadmap, interface contracts, localization & placement accuracy, schedule and risk | `docs/10-接口契约/`, `docs/40-测试与验收/`, `docs/60-项目管理/` |
| **B · Mechanical & hardware** | Structural design, actuators, assembly, BOM, procurement compliance | `hardware/` |
| **C · Control & vision** | Firmware, vision recognition, task scheduling, protocol, statistics display | `embedded/`, `vision/`, `algorithm/` |

**⚠️ The principal risk for a three-person team**: only one person each for mechanical and software; losing either blocks the whole chain.
Mitigation: a **mandatory bi-weekly "hard integration day"** — see [docs/60-项目管理/里程碑.md](docs/60-项目管理/里程碑.md).

### Outstanding Information

Not yet determined; tracked in **[docs/60-项目管理/待确认清单.md](docs/60-项目管理/待确认清单.md)**:

- [ ] Member names, years, majors, skill distribution
- [ ] Advisor information
- [ ] MCU model, camera model, servo/motor models
- [ ] 3D printer availability / machining resources
- [ ] Budget ceiling
- [ ] School / provincial competition dates

---

## 4. Repository Layout

```
2027-Intelligent-Handling-Robot/
├── README.md                  Chinese main entry
├── README.en.md               This file
├── 仓库管理手册.md            ★ Required reading for teammates
├── CONTRIBUTING.md            Branch / commit / PR / review conventions
├── CHANGELOG.md               Changelog (Keep a Changelog)
├── GITHUB_SETUP.md            Remote setup and push instructions
├── push-to-github.bat         ★ Double-click to push to GitHub
├── .gitignore                 Ignore rules
├── .gitattributes             ★ Git LFS rules (CAD / models / video)
├── .github/
│   ├── ISSUE_TEMPLATE/        Issue templates (bug/task/experiment/decision)
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS             Per-directory reviewers
│   └── workflows/             CI: docs / anonymity / firmware / python
├── docs/
│   ├── 00-规则与命题/         Official PDFs + rule interpretation + compliance
│   ├── 05-场地与标定/         Field measurement, ring sizes, turntable timing
│   ├── 10-接口契约/           ★★ ICD, protocol, coordinate frames, task code
│   ├── 20-技术方案/           Architecture / mechanical / control / vision (TBD)
│   ├── 30-实验记录/           Experiment log (numbered by date)
│   ├── 40-测试与验收/         On-site self-scoring sheet
│   ├── 50-决策记录/           ADRs
│   ├── 60-项目管理/           Milestones, risks, open questions
│   └── 90-模板/               Blank templates
├── hardware/                  cad / pcb / bom / drawings / compliance
├── embedded/                  Firmware (shared/ holds protocol definitions)
├── vision/                    calibration / dataset / models / src
├── algorithm/                 Planning, localization, task state machine
├── simulation/                Simulation scenes
├── test/                      bench / field / acceptance
├── tools/                     Calibration, flashing, log analysis, anonymity check
└── release/submission/        ★ Anonymized submission package
```

---

## 5. Quick Start

`git clone <repo-url>` → `git lfs install` → `git checkout develop` → `git checkout -b feature/<task>` → commit → PR into `develop`.

Full instructions: **[仓库管理手册.md](仓库管理手册.md)**

---

## 6. Branching

| Branch | Purpose |
|---|---|
| `main` | Competition-stable release; only merged from `develop`; frozen before the event, bug fixes only |
| `develop` | Daily integration |
| `feature/*` | Feature work, branched from `develop`, PR back to `develop` |
| `fix/*` | Urgent fixes, may PR directly to `main` (reviewed by A) |
| `release/*` | Frozen submission versions, branched from `develop` |

---

## 7. Commit Convention

`<type>(<scope>): <description>` with types `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `hw`, `perf`.
Reference the related issue, e.g. `feat(vision): parse QR task code (#12)`.

---

## 8. Five Team Rules

1. Every code/model change **must** be committed to Git
2. Every technical decision **must** be recorded in [docs/50-决策记录/](docs/50-决策记录/)
3. Every bug and technical question **must** become an Issue
4. Every experiment **must** leave a record
5. Freeze `main` before the competition; bug fixes only

---

## 9. Status

| Stage | Status |
|---|---|
| Rule analysis | ✅ Done |
| Repository & conventions | ✅ Done |
| Technical roadmap | ⬜ In progress (hardware selection pending) |
| Interface contracts | ⬜ Pending roadmap |
| Mechanical design | ⬜ Not started |
| Embedded & firmware | ⬜ Not started |
| Vision & algorithms | ⬜ Not started |
| System integration | ⬜ Not started |

---

## 10. License

[MIT License](LICENSE).
Competition deliverables under `release/submission/` follow the organizer's requirements.

---

<div align="center">

**2027 Engineering Innovation Competition · Intelligent Handling**

</div>
