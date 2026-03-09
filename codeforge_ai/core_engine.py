"""
CodeForge AI - Core Code Generation Engine
Generates syntactically valid, optimized code across multiple languages
"""

from enum import Enum
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Different model types for code generation"""
    PATTERN_BASED = "pattern_based"
    TEMPLATE_BASED = "template_based"
    OPTIMIZATION_FOCUSED = "optimization_focused"
    READABILITY_FOCUSED = "readability_focused"
    PERFORMANCE_FOCUSED = "performance_focused"


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
    model_type: ModelType = ModelType.PATTERN_BASED
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
    """Main code generation engine with multi-language and multi-model support"""
    
    def __init__(self):
        self.language_validators = {
            Language.PYTHON: PythonSyntax(),
            Language.JAVASCRIPT: JavaScriptSyntax(),
        }
        self.syntax_learned = {}  # Store learned patterns
        self.generation_history = []
        self.models_path = Path("models")
        self.models_path.mkdir(exist_ok=True)
        
        # Initialize different model types
        self.models = {
            ModelType.PATTERN_BASED: self._generate_pattern_based,
            ModelType.TEMPLATE_BASED: self._generate_template_based,
            ModelType.OPTIMIZATION_FOCUSED: self._generate_optimization_focused,
            ModelType.READABILITY_FOCUSED: self._generate_readability_focused,
            ModelType.PERFORMANCE_FOCUSED: self._generate_performance_focused,
        }
        
        # Initialize data manager
        self.data_manager = DataManager()
    
    def generate_code(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """
        Generate code based on problem description using selected model
        
        Args:
            request: CodeGenerationRequest with problem details and model type
            
        Returns:
            CodeGenerationResponse with generated code and metadata
        """
        logger.info(f"Generating {request.language.value} code using {request.model_type.value} model for: {request.problem_description[:50]}...")
        
        # Get language-specific validator
        validator = self.language_validators.get(request.language)
        if not validator:
            logger.warning(f"Language {request.language.value} not yet trained, using defaults")
            validator = LanguageSyntaxBase()
        
        # Generate code using selected model
        model_generator = self.models.get(request.model_type, self._generate_pattern_based)
        code = model_generator(request)
        
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
            description=f"Generated solution using {request.model_type.value} model for: {request.problem_description}",
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
        
        # Store generation data for learning
        self._store_generation_data(request, response)
        
        return response
    
    def _store_generation_data(self, request: CodeGenerationRequest, response: CodeGenerationResponse):
        """Store generation data for learning and analysis"""
        generation_data = {
            'problem_description': request.problem_description,
            'language': request.language.value,
            'model_type': request.model_type.value,
            'generated_code': response.code,
            'complexity': response.complexity,
            'confidence': response.confidence,
            'syntax_valid': response.syntax_valid,
            'best_practices_score': response.best_practices_score,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add constraints and examples if available
        if request.constraints:
            generation_data['constraints'] = request.constraints
        if request.examples:
            generation_data['examples'] = request.examples
        
        # Store in data manager for categorization
        self.data_manager.categorize_feedback(generation_data)
    
    def get_similar_problems(self, problem_description: str, limit: int = 5) -> List[Dict]:
        """Find similar problems using data manager"""
        return self.data_manager.find_similar_problems(problem_description, limit)
    
    def get_data_statistics(self) -> Dict:
        """Get statistics about stored training data"""
        return self.data_manager.get_statistics()
    
    def get_recommendations(self, criteria: Dict) -> List[Dict]:
        """Get recommendations based on criteria"""
        return self.data_manager.get_recommendations(criteria)
    
    def _generate_pattern_based(self, request: CodeGenerationRequest) -> str:
        """Generate code using pattern-based approach (original method)"""
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
    
    def _generate_template_based(self, request: CodeGenerationRequest) -> str:
        """Generate code using template-based approach with reusable components"""
        problem = request.problem_description.lower()
        language = request.language
        
        if language == Language.PYTHON:
            if 'fibonacci' in problem:
                code = '''def fibonacci_sequence(n: int) -> list[int]:
    """
    Generate Fibonacci sequence up to n terms using iterative approach.
    
    Args:
        n: Number of terms to generate
        
    Returns:
        List of Fibonacci numbers
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    sequence = [0, 1]
    a, b = 0, 1
    for _ in range(2, n):
        a, b = b, a + b
        sequence.append(b)
    
    return sequence

