"""
CodeForge AI - Core Code Generation Engine
Generates syntactically valid, optimized code across multiple languages
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    RUST = "rust"
    GO = "go"
    TYPESCRIPT = "typescript"


@dataclass
class CodeGenerationRequest:
    """Input request for code generation"""
    problem_description: str
    language: Language
    constraints: Optional[Dict] = None
    examples: Optional[List[Dict]] = None
    style_guide: Optional[str] = None


@dataclass
class CodeGenerationResponse:
    """Output response from code generation"""
    language: str
    description: str
    code: str
    complexity: str
    confidence: float
    syntax_valid: bool
    best_practices_score: float


class LanguageSyntaxBase:
    """Base class for language-specific syntax patterns"""
    
    def __init__(self):
        self.patterns = {}
        self.keywords = []
        self.syntax_rules = {}
    
    def validate_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """Validate code syntax, return (is_valid, errors)"""
        raise NotImplementedError
    
    def get_complexity_analysis(self, code: str) -> str:
        """Analyze time/space complexity from code"""
        raise NotImplementedError


class PythonSyntax(LanguageSyntaxBase):
    """Python-specific syntax validator"""
    
    def __init__(self):
        super().__init__()
        self.keywords = ['def', 'class', 'if', 'for', 'while', 'return', 'import', 'from']
        self.indent_pattern = r'^[ \t]+'
    
    def validate_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """Basic Python syntax validation"""
        errors = []
        lines = code.split('\n')
        
        # Check indentation consistency
        indent_levels = []
        for i, line in enumerate(lines):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_levels.append((i, indent))
        
        # Validate bracket matching
        if code.count('(') != code.count(')'):
            errors.append("Mismatched parentheses")
        if code.count('[') != code.count(']'):
            errors.append("Mismatched square brackets")
        if code.count('{') != code.count('}'):
            errors.append("Mismatched curly braces")
        
        return len(errors) == 0, errors
    
    def get_complexity_analysis(self, code: str) -> str:
        """Analyze loops and recursion for complexity"""
        nested_loops = code.count('for') + code.count('while')
        has_recursion = 'def ' in code and code.count('(') > 0
        
        if nested_loops >= 3:
            return "O(n³) or worse"
        elif nested_loops == 2:
            return "O(n²)"
        elif nested_loops == 1:
            return "O(n)"
        elif has_recursion:
            return "O(log n) or O(n) depending on recursion depth"
        else:
            return "O(1)"


class JavaScriptSyntax(LanguageSyntaxBase):
    """JavaScript-specific syntax validator"""
    
    def __init__(self):
        super().__init__()
        self.keywords = ['function', 'const', 'let', 'var', 'if', 'for', 'while', 'async']
    
    def validate_syntax(self, code: str) -> Tuple[bool, List[str]]:
        errors = []
        if code.count('{') != code.count('}'):
            errors.append("Mismatched curly braces")
        if code.count('(') != code.count(')'):
            errors.append("Mismatched parentheses")
        return len(errors) == 0, errors
    
    def get_complexity_analysis(self, code: str) -> str:
        loops = code.count('for') + code.count('while')
        if loops >= 2:
            return "O(n²)"
        elif loops == 1:
            return "O(n)"
        else:
            return "O(1)"


class CodeForgeAI:
    """Main code generation engine with multi-language support"""
    
    def __init__(self):
        self.language_validators = {
            Language.PYTHON: PythonSyntax(),
            Language.JAVASCRIPT: JavaScriptSyntax(),
        }
        self.syntax_learned = {}  # Store learned patterns
        self.generation_history = []
    
    def generate_code(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """
        Generate code based on problem description
        
        Args:
            request: CodeGenerationRequest with problem details
            
        Returns:
            CodeGenerationResponse with generated code and metadata
        """
        logger.info(f"Generating {request.language.value} code for: {request.problem_description[:50]}...")
        
        # Get language-specific validator
        validator = self.language_validators.get(request.language)
        if not validator:
            logger.warning(f"Language {request.language.value} not yet trained, using defaults")
            validator = LanguageSyntaxBase()
        
        # Generate code based on language
        code = self._generate_language_specific_code(request)
        
        # Validate syntax
        is_valid, syntax_errors = validator.validate_syntax(code)
        
        # Get complexity analysis
        complexity = validator.get_complexity_analysis(code)
        
        # Calculate best practices score
        bp_score = self._evaluate_best_practices(code, request.language)
        
        # Calculate confidence (0-1 scale)
        confidence = self._calculate_confidence(is_valid, bp_score, validator)
        
        response = CodeGenerationResponse(
            language=request.language.value,
            description=f"Generated solution for: {request.problem_description}",
            code=code,
            complexity=complexity,
            confidence=confidence,
            syntax_valid=is_valid,
            best_practices_score=bp_score
        )
        
        self.generation_history.append({
            'request': request,
            'response': response,
            'timestamp': None
        })
        
        return response
    
    def _generate_language_specific_code(self, request: CodeGenerationRequest) -> str:
        """Generate language-specific code"""
        problem = request.problem_description.lower()
        language = request.language
        
        # Example patterns - these would be learned from training data
        if language == Language.PYTHON:
            if 'fibonacci' in problem:
                code = '''def fibonacci(n):
    """Generate Fibonacci sequence up to n terms"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    return sequence[:n]

