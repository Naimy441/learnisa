fn main() {
    let name: &str = "Naim";
    let age: i32 = 22;
    let extra: &str = if age > 21 {
        "Wow you're an unc"
    } else {
        "lil bro *wink*"
    };
    println!("Hello {}, are you {}? If you are... {}", name, age, extra);

    let mut i = 0;
    while i < 20 {
        print!("{}", i);
        i += 1;
    }

    println!();

    for i in 1..3 {
        println!("{}", i);
    }
    let s = add(3, 4);
    println!("{}", s);

    let tokens = ["SEMICOLON", "COLON", "SPACE"];
    for t in tokens {
        println!("{}", t);
    }

    let mut tokens = vec!["SEMICOLON", "COLON"];
    tokens.push("SPACE");
    printvec(tokens);

}

fn add(a: i32, b: i32) -> i32 {
    a+b
}

fn printvec(v: Vec<&str>) {
    for x in v {
        println!("{}", x);
    }
}