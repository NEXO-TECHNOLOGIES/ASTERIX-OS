//! =====================================================================
//! ASTERIX OS - Pure Rust Cryptographic Engine & Hash Analysis Suite
//! Implements: SHA-256 (FIPS 180-4), SHA-512 (FIPS 180-4), MD5 (RFC 1321)
//! Zero External Dependencies - 100% Standalone Memory-Safe Rust
//! =====================================================================

use std::env;
use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, Read, Write};
use std::path::{Path, PathBuf};
use std::time::Instant;

#[allow(dead_code)]
const C_RESET: &str = "\x1b[0m";
#[allow(dead_code)]
const C_BOLD: &str = "\x1b[1m";
#[allow(dead_code)]
const C_RED: &str = "\x1b[38;5;196m";
#[allow(dead_code)]
const C_YELLOW: &str = "\x1b[38;5;220m";
#[allow(dead_code)]
const C_GREEN: &str = "\x1b[38;5;46m";
#[allow(dead_code)]
const C_CYAN: &str = "\x1b[38;5;51m";
#[allow(dead_code)]
const C_BLUE: &str = "\x1b[38;5;45m";
#[allow(dead_code)]
const C_MAGENTA: &str = "\x1b[38;5;201m";
#[allow(dead_code)]
const C_WHITE: &str = "\x1b[38;5;231m";
#[allow(dead_code)]
const C_GRAY: &str = "\x1b[38;5;240m";

const BANNER: &str = r#"
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  █████╗ ███████╗   ██████╗██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗      ║
 ║ ██╔══██╗██╔════╝  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗     ║
 ║ ███████║███████╗  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║     ║
 ║ ██╔══██║╚════██║  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║     ║
 ║ ██║  ██║███████║  ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝     ║
 ║ ╚═╝  ╚═╝╚══════╝   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝      ║
 ║           >> CRYPTOGRAPHIC CORE & INTEGRITY SUITE <<                      ║
 ╚═══════════════════════════════════════════════════════════════════════════╝"#;

// =========================================================================
// 1. Pure Rust SHA-256 Implementation (FIPS 180-4)
// =========================================================================

pub struct Sha256 {
    state: [u32; 8],
    buffer: [u8; 64],
    buf_len: usize,
    total_len: u64,
}

impl Sha256 {
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ];

    pub fn new() -> Self {
        Self {
            state: [
                0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
            ],
            buffer: [0u8; 64],
            buf_len: 0,
            total_len: 0,
        }
    }

    fn compress(&mut self, chunk: &[u8]) {
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                chunk[i * 4],
                chunk[i * 4 + 1],
                chunk[i * 4 + 2],
                chunk[i * 4 + 3],
            ]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }

        let mut a = self.state[0];
        let mut b = self.state[1];
        let mut c = self.state[2];
        let mut d = self.state[3];
        let mut e = self.state[4];
        let mut f = self.state[5];
        let mut g = self.state[6];
        let mut h = self.state[7];

        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let temp1 = h.wrapping_add(s1).wrapping_add(ch).wrapping_add(Self::K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = s0.wrapping_add(maj);

            h = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }

        self.state[0] = self.state[0].wrapping_add(a);
        self.state[1] = self.state[1].wrapping_add(b);
        self.state[2] = self.state[2].wrapping_add(c);
        self.state[3] = self.state[3].wrapping_add(d);
        self.state[4] = self.state[4].wrapping_add(e);
        self.state[5] = self.state[5].wrapping_add(f);
        self.state[6] = self.state[6].wrapping_add(g);
        self.state[7] = self.state[7].wrapping_add(h);
    }

    pub fn update(&mut self, mut data: &[u8]) {
        self.total_len += data.len() as u64;

        if self.buf_len > 0 {
            let needed = 64 - self.buf_len;
            if data.len() >= needed {
                self.buffer[self.buf_len..64].copy_from_slice(&data[..needed]);
                let buf_copy = self.buffer;
                self.compress(&buf_copy);
                self.buf_len = 0;
                data = &data[needed..];
            } else {
                self.buffer[self.buf_len..self.buf_len + data.len()].copy_from_slice(data);
                self.buf_len += data.len();
                return;
            }
        }

        while data.len() >= 64 {
            self.compress(&data[..64]);
            data = &data[64..];
        }

        if !data.is_empty() {
            self.buffer[..data.len()].copy_from_slice(data);
            self.buf_len = data.len();
        }
    }

    pub fn finalize(mut self) -> [u8; 32] {
        let bit_len = self.total_len * 8;
        self.buffer[self.buf_len] = 0x80;
        self.buf_len += 1;

        if self.buf_len > 56 {
            for i in self.buf_len..64 {
                self.buffer[i] = 0;
            }
            let buf_copy = self.buffer;
            self.compress(&buf_copy);
            self.buf_len = 0;
        }

        for i in self.buf_len..56 {
            self.buffer[i] = 0;
        }

        self.buffer[56..64].copy_from_slice(&bit_len.to_be_bytes());
        let buf_copy = self.buffer;
        self.compress(&buf_copy);

        let mut out = [0u8; 32];
        for (i, &val) in self.state.iter().enumerate() {
            out[i * 4..i * 4 + 4].copy_from_slice(&val.to_be_bytes());
        }
        out
    }

    pub fn digest(data: &[u8]) -> String {
        let mut h = Self::new();
        h.update(data);
        bytes_to_hex(&h.finalize())
    }
}

