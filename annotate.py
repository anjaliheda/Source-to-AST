import json
import subprocess
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from typing import Dict, List, Set, Optional

console = Console()

class HardcodedExplainer:
    """Provides hardcoded explanations for AST nodes"""
    
    def __init__(self):
        self.explanations = self._build_explanation_map()
        self.patterns = self._build_pattern_explanations()
    
    def _build_explanation_map(self) -> Dict[str, str]:
        """Comprehensive mapping of AST nodes to explanations"""
        return {
            # Declarations
            'FunctionDecl': "declares a function with its signature and body",
            'CXXMethodDecl': "declares a class method or member function",
            'CXXConstructorDecl': "declares a class constructor",
            'CXXDestructorDecl': "declares a class destructor", 
            'CXXRecordDecl': "declares a class, struct, or union type",
            'ClassTemplateDecl': "declares a class template",
            'VarDecl': "declares a variable with optional initialization",
            'FieldDecl': "declares a class member variable or field",
            'ParmVarDecl': "declares a function parameter",
            'NamespaceDecl': "declares or opens a namespace",
            'UsingDecl': "brings a name from another namespace into scope",
            'TypedefDecl': "creates a type alias using typedef",
            'EnumDecl': "declares an enumeration type",
            'EnumConstantDecl': "declares an enumeration constant",
            
            # Statements
            'CompoundStmt': "represents a block of statements enclosed in braces {}",
            'IfStmt': "represents an if conditional statement",
            'ForStmt': "represents a traditional for loop",
            'WhileStmt': "represents a while loop",
            'CXXForRangeStmt': "represents a range-based for loop (C++11)",
            'SwitchStmt': "represents a switch statement for multi-way branching",
            'CaseStmt': "represents a case label in a switch statement",
            'DefaultStmt': "represents the default case in a switch statement",
            'ReturnStmt': "returns a value from a function",
            'BreakStmt': "breaks out of a loop or switch statement",
            'ContinueStmt': "continues to the next iteration of a loop",
            'DeclStmt': "represents a declaration statement",
            'ExprStmt': "represents an expression used as a statement",
            'NullStmt': "represents an empty statement (just a semicolon)",
            'DoStmt': "represents a do-while loop",
            'GotoStmt': "represents a goto statement",
            'LabelStmt': "represents a labeled statement",
            
            # Expressions
            'BinaryOperator': "performs a binary operation (e.g., +, -, ==, &&)",
            'UnaryOperator': "performs a unary operation (e.g., ++, --, !, ~)",
            'ConditionalOperator': "represents the ternary operator (condition ? true : false)",
            'CallExpr': "represents a function call",
            'CXXOperatorCallExpr': "represents an overloaded operator call in C++",
            'CXXMemberCallExpr': "represents a call to a class member function",
            'MemberExpr': "accesses a member of a struct/class (e.g., obj.member)",
            'ArraySubscriptExpr': "accesses an array element using [] operator",
            'DeclRefExpr': "references a previously declared variable or function",
            'IntegerLiteral': "represents an integer constant (e.g., 42, 0xFF)",
            'FloatingLiteral': "represents a floating-point constant (e.g., 3.14)",
            'StringLiteral': "represents a string literal (e.g., \"hello\")",
            'CharacterLiteral': "represents a character literal (e.g., 'a')",
            'CXXBoolLiteralExpr': "represents a boolean literal (true or false)",
            'CXXNullPtrLiteralExpr': "represents a nullptr literal",
            'AssignmentOperator': "assigns a value to a variable (=, +=, -=, etc.)",
            'CompoundAssignOperator': "performs compound assignment (+=, -=, *=, etc.)",
            
            # C++ Specific Expressions
            'CXXNewExpr': "allocates memory using the new operator",
            'CXXDeleteExpr': "deallocates memory using the delete operator",
            'CXXThisExpr': "represents the 'this' pointer in a class method",
            'CXXThrowExpr': "throws an exception",
            'CXXTryStmt': "represents a try-catch block for exception handling",
            'CXXCatchStmt': "represents a catch block in exception handling",
            'CXXConstructExpr': "constructs an object using a constructor",
            'CXXTemporaryObjectExpr': "creates a temporary object",
            'CXXFunctionalCastExpr': "performs a functional-style cast",
            'CXXStaticCastExpr': "performs a static_cast",
            'CXXDynamicCastExpr': "performs a dynamic_cast",
            'CXXReinterpretCastExpr': "performs a reinterpret_cast",
            'CXXConstCastExpr': "performs a const_cast",
            
            # Type-related
            'ImplicitCastExpr': "performs an implicit type conversion",
            'CStyleCastExpr': "performs a C-style cast",
            'ParenExpr': "represents parenthesized expression",
            'SizeOfExpr': "calculates the size of a type or expression",
            
            # Control Flow Helpers
            'MaterializeTemporaryExpr': "materializes a temporary object",
            'ExprWithCleanups': "manages cleanup of temporary objects",
            'CXXBindTemporaryExpr': "binds a temporary object for cleanup",
            
            # Attributes
            'AlignedAttr': "specifies memory alignment requirements",
            'VisibilityAttr': "controls symbol visibility",
            'DeprecatedAttr': "marks a declaration as deprecated",
            'NoReturnAttr': "indicates a function never returns",
            
            # Template-related
            'TemplateTypeParmDecl': "declares a template type parameter",
            'NonTypeTemplateParmDecl': "declares a non-type template parameter",
            'TemplateTemplateParmDecl': "declares a template template parameter",
            'ClassTemplateSpecializationDecl': "specializes a class template",
            'FunctionTemplateDecl': "declares a function template",
            
            # Advanced C++ Features  
            'LambdaExpr': "defines a lambda expression (anonymous function)",
            'CXXDefaultArgExpr': "represents a default argument in function call",
            'InitListExpr': "represents brace-enclosed initializer list",
            'DesignatedInitExpr': "represents designated initializer (C99/C++20)",
            'CompoundLiteralExpr': "represents a compound literal",
            
            # Preprocessor-related
            'MacroExpansion': "represents an expanded macro",
            'InclusionDirective': "represents a #include directive",
        }
    
    def _build_pattern_explanations(self) -> List[tuple]:
        """Pattern-based explanations for combinations of AST nodes"""
        return [
            # Function patterns
            (['FunctionDecl', 'CompoundStmt'], "defines a function with a body containing statements"),
            (['FunctionDecl', 'ParmVarDecl'], "defines a function that takes parameters"),
            (['CallExpr', 'DeclRefExpr'], "calls a previously declared function"),
            
            # Variable patterns
            (['VarDecl', 'IntegerLiteral'], "declares an integer variable with a literal value"),
            (['VarDecl', 'CallExpr'], "declares a variable initialized by a function call"),
            (['AssignmentOperator', 'DeclRefExpr'], "assigns a value to an existing variable"),
            
            # Control flow patterns
            (['IfStmt', 'BinaryOperator'], "conditional statement with a comparison"),
            (['ForStmt', 'BinaryOperator'], "for loop with a comparison condition"),
            (['WhileStmt', 'BinaryOperator'], "while loop with a comparison condition"),
            
            # Class patterns
            (['CXXRecordDecl', 'CXXMethodDecl'], "defines a class with member methods"),
            (['CXXRecordDecl', 'FieldDecl'], "defines a class with member variables"),
            (['CXXConstructorDecl', 'MemberExpr'], "constructor that initializes member variables"),
            
            # Expression patterns
            (['BinaryOperator', 'DeclRefExpr'], "performs an operation on variables"),
            (['CallExpr', 'MemberExpr'], "calls a method on an object"),
            (['ArraySubscriptExpr', 'DeclRefExpr'], "accesses an array element"),
            
            # Memory management
            (['CXXNewExpr', 'CXXConstructExpr'], "dynamically creates an object"),
            (['CXXDeleteExpr', 'DeclRefExpr'], "deallocates a dynamically allocated object"),
        ]
    
    def explain_ast_nodes(self, ast_nodes: List[str], source_line: str = "") -> str:
        """Generate explanation for a set of AST nodes"""
        if not ast_nodes:
            return ""
        
        # Sort nodes for consistent pattern matching
        sorted_nodes = sorted(ast_nodes)
        
        # Try pattern matching first
        for pattern_nodes, explanation in self.patterns:
            if all(node in sorted_nodes for node in pattern_nodes):
                return explanation
        
        # Fall back to individual node explanations
        explanations = []
        for node in sorted_nodes:
            if node in self.explanations:
                explanations.append(self.explanations[node])
            else:
                # Provide a generic explanation for unknown nodes
                explanations.append(f"AST node: {node}")
        
        # Combine explanations intelligently
        if len(explanations) == 1:
            return explanations[0]
        elif len(explanations) == 2:
            return f"{explanations[0]} and {explanations[1]}"
        else:
            return f"combines {', '.join(explanations[:-1])}, and {explanations[-1]}"
    
    def get_detailed_explanation(self, ast_nodes: List[str], source_line: str = "") -> str:
        """Get more detailed explanation with context"""
        explanation = self.explain_ast_nodes(ast_nodes, source_line)
        
        # Add context based on source line content
        line_lower = source_line.lower().strip()
        
        # Add specific context hints
        if 'main(' in line_lower:
            explanation += " (this is the program's entry point)"
        elif line_lower.startswith('class ') or line_lower.startswith('struct '):
            explanation += " (defining a new data type)"
        elif line_lower.startswith('#include'):
            explanation += " (including external code)"
        elif 'cout' in line_lower or 'printf' in line_lower:
            explanation += " (performing output operation)"
        elif 'cin' in line_lower or 'scanf' in line_lower:
            explanation += " (performing input operation)"
        elif line_lower.endswith(';') and '=' in line_lower and not line_lower.strip().startswith('for'):
            explanation += " (assignment or initialization)"
        
        return explanation