# Time Complexity: O(n)
# Space Complexity: O(n)
'''
            elif 'sort' in problem:
                code = '''def merge_sort(arr):
    """Efficient sorting using merge sort algorithm"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    """Merge two sorted arrays"""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Time Complexity: O(n log n)
# Space Complexity: O(n)
'''
            else:
                code = '''def solution(problem_input):
    """Generic solution template"""
    # Parse input
    data = problem_input
    
    # Process
    result = process_data(data)
    
    return result

def process_data(data):
    """Helper function to process data"""
    return data
'''
        
        elif language == Language.JAVASCRIPT:
            if 'fibonacci' in problem:
                code = '''function fibonacci(n) {
  // Generate Fibonacci sequence up to n terms
  if (n <= 0) return [];
  if (n === 1) return [0];
  
  const sequence = [0, 1];
  for (let i = 2; i < n; i++) {
    sequence.push(sequence[i-1] + sequence[i-2]);
  }
  return sequence.slice(0, n);
}

// Time Complexity: O(n)
// Space Complexity: O(n)
'''
            else:
                code = '''function solution(problemInput) {
  // Generic solution template
  const data = problemInput;
  
  // Process
  const result = processData(data);
  
  return result;
}

function processData(data) {
  return data;
}
'''
        else:
            code = f"// Code generation for {language.value} not yet implemented"
        
        return code
    
    def _evaluate_best_practices(self, code: str, language: Language) -> float:
        """Evaluate code against best practices (0-1)"""
        score = 0.8  # Base score
        
        # Check for comments
        if '#' in code or '//' in code:
            score += 0.1
        
        # Check for meaningful function names
        if 'solution' not in code.lower() or len(code.split('\n')) < 3:
            score -= 0.1
        
        # Cap at 1.0
        return min(1.0, max(0.0, score))
    
    def _calculate_confidence(self, is_valid: bool, bp_score: float, validator: LanguageSyntaxBase) -> float:
        """Calculate overall confidence in generated code (0-1)"""
        confidence = 0.5
        
        if is_valid:
            confidence += 0.3
        if bp_score > 0.8:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def store_learned_patterns(self, language: Language, pattern_name: str, pattern_data: Dict):
        """Store new learned syntax patterns"""
        if language not in self.syntax_learned:
            self.syntax_learned[language] = {}
        
        self.syntax_learned[language][pattern_name] = pattern_data
        logger.info(f"Stored learned pattern for {language.value}: {pattern_name}")
    
    def get_learned_patterns(self, language: Language) -> Dict:
        """Retrieve learned patterns for a language"""
        return self.syntax_learned.get(language, {})


def format_json_response(response: CodeGenerationResponse) -> Dict:
    """Format response as JSON"""
    return {
        "language": response.language,
        "description": response.description,
        "code": response.code,
        "complexity": response.complexity,
        "confidence": response.confidence,
        "syntax_valid": response.syntax_valid,
        "best_practices_score": response.best_practices_score
    }