// =========================================================================
// 2. Pure Rust SHA-512 Implementation (FIPS 180-4)
// =========================================================================

pub struct Sha512 {
    state: [u64; 8],
    buffer: [u8; 128],
    buf_len: usize,
    total_len: u128,
}

impl Sha512 {
    const K: [u64; 80] = [
        0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
        0x3956c25bf348b538, 0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
        0xd807aa98a3030242, 0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
        0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 0xc19bf174cf692694,
        0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
        0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
        0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4,
        0xc6e00bf33da88fc2, 0xd5a79147930aa725, 0x06ca6351e003826f, 0x142929670a0e6e70,
        0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
        0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47867d66, 0x92722c851482353b,
        0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30,
        0xd192e819d6ef5218, 0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
        0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
        0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
        0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
        0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b,
        0xca273eceea26619c, 0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
        0x06f067aa72176fba, 0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
        0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
        0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817,
    ];

    pub fn new() -> Self {
        Self {
            state: [
                0x6a09e667f3bcc908, 0xbb67ae8584caa73b, 0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
                0x510e527fade682d1, 0x9b05688c2b3e6c1f, 0x1f83d9abfb41bd6b, 0x5be0cd19137e2179,
            ],
            buffer: [0u8; 128],
            buf_len: 0,
            total_len: 0,
        }
    }

    fn compress(&mut self, chunk: &[u8]) {
        let mut w = [0u64; 80];
        for i in 0..16 {
            w[i] = u64::from_be_bytes([
                chunk[i * 8],     chunk[i * 8 + 1], chunk[i * 8 + 2], chunk[i * 8 + 3],
                chunk[i * 8 + 4], chunk[i * 8 + 5], chunk[i * 8 + 6], chunk[i * 8 + 7],
            ]);
        }
        for i in 16..80 {
            let s0 = w[i - 15].rotate_right(1) ^ w[i - 15].rotate_right(8) ^ (w[i - 15] >> 7);
            let s1 = w[i - 2].rotate_right(19) ^ w[i - 2].rotate_right(61) ^ (w[i - 2] >> 6);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }

        let mut a = self.state[0];
        let mut b = self.state[1];
        let mut c = self.state[2];
        let mut d = self.state[3];
        let mut e = self.state[4];
        let mut f = self.state[5];
        let mut g = self.state[6];
        let mut h = self.state[7];

        for i in 0..80 {
            let s1 = e.rotate_right(14) ^ e.rotate_right(18) ^ e.rotate_right(41);
            let ch = (e & f) ^ ((!e) & g);
            let temp1 = h.wrapping_add(s1).wrapping_add(ch).wrapping_add(Self::K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(28) ^ a.rotate_right(34) ^ a.rotate_right(39);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = s0.wrapping_add(maj);

            h = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }

        self.state[0] = self.state[0].wrapping_add(a);
        self.state[1] = self.state[1].wrapping_add(b);
        self.state[2] = self.state[2].wrapping_add(c);
        self.state[3] = self.state[3].wrapping_add(d);
        self.state[4] = self.state[4].wrapping_add(e);
        self.state[5] = self.state[5].wrapping_add(f);
        self.state[6] = self.state[6].wrapping_add(g);
        self.state[7] = self.state[7].wrapping_add(h);
    }

    pub fn update(&mut self, mut data: &[u8]) {
        self.total_len += data.len() as u128;

        if self.buf_len > 0 {
            let needed = 128 - self.buf_len;
            if data.len() >= needed {
                self.buffer[self.buf_len..128].copy_from_slice(&data[..needed]);
                let buf_copy = self.buffer;
                self.compress(&buf_copy);
                self.buf_len = 0;
                data = &data[needed..];
            } else {
                self.buffer[self.buf_len..self.buf_len + data.len()].copy_from_slice(data);
                self.buf_len += data.len();
                return;
            }
        }

        while data.len() >= 128 {
            self.compress(&data[..128]);
            data = &data[128..];
        }

        if !data.is_empty() {
            self.buffer[..data.len()].copy_from_slice(data);
            self.buf_len = data.len();
        }
    }

    pub fn finalize(mut self) -> [u8; 64] {
        let bit_len = self.total_len * 8;
        self.buffer[self.buf_len] = 0x80;
        self.buf_len += 1;

        if self.buf_len > 112 {
            for i in self.buf_len..128 {
                self.buffer[i] = 0;
            }
            let buf_copy = self.buffer;
            self.compress(&buf_copy);
            self.buf_len = 0;
        }

        for i in self.buf_len..112 {
            self.buffer[i] = 0;
        }

        self.buffer[112..128].copy_from_slice(&bit_len.to_be_bytes());
        let buf_copy = self.buffer;
        self.compress(&buf_copy);

        let mut out = [0u8; 64];
        for (i, &val) in self.state.iter().enumerate() {
            out[i * 8..i * 8 + 8].copy_from_slice(&val.to_be_bytes());
        }
        out
    }

    pub fn digest(data: &[u8]) -> String {
        let mut h = Self::new();
        h.update(data);
        bytes_to_hex(&h.finalize())
    }
}

// =========================================================================
// 3. Pure Rust MD5 Implementation (RFC 1321)
// =========================================================================

pub struct Md5 {
    state: [u32; 4],
    buffer: [u8; 64],
    buf_len: usize,
    total_len: u64,
}

impl Md5 {
    const S: [u32; 64] = [
        7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
        5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
        4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
        6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,
    ];

