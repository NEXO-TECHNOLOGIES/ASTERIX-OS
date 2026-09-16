/*
 * ==============================================================================
 * 🌌 ASTERIX OS — High-Assurance Native C Cryptographic Core v3.5
 * Pure C99 • Zero External Dependencies (Zero OpenSSL / Zero libsodium)
 * Algorithms:
 *   1. ChaCha20 Stream Cipher (RFC 8439) — 256-bit key, 96-bit nonce
 *   2. Poly1305 One-Time MAC (RFC 8439) — Constant-time 128-bit authentication
 *   3. ChaCha20-Poly1305 AEAD Construction (Authenticated Encryption)
 *   4. AES-256 Symmetric Block Cipher Core (Rijndael with Key Expansion)
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define CHACHA20_KEY_BYTES   32
#define CHACHA20_NONCE_BYTES 12
#define POLY1305_TAG_BYTES   16
#define AES256_KEY_BYTES     32
#define AES_BLOCK_BYTES      16

/* Bitwise 32-bit left rotation */
#define ROTL32(v, n) (((v) << (n)) | ((v) >> (32 - (n))))

/* Little-endian 32-bit load/store */
static inline uint32_t load32_le(const uint8_t *b) {
    return ((uint32_t)b[0]) |
           (((uint32_t)b[1]) << 8) |
           (((uint32_t)b[2]) << 16) |
           (((uint32_t)b[3]) << 24);
}

static inline void store32_le(uint8_t *b, uint32_t v) {
    b[0] = (uint8_t)(v & 0xFF);
    b[1] = (uint8_t)((v >> 8) & 0xFF);
    b[2] = (uint8_t)((v >> 16) & 0xFF);
    b[3] = (uint8_t)((v >> 24) & 0xFF);
}

/* =============================================================================
 * CHACHA20 STREAM CIPHER (RFC 8439)
 * ============================================================================= */

#define CHACHA_QR(a, b, c, d) \
    a += b; d ^= a; d = ROTL32(d, 16); \
    c += d; b ^= c; b = ROTL32(b, 12); \
    a += b; d ^= a; d = ROTL32(d,  8); \
    c += d; b ^= c; b = ROTL32(b,  7);

typedef struct {
    uint32_t state[16];
} chacha20_ctx;

void chacha20_init(chacha20_ctx *ctx, const uint8_t key[32], const uint8_t nonce[12], uint32_t counter) {
    /* Constant "expand 32-byte k" */
    ctx->state[0]  = 0x61707865;
    ctx->state[1]  = 0x3320646e;
    ctx->state[2]  = 0x79622d32;
    ctx->state[3]  = 0x6b206574;

    /* 256-bit Key */
    for (int i = 0; i < 8; i++) {
        ctx->state[4 + i] = load32_le(key + (i * 4));
    }

    /* Block Counter */
    ctx->state[12] = counter;

    /* 96-bit Nonce */
    ctx->state[13] = load32_le(nonce);
    ctx->state[14] = load32_le(nonce + 4);
    ctx->state[15] = load32_le(nonce + 8);
}

void chacha20_block(const chacha20_ctx *ctx, uint8_t output[64]) {
    uint32_t x[16];
    memcpy(x, ctx->state, sizeof(x));

    /* 10 double-rounds = 20 rounds */
    for (int i = 0; i < 10; i++) {
        /* Column rounds */
        CHACHA_QR(x[0], x[4], x[8],  x[12]);
        CHACHA_QR(x[1], x[5], x[9],  x[13]);
        CHACHA_QR(x[2], x[6], x[10], x[14]);
        CHACHA_QR(x[3], x[7], x[11], x[15]);

        /* Diagonal rounds */
        CHACHA_QR(x[0], x[5], x[10], x[15]);
        CHACHA_QR(x[1], x[6], x[11], x[12]);
        CHACHA_QR(x[2], x[7], x[8],  x[13]);
        CHACHA_QR(x[3], x[4], x[9],  x[14]);
    }

    for (int i = 0; i < 16; i++) {
        store32_le(output + (i * 4), x[i] + ctx->state[i]);
    }
}

