// ; CMD: Take command line arguments for file path

// ; READ: Load file into memory

// ; LEXER: Go through every char in the string
// ;   Identify each char and store TOK_TYPE to memory contiguously

// ; PARSER: Generate AST
// ;   Function declaration
// ;   Variable declaration
// ;   Return statement
// ;   End of function

// ; CODE GENERATOR: Turn AST into Assembly/IR
// ;   Map AST nodes to opcodes

// ; BINARY: Turn Assembly/IR into binary
// ;   Map Assembly/IR to binary

// ; WRITE: Write file to .bin

use std::env;
use std::fs;

#[derive(Debug, Clone)]
enum Token {
    Keyword(String),
    Identifier(String),
    IntLiteral(String),
    Operator(String),
    Separator(char),
    Eof,
}

enum Type {
    Int,
    Char,
    Void,
    // Pointer(Box<Type>),
}

struct Program {
    items: Vec<Declaration>,
}

enum Declaration {
    Function {
        name: String,
        ret_type: Type,
        params: Vec<Parameter>,
        body: Box<Statement>,
    },
    Variable {
        name: String,
        var_type: Type,
        init: Expression,
    },
}

struct Parameter {
    name: String,
    var_type: Type,
}

enum Statement {
    Block {
        items: Vec<BlockItem>,
    },
    Expr(Expression),
    Return(Option<Expression>),
    If { 
        // converts else if to nested if (syntatic sugar)
        cond: Expression,
        then_branch: Box<Statement>,
        else_branch: Option<Box<Statement>>,
    },
    While {
        cond: Expression,
        body: Box<Statement>,
    },
    For {
        // converts to while (syntatic sugar)
        init: Option<Box<Statement>>,
        cond: Option<Expression>,
        inc: Option<Expression>,
        body: Box<Statement>,
    },
}

enum BlockItem {
    Decl(Declaration),
    Stmt(Statement),
}

enum Expression {
    IntLiteral(i8),
    CharLiteral(char),
    Variable(String),
    Assign {
        target: Box<Expression>,
        value: Box<Expression>,
    },
    Unary {
        operator: UnaryOp,
        oper: Box<Expression>, 
    },
    Binary {
        operator: BinaryOp,
        left_oper: Box<Expression>,
        right_oper: Box<Expression>,    
    },
    Call {
        name: String,
        args: Vec<Expression>,
    },
}

enum UnaryOp {
    Negate,
    Not,
}

enum BinaryOp {
    Add,
    Sub,
    Multiply,
    Divide,
    And,
    Or,
    Equal,
    NotEqual,
    LessThan,
    LessThanOrEqual,
    GreaterThan,
    GreaterThanOrEqual,
}

fn main() {
    let args: Vec<String> = env::args().collect();
    printvec(&args);

    let file_data: String = fs::read_to_string(&args[1]).expect("failed to read file");
    println!("{}", file_data);

    let tokens: Vec<Token> = lexer(file_data);
    for x in tokens {
        println!("{:?}", x);
    }
}

