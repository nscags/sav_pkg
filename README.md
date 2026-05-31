# Source Address Validation Simulator (sav_pkg)

An extension to the widely-used BGP security simulator [BGPy](https://github.com/jfuruness/bgpy_pkg) to evaluate Source Address Validation (SAV) policies. Built for the EZ-SAVE paper (NSDI '26), it supports simulation of IP spoofing attacks and measurement of SAV effectiveness across realistic internet topologies.

---

## Installation

Clone the repository and install dependencies:

```bash
git clone git@github.com:nscags/sav_pkg.git
cd sav_pkg

# Optional: use a virtual environment
python3 -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Install dependencies (BGPy)
pip install -r requirements.txt
# or install BGPy directly
pip install bgpy_pkg
```

---

## Supported SAV Policies

| Policy | Description |
|--------|-------------|
| `LooseuRPF` | Loose unicast Reverse Path Forwarding (uRPF) |
| `StrictuRPF` | Strict uRPF |
| `FeasiblePathuRPF` | Feasible-path uRPF |
| `FeasiblePathuRPF_All` | Feasible-path uRPF, applied to all interfaces |
| `FeasiblePathuRPF_OTC` | Feasible-path uRPF, applied only to customers |
| `EFP_A` | Enhanced Feasible-Path uRPF Algorithm A (EFP-A) |
| `EFP_A_wPeers` | EFP-A with peer routes |
| `EFP_B` | Enhanced Feasible-Path uRPF Algorithm B (EFP-B) |
| `RFC8704` | RFC 8704 Security Recommendations |
| `BAR_SAV` | BAR-SAV |
| `BAR_SAV_PI` | BAR-SAV Provider Interfaces |
| `BAR_SAV_wBSPI` | BAR-SAV with BAR-SAV-I |
| `BAR_SAV_PI_PP` | BAR-SAV with PI and Path Prepending |
| `ProcedureX` | Procedure X |

---

## Usage

Run a basic simulation:

```bash
cd scripts
JOB_COMPLETION_INDEX=0 python3 test.py
```

Results are written to `~/sav/results/test/`. For the full set of configurations used in the paper, see the [scripts/](scripts/) folder — each script corresponds to a specific scenario or policy variant.

---

## Citation

If you use this code in your research, please cite our paper:

```bibtex
@inproceedings{ez-save,
  author    = {Nicholas Scaglione and Justin Furuness and Yossi Gilad and Hemi Leibowitz and Cameron Morris and Bing Wang and Kotikalapudi Sriram and Amir Herzberg},
  title     = {{EZ-SAVE}: Evaluation of {Easy-to-Deploy} Source Address Validation Policies},
  booktitle = {23rd USENIX Symposium on Networked Systems Design and Implementation (NSDI 26)},
  year      = {2026},
  isbn      = {978-1-939133-54-0},
  address   = {Renton, WA},
  pages     = {2247--2265},
  url       = {https://www.usenix.org/conference/nsdi26/presentation/scaglione},
  publisher = {USENIX Association},
  month     = may
}
```

---

## License

This project is licensed under the BSD 3-Clause License (see [LICENSE.txt](LICENSE.txt)).

---

## Contact

For questions or collaboration:
- njscaglione@gmail.com
- nicholas.scaglione@uconn.edu