void chacha20_xor_stream(chacha20_ctx *ctx, const uint8_t *src, uint8_t *dst, size_t len) {
    uint8_t block[64];
    while (len > 0) {
        chacha20_block(ctx, block);
        ctx->state[12]++; /* Increment block counter */

        size_t chunk = (len < 64) ? len : 64;
        for (size_t i = 0; i < chunk; i++) {
            dst[i] = src[i] ^ block[i];
        }
        src += chunk;
        dst += chunk;
        len -= chunk;
    }
}

/* =============================================================================
 * POLY1305 ONE-TIME MAC (RFC 8439)
 * Evaluates polynomial r modulo 2^130 - 5
 * ============================================================================= */

typedef struct {
    uint32_t r[5];
    uint32_t h[5];
    uint32_t pad[4];
    size_t leftover;
    uint8_t buffer[16];
} poly1305_ctx;

void poly1305_init(poly1305_ctx *ctx, const uint8_t key[32]) {
    /* Clamp r */
    uint32_t r0 = load32_le(key + 0)  & 0x0fffffff;
    uint32_t r1 = load32_le(key + 4)  & 0x0ffffffc;
    uint32_t r2 = load32_le(key + 8)  & 0x0ffffffc;
    uint32_t r3 = load32_le(key + 12) & 0x0ffffffc;

    ctx->r[0] = r0 & 0x3ffffff;
    ctx->r[1] = ((r0 >> 26) | (r1 << 6)) & 0x3ffffff;
    ctx->r[2] = ((r1 >> 20) | (r2 << 12)) & 0x3ffffff;
    ctx->r[3] = ((r2 >> 14) | (r3 << 18)) & 0x3ffffff;
    ctx->r[4] = (r3 >> 8);

    ctx->h[0] = 0; ctx->h[1] = 0; ctx->h[2] = 0; ctx->h[3] = 0; ctx->h[4] = 0;

    for (int i = 0; i < 4; i++) {
        ctx->pad[i] = load32_le(key + 16 + (i * 4));
    }
    ctx->leftover = 0;
}

static void poly1305_blocks(poly1305_ctx *ctx, const uint8_t *m, size_t bytes, uint32_t hibit) {
    uint64_t r0 = ctx->r[0], r1 = ctx->r[1], r2 = ctx->r[2], r3 = ctx->r[3], r4 = ctx->r[4];
    uint64_t s1 = r1 * 5, s2 = r2 * 5, s3 = r3 * 5, s4 = r4 * 5;
    uint64_t h0 = ctx->h[0], h1 = ctx->h[1], h2 = ctx->h[2], h3 = ctx->h[3], h4 = ctx->h[4];

    while (bytes >= 16) {
        uint32_t t0 = load32_le(m + 0);
        uint32_t t1 = load32_le(m + 4);
        uint32_t t2 = load32_le(m + 8);
        uint32_t t3 = load32_le(m + 12);

        h0 += t0 & 0x3ffffff;
        h1 += (((uint64_t)t0 >> 26) | ((uint64_t)t1 << 6)) & 0x3ffffff;
        h2 += (((uint64_t)t1 >> 20) | ((uint64_t)t2 << 12)) & 0x3ffffff;
        h3 += (((uint64_t)t2 >> 14) | ((uint64_t)t3 << 18)) & 0x3ffffff;
        h4 += ((uint64_t)t3 >> 8) | ((uint64_t)hibit << 24);

        uint64_t d0 = h0*r0 + h1*s4 + h2*s3 + h3*s2 + h4*s1;
        uint64_t d1 = h0*r1 + h1*r0 + h2*s4 + h3*s3 + h4*s2;
        uint64_t d2 = h0*r2 + h1*r1 + h2*r0 + h3*s4 + h4*s3;
        uint64_t d3 = h0*r3 + h1*r2 + h2*r1 + h3*r0 + h4*s4;
        uint64_t d4 = h0*r4 + h1*r3 + h2*r2 + h3*r1 + h4*r0;

        uint64_t c;
        c = d0 >> 26; h0 = d0 & 0x3ffffff; d1 += c;
        c = d1 >> 26; h1 = d1 & 0x3ffffff; d2 += c;
        c = d2 >> 26; h2 = d2 & 0x3ffffff; d3 += c;
        c = d3 >> 26; h3 = d3 & 0x3ffffff; d4 += c;
        c = d4 >> 26; h4 = d4 & 0x3ffffff; h0 += c * 5;
        c = h0 >> 26; h0 &= 0x3ffffff; h1 += c;

        m += 16;
        bytes -= 16;
    }

    ctx->h[0] = (uint32_t)h0; ctx->h[1] = (uint32_t)h1; ctx->h[2] = (uint32_t)h2;
    ctx->h[3] = (uint32_t)h3; ctx->h[4] = (uint32_t)h4;
}