fn lexer(s: String) -> Vec<Token> {
    let mut tokens = Vec::new();
    let mut chars = s.chars().peekable();

    while let Some(&c) = chars.peek() { // while PATTERN matches EXPRESSION
        if c.is_whitespace() {
            chars.next();
        } else if c.is_ascii_alphabetic() || c == '_' {
            // get entire keyword or identifier
            let mut buf = String::new();
            while let Some(&buf_c) = chars.peek() {
                if buf_c.is_ascii_alphabetic() || buf_c.is_ascii_digit() || buf_c == '_' {
                    buf.push(buf_c);
                    chars.next();
                } else {
                    break;
                }
            }
            
            // check if buf is a keyword or identifier
            let token = match buf.as_str() {
                "if" | "else" | "for" | "while" | "break" | "continue" | "return" | "int" | "char" | "void" => Token::Keyword(buf),
                _ => Token::Identifier(buf),
            };
            tokens.push(token);
        } else if c.is_ascii_digit() {
            let mut buf = String::new();
            while let Some(&buf_c) = chars.peek() {
                if buf_c.is_ascii_digit() {
                    buf.push(buf_c);
                    chars.next();
                } else {
                    break;
                }
            }
            tokens.push(Token::IntLiteral(buf));
        } else {
            let token = match c {
                '{' | '}' | '(' | ')' | ';' | ',' => {
                    chars.next();
                    Token::Separator(c)
                },
                '~' | '+' | '-' | '*'  => {
                    chars.next();
                    Token::Operator(c.to_string())
                },
                '/' => {
                    // handle comments
                    if matches!(chars.peek(), Some(&'/')) {
                        while !matches!(chars.peek(), Some(&'\n')) {
                            chars.next();
                        }
                        continue;
                    } else {
                        chars.next();
                        Token::Operator(c.to_string())
                    }
                },
                '&' => {
                    // handles &&
                    chars.next();
                    if matches!(chars.peek(), Some(&'&'))  {
                        chars.next();
                        Token::Operator(c.to_string().repeat(2))
                    } else {
                        // ignore single &
                        continue;
                    }
                },
                '|' => {
                    // handles ||
                    chars.next();
                    if matches!(chars.peek(), Some(&'|'))  {
                        chars.next();
                        Token::Operator(c.to_string().repeat(2))
                    } else {
                        // ignore single |
                        continue;
                    }
                },
                '!' => {
                    // handles ! or !=
                    chars.next();
                    if matches!(chars.peek(), Some(&'='))  {
                        chars.next();
                        Token::Operator(c.to_string() + "=")
                    } else {
                        Token::Operator(c.to_string())
                    }
                },
                '=' | '<' | '>' => {
                    // handles == or <= or >=
                    chars.next();
                    if matches!(chars.peek(), Some(&'='))  {
                        chars.next();
                        Token::Operator(c.to_string() + "=")
                    } else {
                        Token::Operator(c.to_string())
                    }
                },
                _ => {
                    chars.next();
                    continue;
                }
            };
            tokens.push(token);
        }
    }

    tokens.push(Token::Eof);
    tokens
}

struct Parser {
    tokens: Vec<Token>,
    pos: usize,
}

impl Parser {
    fn new(tokens: Vec<Token>) -> Self {
        Parser { tokens, pos: 0 }
    }

    fn peek(&self) -> Option<&Token> {
        self.tokens.get(self.pos)
    }

    fn peek_n(&self, n: usize) -> Option<&Token> {
        self.tokens.get(self.pos + n)
    }

    fn next(&mut self) -> Option<Token> {
        let tok = self.tokens.get(self.pos).cloned();
        self.pos += 1;
        tok
    }

    fn parse_program(&mut self) -> Program {
        let mut items = Vec::new();
        while self.peek().is_some() {
            let decl = self.parse_declaration();
            items.push(decl);
        }
        Program { items }
    }

    fn parse_declaration(&mut self) -> Declaration {
        let decl_type = match self.next() {
            Some(Token::Keyword(x)) => match x.as_str() {
                "int" => Type::Int,
                "char" => Type::Char,
                "void" => Type::Void,
                _ => panic!("invalid type"),
            }
            _ => panic!("expected keyword"),
        };

        let name = match self.next() {
            Some(Token::Identifier(x)) => name,
            _ => panic!("expected identifier"),
        };

        match self.next() {
            Some(Token::Separator('(')) => {
                self.parse_function(name, decl_type)
            },
            Some(Token::Operator(x)) if x == "=" => {
                if let Type::Void = decl_type {
                    panic!("invalid type for variable");
                }
                self.parse_variable(name, decl_type)
            },
            Some(Token::Separator(';')) => panic!("expected initialized variable"),
            _ => panic!("expected function or variable"),
        }
    }

    fn parse_function(&mut self, name: String, ret_type: Type) -> Declaration {
        let mut params = Vec::new();
        if !matches(self.peek(), Some(Token::Separator(')'))) {
            // Parse parameters
            loop {
                let var_type = match self.next() {
                    Some(Token::Keyword(x)) => match x.as_str() {
                        "int" => Type::Int,
                        "char" => Type::Char,
                        _ => panic!("invalid type"),
                    }
                    _ => panic!("expected keyword"),
                };
                let name = match self.next() {
                    Some(Token::Identifier(x)) => name,
                    _ => panic!("expected identifier"),
                };
                let p = Parameter { name, var_type }
                params.push(p);

                match self.next() {
                    Some(Token:Separator(',')) => {
                        continue;
                    },
                    Some(Token:Separator(')')) => {
                        break;
                    }
                    _ => panic!("expected comma"),
                }
            }
        }
        let body = self.parse_block_statement();
        Declaration::Function { name, ret_type, params, body }
    }

    fn parse_variable(&mut self, name: String, var_type: Type) -> Declaration {
        let init = self.parse_expression(0.0);
        Declaration::Variable { name, var_type, init }
    }

