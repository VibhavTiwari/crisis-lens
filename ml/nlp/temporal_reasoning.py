from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
from dateutil import parser
from services.observability import observability_service

class TemporalReasoner:
    """
    Temporal reasoning and event timeline extraction
    
    Extracts dates, times, and temporal relationships from text
    """
    
    # Temporal patterns
    RELATIVE_TIME_PATTERNS = {
        'today': 0,
        'yesterday': -1,
        'tomorrow': 1,
        'last week': -7,
        'next week': 7,
        'last month': -30,
        'next month': 30
    }
    
    def extract_temporal_expressions(self, text: str, reference_date: datetime = None) -> List[Dict[str, Any]]:
        """
        Extract temporal expressions from text
        
        Args:
            text: Input text
            reference_date: Reference date for relative expressions
            
        Returns:
            List of temporal expressions with normalized dates
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        expressions = []
        
        # Pattern 1: Explicit dates (YYYY-MM-DD, DD/MM/YYYY, etc.)
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # 2024-01-15
            r'\d{1,2}/\d{1,2}/\d{4}',  # 15/01/2024
            r'\d{1,2}-\d{1,2}-\d{4}',  # 15-01-2024
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                try:
                    date = parser.parse(match.group())
                    expressions.append({
                        'text': match.group(),
                        'type': 'absolute',
                        'datetime': date,
                        'position': match.start()
                    })
                except:
                    pass
        
        # Pattern 2: Relative time expressions
        text_lower = text.lower()
        for phrase, days_offset in self.RELATIVE_TIME_PATTERNS.items():
            if phrase in text_lower:
                date = reference_date + timedelta(days=days_offset)
                expressions.append({
                    'text': phrase,
                    'type': 'relative',
                    'datetime': date,
                    'position': text_lower.find(phrase)
                })
        
        # Pattern 3: Time of day
        time_pattern = r'\d{1,2}:\d{2}(?:\s?(?:AM|PM|am|pm))?'
        for match in re.finditer(time_pattern, text):
            expressions.append({
                'text': match.group(),
                'type': 'time',
                'position': match.start()
            })
        
        # Sort by position
        expressions.sort(key=lambda x: x['position'])
        
        return expressions
    
    def build_timeline(self, texts: List[str], timestamps: List[datetime] = None) -> List[Dict[str, Any]]:
        """
        Build a timeline from multiple texts
        
        Args:
            texts: List of text documents
            timestamps: Creation timestamps for each text
            
        Returns:
            Sorted timeline of events
        """
        timeline = []
        
        for i, text in enumerate(texts):
            ref_date = timestamps[i] if timestamps and i < len(timestamps) else datetime.now()
            
            # Extract temporal expressions
            expressions = self.extract_temporal_expressions(text, ref_date)
            
            for expr in expressions:
                timeline.append({
                    'source_index': i,
                    'source_text': text[:100],  # First 100 chars
                    'expression': expr['text'],
                    'datetime': expr.get('datetime', ref_date),
                    'type': expr['type']
                })
        
        # Sort by datetime
        timeline.sort(key=lambda x: x['datetime'])
        
        return timeline
    
    def find_temporal_relations(self, text: str) -> List[Dict[str, Any]]:
        """
        Find temporal relations between events
        
        Returns:
            List of temporal relations (before, after, during, etc.)
        """
        relations = []
        
        # Temporal connectives
        connectives = {
            'before': 'BEFORE',
            'after': 'AFTER',
            'during': 'DURING',
            'while': 'DURING',
            'since': 'SINCE',
            'until': 'UNTIL',
            'when': 'WHEN'
        }
        
        text_lower = text.lower()
        for word, relation_type in connectives.items():
            if word in text_lower:
                pos = text_lower.find(word)
                relations.append({
                    'connective': word,
                    'type': relation_type,
                    'position': pos
                })
        
        return relations
    
    def normalize_to_absolute(self, temporal_expr: str, reference_date: datetime = None) -> Optional[datetime]:
        """
        Normalize a temporal expression to absolute datetime
        
        Args:
            temporal_expr: Temporal expression (e.g., "yesterday", "last week")
            reference_date: Reference date
            
        Returns:
            Normalized datetime or None
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        expr_lower = temporal_expr.lower().strip()
        
        # Check relative patterns
        if expr_lower in self.RELATIVE_TIME_PATTERNS:
            days_offset = self.RELATIVE_TIME_PATTERNS[expr_lower]
            return reference_date + timedelta(days=days_offset)
        
        # Try parsing as absolute date
        try:
            return parser.parse(temporal_expr)
        except:
            return None
    
    def compute_duration(self, start_time: datetime, end_time: datetime) -> Dict[str,Any]:
        """Compute duration between two times"""
        duration = end_time - start_time
        
        return {
            'seconds': duration.total_seconds(),
            'minutes': duration.total_seconds() / 60,
            'hours': duration.total_seconds() / 3600,
            'days': duration.days,
            'human_readable': str(duration)
        }

# Singleton
temporal_reasoner = TemporalReasoner()