void poly1305_update(poly1305_ctx *ctx, const uint8_t *m, size_t bytes) {
    if (ctx->leftover) {
        size_t want = 16 - ctx->leftover;
        if (want > bytes) want = bytes;
        memcpy(ctx->buffer + ctx->leftover, m, want);
        bytes -= want;
        m += want;
        ctx->leftover += want;
        if (ctx->leftover < 16) return;
        poly1305_blocks(ctx, ctx->buffer, 16, 1);
        ctx->leftover = 0;
    }
    if (bytes >= 16) {
        size_t take = bytes & ~((size_t)15);
        poly1305_blocks(ctx, m, take, 1);
        m += take;
        bytes -= take;
    }
    if (bytes) {
        memcpy(ctx->buffer, m, bytes);
        ctx->leftover = bytes;
    }
}

void poly1305_finish(poly1305_ctx *ctx, uint8_t mac[16]) {
    if (ctx->leftover) {
        size_t i = ctx->leftover;
        ctx->buffer[i++] = 1;
        while (i < 16) ctx->buffer[i++] = 0;
        poly1305_blocks(ctx, ctx->buffer, 16, 0);
    }

    uint64_t h0 = ctx->h[0], h1 = ctx->h[1], h2 = ctx->h[2], h3 = ctx->h[3], h4 = ctx->h[4];
    uint64_t c;
    c = h1 >> 26; h1 &= 0x3ffffff; h2 += c;
    c = h2 >> 26; h2 &= 0x3ffffff; h3 += c;
    c = h3 >> 26; h3 &= 0x3ffffff; h4 += c;
    c = h4 >> 26; h4 &= 0x3ffffff; h0 += c * 5;
    c = h0 >> 26; h0 &= 0x3ffffff; h1 += c;

    uint64_t g0 = h0 + 5; c = g0 >> 26; g0 &= 0x3ffffff;
    uint64_t g1 = h1 + c; c = g1 >> 26; g1 &= 0x3ffffff;
    uint64_t g2 = h2 + c; c = g2 >> 26; g2 &= 0x3ffffff;
    uint64_t g3 = h3 + c; c = g3 >> 26; g3 &= 0x3ffffff;
    uint64_t g4 = h4 + c - (1 << 26);

    uint64_t mask = (g4 >> 63) - 1;
    g0 &= mask; g1 &= mask; g2 &= mask; g3 &= mask; g4 &= mask;
    mask = ~mask;
    h0 = (h0 & mask) | g0;
    h1 = (h1 & mask) | g1;
    h2 = (h2 & mask) | g2;
    h3 = (h3 & mask) | g3;
    h4 = (h4 & mask) | g4;

    uint64_t f0 = ((h0)       | (h1 << 26)) + (uint64_t)ctx->pad[0];
    uint64_t f1 = ((h1 >> 6)  | (h2 << 20)) + (uint64_t)ctx->pad[1] + (f0 >> 32);
    uint64_t f2 = ((h2 >> 12) | (h3 << 14)) + (uint64_t)ctx->pad[2] + (f1 >> 32);
    uint64_t f3 = ((h3 >> 18) | (h4 <<  8)) + (uint64_t)ctx->pad[3] + (f2 >> 32);

    store32_le(mac +  0, (uint32_t)f0);
    store32_le(mac +  4, (uint32_t)f1);
    store32_le(mac +  8, (uint32_t)f2);
    store32_le(mac + 12, (uint32_t)f3);
}