    const K: [u32; 64] = [
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
    ];

    pub fn new() -> Self {
        Self {
            state: [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476],
            buffer: [0u8; 64],
            buf_len: 0,
            total_len: 0,
        }
    }

    fn compress(&mut self, chunk: &[u8]) {
        let mut m = [0u32; 16];
        for i in 0..16 {
            m[i] = u32::from_le_bytes([
                chunk[i * 4], chunk[i * 4 + 1], chunk[i * 4 + 2], chunk[i * 4 + 3]
            ]);
        }

        let mut a = self.state[0];
        let mut b = self.state[1];
        let mut c = self.state[2];
        let mut d = self.state[3];

        for i in 0..64 {
            let (f, g) = if i < 16 {
                ((b & c) | ((!b) & d), i)
            } else if i < 32 {
                ((d & b) | ((!d) & c), (5 * i + 1) % 16)
            } else if i < 48 {
                (b ^ c ^ d, (3 * i + 5) % 16)
            } else {
                (c ^ (b | (!d)), (7 * i) % 16)
            };

            let temp = d;
            d = c;
            c = b;
            let sum = a.wrapping_add(f).wrapping_add(Self::K[i]).wrapping_add(m[g]);
            b = b.wrapping_add(sum.rotate_left(Self::S[i]));
            a = temp;
        }

        self.state[0] = self.state[0].wrapping_add(a);
        self.state[1] = self.state[1].wrapping_add(b);
        self.state[2] = self.state[2].wrapping_add(c);
        self.state[3] = self.state[3].wrapping_add(d);
    }

    pub fn update(&mut self, mut data: &[u8]) {
        self.total_len += data.len() as u64;

        if self.buf_len > 0 {
            let needed = 64 - self.buf_len;
            if data.len() >= needed {
                self.buffer[self.buf_len..64].copy_from_slice(&data[..needed]);
                let buf_copy = self.buffer;
                self.compress(&buf_copy);
                self.buf_len = 0;
                data = &data[needed..];
            } else {
                self.buffer[self.buf_len..self.buf_len + data.len()].copy_from_slice(data);
                self.buf_len += data.len();
                return;
            }
        }

        while data.len() >= 64 {
            self.compress(&data[..64]);
            data = &data[64..];
        }

        if !data.is_empty() {
            self.buffer[..data.len()].copy_from_slice(data);
            self.buf_len = data.len();
        }
    }

    pub fn finalize(mut self) -> [u8; 16] {
        let bit_len = self.total_len * 8;
        self.buffer[self.buf_len] = 0x80;
        self.buf_len += 1;

        if self.buf_len > 56 {
            for i in self.buf_len..64 {
                self.buffer[i] = 0;
            }
            let buf_copy = self.buffer;
            self.compress(&buf_copy);
            self.buf_len = 0;
        }

        for i in self.buf_len..56 {
            self.buffer[i] = 0;
        }

        self.buffer[56..64].copy_from_slice(&bit_len.to_le_bytes());
        let buf_copy = self.buffer;
        self.compress(&buf_copy);

        let mut out = [0u8; 16];
        for (i, &val) in self.state.iter().enumerate() {
            out[i * 4..i * 4 + 4].copy_from_slice(&val.to_le_bytes());
        }
        out
    }

