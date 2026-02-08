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

#[derive(Debug)]
enum Token {
    Keyword(String),
    Identifier(String),
    IntLiteral(String),
    BinaryOperator(String),
    UnaryOperator(char),
    Separator(char),
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

fn lexer(string: String) -> Vec<Token> {
    let mut tokens = Vec::new();
    let mut chars = string.chars().peekable();

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
                "if" | "else" | "for" | "while" | "break" | "continue" | "return" | "int" => Token::Keyword(buf),
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
                '-' | '~' => {
                    chars.next();
                    Token::UnaryOperator(c)
                },
                '+' | '-' | '*' => {
                    chars.next();
                    Token::BinaryOperator(c.to_string())
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
                        Token::BinaryOperator(c.to_string())
                    }
                },
                '&' => {
                    // handles &&
                    chars.next();
                    if matches!(chars.peek(), Some(&'&'))  {
                        chars.next();
                        Token::BinaryOperator(c.to_string().repeat(2))
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
                        Token::BinaryOperator(c.to_string().repeat(2))
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
                        Token::BinaryOperator(c.to_string() + "=")
                    } else {
                        Token::UnaryOperator(c)
                    }
                },
                '=' | '<' | '>' => {
                    // handles == or <= or >=
                    chars.next();
                    if matches!(chars.peek(), Some(&'='))  {
                        chars.next();
                        Token::BinaryOperator(c.to_string() + "=")
                    } else {
                        Token::BinaryOperator(c.to_string())
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

    tokens
}

fn printvec(v: &[String]) {
    for x in v {
        println!("{}", x);
    }
}