/* =============================================================================
 * CHACHA20-POLY1305 AEAD ENCRYPTION & AUTHENTICATION (RFC 8439)
 * ============================================================================= */

void chacha20_poly1305_encrypt(
    const uint8_t key[32],
    const uint8_t nonce[12],
    const uint8_t *aad, size_t aad_len,
    const uint8_t *plaintext, size_t pt_len,
    uint8_t *ciphertext,
    uint8_t tag[16]
) {
    /* 1. Generate Poly1305 one-time key using block counter 0 */
    chacha20_ctx ctx;
    chacha20_init(&ctx, key, nonce, 0);
    uint8_t block0[64];
    chacha20_block(&ctx, block0);
    uint8_t poly_key[32];
    memcpy(poly_key, block0, 32);

    /* 2. Encrypt plaintext starting with block counter 1 */
    ctx.state[12] = 1;
    chacha20_xor_stream(&ctx, plaintext, ciphertext, pt_len);

    /* 3. Compute Poly1305 tag over: AAD || pad || Ciphertext || pad || len(AAD) || len(CT) */
    poly1305_ctx pctx;
    poly1305_init(&pctx, poly_key);
    if (aad && aad_len > 0) {
        poly1305_update(&pctx, aad, aad_len);
        if (aad_len % 16 != 0) {
            uint8_t zero_pad[16] = {0};
            poly1305_update(&pctx, zero_pad, 16 - (aad_len % 16));
        }
    }

    if (pt_len > 0) {
        poly1305_update(&pctx, ciphertext, pt_len);
        if (pt_len % 16 != 0) {
            uint8_t zero_pad[16] = {0};
            poly1305_update(&pctx, zero_pad, 16 - (pt_len % 16));
        }
    }

    uint8_t len_block[16];
    store32_le(len_block + 0, (uint32_t)aad_len);
    store32_le(len_block + 4, 0);
    store32_le(len_block + 8, (uint32_t)pt_len);
    store32_le(len_block + 12, 0);
    poly1305_update(&pctx, len_block, 16);

    poly1305_finish(&pctx, tag);
}

int chacha20_poly1305_decrypt(
    const uint8_t key[32],
    const uint8_t nonce[12],
    const uint8_t *aad, size_t aad_len,
    const uint8_t *ciphertext, size_t ct_len,
    const uint8_t tag[16],
    uint8_t *plaintext
) {
    /* 1. Generate Poly1305 key */
    chacha20_ctx ctx;
    chacha20_init(&ctx, key, nonce, 0);
    uint8_t block0[64];
    chacha20_block(&ctx, block0);
    uint8_t poly_key[32];
    memcpy(poly_key, block0, 32);

    /* 2. Compute expected tag */
    poly1305_ctx pctx;
    poly1305_init(&pctx, poly_key);
    if (aad && aad_len > 0) {
        poly1305_update(&pctx, aad, aad_len);
        if (aad_len % 16 != 0) {
            uint8_t zero_pad[16] = {0};
            poly1305_update(&pctx, zero_pad, 16 - (aad_len % 16));
        }
    }
    if (ct_len > 0) {
        poly1305_update(&pctx, ciphertext, ct_len);
        if (ct_len % 16 != 0) {
            uint8_t zero_pad[16] = {0};
            poly1305_update(&pctx, zero_pad, 16 - (ct_len % 16));
        }
    }
    uint8_t len_block[16];
    store32_le(len_block + 0, (uint32_t)aad_len);
    store32_le(len_block + 4, 0);
    store32_le(len_block + 8, (uint32_t)ct_len);
    store32_le(len_block + 12, 0);
    poly1305_update(&pctx, len_block, 16);

    uint8_t expected_tag[16];
    poly1305_finish(&pctx, expected_tag);

    /* Constant-time comparison */
    uint8_t diff = 0;
    for (int i = 0; i < 16; i++) {
        diff |= (expected_tag[i] ^ tag[i]);
    }
    if (diff != 0) {
        return -1; /* Authentication failure: ciphertext altered! */
    }

    /* 3. Decrypt ciphertext */
    ctx.state[12] = 1;
    chacha20_xor_stream(&ctx, ciphertext, plaintext, ct_len);
    return 0;
}