    pub fn digest(data: &[u8]) -> String {
        let mut h = Self::new();
        h.update(data);
        bytes_to_hex(&h.finalize())
    }
}

// =========================================================================
// 4. Pure Rust ChaCha20 Stream Cipher Implementation (RFC 7539)
// =========================================================================

pub struct ChaCha20 {
    state: [u32; 16],
}

impl ChaCha20 {
    pub fn new(key: &[u8; 32], nonce: &[u8; 12], counter: u32) -> Self {
        let mut state = [0u32; 16];
        state[0] = 0x61707865;
        state[1] = 0x3320646e;
        state[2] = 0x79622d32;
        state[3] = 0x6b206574;
        for i in 0..8 {
            state[4 + i] = u32::from_le_bytes([
                key[i * 4], key[i * 4 + 1], key[i * 4 + 2], key[i * 4 + 3]
            ]);
        }
        state[12] = counter;
        for i in 0..3 {
            state[13 + i] = u32::from_le_bytes([
                nonce[i * 4], nonce[i * 4 + 1], nonce[i * 4 + 2], nonce[i * 4 + 3]
            ]);
        }
        Self { state }
    }

    fn quarter_round(x: &mut [u32; 16], a: usize, b: usize, c: usize, d: usize) {
        x[a] = x[a].wrapping_add(x[b]); x[d] ^= x[a]; x[d] = x[d].rotate_left(16);
        x[c] = x[c].wrapping_add(x[d]); x[b] ^= x[c]; x[b] = x[b].rotate_left(12);
        x[a] = x[a].wrapping_add(x[b]); x[d] ^= x[a]; x[d] = x[d].rotate_left(8);
        x[c] = x[c].wrapping_add(x[d]); x[b] ^= x[c]; x[b] = x[b].rotate_left(7);
    }

