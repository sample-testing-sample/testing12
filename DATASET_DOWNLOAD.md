# NeuroTract MRI Dataset Download & Processing Guide

## Overview

This guide covers downloading, preparing, and processing MRI data for use with the NeuroTract platform.

## Dataset Sources

### 1. Stanford HARDI Dataset (Recommended for Testing)

**Status:** Available within the project
**Size:** ~1GB  
**Description:** High Angular Resolution Diffusion Imaging (HARDI) data from 1 healthy subject

**Already Included:**
The repository includes sample HARDI data from the Stanford dataset:
- Subject: SUB1
- Location: `MRI/Neurotract/datasets/Stanford dataset/`
- Files:
  - `SUB1_b1000_1.nii.gz` - DWI data
  - `SUB1_b1000_1.bvals` - B-values
  - `SUB1_b1000_1.bvecs` - B-vectors
  - `SUB1_aparc-reduced.nii.gz` - Parcellation atlas

### 2. Human Connectome Project (HCP) Dataset

**Status:** Requires authorization
**Size:** 50-200GB per subject
**Description:** Comprehensive imaging, behavioral, and genetic data from 1200+ subjects

**Download Instructions:**
1. Register at: https://www.humanconnectome.org/study/hcp-young-adult/
2. Request dataset access
3. Download using provided scripts or web interface
4. Organize according to BIDS structure

**Key Files:**
- DWI images: `sub-{ID}/ses-01/dwi/sub-{ID}_ses-01_dir-AP_dwi.nii.gz`
- B-values: `sub-{ID}_ses-01_dir-AP_dwi.bval`
- B-vectors: `sub-{ID}_ses-01_dir-AP_dwi.bvec`
- Anatomical: `sub-{ID}/ses-01/anat/sub-{ID}_ses-01_T1w.nii.gz`

### 3. BIDS Test Datasets

**Status:** Open access
**Size:** 100MB - 5GB varies
**Description:** Standardized datasets for testing

**Options:**
- OpenNeuro: https://openneuro.org/ (search for diffusion MRI)
- NITRC: https://www.nitrc.org/ (Neuroimaging Informatics Tools and Resources)
- dMRIprepstandard: https://dmriprep.readthedocs.io/ (includes test data)

### 4. Your Own Data

**Format Requirements:**
- NIfTI format (.nii or .nii.gz)
- BIDS structure (recommended)
- 3D DWI volumes with multiple gradient directions
- Associated B-value and B-vector files

**Minimum Specifications:**
- At least 30 gradient directions (ideally 60+)
- B-value typically 1000 s/mm²
- Spatial resolution: 2mm isotropic or better
- Brain coverage: full brain with some margin

## Setup Instructions

### For Included Stanford Dataset

The Stanford test data is already in the repository. To process it:

```bash
cd MRI/Neurotract

# Activate virtual environment
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows

# Process the data (see Quick Start section below)
```

### For HCP or Custom Data

1. **Organize Data:**
```bash
cd MRI/Neurotract

# Create data directory if not exists
mkdir -p datasets/custom

# Copy/download your DWI data:
cp /path/to/your/dwi.nii.gz datasets/custom/
cp /path/to/your/dwi.bval datasets/custom/
cp /path/to/your/dwi.bvec datasets/custom/
```

2. **Prepare BIDS Structure (Optional but Recommended):**
```
datasets/
├── sub-01/
│   └── ses-01/
│       └── dwi/
│           ├── sub-01_ses-01_dwi.nii.gz
│           ├── sub-01_ses-01_dwi.bval
│           ├── sub-01_ses-01_dwi.bvec
│           └── sub-01_ses-01_dwi.json (optional)
```

## Quick Start: Process Included Stanford Data

### Complete 7-Stage Pipeline

```bash
# From MRI/Neurotract directory with .venv activated

# Step 1: Preprocessing (5-10 minutes)
python -m src.backend.cli preprocess \
  --input "datasets/Stanford dataset/SUB1_b1000_1.nii.gz" \
  --bvals "datasets/Stanford dataset/SUB1_b1000_1.bvals" \
  --bvecs "datasets/Stanford dataset/SUB1_b1000_1.bvecs" \
  --output "output/SUB1/preprocessed" \
  --no-motion-correction

# Step 2: DTI Computation (2-3 minutes)
python -m src.backend.cli dti \
  --input "output/SUB1/preprocessed/preprocessed_dwi.nii.gz" \
  --bvals "output/SUB1/preprocessed/preprocessed_dwi.bval" \
  --bvecs "output/SUB1/preprocessed/preprocessed_dwi.bvec" \
  --mask "output/SUB1/preprocessed/preprocessed_brain_mask.nii.gz" \
  --output "output/SUB1/dti"

# Step 3: CSD/FOD Estimation (10-15 minutes)
python -m src.backend.cli csd \
  --input "output/SUB1/preprocessed/preprocessed_dwi.nii.gz" \
  --bvals "output/SUB1/preprocessed/preprocessed_dwi.bval" \
  --bvecs "output/SUB1/preprocessed/preprocessed_dwi.bvec" \
  --mask "output/SUB1/preprocessed/preprocessed_brain_mask.nii.gz" \
  --output "output/SUB1/fod.nii.gz"

# Step 4: Tractography (2-4 minutes)
python -m src.backend.cli tractography \
  --fod "output/SUB1/fod.nii.gz" \
  --mask "output/SUB1/preprocessed/preprocessed_brain_mask.nii.gz" \
  --fa-map "output/SUB1/dti/dti_fa.nii.gz" \
  --seeds-per-voxel 2 \
  --step-size 0.5 \
  --max-angle 30 \
  --fa-threshold 0.1 \
  --output "output/SUB1/streamlines.trk"

# Step 5: Connectome Construction (5-8 minutes)
python -m src.backend.cli connectome \
  --streamlines "output/SUB1/streamlines.trk" \
  --parcellation "datasets/Stanford dataset/SUB1_aparc-reduced.nii.gz" \
  --weighting count \
  --output "output/SUB1/connectome.npy"

# Step 6: Graph Metrics (1-2 minutes)
python -m src.backend.cli metrics \
  --connectome "output/SUB1/connectome.npy" \
  --output "output/SUB1/metrics.json"

# Step 7: View Results
python -c "import json; print(json.dumps(json.load(open('output/SUB1/metrics.json')), indent=2))"
```