# Example usage:
# fib_nums = fibonacci_sequence(10)
# print(fib_nums)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
'''
            elif 'sort' in problem:
                code = '''def quicksort(arr: list) -> list:
    """
    Sort array using quicksort algorithm.
    
    Args:
        arr: List to sort
        
    Returns:
        Sorted list
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

def merge_sort(arr: list) -> list:
    """
    Sort array using merge sort algorithm.
    
    Args:
        arr: List to sort
        
    Returns:
        Sorted list
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left_half = merge_sort(arr[:mid])
    right_half = merge_sort(arr[mid:])
    
    return _merge(left_half, right_half)

def _merge(left: list, right: list) -> list:
    """Merge two sorted lists"""
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
'''
            else:
                code = '''def solve_problem(input_data):
    """
    Generic problem solver template.
    
    Args:
        input_data: Problem input data
        
    Returns:
        Processed result
    """
    # Input validation
    if not input_data:
        return None
    
    # Process the data
    result = process_input(input_data)
    
    # Return formatted result
    return format_output(result)

def process_input(data):
    """
    Process input data according to problem requirements.
    
    Args:
        data: Input data to process
        
    Returns:
        Processed data
    """
    # Implementation depends on specific problem
    return data

def format_output(result):
    """
    Format the result for output.
    
    Args:
        result: Processing result
        
    Returns:
        Formatted output
    """
    return result
'''
        
        elif language == Language.JAVASCRIPT:
            if 'fibonacci' in problem:
                code = '''/**
 * Generate Fibonacci sequence up to n terms
 * @param {number} n - Number of terms to generate
 * @returns {number[]} Array of Fibonacci numbers
 */
function fibonacciSequence(n) {
  if (n <= 0) return [];
  if (n === 1) return [0];
  
  const sequence = [0, 1];
  let a = 0, b = 1;
  
  for (let i = 2; i < n; i++) {
    [a, b] = [b, a + b];
    sequence.push(b);
  }
  
  return sequence;
}

// Example usage:
// const fibNums = fibonacciSequence(10);
// console.log(fibNums); // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
'''
            else:
                code = '''/**
 * Generic problem solver
 * @param {*} inputData - Problem input data
 * @returns {*} Processed result
 */
function solveProblem(inputData) {
  // Input validation
  if (!inputData) {
    return null;
  }
  
  // Process the data
  const result = processInput(inputData);
  
  // Return formatted result
  return formatOutput(result);
}

/**
 * Process input data
 * @param {*} data - Input data to process
 * @returns {*} Processed data
 */
function processInput(data) {
  // Implementation depends on specific problem
  return data;
}

/**
 * Format result for output
 * @param {*} result - Processing result
 * @returns {*} Formatted output
 */
function formatOutput(result) {
  return result;
}
'''
        else:
            code = f"// Template-based code generation for {language.value} not yet implemented"
        
        return code
    
    def _generate_optimization_focused(self, request: CodeGenerationRequest) -> str:
        """Generate code focused on performance optimization"""
        problem = request.problem_description.lower()
        language = request.language
        
        if language == Language.PYTHON:
            if 'fibonacci' in problem:
                code = '''def fibonacci_optimized(n: int) -> list[int]:
    """
    Generate Fibonacci sequence with optimized space complexity.
    
    Time: O(n), Space: O(n) - necessary for storing sequence
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    return sequence

def fibonacci_iterative(n: int) -> int:
    """
    Get nth Fibonacci number with O(1) space (excluding recursion stack).
    
    Time: O(n), Space: O(1)
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# For large n, consider matrix exponentiation for O(log n) time
'''
            elif 'sort' in problem:
                code = '''def timsort_optimized(arr: list) -> list:
    """
    Timsort - Python's built-in sorting algorithm.
    Highly optimized for real-world data.
    
    Time: O(n log n) average/worst case
    Space: O(n)
    """
    return sorted(arr)

def quicksort_inplace(arr: list, low: int = 0, high: int = None) -> None:
    """
    In-place quicksort with optimized pivot selection.
    
    Time: O(n log n) average, O(n²) worst case
    Space: O(log n) due to recursion
    """
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # Optimized pivot selection (median of three)
        mid = (low + high) // 2
        pivot_candidates = [(arr[low], low), (arr[mid], mid), (arr[high], high)]
        pivot_candidates.sort()
        pivot_idx = pivot_candidates[1][1]  # median
        
        # Swap pivot to end
        arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
        pivot = arr[high]
        
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        pi = i + 1
        
        quicksort_inplace(arr, low, pi - 1)
        quicksort_inplace(arr, pi + 1, high)
