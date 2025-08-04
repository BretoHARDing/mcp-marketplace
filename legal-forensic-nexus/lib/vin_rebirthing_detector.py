#!/usr/bin/env python3
"""
VIN Rebirthing Evidence Detector
Analyzes documents for patterns indicating vehicle identity fraud
Based on global VIN rebirthing research patterns
"""

import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import hashlib
from dataclasses import dataclass, field
from enum import Enum

class FraudIndicator(Enum):
    """Types of fraud indicators"""
    VIN_CHANGE = "vin_alteration"
    REGISTRATION_CHANGE = "registration_transfer" 
    TIMELINE_ANOMALY = "suspicious_timing"
    DOCUMENT_TAMPERING = "metadata_mismatch"
    INSURANCE_MANIPULATION = "insurance_fraud"
    COMPLIANCE_ALTERATION = "compliance_plate_fraud"
    INSIDER_CORRUPTION = "agency_involvement"

@dataclass
class VINEvidence:
    """Evidence of VIN-related fraud"""
    indicator_type: FraudIndicator
    description: str
    confidence: float  # 0.0 to 1.0
    source_file: str
    line_number: Optional[int] = None
    context: Optional[str] = None
    related_vins: List[str] = field(default_factory=list)
    related_regos: List[str] = field(default_factory=list)
    