**Total Time:** 25-45 minutes

### Verify Installation Before Processing

```bash
# Check backend
python -m src.backend.cli --version
# Output: NeuroTract 0.1.0

# Check dependencies
python -m pip list | grep -E "nibabel|dipy|nilearn"

# Verify key datasets exist
ls -la "datasets/Stanford dataset/"
```

## Running NeuroTract with Processed Data

### Backend Server (API)

```bash
# Terminal 1: Start NeuroTract Backend
cd MRI/Neurotract
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows

python -m uvicorn src.backend.api.server:app --host 0.0.0.0 --port 8001

# Output:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8001
# INFO:     Application startup complete
```

### Frontend Server

```bash
# Terminal 2: Start NeuroTract Frontend  
cd MRI/Neurotract/src/frontend

npm run dev

# Output:
# ready - started server on 0.0.0.0:3000
```

### Integrated Platform

```bash
# Terminal 3: Start QuadraDiag (from project root)
source .venv/bin/activate
python app.py

# Access at: http://localhost:8000
# Click "MRI Analysis" in navigation
```

## Accessing Results

### View Metrics
```bash
cat output/SUB1/metrics.json
```

### API Endpoints
- Backend: http://localhost:8001/docs (Swagger UI)
- Frontend: http://localhost:3000
- Integrated: http://localhost:8000/mri

### Output Files

After processing, outputs are located in `output/SUB1/`:
```
output/SUB1/
├── preprocessed/
│   ├── preprocessed_dwi.nii.gz      # Corrected DWI
│   ├── preprocessed_brain_mask.nii.gz     # Brain mask
│   └── quality_report.json             # QC metrics
├── dti/
│   ├── dti_fa.nii.gz                # Fractional Anisotropy
│   ├── dti_md.nii.gz                # Mean Diffusivity
│   └── dti_components.nii.gz        # Tensor eigenvectors/values
├── fod.nii.gz                         # Fiber Orientation Distribution
├── streamlines.trk                     # Tractography results
├── connectome.npy                      # Connectivity matrix
├── metrics.json                        # Network metrics
└── visualizations/                     # 3D visualizations
    └── brain_with_streamlines.html      # Interactive 3D view
```

## Troubleshooting

### Dataset Issues

**"File not found" error:**
- Verify file paths are correct
- Check that .nii.gz files are readable: `file output/SUB1/*.nii.gz`
- Ensure bval/bvec files have correct format (text, space-separated)

**"Shape mismatch" between DWI and b-values:**
- Check number of lines in .bval/.bvec match DWI volumes: 
  ```bash
  gunzip -c your_dwi.nii.gz | python -c "import nibabel as nib; img = nib.load(sys.stdin); print(f'Volumes: {img.shape[3]}')"
  wc -w your_dwi.bval
  ```

### Processing Issues

**Out of memory during processing:**
- Use `--lowmem` flag: `python -m src.backend.cli preprocess --lowmem`
- Process on machine with 16GB+ RAM
- Reduce dataset resolution

**Long processing times:**
- CSD step is most computationally intensive
- Can reduce CSD order with: `--csd-sh-order 4` (default: 8)
- Check system load: `top` (Linux/Mac) or Task Manager (Windows)

**CUDA/GPU not available:**
- NeuroTract falls back to CPU automatically
- GPU acceleration available for select operations
- Install CUDA toolkit if you have compatible GPU

## Download Alternative Datasets

### Using Curl/wget

```bash
# Example: Download from specific source
# Most neuroimaging data repositories provide download links

# OpenNeuro dataset example:
# Visit https://openneuro.org/, find dataset, get download link

# Command line download:
curl -O https://openneuro.org/datasets/ds000248/download
```

### Using Dataset-Specific Tools

```bash
# HCP Connector (requires HCP account)
# Instructions: https://wiki.humanconnectome.org/display/PublicData/HCP+Data+Release

# ADNI download tool
# Instructions: http://adni.loni.usc.edu/

# OpenNeuro (via Python)
pip install openneuro-py
# Then use: aws s3 sync s3://openneuro.org/ds000248 ./local/path
```

## Next Steps

1. **Process your data:** Use the pipeline commands above
2. **Access results:** Open http://localhost:8000/mri
3. **Visualize:** View 3D brain reconstructions in NeuroTract Frontend
4. **Export metrics:** Download connectivity matrices and statistics
5. **Integrate:** Use API endpoints in your clinical workflows

## Resources

- **NeuroTract Documentation:** See `MRI/Neurotract/README.md`
- **DIPY Documentation:** https://dipy.org/
- **NIfTI Format:** https://nifti.nimh.nih.gov/
- **BIDS Specification:** https://bids-standard.github.io/
- **QuadraDiag Integration:** See `SETUP_GUIDE.md`

## Support

For issues with:
- **Data format:** Check BIDS validator (https://bids-standard.github.io/bids-validator/)
- **Processing:** Review logs in `output/SUB1/logs/`
- **API:** Check http://localhost:8001/docs for endpoint documentation
- **Setup:** See `SETUP_GUIDE.md` and `SETUParchitecture.md`
