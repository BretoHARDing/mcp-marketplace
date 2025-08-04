# 📁 GOOGLE DRIVE EVIDENCE PRESERVATION GUIDE
## Harding v Terjon - Securing Your 4000 Files

---

## 🚨 IMMEDIATE ACTIONS (Do This NOW!)

### 1. **Secure Your Google Account**
- [ ] Change your Google password immediately
- [ ] Enable 2-factor authentication
- [ ] Check recent login activity for unauthorized access
- [ ] Remove any unknown shared users

### 2. **Create Evidence Snapshot**
- [ ] **Make a complete backup folder:**
  ```
  1. Create new folder: "HARDING_EVIDENCE_BACKUP_[TODAY'S DATE]"
  2. Select all 4000 files
  3. Right-click → "Make a copy"
  4. Move copies to backup folder
  5. Right-click folder → "Download" (this creates local backup)
  ```

### 3. **Lock Down Sharing**
- [ ] Review all shared files/folders
- [ ] Remove access for anyone associated with:
  - Terjon Services
  - Roderick Storie
  - Any opposing parties
- [ ] Screenshot current sharing settings before changes

---

## 📊 GOOGLE DRIVE ORGANIZATION SYSTEM

### Create This Folder Structure:
```
📁 HARDING_V_TERJON_MASTER
├── 📁 00_ORIGINAL_FILES_DO_NOT_TOUCH
│   └── [Your 4000 original files - NEVER edit these]
├── 📁 01_WORKING_COPIES
│   └── [Copies for analysis]
├── 📁 02_EVIDENCE_BY_DATE
│   ├── 📁 2019_Accident_Period
│   ├── 📁 2020_Local_Court
│   ├── 📁 2021_Supreme_Court
│   ├── 📁 2022_District_Court
│   └── 📁 2023_Settlement
├── 📁 03_KEY_EVIDENCE
│   ├── 📁 VIN_Rebirthing_Proof
│   ├── 📁 Employment_Contradictions
│   ├── 📁 Mechanical_Defects
│   └── 📁 Legal_Malpractice
└── 📁 04_METADATA_HASHES
    └── [Hash verification files]
```

### How to Organize:
1. **DO NOT move original files** - create copies
2. **Use Google Drive labels** for categorization
3. **Add descriptions** to critical files

---

## 🔍 FINDING KEY EVIDENCE IN YOUR 4000 FILES

### Search Terms to Use in Google Drive:

#### **VIN Rebirthing Evidence**
```
Search for: CK89AJ OR XO29MP OR "rego" OR "registration" OR "VIN"
Look for: Registration papers, service records, insurance docs
```

#### **Employment Status**
```
Search for: "contract" OR "employment" OR "contractor" OR "ABN" OR "tax"
Look for: Any employment agreements, especially post-July 2019
```

#### **Accident Evidence**
```
Search for: "July 19" OR "accident" OR "crash" OR "police" OR "defect"
Look for: Police reports, defect notices, mechanical reports
```

#### **Settlement Issues**
```
Search for: "Storie" OR "settlement" OR "deed" OR "consent" OR "$110,000"
Look for: Legal correspondence, settlement negotiations
```

---

## 🛡️ GOOGLE DRIVE SECURITY SETTINGS

### 1. **Enable These Features:**
- [ ] **Version History**: Right-click any file → "Version history"
- [ ] **Activity Dashboard**: Tools → Activity dashboard
- [ ] **Offline Access**: Settings → Offline (for backup)

### 2. **Document Everything:**
```javascript
// Use Google Apps Script to log all file access
function logFileAccess() {
  var files = DriveApp.getFiles();
  var log = SpreadsheetApp.create('Evidence_Access_Log');
  
  while (files.hasNext()) {
    var file = files.next();
    log.appendRow([
      new Date(),
      file.getName(),
      file.getLastUpdated(),
      file.getEditors().join(', ')
    ]);
  }
}
```

### 3. **Share Settings for Legal Team:**
- **Viewer only** - for your new lawyer
- **No download/print** - for sensitive files
- **Expiring access** - set time limits

---

## 📥 DOWNLOADING EVIDENCE PROPERLY