def run_clang_ast_dump(file_path):
    """Run clang AST dump and return parsed JSON"""
    try:
        result = subprocess.run(
            ["clang", "-Xclang", "-ast-dump=json", "-fsyntax-only", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            console.print(f"[bold red]Clang error (exit code {result.returncode}):[/bold red]")
            console.print(result.stderr)
            return None
            
        if not result.stdout.strip():
            console.print("[bold red]Error:[/bold red] Clang produced no output")
            return None
            
        return json.loads(result.stdout)
        
    except subprocess.TimeoutExpired:
        console.print("[bold red]Error:[/bold red] Clang process timed out")
        return None
    except json.JSONDecodeError as e:
        console.print(f"[bold red]JSON parsing error:[/bold red] {e}")
        console.print("Raw output:", result.stdout[:500])
        return None
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] clang not found. Please install clang/LLVM.")
        return None

def should_include_node(kind, filter_config):
    """Determine if a node kind should be included based on filter configuration"""
    if filter_config == "minimal":
        important_nodes = {
            'FunctionDecl', 'CXXMethodDecl', 'CXXConstructorDecl', 'CXXDestructorDecl',
            'CXXRecordDecl', 'ClassTemplateDecl', 'VarDecl', 'FieldDecl',
            'IfStmt', 'ForStmt', 'WhileStmt', 'CXXForRangeStmt', 'SwitchStmt',
            'ReturnStmt', 'BreakStmt', 'ContinueStmt', 'CompoundStmt'
        }
        return kind in important_nodes
    
    elif filter_config == "clean":
        noise_nodes = {
            'MaterializeTemporaryExpr', 'CXXBindTemporaryExpr', 'ExprWithCleanups',
            'ParenExpr', 'AlignedAttr', 'VisibilityAttr'
        }
        return kind not in noise_nodes
    
    elif filter_config == "declarations":
        decl_nodes = {
            'FunctionDecl', 'CXXMethodDecl', 'CXXConstructorDecl', 'CXXDestructorDecl',
            'CXXRecordDecl', 'ClassTemplateDecl', 'VarDecl', 'FieldDecl',
            'ParmVarDecl', 'NamespaceDecl', 'UsingDecl', 'TypedefDecl'
        }
        return kind in decl_nodes
    
    elif filter_config == "statements":
        stmt_nodes = {
            'IfStmt', 'ForStmt', 'WhileStmt', 'CXXForRangeStmt', 'SwitchStmt',
            'ReturnStmt', 'BreakStmt', 'ContinueStmt', 'CompoundStmt',
            'DeclStmt', 'ExprStmt', 'NullStmt'
        }
        return kind in stmt_nodes
    
    else:  # "all"
        return True

def get_node_color(kind):
    """Return color coding for different node types"""
    if kind in ['FunctionDecl', 'CXXMethodDecl', 'CXXConstructorDecl', 'CXXDestructorDecl']:
        return 'bright_blue'
    elif kind in ['CXXRecordDecl', 'ClassTemplateDecl']:
        return 'bright_green'
    elif kind in ['VarDecl', 'FieldDecl', 'ParmVarDecl']:
        return 'bright_yellow'
    elif kind in ['IfStmt', 'ForStmt', 'WhileStmt', 'CXXForRangeStmt', 'SwitchStmt']:
        return 'bright_magenta'
    elif kind in ['ReturnStmt', 'BreakStmt', 'ContinueStmt']:
        return 'bright_red'
    else:
        return 'white'

def collect_line_annotations(node, line_map, target_file_path, filter_config):
    """Recursively collect AST node annotations for each line"""
    def process_location(loc_info, node_kind):
        if not loc_info or not isinstance(loc_info, dict):
            return
            
        file_path = loc_info.get("file", "")
        line = loc_info.get("line")
        
        if line and isinstance(line, int) and node_kind:
            target_abs = os.path.abspath(target_file_path)
            if not file_path:
                if should_include_node(node_kind, filter_config):
                    line_map.setdefault(line, set()).add(node_kind)
            else:
                file_abs = os.path.abspath(file_path) if os.path.isabs(file_path) else file_path
                if (file_abs == target_abs or 
                    os.path.basename(file_abs) == os.path.basename(target_abs)):
                    if should_include_node(node_kind, filter_config):
                        line_map.setdefault(line, set()).add(node_kind)

    if isinstance(node, dict):
        kind = node.get("kind")
        
        loc = node.get("loc")
        if loc:
            process_location(loc, kind)

        range_info = node.get("range")
        if range_info and isinstance(range_info, dict):
            begin = range_info.get("begin")
            end = range_info.get("end")
            if begin:
                process_location(begin, kind)
            if end and end != begin:
                process_location(end, kind)

        for value in node.values():
            collect_line_annotations(value, line_map, target_file_path, filter_config)
            
    elif isinstance(node, list):
        for item in node:
            collect_line_annotations(item, line_map, target_file_path, filter_config)

def annotate_code_with_explanations(file_path, line_map, explainer: HardcodedExplainer,
                                  max_annotations=5, use_colors=True, compact_mode=False, detailed=False):
    """Enhanced interleaved display with hardcoded explanations"""
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding='latin-1') as f:
            lines = f.readlines()
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        return

    max_line_num_width = len(str(len(lines)))
    
    for i, line in enumerate(lines, start=1):
        if compact_mode and not line.strip() and i not in line_map:
            continue
            
        # Build AST node annotation
        ast_annotation = ""
        if i in line_map:
            sorted_kinds = sorted(line_map[i])
            
            if len(sorted_kinds) > max_annotations:
                displayed_kinds = sorted_kinds[:max_annotations]
                displayed_kinds.append(f"... +{len(sorted_kinds) - max_annotations} more")
            else:
                displayed_kinds = sorted_kinds
            
            if use_colors:
                colored_kinds = []
                for kind in displayed_kinds:
                    if kind.startswith("..."):
                        colored_kinds.append(f"[dim]{kind}[/dim]")
                    else:
                        color = get_node_color(kind)
                        colored_kinds.append(f"[{color}]{kind}[/{color}]")
                ast_annotation = " // " + ", ".join(colored_kinds)
            else:
                ast_annotation = " // " + ", ".join(displayed_kinds)
        
        # Display source line with AST annotation
        line_num_str = f"{i:>{max_line_num_width}} "
        code_content = line.rstrip("\n")
        syntax = Syntax(code_content, "cpp", theme="monokai", line_numbers=False, word_wrap=True)
        
        console.print(line_num_str, end="")
        console.print(syntax, end="")
        
        if ast_annotation:
            if len(code_content + ast_annotation) > 120:
                console.print()
                console.print(" " * (max_line_num_width + 1), end="")
            console.print(ast_annotation)
        else:
            console.print()
        
        # Display explanation if available
        if i in line_map:
            ast_nodes = sorted(list(line_map[i]))
            if detailed:
                explanation = explainer.get_detailed_explanation(ast_nodes, code_content)
            else:
                explanation = explainer.explain_ast_nodes(ast_nodes, code_content)
            
            if explanation:
                console.print(" " * (max_line_num_width + 1), end="")
                console.print(f"[dim italic]💡 {explanation}[/dim italic]")

