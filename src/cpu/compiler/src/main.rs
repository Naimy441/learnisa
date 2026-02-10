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

macro_rules! log {
    ($($arg:tt)*) => {
        #[cfg(debug_assertions)]
        println!("[line {}] {}", line!(), format!($($arg)*));
    };
}

macro_rules! logln {
    () => {
        #[cfg(debug_assertions)]
        println!();
    };
}

// Lexer
#[derive(Debug, Clone)]
enum Token {
    Keyword(String),
    Identifier(String),
    IntLiteral(String),
    Operator(String),
    Separator(char),
    Eof,
}

// Parser
#[derive(Debug)]
enum Type {
    Int,
    Char,
    Void,
    // Pointer(Box<Type>),
}

#[derive(Debug)]
struct Program {
    items: Vec<Declaration>,
}

#[derive(Debug)]
enum Declaration {
    Function {
        name: String,
        ret_type: Type,
        params: Vec<Parameter>,
        body: Box<Statement>,
    },
    InitVariable {
        name: String,
        var_type: Type,
        init: Expression,
    },
}

#[derive(Debug)]
struct Parameter {
    name: String,
    var_type: Type,
}

#[derive(Debug)]
enum Statement {
    Block {
        items: Vec<BlockItem>,
    },
    Expr(Expression),
    Return(Option<Expression>),
    Break,
    Continue,
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
        // init, cond, inc are all required unlike C
        init: Declaration,
        cond: Expression,
        inc: Expression,
        body: Box<Statement>,
    },
}

#[derive(Debug)]
enum BlockItem {
    Decl(Declaration),
    Stmt(Statement),
}

#[derive(Debug)]
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

#[derive(Debug, Clone)]
enum UnaryOp {
    Negate,
    Not,
}

#[derive(Debug, Clone)]
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

// Lowerer
#[derive(Debug, Clone)]
enum Value {
    Temp(usize),
    Var(String),
    Const(i32),
}

#[derive(Debug, Clone)]
enum Instruction {
    Assign(Value, Value),
    Unary {
        dest: Value,
        operator: UnaryOp,
        oper: Value, 
    },
    Binary {
        dest: Value,
        operator: BinaryOp,
        left_oper: Value,
        right_oper: Value,    
    },
    Call {
        dest: Value,
        name: String,
        args: Vec<Value>,
    },
    Label(String),
    Goto(String),
    IfGoto {
        cond: Value,
        label: String,
    },
    Return(Option<Value>),
}