### Best Practices:
1. **Download in batches** (500 files at a time)
2. **Use Google Takeout** for complete archive
3. **Maintain folder structure**
4. **Verify downloads with file count

### Google Takeout Instructions:
```
1. Go to: takeout.google.com
2. Deselect all
3. Select only "Drive"
4. Choose your evidence folders
5. Export every 2 months (50GB)
6. Download to external drive
```

---

## 🔐 HASH GENERATION FOR GOOGLE DRIVE FILES

### Method 1: Using Google Colab (Free)
```python
# Run this in Google Colab
from google.colab import drive
import hashlib
import os
import pandas as pd

# Mount Drive
drive.mount('/content/drive')

# Generate hashes
def generate_file_hashes(folder_path):
    hashes = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            filepath = os.path.join(root, file)
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            hashes.append({
                'file': file,
                'path': filepath,
                'hash': sha256_hash.hexdigest(),
                'date': pd.Timestamp.now()
            })
    return pd.DataFrame(hashes)

# Run on your evidence folder
evidence_hashes = generate_file_hashes('/content/drive/MyDrive/HARDING_EVIDENCE')
evidence_hashes.to_csv('evidence_hashes.csv', index=False)
```

### Method 2: Download & Hash Locally
- Use **HashMyFiles** (Windows)
- Use **Hasher** (Mac)
- Save hash list with timestamp

---

## 📋 CRITICAL FILES TO FIND IMMEDIATELY

### Priority 1 - Smoking Guns
- [ ] Original employment documents (pre-accident)
- [ ] Backdated contractor agreements
- [ ] HMIA assessor report showing "repairable write-off"
- [ ] Service records showing CK89AJ = XO29MP
- [ ] 20+ defect notices
- [ ] Roderick Storie's settlement emails

### Priority 2 - Supporting Evidence  
- [ ] Your medical records post-accident
- [ ] Psychologist reports
- [ ] Bank statements showing payments
- [ ] Text messages about the case
- [ ] Photos of the truck/accident scene

### Priority 3 - Background
- [ ] Terjon company searches
- [ ] Joe Dimech background
- [ ] Insurance policies
- [ ] Media coverage

---

## 🚀 AUTOMATION TOOLS

### Google Drive Add-ons to Install:
1. **Drive Explorer** - Advanced search and organization
2. **Folder Colorizer** - Visual organization
3. **Drive Migrator** - Bulk operations

### Useful Scripts:
```javascript
// Find all files modified after accident
function findSuspiciousFiles() {
  var files = DriveApp.searchFiles(
    'modifiedDate > "2019-07-19" and (title contains "employment" or title contains "contract")'
  );
  // List these for review
}

// Identify duplicate files
function findDuplicates() {
  // Compare file sizes and names
  // Flag potential tampered versions
}
```

---

## ⚠️ WARNING SIGNS TO LOOK FOR

### In Your 4000 Files, Flag These:
1. **Files modified after July 19, 2019** that claim to be from before
2. **Multiple versions** of the same document with different content
3. **Missing pages** in PDF documents
4. **Metadata mismatches** (creation date vs. document date)
5. **Unusual file names** suggesting concealment

---

## 📞 SHARING WITH NEW LEGAL TEAM

### Safe Sharing Protocol:
1. Create read-only shared folder
2. Include hash verification file
3. Document what's shared and when
4. Set expiration date on access
5. Monitor access logs

### What to Share:
```
📁 LEGAL_TEAM_ACCESS
├── 📄 Evidence_Index.xlsx
├── 📄 Hash_Verification.csv
├── 📁 Priority_Documents
├── 📁 Contradictions_Found
└── 📄 Chain_of_Custody.pdf
```

---

## 🎯 NEXT STEPS

### Today:
1. Secure your Google account
2. Create backup folder structure
3. Start searching for priority files
4. Generate initial hash records

### This Week:
1. Organize files into evidence categories
2. Create comprehensive index
3. Download full backup via Takeout
4. Share with new legal counsel

### Ongoing:
1. Weekly hash verification
2. Monitor file access
3. Document any changes
4. Regular backups

---

**Remember:** Your Google Drive likely contains evidence that could overturn those judgments and expose criminal fraud. Protect it like your home depends on it - because it does!