'''
            else:
                code = '''def optimized_solution(input_data):
    """
    Optimized solution with focus on performance.
    
    Key optimizations:
    - Early termination conditions
    - Efficient data structures
    - Minimal memory allocations
    """
    if not input_data:
        return None
    
    # Pre-allocate result if possible
    result_size = estimate_result_size(input_data)
    result = [None] * result_size if result_size > 0 else []
    
    # Process in chunks for memory efficiency
    chunk_size = 1000
    for i in range(0, len(input_data), chunk_size):
        chunk = input_data[i:i + chunk_size]
        process_chunk_optimized(chunk, result, i)
    
    return result

def estimate_result_size(data) -> int:
    """Estimate result size to pre-allocate memory"""
    return len(data)  # Adjust based on problem

def process_chunk_optimized(chunk, result, offset):
    """Process data chunk with optimizations"""
    for i, item in enumerate(chunk):
        result[offset + i] = process_item(item)

def process_item(item):
    """Process individual item efficiently"""
    return item  # Implementation depends on problem
'''
        
        elif language == Language.JAVASCRIPT:
            if 'fibonacci' in problem:
                code = '''/**
 * Optimized Fibonacci sequence generation
 * Time: O(n), Space: O(n) for sequence, O(1) for single number
 */
function fibonacciOptimized(n) {
  if (n <= 0) return [];
  if (n === 1) return [0];
  
  const sequence = new Array(n);
  sequence[0] = 0;
  sequence[1] = 1;
  
  for (let i = 2; i < n; i++) {
    sequence[i] = sequence[i-1] + sequence[i-2];
  }
  
  return sequence;
}

function fibonacciNth(n) {
  if (n <= 0) return 0;
  if (n === 1) return 1;
  
  let a = 0, b = 1;
  for (let i = 2; i <= n; i++) {
    [a, b] = [b, a + b];
  }
  return b;
}

// For very large n, consider memoization or matrix exponentiation
'''
            else:
                code = '''/**
 * Performance-optimized solution
 */
function optimizedSolution(inputData) {
  if (!inputData) return null;
  
  // Pre-allocate result array if size is known
  const resultSize = estimateResultSize(inputData);
  const result = resultSize > 0 ? new Array(resultSize) : [];
  
  // Process in chunks to avoid memory spikes
  const chunkSize = 1000;
  for (let i = 0; i < inputData.length; i += chunkSize) {
    const chunk = inputData.slice(i, i + chunkSize);
    processChunkOptimized(chunk, result, i);
  }
  
  return result;
}

function estimateResultSize(data) {
  return data.length; // Adjust based on problem
}

function processChunkOptimized(chunk, result, offset) {
  for (let i = 0; i < chunk.length; i++) {
    result[offset + i] = processItem(chunk[i]);
  }
}

function processItem(item) {
  return item; // Implementation depends on problem
}
'''
        else:
            code = f"// Optimization-focused code generation for {language.value} not yet implemented"
        
        return code
    
    def _generate_readability_focused(self, request: CodeGenerationRequest) -> str:
        """Generate code focused on readability and maintainability"""
        problem = request.problem_description.lower()
        language = request.language
        
        if language == Language.PYTHON:
            if 'fibonacci' in problem:
                code = '''def generate_fibonacci_sequence(number_of_terms):
    """
    Create a Fibonacci sequence with the specified number of terms.
    
    This function generates the famous Fibonacci sequence where each number
    is the sum of the two preceding ones. The sequence starts with 0 and 1.
    
    Parameters:
    -----------
    number_of_terms : int
        The number of Fibonacci numbers to generate.
        Must be a positive integer.
    
    Returns:
    --------
    list
        A list containing the Fibonacci sequence.
        Returns empty list if number_of_terms <= 0.
    
    Examples:
    ---------
    >>> generate_fibonacci_sequence(5)
    [0, 1, 1, 2, 3]
    
    >>> generate_fibonacci_sequence(1)
    [0]
    """
    # Handle edge cases
    if number_of_terms <= 0:
        return []
    
    if number_of_terms == 1:
        return [0]
    
    # Initialize the sequence with the first two numbers
    fibonacci_sequence = [0, 1]
    
    # Generate the remaining terms
    for current_index in range(2, number_of_terms):
        # Calculate the next number by adding the last two numbers
        next_number = (fibonacci_sequence[current_index - 1] + 
                      fibonacci_sequence[current_index - 2])
        fibonacci_sequence.append(next_number)
    
    return fibonacci_sequence