    pub fn process(&mut self, data: &mut [u8]) {
        for chunk in data.chunks_mut(64) {
            let mut working = self.state;
            for _ in 0..10 {
                // Column rounds
                Self::quarter_round(&mut working, 0, 4, 8, 12);
                Self::quarter_round(&mut working, 1, 5, 9, 13);
                Self::quarter_round(&mut working, 2, 6, 10, 14);
                Self::quarter_round(&mut working, 3, 7, 11, 15);
                // Diagonal rounds
                Self::quarter_round(&mut working, 0, 5, 10, 15);
                Self::quarter_round(&mut working, 1, 6, 11, 12);
                Self::quarter_round(&mut working, 2, 7, 8, 13);
                Self::quarter_round(&mut working, 3, 4, 9, 14);
            }

            for i in 0..16 {
                working[i] = working[i].wrapping_add(self.state[i]);
            }

            let mut keystream = [0u8; 64];
            for i in 0..16 {
                keystream[i * 4..i * 4 + 4].copy_from_slice(&working[i].to_le_bytes());
            }

            let chunk_len = chunk.len();
            for (b, &k) in chunk.iter_mut().zip(&keystream[..chunk_len]) {
                *b ^= k;
            }

            self.state[12] = self.state[12].wrapping_add(1);
        }
    }
}

pub fn derive_cipher_keys(passphrase: &str) -> ([u8; 32], [u8; 12]) {
    let mut s256 = Sha256::new();
    s256.update(passphrase.as_bytes());
    let key = s256.finalize();

    let mut smd5 = Md5::new();
    smd5.update(&key);
    let md5_hash = smd5.finalize();
    let mut nonce = [0u8; 12];
    nonce.copy_from_slice(&md5_hash[0..12]);

    (key, nonce)
}

fn bytes_to_hex(bytes: &[u8]) -> String {
    let mut s = String::with_capacity(bytes.len() * 2);
    for &b in bytes {
        s.push_str(&format!("{:02x}", b));
    }
    s
}

fn calculate_entropy(data: &[u8]) -> f64 {
    if data.is_empty() {
        return 0.0;
    }
    let mut counts = [0usize; 256];
    for &b in data {
        counts[b as usize] += 1;
    }
    let len_f = data.len() as f64;
    let mut entropy = 0.0;
    for &count in &counts {
        if count > 0 {
            let p = count as f64 / len_f;
            entropy -= p * p.log2();
        }
    }
    entropy
}

fn identify_hash(hash_str: &str) {
    let trimmed = hash_str.trim();
    println!("{C_CYAN}{C_BOLD} 🔎 ASTERIX CRYPTOGRAPHIC HASH IDENTIFIER{C_RESET}");
    println!("{C_GRAY}{}{C_RESET}", "─".repeat(65));
    println!("  {C_WHITE}Input String:{C_RESET} {C_YELLOW}{trimmed}{C_RESET}");
    println!("  {C_WHITE}Length:{C_RESET}       {} characters", trimmed.len());

    let is_hex = trimmed.chars().all(|c| c.is_ascii_hexdigit());

    println!("  {C_CYAN}Possible Hash Formats:{C_RESET}");
    if trimmed.starts_with("$6$") {
        println!("  {C_GREEN}✔ SHA-512 Crypt (UNIX /etc/shadow standard){C_RESET}");
    } else if trimmed.starts_with("$5$") {
        println!("  {C_GREEN}✔ SHA-256 Crypt (UNIX /etc/shadow standard){C_RESET}");
    } else if trimmed.starts_with("$1$") {
        println!("  {C_YELLOW}✔ MD5 Crypt (Legacy UNIX /etc/shadow){C_RESET}");
    } else if trimmed.starts_with("$2a$") || trimmed.starts_with("$2b$") || trimmed.starts_with("$2y$") {
        println!("  {C_GREEN}✔ bcrypt Password Hash{C_RESET}");
    } else if trimmed.starts_with("$argon2") {
        println!("  {C_GREEN}✔ Argon2 Password Hashing Function{C_RESET}");
    } else if is_hex {
        match trimmed.len() {
            32 => {
                println!("  {C_GREEN}✔ MD5 (128-bit RFC 1321){C_RESET}");
                println!("  {C_GREEN}✔ NTLM (Windows NT LAN Manager){C_RESET}");
                println!("  {C_GREEN}✔ MD4 / LM Hash{C_RESET}");
            }
            40 => {
                println!("  {C_GREEN}✔ SHA-1 (160-bit FIPS 180-1){C_RESET}");
                println!("  {C_GREEN}✔ RIPEMD-160{C_RESET}");
            }
            56 => {
                println!("  {C_GREEN}✔ SHA-224 / SHA3-224{C_RESET}");
            }
            64 => {
                println!("  {C_GREEN}✔ SHA-256 (256-bit FIPS 180-4 standard){C_RESET}");
                println!("  {C_GREEN}✔ Blake2s / Blake3{C_RESET}");
                println!("  {C_GREEN}✔ Keccak-256 / SHA3-256{C_RESET}");
            }
            96 => {
                println!("  {C_GREEN}✔ SHA-384 (384-bit FIPS 180-4){C_RESET}");
            }
            128 => {
                println!("  {C_GREEN}✔ SHA-512 (512-bit FIPS 180-4){C_RESET}");
                println!("  {C_GREEN}✔ Whirlpool / Keccak-512 / Blake2b{C_RESET}");
            }
            _ => {
                println!("  {C_YELLOW}[!] Non-standard hex hash length. Custom algorithm or partial digest.{C_RESET}");
            }
        }
    } else {
        println!("  {C_YELLOW}[!] Non-hexadecimal input. Might be base64-encoded digest or salted string.{C_RESET}");
    }
    println!("{C_GRAY}{}{C_RESET}\n", "─".repeat(65));
}

fn hash_stream<R: Read>(mut r: R, algo: &str) -> io::Result<(String, String, String)> {
    let mut s256 = Sha256::new();
    let mut s512 = Sha512::new();
    let mut smd5 = Md5::new();

    let mut buf = [0u8; 65536];
    loop {
        let n = r.read(&mut buf)?;
        if n == 0 { break; }
        let chunk = &buf[..n];
        if algo == "sha256" || algo == "all" { s256.update(chunk); }
        if algo == "sha512" || algo == "all" { s512.update(chunk); }
        if algo == "md5" || algo == "all" { smd5.update(chunk); }
    }

    let h256 = if algo == "sha256" || algo == "all" { bytes_to_hex(&s256.finalize()) } else { String::new() };
    let h512 = if algo == "sha512" || algo == "all" { bytes_to_hex(&s512.finalize()) } else { String::new() };
    let hmd5 = if algo == "md5" || algo == "all" { bytes_to_hex(&smd5.finalize()) } else { String::new() };

    Ok((h256, h512, hmd5))
}

fn create_manifest(dir: &Path, output_file: &Path) -> io::Result<()> {
    println!("{C_CYAN}{C_BOLD}[*] Generating ASTERIX Cryptographic Integrity Manifest (.axsum)...{C_RESET}");
    let mut entries = Vec::new();

    fn collect_files(dir: &Path, list: &mut Vec<PathBuf>) -> io::Result<()> {
        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();
            if path.is_file() {
                list.push(path);
            } else if path.is_dir() {
                collect_files(&path, list)?;
            }
        }
        Ok(())
    }