class VINRebirthingDetector:
    """Detects patterns of VIN rebirthing fraud in documents"""
    
    def __init__(self):
        # Known patterns from the case
        self.known_vins = []
        self.known_regos = ["CK89AJ", "XO29MP"]
        
        # Regex patterns for detection
        self.vin_pattern = re.compile(r'\b[A-HJ-NPR-Z0-9]{17}\b')
        self.nsw_rego_pattern = re.compile(r'\b[A-Z]{2}\d{2}[A-Z]{2}\b|\b[A-Z]{3}\d{2}[A-Z]\b')
        
        # Date patterns
        self.date_pattern = re.compile(
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b|'
            r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b|'
            r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b',
            re.IGNORECASE
        )
        
        # Suspicious keywords
        self.fraud_keywords = {
            'rebirth': ['rebirth', 'rebirthing', 're-birth'],
            'writeoff': ['write-off', 'writeoff', 'written off', 'total loss'],
            'salvage': ['salvage', 'scrap', 'wreck'],
            'transfer': ['transfer', 'change of', 'new registration'],
            'compliance': ['compliance plate', 'build plate', 'VIN plate'],
            'repairable': ['repairable', 'repair', 'fixed'],
            'assessor': ['assessor', 'assessment', 'inspector'],
            'fraudulent': ['fraudulent', 'false', 'fake', 'forged'],
        }
        
        # Critical date: July 19, 2019 accident
        self.accident_date = datetime(2019, 7, 19)
        
    def analyze_file(self, file_path: Path, content: str) -> List[VINEvidence]:
        """Analyze a file for VIN rebirthing evidence"""
        evidence = []
        
        # Check for VIN patterns
        evidence.extend(self._check_vin_patterns(content, str(file_path)))
        
        # Check for registration changes
        evidence.extend(self._check_registration_patterns(content, str(file_path)))
        
        # Check timeline anomalies
        evidence.extend(self._check_timeline_anomalies(content, str(file_path)))
        
        # Check for fraud keywords
        evidence.extend(self._check_fraud_keywords(content, str(file_path)))
        
        # Check document metadata if available
        if file_path.suffix.lower() == '.pdf':
            evidence.extend(self._check_pdf_metadata(file_path))
            
        return evidence
        
    def _check_vin_patterns(self, content: str, source: str) -> List[VINEvidence]:
        """Check for VIN-related patterns"""
        evidence = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Find all VINs in the line
            vins = self.vin_pattern.findall(line)
            
            if len(vins) > 1:
                # Multiple VINs in same document is suspicious
                evidence.append(VINEvidence(
                    indicator_type=FraudIndicator.VIN_CHANGE,
                    description=f"Multiple VINs found in same document: {', '.join(vins)}",
                    confidence=0.8,
                    source_file=source,
                    line_number=i+1,
                    context=line.strip(),
                    related_vins=vins
                ))
                
            # Check for VIN near registration numbers
            if vins and any(rego in line for rego in self.known_regos):
                evidence.append(VINEvidence(
                    indicator_type=FraudIndicator.VIN_CHANGE,
                    description=f"VIN found near known registration {[r for r in self.known_regos if r in line]}",
                    confidence=0.9,
                    source_file=source,
                    line_number=i+1,
                    context=line.strip(),
                    related_vins=vins,
                    related_regos=[r for r in self.known_regos if r in line]
                ))
                
        return evidence
        
    def _check_registration_patterns(self, content: str, source: str) -> List[VINEvidence]:
        """Check for registration change patterns"""
        evidence = []
        
        # Check if both known registrations appear
        if all(rego in content for rego in self.known_regos):
            evidence.append(VINEvidence(
                indicator_type=FraudIndicator.REGISTRATION_CHANGE,
                description=f"Document contains both registrations: {', '.join(self.known_regos)}",
                confidence=0.95,
                source_file=source,
                related_regos=self.known_regos
            ))
            
        # Check for XO29MP (the rebirthed registration)
        if "XO29MP" in content:
            evidence.append(VINEvidence(
                indicator_type=FraudIndicator.REGISTRATION_CHANGE,
                description="Document contains rebirthed registration XO29MP",
                confidence=1.0,
                source_file=source,
                related_regos=["XO29MP"]
            ))
            
        # Look for registration transfer language
        transfer_phrases = [
            "registration transfer",
            "change of registration",
            "new registration",
            "re-registered",
            "registration changed"
        ]
        
        for phrase in transfer_phrases:
            if phrase.lower() in content.lower():
                evidence.append(VINEvidence(
                    indicator_type=FraudIndicator.REGISTRATION_CHANGE,
                    description=f"Registration transfer language found: '{phrase}'",
                    confidence=0.7,
                    source_file=source
                ))
                
        return evidence
        
    def _check_timeline_anomalies(self, content: str, source: str) -> List[VINEvidence]:
        """Check for suspicious timing patterns"""
        evidence = []
        
        # Find all dates in content
        dates = []
        for match in self.date_pattern.finditer(content):
            try:
                # Parse the date based on which groups matched
                if match.group(1) and match.group(2) and match.group(3):
                    # DD/MM/YYYY or MM/DD/YYYY format
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = int(match.group(3))
                    if day > 12:  # Assume DD/MM/YYYY
                        date = datetime(year, month, day)
                    else:  # Could be either format
                        date = datetime(year, month, day)
                elif match.group(4):
                    # YYYY-MM-DD format
                    date = datetime(int(match.group(4)), int(match.group(5)), int(match.group(6)))
                else:
                    # Month name format
                    months = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                             'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
                    month = months[match.group(8).lower()[:3]]
                    date = datetime(int(match.group(9)), month, int(match.group(7)))
                    
                dates.append((date, match.start()))
            except:
                continue
                
        # Check for suspiciously quick processing
        writeoff_date = datetime(2019, 8, 2)  # Known write-off date
        
        for date, pos in dates:
            # Documents dated before accident but mentioning post-accident events
            if date < self.accident_date and "write-off" in content[pos:pos+200].lower():
                evidence.append(VINEvidence(
                    indicator_type=FraudIndicator.TIMELINE_ANOMALY,
                    description=f"Document dated {date.strftime('%Y-%m-%d')} mentions write-off (before accident)",
                    confidence=0.9,
                    source_file=source
                ))
                
            # Very quick write-off determination (within 14 days)
            if self.accident_date < date < writeoff_date:
                days_diff = (date - self.accident_date).days
                if days_diff < 14:
                    evidence.append(VINEvidence(
                        indicator_type=FraudIndicator.TIMELINE_ANOMALY,
                        description=f"Suspiciously fast processing: only {days_diff} days after accident",
                        confidence=0.8,
                        source_file=source
                    ))
                    
        return evidence
        
    def _check_fraud_keywords(self, content: str, source: str) -> List[VINEvidence]:
        """Check for fraud-related keywords"""
        evidence = []
        content_lower = content.lower()
        
        # Check each category of keywords
        for category, keywords in self.fraud_keywords.items():
            found_keywords = [kw for kw in keywords if kw in content_lower]
            
            if found_keywords:
                # Special handling for certain combinations
                if category == 'writeoff' and any(kw in content_lower for kw in self.fraud_keywords['repairable']):
                    evidence.append(VINEvidence(
                        indicator_type=FraudIndicator.INSURANCE_MANIPULATION,
                        description="Document mentions both 'write-off' and 'repairable' - classic rebirthing pattern",
                        confidence=0.95,
                        source_file=source
                    ))
                    
                elif category == 'compliance':
                    evidence.append(VINEvidence(
                        indicator_type=FraudIndicator.COMPLIANCE_ALTERATION,
                        description=f"Compliance plate manipulation keywords found: {found_keywords}",
                        confidence=0.85,
                        source_file=source
                    ))
                    
        # Check for HMIA (the insurer)
        if "HMIA" in content:
            evidence.append(VINEvidence(
                indicator_type=FraudIndicator.INSURANCE_MANIPULATION,
                description="HMIA insurance company mentioned - key player in write-off declaration",
                confidence=0.9,
                source_file=source
            ))
            
        # Check for RMS/Service NSW corruption indicators
        if any(term in content_lower for term in ['rms', 'roads and maritime', 'service nsw']):
            if any(term in content_lower for term in ['corruption', 'investigation', 'icac', 'ember', 'mistral']):
                evidence.append(VINEvidence(
                    indicator_type=FraudIndicator.INSIDER_CORRUPTION,
                    description="Document references RMS/Service NSW with corruption-related terms",
                    confidence=0.85,
                    source_file=source
                ))
                
        return evidence
        
    def _check_pdf_metadata(self, file_path: Path) -> List[VINEvidence]:
        """Check PDF metadata for tampering evidence"""
        evidence = []
        
        # This would require PyPDF2 or similar library
        # For now, we'll check file modification times
        try:
            stat = file_path.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            
            # If file was modified after the accident but claims to be from before
            if mod_time > self.accident_date:
                # Check if filename suggests pre-accident document
                if any(year in str(file_path) for year in ['2018', '2019'] if '2019-07' not in str(file_path)):
                    evidence.append(VINEvidence(
                        indicator_type=FraudIndicator.DOCUMENT_TAMPERING,
                        description=f"File modified {mod_time.strftime('%Y-%m-%d')} but appears to be pre-accident",
                        confidence=0.7,
                        source_file=str(file_path)
                    ))
        except:
            pass
            
        return evidence
        
    def generate_report(self, all_evidence: List[VINEvidence]) -> Dict:
        """Generate a comprehensive fraud analysis report"""
        report = {
            'total_indicators': len(all_evidence),
            'high_confidence_indicators': len([e for e in all_evidence if e.confidence >= 0.8]),
            'evidence_by_type': {},
            'critical_findings': [],
            'recommended_actions': []
        }
        
        # Group by indicator type
        for indicator_type in FraudIndicator:
            type_evidence = [e for e in all_evidence if e.indicator_type == indicator_type]
            if type_evidence:
                report['evidence_by_type'][indicator_type.value] = {
                    'count': len(type_evidence),
                    'max_confidence': max(e.confidence for e in type_evidence),
                    'details': [
                        {
                            'description': e.description,
                            'confidence': e.confidence,
                            'source': e.source_file
                        }
                        for e in sorted(type_evidence, key=lambda x: x.confidence, reverse=True)[:3]
                    ]
                }
                
        # Identify critical findings
        if any(e.indicator_type == FraudIndicator.VIN_CHANGE and e.confidence > 0.8 for e in all_evidence):
            report['critical_findings'].append("Strong evidence of VIN alteration detected")
            
        if any("XO29MP" in e.related_regos for e in all_evidence):
            report['critical_findings'].append("Rebirthed registration XO29MP found in documents")
            
        if report['high_confidence_indicators'] > 5:
            report['critical_findings'].append(f"Multiple high-confidence fraud indicators ({report['high_confidence_indicators']}) suggest organized rebirthing operation")
            
        # Recommended actions
        if report['critical_findings']:
            report['recommended_actions'] = [
                "Immediately report findings to NSW Police Fraud Squad",
                "File complaint with ICAC regarding potential RMS corruption",
                "Engage forensic document examiner for detailed analysis",
                "Preserve all evidence with hash verification",
                "Consider criminal prosecution under s154G Crimes Act (14 years imprisonment)"
            ]
            
        return report

# Example usage
if __name__ == "__main__":
    detector = VINRebirthingDetector()
    
    # Test with sample content
    sample_content = """
    Vehicle Inspection Report
    Date: 15/08/2019
    
    Registration: CK89AJ
    VIN: 1M2AX18C4JM123456
    
    This vehicle has been assessed as a repairable write-off following
    the accident on 19/07/2019. HMIA Insurance has approved the claim.
    
    Update 20/09/2019: Vehicle re-registered as XO29MP
    Same VIN: 1M2AX18C4JM123456
    """
    
    evidence = detector.analyze_file(Path("test.txt"), sample_content)
    report = detector.generate_report(evidence)
    
    print(json.dumps(report, indent=2))