fn main() {
    let args: Vec<String> = env::args().collect();
    for a in &args {
        log!("{}", a);
    }
    logln!();

    let file_data: String = fs::read_to_string(&args[1]).expect("failed to read file");
    log!("{}\n", file_data);

    let tokens: Vec<Token> = lexer(file_data);
    for t in &tokens {
        log!("{:?}", t);
    }
    logln!();

    let mut parser: Parser = Parser::new(tokens);
    let program: Program = parser.parse_program();
    logln!();
    log!("{:#?}", program);


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
                    chars.next();
                    if matches!(chars.peek(), Some(&'/')) {
                        while !matches!(chars.peek(), Some(&'\n')) {
                            chars.next();
                        }
                        continue;
                    } else {
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
        log!("token: {:?}", tok);
        self.pos += 1;
        tok
    }

    fn parse_program(&mut self) -> Program {
        log!("parse_program: {:?}", self.peek());

        let mut items = Vec::new();
        while !matches!(self.peek(), Some(Token::Eof)) {
            log!("parse_program1: {:?}", self.peek());
            let decl = self.parse_declaration();
            items.push(decl);
        }
        Program { items }
    }

    fn parse_declaration(&mut self) -> Declaration {
        log!("parse_declaration: {:?}", self.peek());

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
            Some(Token::Identifier(x)) => x,
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
        log!("parse_function: {:?}", self.peek());

        let mut params = Vec::new();
        if !matches!(self.peek(), Some(Token::Separator(')'))) {
            // parse parameters
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
                    Some(Token::Identifier(x)) => x,
                    _ => panic!("expected identifier"),
                };
                let p = Parameter { name, var_type };
                params.push(p);

                match self.next() {
                    Some(Token::Separator(',')) => {
                        continue;
                    },
                    Some(Token::Separator(')')) => {
                        break;
                    }
                    _ => panic!("expected comma"),
                }
            }
        } else {
            self.next(); // consume )
        }
        let body = Box::new(self.parse_statement());
        log!("parse_function1: {:?}", self.peek());
        Declaration::Function { name, ret_type, params, body }
    }

    fn parse_variable(&mut self, name: String, var_type: Type) -> Declaration {
        log!("parse_variable: {:?}", self.peek());

        let init = self.parse_expression(0.0);
        self.next();
        Declaration::InitVariable { name, var_type, init }
    }

    fn parse_statement(&mut self) -> Statement {
        log!("parse_statement: {:?}", self.peek());

        match self.peek() {
            // block statement
            Some(Token::Separator('{')) => {
                let mut items: Vec<BlockItem> = Vec::new();
                self.next(); // consume {
                while !matches!(self.peek(), Some(Token::Separator('}'))) {       
                    match self.peek() {
                        Some(Token::Keyword(x)) => match x.as_str() {
                            "int" | "char" | "void" => {
                                let item: Declaration = self.parse_declaration();
                                items.push(BlockItem::Decl(item));
                            },
                            "if" | "while" | "for" | "return" | "break" | "continue" => {
                                let item: Statement = self.parse_statement();
                                items.push(BlockItem::Stmt(item));
                            }
                            _ => panic!("expected declaration or statement"),
                        },
                        _ => {
                            // could be an expression, such as foo(bar);
                            let item: Statement = self.parse_statement();
                            items.push(BlockItem::Stmt(item));
                        },
                    }
                    log!("parse_statement1: {:?}", self.peek());
                }
                self.next(); // consume }
                Statement::Block { items }
            },
            // expression with assignment
            Some(Token::Identifier(_x)) => {
                let expr = self.parse_expression(0.0);
                self.next();
                Statement::Expr(expr)
            },
            Some(Token::Keyword(x)) => match x.as_str() {
                "return" => {
                    self.next(); // consume return
                    if let Some(Token::Separator(';')) = self.peek() {
                        self.next(); // consume ;
                        Statement::Return(None)
                    } else {
                        let expr = self.parse_expression(0.0);
                        self.next(); // consume ;
                        Statement::Return(Some(expr))
                    }
                },
                "break" => {
                    self.next(); // consume break
                    if let Some(Token::Separator(';')) = self.next() {
                        Statement::Break
                    } else {
                        panic!("expected semicolon");
                    }
                },
                "continue" => {
                    self.next(); // consume break
                    if let Some(Token::Separator(';')) = self.next() {
                        Statement::Continue
                    } else {
                        panic!("expected semicolon");
                    }
                },
                "if" => {
                    self.next(); // consume if
                    match self.next() {
                        Some(Token::Separator('(')) => {
                            let cond = self.parse_expression(0.0);
                            self.next(); // consume )
                            let then_branch = Box::new(self.parse_statement());
                            let else_branch = if matches!(self.peek(), Some(Token::Keyword(x)) if x == "else") {
                                self.next(); // consume else
                                Some(Box::new(self.parse_statement())) // to the parser, this looks like regular if so it does nesting
                            } else {
                                None
                            };
                            Statement::If {
                                cond, then_branch, else_branch
                            }
                        }
                        _ => panic!("expected open paranthese ("),
                    }
                },
                "while" => {
                    self.next(); // consume while
                    match self.next() {
                        Some(Token::Separator('(')) => {
                            let cond = self.parse_expression(0.0);
                            self.next(); // consume )
                            let body = Box::new(self.parse_statement());
                            Statement::While {
                                cond, body
                            }
                        }
                        _ => panic!("expected open paranthese ("),
                    }
                },
                "for" => {
                    self.next(); // consume for
                    match self.next() {
                        Some(Token::Separator('(')) => {
                            let init = self.parse_declaration();
                            let cond = self.parse_expression(0.0);
                            self.next(); // consume )
                            let inc = self.parse_expression(0.0);
                            self.next(); // consume )
                            let body = Box::new(self.parse_statement());
                            Statement::For {
                                init, cond, inc, body
                            }
                        },
                        _ => panic!("expected open paranthese ("),
                    }
                },
                _ => panic!("expected valid keyword"),
            },
            _ => panic!("expected statement"),
        }
    }

    fn get_binding_power(&mut self, operator: &BinaryOp) -> (f32, f32) {
        log!("get_binding_power: {:?}", self.peek());

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
        }
    }
    
    fn parse_expression(&mut self, min_bp: f32) -> Expression {
        log!("parse_expression: {:?}", self.peek());

        // parse prefix
        let mut left_oper = match self.next() {
            Some(Token::IntLiteral(x)) => Expression::IntLiteral(x.parse().unwrap()),
            Some(Token::Identifier(name)) => {
                if matches!(self.peek(), Some(Token::Separator('('))) {
                    self.parse_call(name)
                } else {
                    Expression::Variable(name)
                }
            },
            Some(Token::Operator(operator)) if operator.as_str() == "-" => Expression::Unary {
                operator: UnaryOp::Negate,
                oper: Box::new(self.parse_expression(7.0)),
            },
            Some(Token::Operator(operator)) if operator.as_str() == "!" => Expression::Unary {
                operator: UnaryOp::Not,
                oper: Box::new(self.parse_expression(7.0)),
            },
            Some(Token::Separator('(')) => {
                let expr = self.parse_expression(0.0);
                self.next(); // consume )
                expr
            },
            _ => panic!("expected integer literal"),
        };

        // parse infix
        loop {
            log!("parse_expression_loop: {:?}", self.peek());
            if let Some(Token::Operator(x)) = self.peek() {
                if x.as_str() == "=" {
                    self.next(); // consume assignment =
                    let right_oper = self.parse_expression(0.0);
                    return Expression::Assign {
                        target: Box::new(left_oper),
                        value: Box::new(right_oper),
                    }
                }
            }

            let operator: BinaryOp = match self.peek() {
                Some(Token::Operator(x)) => match x.as_str() {
                    "+" => BinaryOp::Add,
                    "-" => BinaryOp::Sub,
                    "*" => BinaryOp::Multiply,
                    "/" => BinaryOp::Divide,
                    "&&" => BinaryOp::And,
                    "||" => BinaryOp::Or,
                    "==" => BinaryOp::Equal,
                    "!=" => BinaryOp::NotEqual,
                    "<" => BinaryOp::LessThan,
                    "<=" => BinaryOp::LessThanOrEqual,
                    ">" => BinaryOp::GreaterThan,
                    ">=" => BinaryOp::GreaterThanOrEqual,
                    _ => panic!("invalid operator"),
                },
                Some(Token::Separator(')'))
                | Some(Token::Separator(';'))
                | Some(Token::Separator(',')) => break,
                _ => panic!("expected operator"),
            };
            log!("parse_expression_operator: {:?}", operator);
            let (l_bp, r_bp) = self.get_binding_power(&operator);
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
        log!("parse_expression1: {:?}", self.peek());
        left_oper
    }

    fn parse_call(&mut self, name: String) -> Expression {
        log!("parse_call: {:?}", self.peek());

        self.next(); // consume open paranthese (

        let mut args = Vec::new();
        if !matches!(self.peek(), Some(Token::Separator(')'))) {
            // parse arguments
            loop {
                args.push(self.parse_expression(0.0));

                match self.next() {
                    Some(Token::Separator(',')) => continue,
                    Some(Token::Separator(')')) => break,
                    _ => panic!("expected comma or paranthese"),
                }
            }
        } else {
            self.next(); // consume close paranthese )
        }
        Expression::Call { name, args }
    }
 }

struct Lowerer {
    code: Vec<Instruction>,
    temp_count: usize,
    label_count: usize,
    loop_stack: Vec<LoopContext>,
}

struct LoopContext {
    break_label: String,
    continue_label: String,
}

impl Lowerer {
    fn new() -> Self {
        Lowerer { 
            code: Vec::new(), 
            temp_count: 0, 
            label_count: 0, 
            loop_stack: Vec::new() 
        }
    }

    fn emit(&mut self, instr: Instruction) {
        log!("{:?}", &instr);
        self.code.push(instr);
    }

    fn next_temp(&mut self) -> Value {
        let count = self.temp_count;
        self.temp_count += 1;
        Value::Temp(count)
    }

    fn next_label(&mut self) -> String {
        let count = self.label_count;
        self.temp_count += 1;
        format!("L{}", count)
    }


}