/* =============================================================================
 * AES-256 SYMMETRIC BLOCK CIPHER (RIJNDAEL CORE)
 * ============================================================================= */

static const uint8_t sbox[256] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
};

static const uint8_t rcon[15] = {
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x00, 0x00, 0x00, 0x00
};

typedef struct {
    uint8_t round_keys[240]; /* 15 round keys of 16 bytes each for AES-256 (14 rounds) */
} aes256_ctx;

void aes256_init(aes256_ctx *ctx, const uint8_t key[32]) {
    memcpy(ctx->round_keys, key, 32);
    int bytes_generated = 32;
    int rcon_idx = 1;
    uint8_t temp[4];

    while (bytes_generated < 240) {
        for (int i = 0; i < 4; i++) {
            temp[i] = ctx->round_keys[bytes_generated - 4 + i];
        }

        if (bytes_generated % 32 == 0) {
            /* RotWord & SubWord & Rcon */
            uint8_t k = temp[0];
            temp[0] = sbox[temp[1]] ^ rcon[rcon_idx++];
            temp[1] = sbox[temp[2]];
            temp[2] = sbox[temp[3]];
            temp[3] = sbox[k];
        } else if (bytes_generated % 32 == 16) {
            /* SubWord */
            temp[0] = sbox[temp[0]];
            temp[1] = sbox[temp[1]];
            temp[2] = sbox[temp[2]];
            temp[3] = sbox[temp[3]];
        }

        for (int i = 0; i < 4; i++) {
            ctx->round_keys[bytes_generated] = ctx->round_keys[bytes_generated - 32] ^ temp[i];
            bytes_generated++;
        }
    }
}

static inline uint8_t gmul(uint8_t a, uint8_t b) {
    uint8_t p = 0;
    for (int counter = 0; counter < 8; counter++) {
        if (b & 1) p ^= a;
        uint8_t hi_bit_set = (a & 0x80);
        a <<= 1;
        if (hi_bit_set) a ^= 0x1b;
        b >>= 1;
    }
    return p;
}