    collect_files(dir, &mut entries)?;
    entries.sort();

    let mut out = File::create(output_file)?;
    writeln!(out, "# ASTERIX OS Cryptographic Integrity Manifest (.axsum)")?;
    writeln!(out, "# Algorithm: SHA-256 (FIPS 180-4)")?;
    writeln!(out, "# Generated At: {:?}", std::time::SystemTime::now())?;

    for p in &entries {
        if let Ok(file) = File::open(p) {
            if let Ok((h256, _, _)) = hash_stream(file, "sha256") {
                let rel = p.strip_prefix(dir).unwrap_or(p);
                writeln!(out, "{}  {}", h256, rel.display())?;
                println!("  {C_GREEN}✔{C_RESET} {C_CYAN}{h256}{C_RESET}  {C_WHITE}{}{C_RESET}", rel.display());
            }
        }
    }

    println!("{C_GREEN}{C_BOLD}[✔] Manifest saved to: {}{C_RESET}\n", output_file.display());
    Ok(())
}

fn verify_manifest(manifest_file: &Path, base_dir: &Path) -> io::Result<()> {
    println!("{C_CYAN}{C_BOLD}[*] Verifying Integrity against Manifest: {}...{C_RESET}\n", manifest_file.display());
    let file = File::open(manifest_file)?;
    let reader = BufReader::new(file);

    let mut passed = 0usize;
    let mut failed = 0usize;
    let mut missing = 0usize;

    for line in reader.lines() {
        let line = line?;
        let trimmed = line.trim();
        if trimmed.starts_with('#') || trimmed.is_empty() {
            continue;
        }

        let parts: Vec<&str> = trimmed.split_whitespace().collect();
        if parts.len() < 2 {
            continue;
        }

        let expected_hash = parts[0];
        let rel_path = parts[1..].join(" ");
        let full_path = base_dir.join(&rel_path);

        if !full_path.exists() {
            println!("  {C_RED}✖ MISSING:{C_RESET}  {}", rel_path);
            missing += 1;
            continue;
        }

        match File::open(&full_path) {
            Ok(f) => {
                if let Ok((actual_hash, _, _)) = hash_stream(f, "sha256") {
                    if actual_hash.eq_ignore_ascii_case(expected_hash) {
                        println!("  {C_GREEN}✔ OK:{C_RESET}       {}", rel_path);
                        passed += 1;
                    } else {
                        println!("  {C_RED}✖ MISMATCH:{C_RESET} {} (Expected {expected_hash}, got {actual_hash})", rel_path);
                        failed += 1;
                    }
                }
            }
            Err(e) => {
                println!("  {C_RED}✖ ERROR:{C_RESET}    {} ({})", rel_path, e);
                failed += 1;
            }
        }
    }

    println!("\n{C_BLUE}{}{C_RESET}", "═".repeat(65));
    println!(" {C_WHITE}Integrity Verification Summary:{C_RESET}");
    println!("  {C_GREEN}Passed:{C_RESET}  {}", passed);
    println!("  {C_RED}Failed:{C_RESET}  {}", failed);
    println!("  {C_YELLOW}Missing:{C_RESET} {}", missing);
    println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(65));

    Ok(())
}

fn run_benchmarks() {
    println!("{C_CYAN}{C_BOLD} ⚡ BENCHMARKING CRYPTOGRAPHIC HASH THROUGHPUT{C_RESET}");
    println!("{C_GRAY}{}{C_RESET}", "─".repeat(65));

    let size_bytes = 10 * 1024 * 1024; // 10 MB buffer
    let buffer = vec![0x5Au8; size_bytes];

    // SHA-256
    let start = Instant::now();
    let _ = Sha256::digest(&buffer);
    let dur256 = start.elapsed().as_secs_f64();
    let mb256 = (size_bytes as f64 / (1024.0 * 1024.0)) / dur256;
    println!("  {C_WHITE}SHA-256 (FIPS 180-4):{C_RESET} {C_GREEN}{:.2} MB/s{C_RESET} ({:.3}s for 10MB)", mb256, dur256);

    // SHA-512
    let start = Instant::now();
    let _ = Sha512::digest(&buffer);
    let dur512 = start.elapsed().as_secs_f64();
    let mb512 = (size_bytes as f64 / (1024.0 * 1024.0)) / dur512;
    println!("  {C_WHITE}SHA-512 (FIPS 180-4):{C_RESET} {C_GREEN}{:.2} MB/s{C_RESET} ({:.3}s for 10MB)", mb512, dur512);

    // MD5
    let start = Instant::now();
    let _ = Md5::digest(&buffer);
    let durmd5 = start.elapsed().as_secs_f64();
    let mbmd5 = (size_bytes as f64 / (1024.0 * 1024.0)) / durmd5;
    println!("  {C_WHITE}MD5 (RFC 1321):{C_RESET}       {C_YELLOW}{:.2} MB/s{C_RESET} ({:.3}s for 10MB)", mbmd5, durmd5);

    println!("{C_GRAY}{}{C_RESET}\n", "─".repeat(65));
}

