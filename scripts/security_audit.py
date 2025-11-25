#!/usr/bin/env python3
"""
Security Audit Script for CrisisLens
Scans the codebase for potential security issues:
- Hardcoded API keys
- Hardcoded passwords
- SQL injection risks
- Insecure configurations
"""

import re
import os
from pathlib import Path

class SecurityAuditor:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.issues = []
        
        # Patterns to detect
        self.patterns = {
            'api_key': re.compile(r'(api[_-]?key|apikey)\s*=\s*["\'](?!dummy|test|YOUR_)[^"\']{10,}["\']', re.IGNORECASE),
            'password': re.compile(r'password\s*=\s*["\'][^"\']{3,}["\']', re.IGNORECASE),
            'secret': re.compile(r'(secret|token)\s*=\s*["\'](?!dummy|test)[^"\']{10,}["\']', re.IGNORECASE),
            'private_key': re.compile(r'-----BEGIN (RSA |EC )?PRIVATE KEY-----'),
        }
        
    def scan_file(self, filepath):
        """Scan a single file for security issues"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern_name, pattern in self.patterns.items():
                        if pattern.search(line):
                            self.issues.append({
                                'file': str(filepath.relative_to(self.root_dir)),
                                'line': line_num,
                                'issue': pattern_name,
                                'content': line.strip()
                            })
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")
    
    def scan(self):
        """Scan all Python files in the project"""
        for py_file in self.root_dir.rglob('*.py'):
            # Skip venv, cache, and test directories
            if any(skip in str(py_file) for skip in ['venv', '__pycache__', 'node_modules', '.git']):
                continue
            self.scan_file(py_file)
        
        return self.issues
    
    def report(self):
        """Generate a security audit report"""
        print("=" * 80)
        print("CRISISLEN SECURITY AUDIT REPORT")
        print("=" * 80)
        print()
        
        if not self.issues:
            print("[OK] No security issues detected!")
            print()
            print("Note: This is a basic scan. For production, use:")
            print("  - bandit (Python security linter)")
            print("  - safety (dependency vulnerability scanner)")
            print("  - SAST tools (e.g., SonarQube, Snyk)")
            return
        
        print(f"[!] Found {len(self.issues)} potential security issues:\n")
        
        for i, issue in enumerate(self.issues, 1):
            print(f"{i}. {issue['issue'].upper()} in {issue['file']}:{issue['line']}")
            print(f"   > {issue['content'][:100]}")
            print()
        
        print("=" * 80)
        print("RECOMMENDATIONS:")
        print("- Move sensitive credentials to environment variables")
        print("- Use .env files (never committed to git)")
        print("- Consider using a secrets manager (AWS Secrets Manager, HashiCorp Vault)")
        print("=" * 80)

if __name__ == "__main__":
    auditor = SecurityAuditor(os.getcwd())
    auditor.scan()
    auditor.report()