# Usage example:
# fibonacci_numbers = generate_fibonacci_sequence(10)
# print("First 10 Fibonacci numbers:", fibonacci_numbers)
'''
            else:
                code = '''def solve_problem(input_data):
    """
    Solve the given problem with clear, readable code.
    
    This function provides a clean and understandable solution
    to the problem described in the input data.
    
    Parameters:
    -----------
    input_data : any
        The input data containing problem specifications.
        The exact format depends on the specific problem.
    
    Returns:
    --------
    any
        The solution to the problem.
        Return type varies based on the problem requirements.
    
    Raises:
    -------
    ValueError
        If the input data is invalid or cannot be processed.
    """
    # Step 1: Validate input data
    if not input_data:
        raise ValueError("Input data cannot be empty")
    
    # Step 2: Parse and understand the problem
    problem_description = extract_problem_description(input_data)
    
    # Step 3: Choose appropriate solution strategy
    solution_strategy = determine_solution_strategy(problem_description)
    
    # Step 4: Apply the solution
    result = apply_solution_strategy(input_data, solution_strategy)
    
    # Step 5: Validate and format the result
    validated_result = validate_and_format_result(result)
    
    return validated_result


def extract_problem_description(data):
    """
    Extract the problem description from input data.
    
    Parameters:
    -----------
    data : any
        The input data containing problem information.
    
    Returns:
    --------
    str
        A clear description of the problem to solve.
    """
    # Implementation depends on input data format
    return str(data)


def determine_solution_strategy(description):
    """
    Determine the best strategy to solve the problem.
    
    Parameters:
    -----------
    description : str
        Description of the problem to solve.
    
    Returns:
    --------
    str
        The name of the solution strategy to use.
    """
    # Simple strategy selection logic
    if "sort" in description.lower():
        return "sorting_algorithm"
    elif "search" in description.lower():
        return "search_algorithm"
    else:
        return "general_algorithm"


def apply_solution_strategy(data, strategy):
    """
    Apply the chosen solution strategy to the data.
    
    Parameters:
    -----------
    data : any
        The input data to process.
    strategy : str
        The solution strategy to apply.
    
    Returns:
    --------
    any
        The result of applying the strategy.
    """
    # Implementation depends on the strategy
    return data


def validate_and_format_result(result):
    """
    Validate the result and format it appropriately.
    
    Parameters:
    -----------
    result : any
        The raw result from solution application.
    
    Returns:
    --------
    any
        The validated and formatted result.
    """
    # Basic validation
    if result is None:
        raise ValueError("Solution produced no result")
    
    return result
'''
        
        elif language == Language.JAVASCRIPT:
            if 'fibonacci' in problem:
                code = '''/**
 * Generate a Fibonacci sequence with clear, readable code.
 * 
 * This function creates the famous Fibonacci sequence where each number
 * is the sum of the two preceding ones. The sequence starts with 0 and 1.
 * 
 * @param {number} numberOfTerms - The number of Fibonacci numbers to generate
 * @returns {number[]} An array containing the Fibonacci sequence
 * @throws {Error} If numberOfTerms is not a positive integer
 * 
 * @example
 * // Generate first 5 Fibonacci numbers
 * const fibonacciNumbers = generateFibonacciSequence(5);
 * console.log(fibonacciNumbers); // [0, 1, 1, 2, 3]
 * 
 * @example
 * // Generate first Fibonacci number
 * const firstNumber = generateFibonacciSequence(1);
 * console.log(firstNumber); // [0]
 */
function generateFibonacciSequence(numberOfTerms) {
  // Validate input
  if (!Number.isInteger(numberOfTerms) || numberOfTerms < 0) {
    throw new Error("numberOfTerms must be a non-negative integer");
  }
  
  // Handle edge cases
  if (numberOfTerms === 0) {
    return [];
  }
  
  if (numberOfTerms === 1) {
    return [0];
  }
  
  // Initialize the sequence with the first two numbers
  const fibonacciSequence = [0, 1];
  
  // Generate the remaining terms
  for (let currentIndex = 2; currentIndex < numberOfTerms; currentIndex++) {
    // Calculate the next number by adding the last two numbers
    const nextNumber = fibonacciSequence[currentIndex - 1] + 
                      fibonacciSequence[currentIndex - 2];
    fibonacciSequence.push(nextNumber);
  }
  
  return fibonacciSequence;
}

// Usage example:
// const fibonacciNumbers = generateFibonacciSequence(10);
// console.log("First 10 Fibonacci numbers:", fibonacciNumbers);
'''
            else:
                code = '''/**
 * Solve the given problem with clear, readable code.
 * 
 * This function provides a clean and understandable solution
 * to the problem described in the input data.
 * 
 * @param {*} inputData - The input data containing problem specifications
 * @returns {*} The solution to the problem
 * @throws {Error} If the input data is invalid
 * 
 * @example
 * const result = solveProblem(inputData);
 * console.log("Solution:", result);
 */
