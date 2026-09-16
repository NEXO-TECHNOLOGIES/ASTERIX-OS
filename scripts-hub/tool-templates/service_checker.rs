use std::env;
use std::process::Command;

fn main() {
    let args: Vec<String> = env::args().collect();
    let service = args.get(1).map(String::as_str).unwrap_or("sshd");

    let status = Command::new("systemctl")
        .args(["is-active", service])
        .output();

    match status {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);
            let exit_code = output.status.code().unwrap_or(-1);

            println!("service: {service}");
            println!("exit_code: {exit_code}");
            println!("status: {}", stdout.trim());
            if !stderr.trim().is_empty() {
                eprintln!("stderr: {}", stderr.trim());
            }
        }
        Err(err) => {
            eprintln!("failed to check service: {err}");
            std::process::exit(2);
        }
    }
}