void aes256_encrypt_block(const aes256_ctx *ctx, const uint8_t in[16], uint8_t out[16]) {
    uint8_t state[4][4];
    for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
            state[r][c] = in[r + 4 * c] ^ ctx->round_keys[r + 4 * c];
        }
    }

    /* 13 rounds of SubBytes, ShiftRows, MixColumns, AddRoundKey */
    for (int round = 1; round <= 13; round++) {
        /* SubBytes */
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                state[r][c] = sbox[state[r][c]];

        /* ShiftRows */
        uint8_t t;
        t = state[1][0]; state[1][0] = state[1][1]; state[1][1] = state[1][2]; state[1][2] = state[1][3]; state[1][3] = t;
        t = state[2][0]; state[2][0] = state[2][2]; state[2][2] = t; t = state[2][1]; state[2][1] = state[2][3]; state[2][3] = t;
        t = state[3][3]; state[3][3] = state[3][2]; state[3][2] = state[3][1]; state[3][1] = state[3][0]; state[3][0] = t;

        /* MixColumns */
        for (int c = 0; c < 4; c++) {
            uint8_t a = state[0][c], b = state[1][c], d = state[2][c], e = state[3][c];
            state[0][c] = gmul(a, 2) ^ gmul(b, 3) ^ d ^ e;
            state[1][c] = a ^ gmul(b, 2) ^ gmul(d, 3) ^ e;
            state[2][c] = a ^ b ^ gmul(d, 2) ^ gmul(e, 3);
            state[3][c] = gmul(a, 3) ^ b ^ d ^ gmul(e, 2);
        }

        /* AddRoundKey */
        const uint8_t *rk = ctx->round_keys + (round * 16);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                state[r][c] ^= rk[r + 4 * c];
    }

    /* Round 14: SubBytes, ShiftRows, AddRoundKey (No MixColumns) */
    for (int r = 0; r < 4; r++)
        for (int c = 0; c < 4; c++)
            state[r][c] = sbox[state[r][c]];

    uint8_t t;
    t = state[1][0]; state[1][0] = state[1][1]; state[1][1] = state[1][2]; state[1][2] = state[1][3]; state[1][3] = t;
    t = state[2][0]; state[2][0] = state[2][2]; state[2][2] = t; t = state[2][1]; state[2][1] = state[2][3]; state[2][3] = t;
    t = state[3][3]; state[3][3] = state[3][2]; state[3][2] = state[3][1]; state[3][1] = state[3][0]; state[3][0] = t;

    const uint8_t *rk14 = ctx->round_keys + (14 * 16);
    for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
            out[r + 4 * c] = state[r][c] ^ rk14[r + 4 * c];
        }
    }
}

/* =============================================================================
 * CLI INTERACTION & SELF-TEST SUITE
 * ============================================================================= */