function solveProblem(inputData) {
  // Step 1: Validate input data
  if (!inputData) {
    throw new Error("Input data cannot be empty");
  }
  
  // Step 2: Parse and understand the problem
  const problemDescription = extractProblemDescription(inputData);
  
  // Step 3: Choose appropriate solution strategy
  const solutionStrategy = determineSolutionStrategy(problemDescription);
  
  // Step 4: Apply the solution
  const result = applySolutionStrategy(inputData, solutionStrategy);
  
  // Step 5: Validate and format the result
  const validatedResult = validateAndFormatResult(result);
  
  return validatedResult;
}

/**
 * Extract the problem description from input data.
 * 
 * @param {*} data - The input data containing problem information
 * @returns {string} A clear description of the problem to solve
 */
function extractProblemDescription(data) {
  // Implementation depends on input data format
  return String(data);
}

/**
 * Determine the best strategy to solve the problem.
 * 
 * @param {string} description - Description of the problem to solve
 * @returns {string} The name of the solution strategy to use
 */
function determineSolutionStrategy(description) {
  // Simple strategy selection logic
  const lowerDescription = description.toLowerCase();
  
  if (lowerDescription.includes("sort")) {
    return "sorting_algorithm";
  } else if (lowerDescription.includes("search")) {
    return "search_algorithm";
  } else {
    return "general_algorithm";
  }
}

/**
 * Apply the chosen solution strategy to the data.
 * 
 * @param {*} data - The input data to process
 * @param {string} strategy - The solution strategy to apply
 * @returns {*} The result of applying the strategy
 */
function applySolutionStrategy(data, strategy) {
  // Implementation depends on the strategy
  return data;
}

/**
 * Validate the result and format it appropriately.
 * 
 * @param {*} result - The raw result from solution application
 * @returns {*} The validated and formatted result
 * @throws {Error} If the result is invalid
 */
function validateAndFormatResult(result) {
  // Basic validation
  if (result === null || result === undefined) {
    throw new Error("Solution produced no result");
  }
  
  return result;
}
'''
        else:
            code = f"// Readability-focused code generation for {language.value} not yet implemented"
        
        return code
    
    def _generate_performance_focused(self, request: CodeGenerationRequest) -> str:
        """Generate code focused on maximum performance and efficiency"""
        problem = request.problem_description.lower()
        language = request.language
        
        if language == Language.PYTHON:
            if 'fibonacci' in problem:
                code = '''# Performance-optimized Fibonacci implementations

def fibonacci_matrix(n: int) -> int:
    """
    Get nth Fibonacci number using matrix exponentiation.
    Time: O(log n), Space: O(log n) due to recursion
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    def matrix_multiply(a, b):
        return [[a[0][0]*b[0][0] + a[0][1]*b[1][0], a[0][0]*b[0][1] + a[0][1]*b[1][1]],
                [a[1][0]*b[0][0] + a[1][1]*b[1][0], a[1][0]*b[0][1] + a[1][1]*b[1][1]]]
    
    def matrix_power(matrix, power):
        result = [[1, 0], [0, 1]]  # Identity matrix
        while power > 0:
            if power % 2 == 1:
                result = matrix_multiply(result, matrix)
            matrix = matrix_multiply(matrix, matrix)
            power //= 2
        return result
    
    transformation = [[1, 1], [1, 0]]
    result_matrix = matrix_power(transformation, n - 1)
    return result_matrix[0][0]

def fibonacci_iterative_optimized(n: int) -> int:
    """
    Iterative Fibonacci with minimal operations.
    Time: O(n), Space: O(1)
    """
    if n <= 0:
        return 0
    a, b = 0, 1
    for _ in range(1, n):
        a, b = b, a + b
    return b

# For sequence generation with caching
_fib_cache = {}
def fibonacci_cached(n: int) -> list[int]:
    """
    Generate Fibonacci sequence with memoization.
    Time: O(n), Space: O(n)
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    if n in _fib_cache:
        return _fib_cache[n]
    
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    
    _fib_cache[n] = sequence
    return sequence
'''
            else:
                code = '''# High-performance solution template

from typing import List, Dict, Any, Optional
import sys
from collections import defaultdict, deque
import heapq

def high_performance_solution(input_data: Any) -> Any:
    """
    Maximum performance solution with algorithmic optimizations.
    
    Techniques used:
    - Early termination
    - Efficient data structures
    - Memory pooling where applicable
    - Cache-friendly access patterns
    """
    if not input_data:
        return None
    
    # Pre-processing for better cache performance
    processed_data = preprocess_for_performance(input_data)
    
    # Choose optimal algorithm based on input characteristics
    algorithm = select_optimal_algorithm(processed_data)
    
    # Execute with performance monitoring
    result = execute_optimized_algorithm(processed_data, algorithm)
    
    return result

