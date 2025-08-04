#!/usr/bin/env python3
"""
Claude Opus 4 Task Runner
Direct task execution interface for legal engineering operations
"""

import argparse
import json
import asyncio
from pathlib import Path
from typing import Dict, Any
import sys

sys.path.append(str(Path(__file__).parent.parent))

from lib.task_manager import TaskManager
from agents.claude_agent import ClaudeOpus4Agent


class ClaudeOpusTasker:
    """Direct task execution interface for Claude Opus 4."""
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "nexus_config.json"
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        
        self.agent = ClaudeOpus4Agent(self.config["agents"]["Claude_Opus_4"])
        self.task_manager = TaskManager(agent_name="Claude_Opus_4")
    
    async def execute_task(self, task_description: str) -> Dict[str, Any]:
        """Execute a specific task based on description."""
        
        # Task mapping
        task_handlers = {
            "legalbert integration wrapper": self.create_legalbert_wrapper,
            "human rights violation flagger": self.create_rights_violation_flagger,
            "constitutional argument generator": self.create_constitutional_generator,
            "affidavit contradiction scanner": self.create_contradiction_scanner,
            "forensic metadata analyzer": self.create_metadata_analyzer,
            "statutory term matcher": self.create_statutory_matcher
        }
        
        # Find matching task handler
        task_lower = task_description.lower()
        for key, handler in task_handlers.items():
            if key in task_lower:
                return await handler(task_description)
        
        # Default: Create custom tool based on description
        return await self.create_custom_tool(task_description)
    
    async def create_legalbert_wrapper(self, task_desc: str) -> Dict[str, Any]:
        """Create a Python wrapper for LegalBERT API integration."""
        
        code = '''"""
LegalBERT API Wrapper
Integrates with HuggingFace LegalBERT for statutory analysis
"""

import requests
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModel
import torch


class LegalBERTWrapper:
    """Wrapper for LegalBERT API integration."""
    
    def __init__(self, model_name: str = "nlpaueb/legal-bert-base-uncased"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.statutes = {
            "EvidenceAct1995": self._load_evidence_act(),
            "CrimesAct1900": self._load_crimes_act()
        }
    
    def _load_evidence_act(self) -> Dict[str, str]:
        """Load Evidence Act 1995 provisions."""
        return {
            "s59": "Proof of facts",
            "s79": "Opinion rule",
            "s90": "Discretion to exclude admissions",
            "s135": "General discretion to exclude evidence",
            "s137": "Exclusion of prejudicial evidence in criminal proceedings",
            "s138": "Exclusion of improperly obtained evidence"
        }
    
    def _load_crimes_act(self) -> Dict[str, str]:
        """Load Crimes Act 1900 provisions."""
        return {
            "s316": "Concealing serious indictable offence",
            "s319": "Perverting the course of justice",
            "s61J": "Aggravated sexual assault",
            "s93C": "Affray",
            "s112": "Breaking and entering",
            "s154C": "Taking motor vehicle without consent"
        }
    
    def match_statutory_terms(self, text: str, acts: List[str]) -> Dict[str, Any]:
        """Match text against statutory provisions."""
        results = {
            "matches": [],
            "confidence_scores": {},
            "relevant_sections": []
        }
        
        # Tokenize input text
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            text_embedding = outputs.last_hidden_state.mean(dim=1)
        
        # Match against each act
        for act in acts:
            if act in self.statutes:
                provisions = self.statutes[act]
                for section, description in provisions.items():
                    # Compare embeddings
                    section_inputs = self.tokenizer(description, return_tensors="pt", truncation=True)
                    with torch.no_grad():
                        section_outputs = self.model(**section_inputs)
                        section_embedding = section_outputs.last_hidden_state.mean(dim=1)
                    
                    # Calculate similarity
                    similarity = torch.cosine_similarity(text_embedding, section_embedding).item()
                    
                    if similarity > 0.7:  # Threshold for relevance
                        results["matches"].append({
                            "act": act,
                            "section": section,
                            "description": description,
                            "confidence": similarity
                        })
                        results["confidence_scores"][f"{act}_{section}"] = similarity
        
        # Sort by confidence
        results["matches"].sort(key=lambda x: x["confidence"], reverse=True)
        results["relevant_sections"] = [m["section"] for m in results["matches"][:5]]
        
        return results
    
    def analyze_legal_text(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform comprehensive legal text analysis."""
        analysis = {
            "entities": self._extract_legal_entities(text),
            "citations": self._extract_citations(text),
            "key_terms": self._extract_key_terms(text),
            "jurisdiction": self._identify_jurisdiction(text),
            "legal_issues": self._identify_legal_issues(text, context)
        }
        
        return analysis
    
    def _extract_legal_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract legal entities (parties, courts, etc.)."""
        # Simplified entity extraction
        entities = []
        
        # Court patterns
        court_patterns = ["Supreme Court", "District Court", "Local Court", "Federal Court"]
        for court in court_patterns:
            if court in text:
                entities.append({"type": "court", "name": court})
        
        # Party patterns (simplified)
        if " v " in text or " v. " in text:
            parts = text.split(" v " if " v " in text else " v. ")
            if len(parts) >= 2:
                entities.append({"type": "plaintiff", "name": parts[0].strip()})
                entities.append({"type": "defendant", "name": parts[1].split()[0].strip()})
        
        return entities
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract legal citations from text."""
        import re
        
        # Pattern for Australian citations
        citation_pattern = r'\[\d{4}\]\s+\w+\s+\d+'
        citations = re.findall(citation_pattern, text)
        
        # Pattern for section references
        section_pattern = r's\s?\d+[A-Z]?(?:\(\d+\))?'
        sections = re.findall(section_pattern, text)
        
        return citations + sections
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key legal terms."""
        key_terms = [
            "negligence", "breach", "duty of care", "damages", "liability",
            "evidence", "admissible", "hearsay", "witness", "testimony",
            "conviction", "acquittal", "sentence", "appeal", "jurisdiction"
        ]
        
        found_terms = []
        text_lower = text.lower()
        for term in key_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _identify_jurisdiction(self, text: str) -> str:
        """Identify the legal jurisdiction."""
        jurisdictions = {
            "NSW": ["New South Wales", "NSW", "Sydney"],
            "VIC": ["Victoria", "VIC", "Melbourne"],
            "QLD": ["Queensland", "QLD", "Brisbane"],
            "Federal": ["Commonwealth", "Federal", "Australia"]
        }
        
        for juris, indicators in jurisdictions.items():
            for indicator in indicators:
                if indicator in text:
                    return juris
        
        return "Unknown"
    
    def _identify_legal_issues(self, text: str, context: Dict[str, Any] = None) -> List[str]:
        """Identify potential legal issues in the text."""
        issues = []
        
        # Check for evidence issues
        if any(term in text.lower() for term in ["hearsay", "admissible", "excluded"]):
            issues.append("Evidence admissibility")
        
        # Check for procedural issues
        if any(term in text.lower() for term in ["jurisdiction", "standing", "limitation"]):
            issues.append("Procedural matters")
        
        # Check for criminal law issues
        if any(term in text.lower() for term in ["guilty", "conviction", "sentence"]):
            issues.append("Criminal law")
        
        return issues


# Example usage
if __name__ == "__main__":
    wrapper = LegalBERTWrapper()
    
    # Test text
    test_text = """
    The defendant was charged under s319 of the Crimes Act 1900 for perverting 
    the course of justice. The prosecution relied on evidence obtained under 
    s138 of the Evidence Act 1995.
    """
    
    # Match statutory terms
    matches = wrapper.match_statutory_terms(
        test_text, 
        ["EvidenceAct1995", "CrimesAct1900"]
    )
    
    print("Statutory Matches:", json.dumps(matches, indent=2))
    
    # Analyze legal text
    analysis = wrapper.analyze_legal_text(test_text)
    print("\\nLegal Analysis:", json.dumps(analysis, indent=2))
'''
        
        # Save the code
        output_path = Path(__file__).parent.parent / "lib" / "legalbert_wrapper.py"
        output_path.write_text(code)
        
        return {
            "status": "success",
            "file_created": str(output_path),
            "description": "LegalBERT wrapper with statutory matching capabilities",
            "features": [
                "Evidence Act 1995 provisions",
                "Crimes Act 1900 provisions",
                "Semantic similarity matching",
                "Legal entity extraction",
                "Citation extraction"
            ]
        }
    
    async def create_rights_violation_flagger(self, task_desc: str) -> Dict[str, Any]:
        """Create a human rights violation detection class."""
        
        code = '''"""
Human Rights Violation Flagger
Detects potential violations of ICCPR, ECHR, and other human rights instruments
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import PyPDF2
import json


@dataclass
class ViolationFlag:
    """Represents a potential human rights violation."""
    article: str
    instrument: str  # ICCPR, ECHR, etc.
    violation_type: str
    severity: str  # low, medium, high, critical
    evidence: str
    location: Dict[str, Any]  # page, paragraph, line
    confidence: float


class HumanRightsViolationFlagger:
    """Detects and flags potential human rights violations in legal documents."""
    
    def __init__(self):
        self.instruments = {
            "ICCPR": self._load_iccpr_articles(),
            "ECHR": self._load_echr_articles(),
            "UDHR": self._load_udhr_articles()
        }
        self.violation_patterns = self._load_violation_patterns()
    
    def _load_iccpr_articles(self) -> Dict[str, Dict[str, Any]]:
        """Load ICCPR (International Covenant on Civil and Political Rights) articles."""
        return {
            "Article 7": {
                "title": "Prohibition of torture",
                "keywords": ["torture", "cruel", "inhuman", "degrading", "punishment"],
                "violations": ["physical abuse", "psychological torture", "degrading treatment"]
            },
            "Article 9": {
                "title": "Liberty and security",
                "keywords": ["arbitrary", "detention", "arrest", "liberty", "security"],
                "violations": ["arbitrary arrest", "unlawful detention", "habeas corpus denial"]
            },
            "Article 14": {
                "title": "Fair trial",
                "keywords": ["fair", "trial", "tribunal", "equality", "presumption", "innocent"],
                "violations": [
                    "denial of legal representation",
                    "lack of independent tribunal",
                    "presumption of guilt",
                    "denial of appeal rights",
                    "excessive delay in proceedings"
                ]
            },
            "Article 17": {
                "title": "Privacy",
                "keywords": ["privacy", "family", "home", "correspondence", "honour"],
                "violations": ["unlawful surveillance", "privacy breach", "unauthorized search"]
            },
            "Article 19": {
                "title": "Freedom of expression",
                "keywords": ["expression", "opinion", "information", "ideas", "freedom"],
                "violations": ["censorship", "suppression of speech", "retaliation for expression"]
            }
        }
    
    def _load_echr_articles(self) -> Dict[str, Dict[str, Any]]:
        """Load ECHR (European Convention on Human Rights) articles."""
        return {
            "Article 3": {
                "title": "Prohibition of torture",
                "keywords": ["torture", "inhuman", "degrading"],
                "violations": ["torture", "inhuman treatment"]
            },
            "Article 5": {
                "title": "Right to liberty and security",
                "keywords": ["liberty", "security", "detention", "arrest"],
                "violations": ["arbitrary detention", "unlawful arrest"]
            },
            "Article 6": {
                "title": "Right to a fair trial",
                "keywords": ["fair", "trial", "reasonable time", "independent", "impartial"],
                "violations": ["unfair trial", "biased tribunal", "excessive delay"]
            },
            "Article 8": {
                "title": "Right to respect for private life",
                "keywords": ["private", "family", "home", "correspondence"],
                "violations": ["privacy violation", "family separation"]
            }
        }
    
    def _load_udhr_articles(self) -> Dict[str, Dict[str, Any]]:
        """Load UDHR (Universal Declaration of Human Rights) articles."""
        return {
            "Article 5": {
                "title": "No torture",
                "keywords": ["torture", "cruel", "inhuman", "degrading"],
                "violations": ["torture", "cruel treatment"]
            },
            "Article 9": {
                "title": "No arbitrary detention",
                "keywords": ["arbitrary", "arrest", "detention", "exile"],
                "violations": ["arbitrary arrest", "unlawful detention"]
            },
            "Article 11": {
                "title": "Presumption of innocence",
                "keywords": ["presumed", "innocent", "proved", "guilty"],
                "violations": ["presumption of guilt", "burden of proof reversal"]
            }
        }
    
    def _load_violation_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for detecting violations."""
        return {
            "torture": [
                r"physical\s+(?:force|violence|abuse)",
                r"beaten|beating|struck|hitting",
                r"electric\s+shock|waterboard",
                r"sleep\s+deprivation",
                r"stress\s+position"
            ],
            "arbitrary_detention": [
                r"held\s+without\s+charge",
                r"detained\s+(?:indefinitely|without\s+trial)",
                r"no\s+(?:reason|justification)\s+(?:given|provided)",
                r"arrest\s+without\s+warrant"
            ],
            "fair_trial": [
                r"denied\s+(?:lawyer|counsel|representation)",
                r"no\s+(?:interpreter|translation)",
                r"closed\s+(?:trial|hearing|proceedings)",
                r"judge\s+(?:bias|prejudice|conflict)",
                r"coerced\s+(?:confession|statement|testimony)"
            ],
            "privacy": [
                r"searched\s+without\s+(?:warrant|consent)",
                r"surveillance\s+without\s+(?:authorization|warrant)",
                r"intercepted\s+(?:communications|correspondence)",
                r"personal\s+data\s+(?:breach|leaked|exposed)"
            ]
        }
    
    def parse_pdf_affidavit(self, pdf_path: str) -> str:
        """Extract text from PDF affidavit."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += f"\\n--- Page {page_num + 1} ---\\n"
                    text += page.extract_text()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return text
    
    def flag_violations(self, text: str, instrument: str = "ICCPR") -> List[ViolationFlag]:
        """Flag potential human rights violations in text."""
        violations = []
        
        if instrument not in self.instruments:
            raise ValueError(f"Unknown instrument: {instrument}")
        
        articles = self.instruments[instrument]
        
        # Check each article
        for article_num, article_info in articles.items():
            # Check for keyword matches
            for keyword in article_info["keywords"]:
                if keyword.lower() in text.lower():
                    # Check for specific violation patterns
                    for violation_type in article_info["violations"]:
                        if self._check_violation_pattern(text, violation_type):
                            violation = self._create_violation_flag(
                                article_num,
                                instrument,
                                violation_type,
                                text,
                                keyword
                            )
                            violations.append(violation)
        
        return violations
    
    def _check_violation_pattern(self, text: str, violation_type: str) -> bool:
        """Check if text contains patterns indicating a specific violation."""
        # Map violation types to pattern categories
        pattern_map = {
            "physical abuse": "torture",
            "psychological torture": "torture",
            "degrading treatment": "torture",
            "arbitrary arrest": "arbitrary_detention",
            "unlawful detention": "arbitrary_detention",
            "denial of legal representation": "fair_trial",
            "lack of independent tribunal": "fair_trial",
            "unlawful surveillance": "privacy",
            "privacy breach": "privacy"
        }
        
        pattern_category = pattern_map.get(violation_type, violation_type.replace(" ", "_"))
        
        if pattern_category in self.violation_patterns:
            patterns = self.violation_patterns[pattern_category]
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        
        return False
    
    def _create_violation_flag(
        self, 
        article: str, 
        instrument: str, 
        violation_type: str,
        text: str,
        keyword: str
    ) -> ViolationFlag:
        """Create a violation flag with details."""
        # Find location of violation in text
        location = self._find_violation_location(text, keyword)
        
        # Assess severity
        severity = self._assess_severity(violation_type, text)
        
        # Extract evidence snippet
        evidence = self._extract_evidence(text, keyword, 100)
        
        # Calculate confidence
        confidence = self._calculate_confidence(violation_type, text)
        
        return ViolationFlag(
            article=article,
            instrument=instrument,
            violation_type=violation_type,
            severity=severity,
            evidence=evidence,
            location=location,
            confidence=confidence
        )
    
    def _find_violation_location(self, text: str, keyword: str) -> Dict[str, Any]:
        """Find the location of violation in the text."""
        lines = text.split('\\n')
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                # Extract page number if present
                page_match = re.search(r'--- Page (\\d+) ---', text[:text.find(line)])
                page = int(page_match.group(1)) if page_match else 1
                
                return {
                    "page": page,
                    "line": i + 1,
                    "paragraph": self._find_paragraph_number(lines, i)
                }
        
        return {"page": 1, "line": 1, "paragraph": 1}
    
    def _find_paragraph_number(self, lines: List[str], line_index: int) -> int:
        """Find paragraph number for a given line."""
        paragraph_count = 1
        for i in range(line_index):
            if lines[i].strip() == "":
                paragraph_count += 1
        return paragraph_count
    
    def _assess_severity(self, violation_type: str, text: str) -> str:
        """Assess the severity of a violation."""
        critical_violations = ["torture", "arbitrary execution", "forced disappearance"]
        high_violations = ["arbitrary arrest", "denial of legal representation", "coerced confession"]
        medium_violations = ["privacy breach", "excessive delay", "lack of interpreter"]
        
        if any(v in violation_type.lower() for v in critical_violations):
            return "critical"
        elif any(v in violation_type.lower() for v in high_violations):
            return "high"
        elif any(v in violation_type.lower() for v in medium_violations):
            return "medium"
        else:
            return "low"
    
    def _extract_evidence(self, text: str, keyword: str, context_chars: int = 100) -> str:
        """Extract evidence snippet around keyword."""
        keyword_lower = keyword.lower()
        text_lower = text.lower()
        
        pos = text_lower.find(keyword_lower)
        if pos == -1:
            return ""
        
        start = max(0, pos - context_chars)
        end = min(len(text), pos + len(keyword) + context_chars)
        
        evidence = text[start:end]
        
        # Clean up evidence
        evidence = evidence.replace('\\n', ' ')
        evidence = ' '.join(evidence.split())
        
        if start > 0:
            evidence = "..." + evidence
        if end < len(text):
            evidence = evidence + "..."
        
        return evidence
    
    def _calculate_confidence(self, violation_type: str, text: str) -> float:
        """Calculate confidence score for violation detection."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for multiple pattern matches
        pattern_matches = 0
        for patterns in self.violation_patterns.values():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    pattern_matches += 1
        
        confidence += min(0.3, pattern_matches * 0.05)
        
        # Increase confidence for explicit language
        explicit_terms = ["clearly", "obviously", "undeniably", "confirmed", "admitted"]
        for term in explicit_terms:
            if term in text.lower():
                confidence += 0.1
                break
        
        return min(1.0, confidence)
    
    def generate_report(self, violations: List[ViolationFlag]) -> Dict[str, Any]:
        """Generate a comprehensive violation report."""
        report = {
            "summary": {
                "total_violations": len(violations),
                "critical_violations": sum(1 for v in violations if v.severity == "critical"),
                "high_violations": sum(1 for v in violations if v.severity == "high"),
                "instruments_violated": list(set(v.instrument for v in violations)),
                "articles_violated": list(set(f"{v.instrument} {v.article}" for v in violations))
            },
            "violations": [
                {
                    "article": f"{v.instrument} {v.article}",
                    "type": v.violation_type,
                    "severity": v.severity,
                    "evidence": v.evidence,
                    "location": v.location,
                    "confidence": v.confidence
                }
                for v in violations
            ],
            "recommendations": self._generate_recommendations(violations),
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def _generate_recommendations(self, violations: List[ViolationFlag]) -> List[str]:
        """Generate recommendations based on violations found."""
        recommendations = []
        
        if any(v.severity == "critical" for v in violations):
            recommendations.append("URGENT: Immediate intervention required for critical violations")
            recommendations.append("Consider emergency legal remedies or protective orders")
        
        if any("Article 14" in v.article for v in violations):
            recommendations.append("Review fair trial guarantees and ensure legal representation")
        
        if any("Article 9" in v.article for v in violations):
            recommendations.append("Challenge detention legality through habeas corpus")
        
        if any("torture" in v.violation_type.lower() for v in violations):
            recommendations.append("Document all evidence of torture for international bodies")
            recommendations.append("Consider complaint to UN Committee Against Torture")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    flagger = HumanRightsViolationFlagger()
    
    # Test with sample text
    sample_text = """
    The defendant was held in custody for 6 months without being brought before 
    a judge. During interrogation, he was denied access to a lawyer and was 
    subjected to sleep deprivation for 48 hours. The confession obtained under 
    these circumstances was used as the primary evidence in trial.
    """
    
    # Flag violations
    violations = flagger.flag_violations(sample_text, "ICCPR")
    
    # Generate report
    report = flagger.generate_report(violations)
    
    print(json.dumps(report, indent=2))
'''
        
        # Save the code
        output_path = Path(__file__).parent.parent / "lib" / "human_rights_flagger.py"
        output_path.write_text(code)
        
        return {
            "status": "success",
            "file_created": str(output_path),
            "description": "Human rights violation detection system",
            "features": [
                "ICCPR Article 14 violation detection",
                "Multi-instrument support (ICCPR, ECHR, UDHR)",
                "PDF affidavit parsing",
                "Severity assessment",
                "Evidence extraction with location tracking",
                "Comprehensive violation reporting"
            ]
        }
    
    async def create_constitutional_generator(self, task_desc: str) -> Dict[str, Any]:
        """Create a constitutional argument generator focusing on Kable Principle."""
        
        code = '''"""
Constitutional Argument Generator
Generates Kable Principle arguments from timeline contradictions and procedural issues
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum


class ConstitutionalPrinciple(Enum):
    """Constitutional principles for analysis."""
    KABLE = "Kable Principle"
    SEPARATION_OF_POWERS = "Separation of Powers"
    JUDICIAL_INDEPENDENCE = "Judicial Independence"
    RULE_OF_LAW = "Rule of Law"
    DUE_PROCESS = "Due Process"


@dataclass
class TimelineEvent:
    """Represents an event in case timeline."""
    timestamp: datetime
    description: str
    source: str  # Document/affidavit source
    actors: List[str]
    location: Optional[str] = None
    
    
@dataclass
class Contradiction:
    """Represents a contradiction between timeline events."""
    event1: TimelineEvent
    event2: TimelineEvent
    type: str  # temporal, factual, procedural
    severity: str  # low, medium, high
    explanation: str


class KablePrincipleArgumentGenerator:
    """
    Generates constitutional arguments based on the Kable Principle.
    
    The Kable Principle (from Kable v DPP (NSW) (1996) 189 CLR 51) establishes that:
    - State parliaments cannot confer powers on state courts that are incompatible 
      with their role as repositories of federal judicial power
    - Protects the institutional integrity of state courts
    - Prevents legislative interference with judicial independence
    """
    
    def __init__(self):
        self.kable_elements = {
            "institutional_integrity": {
                "description": "Court's institutional integrity and impartiality",
                "indicators": [
                    "legislative direction of judicial outcomes",
                    "removal of judicial discretion",
                    "predetermined findings of fact",
                    "executive interference in proceedings"
                ]
            },
            "judicial_independence": {
                "description": "Independence from legislative and executive branches",
                "indicators": [
                    "pressure on judicial officers",
                    "constraints on judicial reasoning",
                    "mandatory sentencing without discretion",
                    "removal of appeal rights"
                ]
            },
            "separation_of_powers": {
                "description": "Proper separation between branches of government",
                "indicators": [
                    "executive performing judicial functions",
                    "legislative determination of guilt",
                    "administrative tribunals exercising judicial power",
                    "merger of prosecutorial and adjudicative roles"
                ]
            },
            "procedural_fairness": {
                "description": "Maintenance of fair judicial procedures",
                "indicators": [
                    "denial of natural justice",
                    "exclusion of relevant evidence",
                    "reversal of burden of proof",
                    "removal of right to legal representation"
                ]
            }
        }
    
    def analyze_timeline_contradictions(
        self, 
        timeline: List[TimelineEvent],
        affidavits: List[Dict[str, Any]]
    ) -> List[Contradiction]:
        """Analyze timeline for contradictions that may indicate Kable violations."""
        contradictions = []
        
        # Sort timeline by timestamp
        sorted_timeline = sorted(timeline, key=lambda x: x.timestamp)
        
        # Check for temporal impossibilities
        for i, event1 in enumerate(sorted_timeline):
            for event2 in sorted_timeline[i+1:]:
                contradiction = self._check_temporal_contradiction(event1, event2)
                if contradiction:
                    contradictions.append(contradiction)
        
        # Check for factual contradictions
        for i, event1 in enumerate(timeline):
            for event2 in timeline[i+1:]:
                contradiction = self._check_factual_contradiction(event1, event2)
                if contradiction:
                    contradictions.append(contradiction)
        
        # Check affidavit inconsistencies
        affidavit_contradictions = self._analyze_affidavit_inconsistencies(affidavits)
        contradictions.extend(affidavit_contradictions)
        
        return contradictions
    
    def _check_temporal_contradiction(
        self, 
        event1: TimelineEvent, 
        event2: TimelineEvent
    ) -> Optional[Contradiction]:
        """Check for temporal impossibilities between events."""
        # Example: Person in two places at once
        if event1.timestamp == event2.timestamp:
            common_actors = set(event1.actors) & set(event2.actors)
            if common_actors and event1.location and event2.location:
                if event1.location != event2.location:
                    return Contradiction(
                        event1=event1,
                        event2=event2,
                        type="temporal",
                        severity="high",
                        explanation=f"Actor(s) {common_actors} allegedly in two places simultaneously"
                    )
        
        # Example: Insufficient time between locations
        time_diff = abs((event2.timestamp - event1.timestamp).total_seconds() / 60)  # minutes
        if time_diff < 30:  # Less than 30 minutes
            common_actors = set(event1.actors) & set(event2.actors)
            if common_actors and event1.location and event2.location:
                if self._locations_far_apart(event1.location, event2.location):
                    return Contradiction(
                        event1=event1,
                        event2=event2,
                        type="temporal",
                        severity="medium",
                        explanation=f"Insufficient time for {common_actors} to travel between locations"
                    )
        
        return None
    
    def _check_factual_contradiction(
        self, 
        event1: TimelineEvent, 
        event2: TimelineEvent
    ) -> Optional[Contradiction]:
        """Check for factual contradictions between events."""
        # Check if events describe the same incident differently
        if self._events_describe_same_incident(event1, event2):
            if self._descriptions_contradict(event1.description, event2.description):
                return Contradiction(
                    event1=event1,
                    event2=event2,
                    type="factual",
                    severity="high",
                    explanation="Conflicting descriptions of the same incident"
                )
        
        return None
    
    def _analyze_affidavit_inconsistencies(
        self, 
        affidavits: List[Dict[str, Any]]
    ) -> List[Contradiction]:
        """Analyze affidavits for missing signatures and inconsistencies."""
        contradictions = []
        
        for i, aff1 in enumerate(affidavits):
            # Check for missing signatures
            if not aff1.get("signature") or not aff1.get("date_signed"):
                # Create pseudo-events for contradiction tracking
                event = TimelineEvent(
                    timestamp=datetime.now(),
                    description=f"Affidavit {aff1.get('id', i)} lacks proper signature/date",
                    source=f"Affidavit {aff1.get('id', i)}",
                    actors=[aff1.get('deponent', 'Unknown')]
                )
                
                contradictions.append(Contradiction(
                    event1=event,
                    event2=event,  # Self-reference for procedural issues
                    type="procedural",
                    severity="high",
                    explanation="Unsigned or undated affidavit undermines evidentiary value"
                ))
            
            # Compare with other affidavits
            for aff2 in affidavits[i+1:]:
                if aff1.get('deponent') == aff2.get('deponent'):
                    # Same deponent, check for inconsistencies
                    if self._affidavits_contradict(aff1, aff2):
                        event1 = TimelineEvent(
                            timestamp=aff1.get('date_signed', datetime.now()),
                            description=aff1.get('summary', ''),
                            source=f"Affidavit {aff1.get('id', i)}",
                            actors=[aff1.get('deponent', 'Unknown')]
                        )
                        event2 = TimelineEvent(
                            timestamp=aff2.get('date_signed', datetime.now()),
                            description=aff2.get('summary', ''),
                            source=f"Affidavit {aff2.get('id', i+1)}",
                            actors=[aff2.get('deponent', 'Unknown')]
                        )
                        
                        contradictions.append(Contradiction(
                            event1=event1,
                            event2=event2,
                            type="factual",
                            severity="high",
                            explanation="Same deponent provides contradictory statements"
                        ))
        
        return contradictions
    
    def generate_kable_argument(
        self,
        contradictions: List[Contradiction],
        case_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive Kable Principle argument from contradictions."""
        
        argument = {
            "principle": ConstitutionalPrinciple.KABLE.value,
            "case_citation": "Kable v Director of Public Prosecutions (NSW) (1996) 189 CLR 51",
            "thesis": self._generate_thesis(contradictions, case_context),
            "key_points": [],
            "supporting_evidence": [],
            "legal_framework": self._establish_legal_framework(),
            "application_to_facts": [],
            "remedies_sought": [],
            "conclusion": ""
        }
        
        # Analyze contradictions for Kable violations
        kable_violations = self._identify_kable_violations(contradictions, case_context)
        
        # Build key points
        for violation in kable_violations:
            argument["key_points"].append(self._create_key_point(violation))
        
        # Add supporting evidence
        argument["supporting_evidence"] = self._gather_supporting_evidence(
            contradictions, 
            kable_violations
        )
        
        # Apply law to facts
        argument["application_to_facts"] = self._apply_law_to_facts(
            kable_violations,
            case_context
        )
        
        # Determine appropriate remedies
        argument["remedies_sought"] = self._determine_remedies(kable_violations)
        
        # Generate conclusion
        argument["conclusion"] = self._generate_conclusion(argument)
        
        return argument
    
    def _generate_thesis(
        self, 
        contradictions: List[Contradiction],
        case_context: Dict[str, Any]
    ) -> str:
        """Generate the main thesis of the Kable argument."""
        high_severity_count = sum(1 for c in contradictions if c.severity == "high")
        
        if high_severity_count >= 3:
            return (
                "The proceedings demonstrate a fundamental breach of the Kable principle through "
                "systematic procedural irregularities and evidentiary contradictions that "
                "compromise the institutional integrity of the court and violate the separation "
                "of powers doctrine."
            )
        elif high_severity_count >= 1:
            return (
                "The identified contradictions and procedural deficiencies indicate a violation "
                "of the Kable principle by undermining the court's ability to exercise judicial "
                "power independently and impartially."
            )
        else:
            return (
                "The procedural irregularities present in this case raise concerns under the "
                "Kable principle regarding the proper exercise of judicial power."
            )
    
    def _identify_kable_violations(
        self,
        contradictions: List[Contradiction],
        case_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify specific Kable principle violations from contradictions."""
        violations = []
        
        # Check for institutional integrity issues
        procedural_contradictions = [c for c in contradictions if c.type == "procedural"]
        if len(procedural_contradictions) >= 2:
            violations.append({
                "element": "institutional_integrity",
                "description": "Multiple procedural irregularities undermine court's integrity",
                "evidence": procedural_contradictions,
                "severity": "high"
            })
        
        # Check for predetermined outcomes
        timeline_contradictions = [c for c in contradictions if c.type == "temporal"]
        if timeline_contradictions:
            violations.append({
                "element": "judicial_independence",
                "description": "Timeline impossibilities suggest predetermined narrative",
                "evidence": timeline_contradictions,
                "severity": "high"
            })
        
        # Check for separation of powers issues
        if case_context.get("executive_involvement"):
            violations.append({
                "element": "separation_of_powers",
                "description": "Executive interference in judicial proceedings",
                "evidence": [case_context["executive_involvement"]],
                "severity": "critical"
            })
        
        return violations
    
    def _establish_legal_framework(self) -> Dict[str, Any]:
        """Establish the legal framework for Kable arguments."""
        return {
            "primary_authority": {
                "case": "Kable v Director of Public Prosecutions (NSW)",
                "citation": "(1996) 189 CLR 51",
                "principles": [
                    "State courts exercising federal jurisdiction must maintain institutional integrity",
                    "Legislative cannot direct judicial outcomes",
                    "Courts must retain essential characteristics of judicial power"
                ]
            },
            "supporting_authorities": [
                {
                    "case": "Kirk v Industrial Court of NSW",
                    "citation": "(2010) 239 CLR 531",
                    "principle": "State Supreme Courts' supervisory jurisdiction cannot be removed"
                },
                {
                    "case": "South Australia v Totani",
                    "citation": "(2010) 242 CLR 1",
                    "principle": "Courts must retain discretion in decision-making"
                }
            ],
            "constitutional_provisions": [
                "Chapter III of the Constitution",
                "Section 71 - Judicial power of the Commonwealth",
                "Section 73 - Appellate jurisdiction"
            ]
        }
    
    def _create_key_point(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """Create a key argument point from a Kable violation."""
        element = violation["element"]
        element_info = self.kable_elements[element]
        
        return {
            "heading": f"Breach of {element_info['description']}",
            "argument": violation["description"],
            "legal_basis": element_info["description"],
            "factual_basis": [e.explanation for e in violation["evidence"][:3]],  # Top 3
            "significance": violation["severity"]
        }
    
    def _gather_supporting_evidence(
        self,
        contradictions: List[Contradiction],
        kable_violations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Gather supporting evidence for Kable argument."""
        evidence = []
        
        # Evidence from contradictions
        for contradiction in contradictions[:5]:  # Top 5 most relevant
            evidence.append({
                "type": "Timeline Contradiction",
                "description": contradiction.explanation,
                "source": f"{contradiction.event1.source} vs {contradiction.event2.source}",
                "relevance": "Demonstrates procedural irregularity"
            })
        
        # Evidence from violations
        for violation in kable_violations:
            evidence.append({
                "type": "Constitutional Violation",
                "description": violation["description"],
                "element": violation["element"],
                "relevance": "Direct breach of Kable principle"
            })
        
        return evidence
    
    def _apply_law_to_facts(
        self,
        kable_violations: List[Dict[str, Any]],
        case_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply Kable principle to the specific facts of the case."""
        applications = []
        
        for violation in kable_violations:
            element = violation["element"]
            
            if element == "institutional_integrity":
                applications.append({
                    "principle": "Courts must maintain public confidence",
                    "facts": violation["description"],
                    "analysis": (
                        "The procedural irregularities identified fundamentally undermine "
                        "public confidence in the judicial process, breaching the requirement "
                        "that courts maintain their institutional integrity."
                    ),
                    "conclusion": "The proceedings are constitutionally invalid"
                })
            
            elif element == "judicial_independence":
                applications.append({
                    "principle": "Courts must exercise independent judgment",
                    "facts": violation["description"],
                    "analysis": (
                        "The timeline contradictions and predetermined narrative remove the "
                        "court's ability to make independent findings of fact, violating the "
                        "essential characteristic of judicial power."
                    ),
                    "conclusion": "The court cannot properly exercise judicial power"
                })
            
            elif element == "separation_of_powers":
                applications.append({
                    "principle": "Judicial power must remain with the judiciary",
                    "facts": violation["description"],
                    "analysis": (
                        "Executive involvement in directing judicial outcomes breaches the "
                        "fundamental separation of powers required by Chapter III of the "
                        "Constitution."
                    ),
                    "conclusion": "The proceedings involve unconstitutional executive overreach"
                })
        
        return applications
    
    def _determine_remedies(self, kable_violations: List[Dict[str, Any]]) -> List[str]:
        """Determine appropriate remedies for Kable violations."""
        remedies = []
        
        # Always include stay/dismissal for Kable violations
        remedies.append("Permanent stay of proceedings due to constitutional invalidity")
        remedies.append("Declaration that the proceedings breach the Kable principle")
        
        # Specific remedies based on violations
        for violation in kable_violations:
            if violation["severity"] == "critical":
                remedies.append("Immediate release if in custody")
                remedies.append("Compensation for unlawful proceedings")
                break
        
        # Systemic remedies
        if len(kable_violations) >= 3:
            remedies.append("Referral to appropriate authorities for systemic investigation")
            remedies.append("Publication of reasons to prevent future violations")
        
        return remedies
    
    def _generate_conclusion(self, argument: Dict[str, Any]) -> str:
        """Generate a powerful conclusion for the Kable argument."""
        remedy_count = len(argument["remedies_sought"])
        violation_count = len(argument["key_points"])
        
        conclusion = (
            f"The {violation_count} identified breaches of the Kable principle demonstrate "
            f"that these proceedings are fundamentally incompatible with the exercise of "
            f"judicial power under Chapter III of the Constitution. The timeline contradictions, "
            f"procedural irregularities, and missing affidavit signatures reveal a systematic "
            f"failure to maintain the institutional integrity required of courts exercising "
            f"federal jurisdiction. "
        )
        
        conclusion += (
            f"\\n\\nThe Court must grant the {remedy_count} remedies sought to vindicate "
            f"the constitutional principles at stake and prevent further damage to the "
            f"integrity of the judicial system. To allow these proceedings to continue would "
            f"be to countenance a fundamental breach of the separation of powers and the "
            f"rule of law itself."
        )
        
        return conclusion
    
    def _locations_far_apart(self, location1: str, location2: str) -> bool:
        """Determine if two locations are far apart (simplified)."""
        # In a real implementation, this would use geocoding
        different_suburbs = location1.lower() != location2.lower()
        return different_suburbs
    
    def _events_describe_same_incident(
        self, 
        event1: TimelineEvent, 
        event2: TimelineEvent
    ) -> bool:
        """Determine if two events describe the same incident."""
        # Check time proximity (within 1 hour)
        time_diff = abs((event2.timestamp - event1.timestamp).total_seconds() / 3600)
        if time_diff > 1:
            return False
        
        # Check actor overlap
        common_actors = set(event1.actors) & set(event2.actors)
        if not common_actors:
            return False
        
        # Check location match
        if event1.location and event2.location:
            if event1.location == event2.location:
                return True
        
        return False
    
    def _descriptions_contradict(self, desc1: str, desc2: str) -> bool:
        """Check if two descriptions contradict each other (simplified)."""
        # In a real implementation, this would use NLP
        contradictory_pairs = [
            ("arrested", "free"),
            ("present", "absent"),
            ("guilty", "innocent"),
            ("confessed", "denied"),
            ("violent", "peaceful")
        ]
        
        desc1_lower = desc1.lower()
        desc2_lower = desc2.lower()
        
        for word1, word2 in contradictory_pairs:
            if (word1 in desc1_lower and word2 in desc2_lower) or \
               (word2 in desc1_lower and word1 in desc2_lower):
                return True
        
        return False
    
    def _affidavits_contradict(self, aff1: Dict[str, Any], aff2: Dict[str, Any]) -> bool:
        """Check if two affidavits from the same deponent contradict."""
        # Compare key assertions
        if aff1.get("summary") and aff2.get("summary"):
            return self._descriptions_contradict(
                aff1["summary"], 
                aff2["summary"]
            )
        return False


# Example usage
if __name__ == "__main__":
    generator = KablePrincipleArgumentGenerator()
    
    # Create sample timeline
    timeline = [
        TimelineEvent(
            timestamp=datetime(2023, 6, 1, 10, 0),
            description="Defendant arrested at home",
            source="Police Statement",
            actors=["Defendant", "Officer Smith"],
            location="123 Main St"
        ),
        TimelineEvent(
            timestamp=datetime(2023, 6, 1, 10, 0),
            description="Defendant seen at shopping center",
            source="Witness Statement",
            actors=["Defendant", "Witness Jones"],
            location="Westfield Mall"
        ),
        TimelineEvent(
            timestamp=datetime(2023, 6, 1, 14, 0),
            description="Confession obtained",
            source="Police Interview",
            actors=["Defendant", "Detective Brown"],
            location="Police Station"
        )
    ]
    
    # Sample affidavits with issues
    affidavits = [
        {
            "id": "AFF001",
            "deponent": "Officer Smith",
            "summary": "Defendant violently resisted arrest",
            "signature": None,  # Missing signature!
            "date_signed": None
        },
        {
            "id": "AFF002",
            "deponent": "Officer Smith",
            "summary": "Defendant cooperated fully with arrest",
            "signature": "J Smith",
            "date_signed": datetime(2023, 6, 2)
        }
    ]
    
    # Analyze contradictions
    contradictions = generator.analyze_timeline_contradictions(timeline, affidavits)
    
    # Generate Kable argument
    case_context = {
        "case_name": "R v Defendant",
        "jurisdiction": "NSW",
        "executive_involvement": "Minister directed prosecution priorities"
    }
    
    argument = generator.generate_kable_argument(contradictions, case_context)
    
    print(json.dumps(argument, indent=2, default=str))
'''
        
        # Save the code
        output_path = Path(__file__).parent.parent / "lib" / "constitutional_argument_generator.py"
        output_path.write_text(code)
        
        return {
            "status": "success",
            "file_created": str(output_path),
            "description": "Kable Principle argument generator with timeline analysis",
            "features": [
                "Timeline contradiction detection",
                "Affidavit signature verification",
                "Kable principle violation identification",
                "Structured constitutional argument generation",
                "Remedy determination",
                "Supporting case law integration"
            ]
        }
    
    async def create_custom_tool(self, task_description: str) -> Dict[str, Any]:
        """Create a custom tool based on task description."""
        # This would use AI to generate appropriate code based on description
        return {
            "status": "pending",
            "description": "Custom tool generation requires additional context",
            "next_steps": [
                "Provide more specific requirements",
                "Specify input/output formats",
                "Define legal frameworks to incorporate"
            ]
        }


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Claude Opus 4 Task Runner")
    
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="Task description for Claude to execute"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="./output",
        help="Output directory for generated code"
    )
    
    args = parser.parse_args()
    
    # Create tasker instance
    tasker = ClaudeOpusTasker()
    
    # Execute task
    result = await tasker.execute_task(args.task)
    
    # Print result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())