fn print_help() {
    println!("{C_CYAN}{C_BOLD}{}{C_RESET}", BANNER);
    println!(r#"
USAGE:
    asterix-crypto-core <SUBCOMMAND> [OPTIONS]

SUBCOMMANDS:
    hash <FILE|STRING>      Calculate cryptographic hashes (SHA-256, SHA-512, MD5)
        --algo <ALGO>       Algorithm: sha256 | sha512 | md5 | all (Default: all)
        --str               Treat argument as raw string instead of file path
    identify <HASH>         Identify cryptographic hash algorithm by length & structure
    entropy <FILE>          Calculate Shannon entropy & randomness distribution
    manifest <DIR>          Generate cryptographic '.axsum' directory manifest
        -o, --out <FILE>    Output manifest file (Default: manifest.axsum)
    verify <MANIFEST>       Verify directory files against an '.axsum' manifest
        -d, --dir <DIR>     Base directory to verify against (Default: .)
    bench                   Run microsecond hashing throughput benchmark
    -h, --help              Show this help manual

EXAMPLES:
    asterix-crypto-core hash /bin/bash --algo sha256
    asterix-crypto-core hash "cyber-secret-key" --str
    asterix-crypto-core identify 5f4dcc3b5aa765d61d8327deb882cf99
    asterix-crypto-core manifest /etc/asterix -o asterix-core.axsum
    asterix-crypto-core verify asterix-core.axsum -d /etc/asterix
    asterix-crypto-core bench
"#);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 || args.contains(&"--help".to_string()) || args.contains(&"-h".to_string()) {
        print_help();
        return;
    }

    match args[1].as_str() {
        "hash" => {
            if args.len() < 3 {
                eprintln!("{C_RED}[!] Error: Missing target file or string to hash.{C_RESET}");
                return;
            }
            let is_str = args.contains(&"--str".to_string());
            let mut algo = "all".to_string();
            if let Some(pos) = args.iter().position(|a| a == "--algo") {
                if pos + 1 < args.len() {
                    algo = args[pos + 1].to_lowercase();
                }
            }

            let input = &args[2];
            println!("{C_CYAN}{C_BOLD}{}{C_RESET}", BANNER);
            println!("{C_BLUE}{}{C_RESET}", "═".repeat(78));

            if is_str {
                println!(" {C_WHITE}INPUT STRING:{C_RESET} {C_YELLOW}{}{C_RESET}", input);
                println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(78));
                let bytes = input.as_bytes();
                if algo == "sha256" || algo == "all" {
                    println!("  {C_CYAN}SHA-256:{C_RESET} {C_GREEN}{}{C_RESET}", Sha256::digest(bytes));
                }
                if algo == "sha512" || algo == "all" {
                    println!("  {C_CYAN}SHA-512:{C_RESET} {C_GREEN}{}{C_RESET}", Sha512::digest(bytes));
                }
                if algo == "md5" || algo == "all" {
                    println!("  {C_CYAN}MD5:    {C_RESET} {C_YELLOW}{}{C_RESET}", Md5::digest(bytes));
                }
            } else {
                let p = Path::new(input);
                if !p.exists() {
                    eprintln!("{C_RED}[!] Error: File '{}' not found.{C_RESET}", input);
                    return;
                }
                println!(" {C_WHITE}TARGET FILE:{C_RESET} {C_YELLOW}{}{C_RESET}", input);
                println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(78));

                if let Ok(file) = File::open(p) {
                    if let Ok((h256, h512, hmd5)) = hash_stream(file, &algo) {
                        if !h256.is_empty() { println!("  {C_CYAN}SHA-256:{C_RESET} {C_GREEN}{}{C_RESET}", h256); }
                        if !h512.is_empty() { println!("  {C_CYAN}SHA-512:{C_RESET} {C_GREEN}{}{C_RESET}", h512); }
                        if !hmd5.is_empty() { println!("  {C_CYAN}MD5:    {C_RESET} {C_YELLOW}{}{C_RESET}", hmd5); }
                    }
                }
            }
            println!();
        }
        "identify" | "id" => {
            if args.len() < 3 {
                eprintln!("{C_RED}[!] Error: Hash string not provided.{C_RESET}");
                return;
            }
            identify_hash(&args[2]);
        }
        "entropy" => {
            if args.len() < 3 {
                eprintln!("{C_RED}[!] Error: Target file not provided.{C_RESET}");
                return;
            }
            let p = Path::new(&args[2]);
            if let Ok(mut f) = File::open(p) {
                let mut buf = Vec::new();
                if f.read_to_end(&mut buf).is_ok() {
                    let ent = calculate_entropy(&buf);
                    println!("{C_CYAN}{C_BOLD} 📊 SHANNON ENTROPY AUDIT: {}{C_RESET}", args[2]);
                    println!("{C_GRAY}{}{C_RESET}", "─".repeat(60));
                    println!("  {C_WHITE}Entropy:{C_RESET}     {C_YELLOW}{:.4}{C_RESET} / 8.0000", ent);
                    if ent > 7.2 {
                        println!("  {C_WHITE}Classification:{C_RESET} {C_RED}HIGH ENTROPY (Encrypted, Compressed, or Packed Data){C_RESET}");
                    } else if ent > 4.5 {
                        println!("  {C_WHITE}Classification:{C_RESET} {C_GREEN}MODERATE ENTROPY (Standard Executable Code / Data){C_RESET}");
                    } else {
                        println!("  {C_WHITE}Classification:{C_RESET} {C_CYAN}LOW ENTROPY (Plaintext or Sparse Binary){C_RESET}");
                    }
                    println!("{C_GRAY}{}{C_RESET}\n", "─".repeat(60));
                }
            }
        }
        "manifest" => {
            if args.len() < 3 {
                eprintln!("{C_RED}[!] Error: Target directory not provided.{C_RESET}");
                return;
            }
            let target_dir = Path::new(&args[2]);
            let mut out_file = PathBuf::from("manifest.axsum");
            if let Some(pos) = args.iter().position(|a| a == "-o" || a == "--out") {
                if pos + 1 < args.len() {
                    out_file = PathBuf::from(&args[pos + 1]);
                }
            }
            let _ = create_manifest(target_dir, &out_file);
        }
        "verify" => {
            if args.len() < 3 {
                eprintln!("{C_RED}[!] Error: Manifest file not provided.{C_RESET}");
                return;
            }
            let manifest_path = Path::new(&args[2]);
            let mut base_dir = PathBuf::from(".");
            if let Some(pos) = args.iter().position(|a| a == "-d" || a == "--dir") {
                if pos + 1 < args.len() {
                    base_dir = PathBuf::from(&args[pos + 1]);
                }
            }
            let _ = verify_manifest(manifest_path, &base_dir);
        }
        "bench" => {
            run_benchmarks();
        }
        "encrypt" | "decrypt" | "enc" | "dec" => {
            if args.len() < 5 {
                eprintln!("{C_RED}[!] Error: Usage: asterix-crypto-core encrypt/decrypt <input> <output> <passphrase>{C_RESET}");
                return;
            }
            let in_path = Path::new(&args[2]);
            let out_path = Path::new(&args[3]);
            let passphrase = &args[4];

            let mut input_data = Vec::new();
            match File::open(in_path) {
                Ok(mut f) => {
                    if let Err(e) = f.read_to_end(&mut input_data) {
                        eprintln!("{C_RED}[!] Error reading file {}: {}{C_RESET}", in_path.display(), e);
                        return;
                    }
                }
                Err(e) => {
                    eprintln!("{C_RED}[!] Failed to open input {}: {}{C_RESET}", in_path.display(), e);
                    return;
                }
            }

            println!("{C_CYAN}{C_BOLD}[*] Applying ChaCha20-256 Cryptographic Transformation...{C_RESET}");
            let (key, nonce) = derive_cipher_keys(passphrase);
            let mut cipher = ChaCha20::new(&key, &nonce, 1);
            cipher.process(&mut input_data);

            match File::create(out_path) {
                Ok(mut out) => {
                    if let Err(e) = out.write_all(&input_data) {
                        eprintln!("{C_RED}[!] Error writing to {}: {}{C_RESET}", out_path.display(), e);
                        return;
                    }
                    println!("{C_GREEN}{C_BOLD}[✔] SUCCESS: Operation completed. Output written to: {}{C_RESET}", out_path.display());
                }
                Err(e) => {
                    eprintln!("{C_RED}[!] Failed to create output {}: {}{C_RESET}", out_path.display(), e);
                }
            }
        }
        _ => {
            print_help();
        }
    }
}