def preprocess_for_performance(data: Any) -> Any:
    """
    Preprocess data for optimal memory access patterns.
    """
    # Convert to most efficient format for the algorithm
    if isinstance(data, list):
        # Ensure contiguous memory layout
        return list(data)  # Creates new contiguous list
    return data

def select_optimal_algorithm(data: Any) -> str:
    """
    Select the most efficient algorithm based on input analysis.
    """
    data_size = len(data) if hasattr(data, '__len__') else 1
    
    if data_size < 1000:
        return "quadratic_time"  # O(n²) might be faster for small n
    elif data_size < 100000:
        return "linearithmic"    # O(n log n)
    else:
        return "linear_time"     # O(n) or better

def execute_optimized_algorithm(data: Any, algorithm: str) -> Any:
    """
    Execute the selected algorithm with maximum efficiency.
    """
    if algorithm == "quadratic_time":
        return quadratic_solution(data)
    elif algorithm == "linearithmic":
        return nlogn_solution(data)
    else:
        return linear_solution(data)

def quadratic_solution(data):
    """O(n²) solution - optimal for small datasets"""
    # Implementation for small data
    return data

def nlogn_solution(data):
    """O(n log n) solution - good general purpose"""
    # Implementation for medium data
    return sorted(data) if isinstance(data, list) else data

def linear_solution(data):
    """O(n) solution - optimal for large datasets"""
    # Implementation for large data
    return data

# Utility functions for performance monitoring
def time_execution(func):
    """Decorator to measure execution time"""
    def wrapper(*args, **kwargs):
        import time
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} executed in {end - start:.6f} seconds")
        return result
    return wrapper

def memory_usage():
    """Get current memory usage in MB"""
    import psutil
    import os
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024
'''
        
        elif language == Language.JAVASCRIPT:
            if 'fibonacci' in problem:
                code = '''// High-performance Fibonacci implementations

/**
 * Matrix exponentiation for Fibonacci - O(log n) time
 */
function fibonacciMatrix(n) {
  if (n <= 0) return 0;
  if (n === 1) return 1;
  
  function matrixMultiply(a, b) {
    return [
      [a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]],
      [a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]]
    ];
  }
  
  function matrixPower(matrix, power) {
    let result = [[1, 0], [0, 1]]; // Identity matrix
    while (power > 0) {
      if (power % 2 === 1) {
        result = matrixMultiply(result, matrix);
      }
      matrix = matrixMultiply(matrix, matrix);
      power = Math.floor(power / 2);
    }
    return result;
  }
  
  const transformation = [[1, 1], [1, 0]];
  const resultMatrix = matrixPower(transformation, n - 1);
  return resultMatrix[0][0];
}

/**
 * Iterative Fibonacci with minimal operations - O(n) time, O(1) space
 */
function fibonacciIterativeOptimized(n) {
  if (n <= 0) return 0;
  if (n === 1) return 1;
  
  let a = 0, b = 1;
  for (let i = 1; i < n; i++) {
    [a, b] = [b, a + b];
  }
  return b;
}

// Cached sequence generation with memoization
const fibCache = new Map();

function fibonacciCached(n) {
  if (n <= 0) return [];
  if (n === 1) return [0];
  if (n === 2) return [0, 1];
  
  if (fibCache.has(n)) {
    return fibCache.get(n);
  }
  
  const sequence = [0, 1];
  for (let i = 2; i < n; i++) {
    sequence.push(sequence[i - 1] + sequence[i - 2]);
  }
  
  fibCache.set(n, sequence);
  return sequence;
}
'''
            else:
                code = '''/**
 * High-performance solution with algorithmic optimizations
 */
function highPerformanceSolution(inputData) {
  if (!inputData) return null;
  
  // Pre-processing for better cache performance
  const processedData = preprocessForPerformance(inputData);
  
  // Choose optimal algorithm based on input characteristics
  const algorithm = selectOptimalAlgorithm(processedData);
  
  // Execute with performance monitoring
  const result = executeOptimizedAlgorithm(processedData, algorithm);
  
  return result;
}

function preprocessForPerformance(data) {
  // Convert to most efficient format for the algorithm
  if (Array.isArray(data)) {
    // Ensure optimal array layout
    return [...data]; // Creates new optimized array
  }
  return data;
}

function selectOptimalAlgorithm(data) {
  const dataSize = Array.isArray(data) ? data.length : 1;
  
  if (dataSize < 1000) {
    return "quadratic_time"; // O(n²) might be faster for small n
  } else if (dataSize < 100000) {
    return "linearithmic";   // O(n log n)
  } else {
    return "linear_time";    // O(n) or better
  }
}