    fn parse_block_statement(&mut self) -> Statement {
        let mut items: Vec<BlockItem> = Vec::new();
        match self.next() {
            Some(Token:Separator('{')) => {
                while !matches!(self.peek(), Some(Token::Separator('}'))) {                    
                    match self.peek_n(1) {
                        Some(Token::Keyword(x)) => match x.as_str() {
                            "int" | "char" | "void" => {
                                let item: Declaration = self.parse_declaration();
                                items.push(BlockItem::Decl(item));
                            },
                            "if" | "while" | "for" | "return" => {
                                let item: Statement = self.parse_statement();
                                items.push(BlockItem::Stmt(item));
                            }
                            _ => panic!("expected declaration or statement"),
                        },
                        _ => {
                            // Could be an expression, such as foo(bar);
                            let item: Statement = self.parse_statement();
                            items.push(BlockItem::Stmt(item));
                        },
                    }
                    self.next();
                }
                Block { items }
            },
            _ => panic!("expected open bracket {"),
        }
    }

    fn parse_statement(&mut self) -> Statement {

    }

    fn get_binding_power(&mut self, operator: BinaryOp) -> (f32, f32) {
        match operator {
            BinaryOp::Or => (1.0, 1.1),
            BinaryOp::And => (2.0, 2.1),
            BinaryOp::Equal | BinaryOp::NotEqual => (3.0, 3.1),
            BinaryOp::LessThan 
            | BinaryOp::LessThanOrEqual 
            | BinaryOp::GreaterThan 
            | BinaryOp::GreaterThanOrEqual => (4.0, 4.1),
            BinaryOp::Add | BinaryOp::Sub => (5.0, 5.1),
            BinaryOp::Multiply | BinaryOp::Divide => (6.0, 6.1),
            _ => panic!("expected valid binary operator");
        }
    }
    
    fn parse_expression(&mut self, min_bp: f32) -> Expression {
        // parse prefix
        let mut left_oper = match self.next() {
            Some(Token::IntLiteral(x)) => Expression::IntLiteral(x.parse().unwrap()),
            Some(Token::Identifier(name)) => {
                if matches!(self.peek_n(1), Some(Token::Separator('('))) {
                    self.parse_call(name);
                } else {
                    Expression::Variable(name)
                }
            },
            Some(Token::Operator(operator)) if operator == '-' => Expression::Unary {
                operator: UnaryOp::Negate,
                oper: Box::new(self.parse_expression(7.0)),
            },
            Some(Token::Operator(operator)) if operator == '!' => Expression::Unary {
                operator: UnaryOp::Not,
                oper: Box::new(self.parse_expression(7.0)),
            },
            Some(Token::Separator('(')) => self.parse_expression(0.0),
            _ => panic!("expected integer literal"),
        };

        // parse infix
        loop {
            let operator: BinaryOp = match self.peek_n(1) {
                Some(Token::Operator(x)) => match x {
                    '+' => BinaryOp::Add,
                    '-' => BinaryOp::Sub,
                    '*' => BinaryOp::Multiply,
                    '/' => BinaryOp::Divide,
                    "&&" => BinaryOp::And,
                    "||" => BinaryOp::Or,
                    "=" => BinaryOp::Equal,
                    "!=" => BinaryOp::NotEqual,
                    "<" => BinaryOp::LessThan,
                    "<=" => BinaryOp::LessThanOrEqual,
                    ">" => BinaryOp::GreaterThan,
                    ">=" => BinaryOp::GreaterThanOrEqual,
                    _ => panic("invalid operator"),
                },
                Some(Token::Separator(')')) | Some(Token::Separator(';')) => break,
                _ => panic!("expected operator")
            }
            let (l_bp, r_bp) = self.get_binding_power(operator);
            // if min_bp (previous operator bp) is greater than l_bp (current operator bp)
            // then break and move back to outer expression
            // else check the next operator
            if l_bp < min_bp {
                break;
            }
            self.next();
            let right_oper = self.parse_expression(r_bp);
            left_oper = Expression::Binary { 
                operator, 
                left_oper: Box::new(left_oper), 
                right_oper: Box::new(right_oper) 
            };
        }
        left_oper
    }

    fn parse_call() -> Expression {
        
    }
 }

fn parser(v: Vec<Token>) {

}

fn printvec(v: &[String]) {
    for x in v {
        println!("{}", x);
    }
}