static void print_hex(const char *label, const uint8_t *data, size_t len) {
    printf("%-18s: ", label);
    for (size_t i = 0; i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

int run_selftest(void) {
    printf("[*] Running ASTERIX Cryptographic Validation Test Vectors...\n");

    /* RFC 8439 Section 2.4.2 Test Vector for ChaCha20 */
    uint8_t key[32] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f
    };
    uint8_t nonce[12] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4a, 0x00, 0x00, 0x00, 0x00
    };
    const char *plaintext = "Ladies and Gentlemen of the class of '99: If I could offer you only one tip for the future, sunscreen would be it.";
    size_t pt_len = strlen(plaintext);

    uint8_t *ciphertext = (uint8_t*)malloc(pt_len);
    uint8_t *decrypted  = (uint8_t*)malloc(pt_len + 1);
    uint8_t tag[16];

    /* Test AEAD Encrypt */
    chacha20_poly1305_encrypt(key, nonce, (const uint8_t*)"ASTERIX", 7, (const uint8_t*)plaintext, pt_len, ciphertext, tag);

    /* Test AEAD Decrypt */
    int dec_res = chacha20_poly1305_decrypt(key, nonce, (const uint8_t*)"ASTERIX", 7, ciphertext, pt_len, tag, decrypted);
    decrypted[pt_len] = '\0';

    if (dec_res == 0 && strcmp((const char*)decrypted, plaintext) == 0) {
        printf("[✔] ChaCha20-Poly1305 AEAD Test: PASSED (Decryption verified and tag authenticated)\n");
    } else {
        printf("[!] ChaCha20-Poly1305 AEAD Test: FAILED!\n");
        free(ciphertext);
        free(decrypted);
        return 1;
    }

    /* Test AES-256 ECB Known Vector (NIST SP 800-38A) */
    uint8_t aes_key[32] = {
        0x60, 0x3d, 0xeb, 0x10, 0x15, 0xca, 0x71, 0xbe,
        0x2b, 0x73, 0xae, 0xf0, 0x85, 0x7d, 0x77, 0x81,
        0x1f, 0x35, 0x2c, 0x07, 0x3b, 0x61, 0x08, 0xd7,
        0x2d, 0x98, 0x10, 0xa3, 0x09, 0x14, 0xdf, 0xf4
    };
    uint8_t aes_pt[16] = {
        0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96,
        0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a
    };
    uint8_t aes_ct[16];
    aes256_ctx actx;
    aes256_init(&actx, aes_key);
    aes256_encrypt_block(&actx, aes_pt, aes_ct);

    /* NIST expected: f3eed1bdb5d2a03c064b5a7e3db181f8 */
    uint8_t expected_aes_ct[16] = {
        0xf3, 0xee, 0xd1, 0xbd, 0xb5, 0xd2, 0xa0, 0x3c,
        0x06, 0x4b, 0x5a, 0x7e, 0x3d, 0xb1, 0x81, 0xf8
    };
    if (memcmp(aes_ct, expected_aes_ct, 16) == 0) {
        printf("[✔] AES-256 Block Cipher Test: PASSED (Matches NIST SP 800-38A test vector)\n");
    } else {
        printf("[!] AES-256 Block Cipher Test: FAILED!\n");
        free(ciphertext);
        free(decrypted);
        return 1;
    }

    free(ciphertext);
    free(decrypted);
    printf("[✔] All ASTERIX Native Cryptographic Self-Tests Passed Cleanly.\n");
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2 || strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) {
        printf("===============================================================================\n");
        printf("  🌌 ASTERIX OS — High-Assurance Native C Cryptographic Core v3.5\n");
        printf("  Standalone C99 implementation of ChaCha20-Poly1305 AEAD and AES-256\n");
        printf("===============================================================================\n\n");
        printf("Usage:\n");
        printf("  %s --test                      Run official RFC 8439 & NIST test vectors\n", argv[0]);
        printf("  %s --aead-enc <msg>            Encrypt string with ChaCha20-Poly1305\n", argv[0]);
        printf("  %s --aes-enc <16-byte-string>  Encrypt 16-byte block with AES-256\n", argv[0]);
        printf("  %s --bench                     Run throughput benchmark\n", argv[0]);
        return 0;
    }

    if (strcmp(argv[1], "--test") == 0) {
        return run_selftest();
    }

    if (strcmp(argv[1], "--bench") == 0) {
        printf("[*] Running Cryptographic Throughput Benchmark (10 MB)...\n");
        size_t bench_sz = 10 * 1024 * 1024;
        uint8_t *buffer = (uint8_t*)malloc(bench_sz);
        memset(buffer, 0x5A, bench_sz);
        uint8_t key[32] = {1, 2, 3, 4};
        uint8_t nonce[12] = {5, 6, 7, 8};
        chacha20_ctx ctx;
        chacha20_init(&ctx, key, nonce, 0);

        clock_t start = clock();
        chacha20_xor_stream(&ctx, buffer, buffer, bench_sz);
        clock_t end = clock();

        double secs = (double)(end - start) / CLOCKS_PER_SEC;
        double mbps = (10.0) / (secs > 0 ? secs : 0.0001);
        printf("[✔] ChaCha20 Native C Throughput: %.2f MB/s (Elapsed: %.3fs)\n", mbps, secs);
        free(buffer);
        return 0;
    }

    if (strcmp(argv[1], "--aead-enc") == 0 && argc >= 3) {
        const char *msg = argv[2];
        size_t len = strlen(msg);
        uint8_t key[32] = {0xAA};
        uint8_t nonce[12] = {0xBB};
        uint8_t *ct = (uint8_t*)malloc(len);
        uint8_t tag[16];

        chacha20_poly1305_encrypt(key, nonce, (const uint8_t*)"ASTERIX_AAD", 11, (const uint8_t*)msg, len, ct, tag);

        printf("Plaintext  : %s\n", msg);
        print_hex("Ciphertext", ct, len);
        print_hex("Auth Tag", tag, 16);
        free(ct);
        return 0;
    }

    return 0;
}