function executeOptimizedAlgorithm(data, algorithm) {
  switch (algorithm) {
    case "quadratic_time":
      return quadraticSolution(data);
    case "linearithmic":
      return nlognSolution(data);
    default:
      return linearSolution(data);
  }
}

function quadraticSolution(data) {
  // O(n²) solution - optimal for small datasets
  return data;
}

function nlognSolution(data) {
  // O(n log n) solution - good general purpose
  return Array.isArray(data) ? data.slice().sort() : data;
}

function linearSolution(data) {
  // O(n) solution - optimal for large datasets
  return data;
}

// Performance monitoring utilities
function timeExecution(func) {
  return function(...args) {
    const start = performance.now();
    const result = func.apply(this, args);
    const end = performance.now();
    console.log(`${func.name} executed in ${(end - start).toFixed(6)} milliseconds`);
    return result;
  };
}

function memoryUsage() {
  if (performance.memory) {
    return performance.memory.usedJSHeapSize / 1024 / 1024; // MB
  }
  return 0; // Not available in all browsers
}
'''
        else:
            code = f"// Performance-focused code generation for {language.value} not yet implemented"
        
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


class DataManager:
    """
    Manages and differentiates training data based on various criteria
    """
    
    def __init__(self, storage_path: str = "training_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.data_categories = {
            'language_specific': {},
            'problem_type': {},
            'complexity_level': {},
            'performance_metrics': {},
            'user_feedback': {}
        }
        self._load_data()
    
    def _load_data(self):
        """Load existing categorized data"""
        for category in self.data_categories.keys():
            file_path = self.storage_path / f"{category}_data.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    self.data_categories[category] = json.load(f)
    
    def _save_data(self):
        """Save categorized data to disk"""
        for category, data in self.data_categories.items():
            file_path = self.storage_path / f"{category}_data.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def categorize_feedback(self, feedback_data: Dict):
        """
        Categorize feedback data based on multiple criteria
        
        Args:
            feedback_data: Dictionary containing feedback information
        """
        # Language-based categorization
        language = feedback_data.get('language', 'unknown')
        if language not in self.data_categories['language_specific']:
            self.data_categories['language_specific'][language] = []
        self.data_categories['language_specific'][language].append(feedback_data)
        
        # Problem type categorization
        problem_type = self._classify_problem_type(feedback_data.get('problem_description', ''))
        if problem_type not in self.data_categories['problem_type']:
            self.data_categories['problem_type'][problem_type] = []
        self.data_categories['problem_type'][problem_type].append(feedback_data)
        
        # Complexity level categorization
        complexity = self._assess_complexity(feedback_data)
        if complexity not in self.data_categories['complexity_level']:
            self.data_categories['complexity_level'][complexity] = []
        self.data_categories['complexity_level'][complexity].append(feedback_data)
        
        # Performance metrics categorization
        if 'execution_time' in feedback_data:
            perf_category = self._categorize_performance(feedback_data['execution_time'])
            if perf_category not in self.data_categories['performance_metrics']:
                self.data_categories['performance_metrics'][perf_category] = []
            self.data_categories['performance_metrics'][perf_category].append(feedback_data)
        
        # User feedback categorization
        rating = feedback_data.get('rating', 3)
        feedback_category = self._categorize_feedback_rating(rating)
        if feedback_category not in self.data_categories['user_feedback']:
            self.data_categories['user_feedback'][feedback_category] = []
        self.data_categories['user_feedback'][feedback_category].append(feedback_data)
        
        self._save_data()
    
    def _classify_problem_type(self, problem_description: str) -> str:
        """Classify problem type based on description"""
        desc_lower = problem_description.lower()
        
        if any(keyword in desc_lower for keyword in ['fibonacci', 'sequence', 'series']):
            return 'sequence_generation'
        elif any(keyword in desc_lower for keyword in ['sort', 'sorting', 'order']):
            return 'sorting'
        elif any(keyword in desc_lower for keyword in ['search', 'find', 'lookup']):
            return 'search'
        elif any(keyword in desc_lower for keyword in ['graph', 'tree', 'network']):
            return 'graph_algorithm'
        elif any(keyword in desc_lower for keyword in ['array', 'list', 'string']):
            return 'data_structure'
        elif any(keyword in desc_lower for keyword in ['math', 'calculation', 'compute']):
            return 'mathematical'
        else:
            return 'general'
    
    def _assess_complexity(self, feedback_data: Dict) -> str:
        """Assess problem complexity"""
        description = feedback_data.get('problem_description', '')
        constraints = feedback_data.get('constraints', {})
        
        # Simple heuristics for complexity assessment
        complexity_score = 0
        
        # Length of description
        if len(description) > 200:
            complexity_score += 2
        elif len(description) > 100:
            complexity_score += 1
        
        # Number of constraints
        constraint_count = len(constraints)
        complexity_score += min(constraint_count, 3)
        
        # Keywords indicating complexity
        complex_keywords = ['optimize', 'efficient', 'performance', 'memory', 'time']
        desc_lower = description.lower()
        complexity_score += sum(1 for keyword in complex_keywords if keyword in desc_lower)
        
        # Execution time if available
        if 'execution_time' in feedback_data and feedback_data['execution_time'] > 1.0:
            complexity_score += 1
        
        if complexity_score >= 5:
            return 'high'
        elif complexity_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _categorize_performance(self, execution_time: float) -> str:
        """Categorize based on execution time"""
        if execution_time < 0.01:
            return 'very_fast'
        elif execution_time < 0.1:
            return 'fast'
        elif execution_time < 1.0:
            return 'moderate'
        elif execution_time < 10.0:
            return 'slow'
        else:
            return 'very_slow'
    
    def _categorize_feedback_rating(self, rating: int) -> str:
        """Categorize based on user rating"""
        if rating >= 4:
            return 'excellent'
        elif rating >= 3:
            return 'good'
        elif rating >= 2:
            return 'fair'
        else:
            return 'poor'
    
    def get_data_by_category(self, category: str, subcategory: str = None) -> List[Dict]:
        """
        Retrieve data by category and optional subcategory
        
        Args:
            category: Main category (language_specific, problem_type, etc.)
            subcategory: Specific subcategory within the category
            
        Returns:
            List of data items matching the criteria
        """
        if category not in self.data_categories:
            return []
        
        if subcategory:
            return self.data_categories[category].get(subcategory, [])
        else:
            # Return all data in the category
            all_data = []
            for subcat_data in self.data_categories[category].values():
                all_data.extend(subcat_data)
            return all_data
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the categorized data
        
        Returns:
            Dictionary with statistics for each category
        """
        stats = {}
        for category, data in self.data_categories.items():
            stats[category] = {
                'total_items': sum(len(items) for items in data.values()),
                'subcategories': len(data),
                'subcategory_counts': {subcat: len(items) for subcat, items in data.items()}
            }
        return stats
    
    def find_similar_problems(self, problem_description: str, limit: int = 5) -> List[Dict]:
        """
        Find similar problems based on description
        
        Args:
            problem_description: Description of the problem to find similar items for
            limit: Maximum number of similar items to return
            
        Returns:
            List of similar problem data
        """
        problem_type = self._classify_problem_type(problem_description)
        similar_problems = self.get_data_by_category('problem_type', problem_type)
        
        # Simple similarity scoring based on keyword overlap
        desc_words = set(problem_description.lower().split())
        
        scored_problems = []
        for problem in similar_problems:
            prob_desc = problem.get('problem_description', '').lower()
            prob_words = set(prob_desc.split())
            similarity = len(desc_words.intersection(prob_words)) / len(desc_words.union(prob_words))
            scored_problems.append((similarity, problem))
        
        # Sort by similarity score and return top matches
        scored_problems.sort(key=lambda x: x[0], reverse=True)
        return [problem for _, problem in scored_problems[:limit]]
    
    def get_recommendations(self, criteria: Dict) -> List[Dict]:
        """
        Get recommendations based on specified criteria
        
        Args:
            criteria: Dictionary with filtering criteria
                e.g., {'language': 'python', 'problem_type': 'sorting', 'complexity': 'medium'}
                
        Returns:
            List of recommended data items
        """
        candidates = []
        
        # Start with all data
        for category_data in self.data_categories.values():
            for subcat_data in category_data.values():
                candidates.extend(subcat_data)
        
        # Apply filters
        filtered = []
        for item in candidates:
            match = True
            for key, value in criteria.items():
                if key == 'language':
                    if item.get('language') != value:
                        match = False
                        break
                elif key == 'problem_type':
                    item_problem_type = self._classify_problem_type(item.get('problem_description', ''))
                    if item_problem_type != value:
                        match = False
                        break
                elif key == 'complexity':
                    item_complexity = self._assess_complexity(item)
                    if item_complexity != value:
                        match = False
                        break
                elif key == 'min_rating':
                    if item.get('rating', 0) < value:
                        match = False
                        break
            
            if match:
                filtered.append(item)
        
        return filtered
