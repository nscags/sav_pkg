# Source Address Validation Simulator (sav_pkg)

This repository contains the reference implementation for our research on source address validation (SAV).  
The work has been **submitted for publication** — once the paper is accepted, we will update this README with full citation details.

---

## Installation

Clone the repository and install dependencies:

```
git clone git@github.com:nscags/sav_pkg.git
cd sav_pkg
pip install -r requirements.txt
# alternatively, you can download BGPy directly
pip install bgpy_pkg==8.1.1
```
You may want to use a virtual environment:
```
python3 -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```
---

## Usage

Example run:
```
cd sav_pkg/scripts
python3 test.py
# NOTE: you can also use pypy3
```
For more configurations, such as the ones used in the paper, see the scripts/ folder.

---

## Citation

If you use this code in your research, please cite our paper:

Title TBD  
Authors TBD  
Submitted, 2025

A BibTeX entry will be added once the paper is published.

---

## License

This project is licensed under the BSD 3-Clause License (see LICENSE).

---

## Contact

For questions or collaboration, please contact:  
njscaglione@gmail.com