def validate_file(file_path):
    """Validate input file exists and has appropriate extension"""
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File does not exist: {file_path}")
        return False
    
    if not os.path.isfile(file_path):
        console.print(f"[bold red]Error:[/bold red] Path is not a file: {file_path}")
        return False
    
    valid_extensions = {'.c', '.cpp', '.cxx', '.cc', '.C', '.h', '.hpp', '.hxx', '.hh'}
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext not in valid_extensions:
        console.print(f"[bold yellow]Warning:[/bold yellow] File extension '{file_ext}' may not be a C/C++ file")
        
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Annotate C/C++ source code with Clang AST information and hardcoded explanations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Filter options:
  minimal      - Show only the most important structural nodes
  clean        - Filter out common noise nodes (default)
  declarations - Show only declaration nodes
  statements   - Show only statement and control flow nodes
  all          - Show all AST nodes (very verbose)

Examples:
  python3 annotate.py file.cpp
  python3 annotate.py file.cpp --detailed
  python3 annotate.py file.cpp --filter minimal --detailed
        """
    )
    
    parser.add_argument("file", help="C/C++ source file to annotate")
    parser.add_argument("--filter", choices=["minimal", "clean", "declarations", "statements", "all"], 
                       default="clean", help="Filter level for AST nodes (default: clean)")
    parser.add_argument("--max-annotations", type=int, default=5, 
                       help="Maximum number of annotations per line (default: 5)")
    parser.add_argument("--no-colors", action="store_true", 
                       help="Disable color coding of annotations")
    parser.add_argument("--compact", action="store_true", 
                       help="Skip empty lines without annotations")
    parser.add_argument("--detailed", action="store_true",
                       help="Show detailed explanations with context")
    
    args = parser.parse_args()
    
    if not validate_file(args.file):
        sys.exit(1)
    
    file_path = os.path.abspath(args.file)
    
    # Initialize hardcoded explainer
    explainer = HardcodedExplainer()
    
    console.print(f"[bold green]Processing:[/bold green] {file_path}")
    console.print(f"[dim]Filter: {args.filter}, Max annotations: {args.max_annotations}[/dim]")
    
    ast_json = run_clang_ast_dump(file_path)
    if ast_json is None:
        sys.exit(1)
    
    line_map = {}
    collect_line_annotations(ast_json, line_map, file_path, args.filter)
    
    if not line_map:
        console.print("[bold yellow]Warning:[/bold yellow] No AST annotations found")
        return
    else:
        total_annotations = sum(len(annotations) for annotations in line_map.values())
        console.print(f"[bold green]Found {total_annotations} annotations on {len(line_map)} lines[/bold green]")
    
    # Display results
    console.rule("[bold blue]Annotated Source Code")
    annotate_code_with_explanations(file_path, line_map, explainer,
                                  args.max_annotations, not args.no_colors, args.compact, args.detailed)

if __name__ == "__main__":
    main()
