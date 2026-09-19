Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildDir = Join-Path $scriptDir 'build'
$outDir = Join-Path $scriptDir 'bin'
$srcDir = Join-Path $scriptDir 'src'
$elfPath = Join-Path $outDir 'asterix-microkernel.elf'
$binPath = Join-Path $outDir 'asterix-microkernel.bin'

function Get-RequiredTool {
    param(
        [string]$Name,
        [string]$InstallHint,
        [string[]]$SearchPaths = @()
    )

    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    foreach ($candidate in $SearchPaths) {
        if (-not $candidate) { continue }
        $path = if ($candidate.EndsWith('\')) { $candidate + $Name } else { Join-Path $candidate $Name }
        if (Test-Path $path) {
            return (Resolve-Path $path).Path
        }
    }

    foreach ($base in @(
        $env:ProgramFiles,
        ${env:ProgramFiles(x86)},
        $env:LOCALAPPDATA + '\Programs',
        $env:LOCALAPPDATA + '\bin'
    )) {
        if (-not $base) { continue }
        foreach ($sub in @('LLVM\bin', 'NASM', 'qemu', 'QEMU', '')) {
            $path = if ($sub) { Join-Path $base $sub } else { $base }
            $candidate = Join-Path $path $Name
            if (Test-Path $candidate) {
                return (Resolve-Path $candidate).Path
            }
            if (Test-Path ($candidate + '.exe')) {
                return (Resolve-Path ($candidate + '.exe')).Path
            }
        }
    }

    throw "Required tool '$Name' was not found in PATH or in the standard Windows install locations. Install it first: $InstallHint"
}

function Write-Step {
    param([string]$Message)
    Write-Host "[ASTERIX KERNEL] $Message" -ForegroundColor Cyan
}

New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Step 'Checking project toolchain...'
$clang = Get-RequiredTool -Name 'clang.exe' -InstallHint 'Install the LLVM toolchain for your host setup' -SearchPaths @(
    'C:\Program Files\LLVM\bin',
    'C:\Program Files\LLVM\bin\\'
)
$nasm = Get-RequiredTool -Name 'nasm.exe' -InstallHint 'Install NASM for your host setup' -SearchPaths @(
    'C:\Program Files\NASM',
    'C:\Program Files\NASM\\',
    (Join-Path $env:LOCALAPPDATA 'bin\NASM'),
    (Join-Path $env:LOCALAPPDATA 'Programs\NASM')
)

$bootObj     = Join-Path $buildDir 'boot.o'
$isrObj      = Join-Path $buildDir 'isr.o'
$serialObj   = Join-Path $buildDir 'serial.o'
$pagingObj   = Join-Path $buildDir 'paging.o'
$heapObj     = Join-Path $buildDir 'heap.o'
$timerObj    = Join-Path $buildDir 'timer.o'
$keyboardObj = Join-Path $buildDir 'keyboard.o'
$vfsObj      = Join-Path $buildDir 'vfs.o'
$shellObj    = Join-Path $buildDir 'shell.o'
$kernelObj   = Join-Path $buildDir 'kernel.o'

Write-Step "Assembling bootloader: $bootObj"
& $nasm -f elf32 (Join-Path $srcDir 'boot.asm') -o $bootObj
if ($LASTEXITCODE -ne 0) { throw 'NASM boot assembly failed.' }

Write-Step "Assembling interrupt stubs: $isrObj"
& $nasm -f elf32 (Join-Path $srcDir 'isr.asm') -o $isrObj
if ($LASTEXITCODE -ne 0) { throw 'NASM isr assembly failed.' }

Write-Step "Compiling 16550 UART serial driver: $serialObj"
& $clang -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin -mno-sse -mno-mmx -mno-sse2 -O2 -Wall -Wextra -c (Join-Path $srcDir 'serial.c') -I (Join-Path $scriptDir 'include') -o $serialObj
if ($LASTEXITCODE -ne 0) { throw 'clang serial compilation failed.' }

Write-Step "Compiling hardware MMU paging driver: $pagingObj"
& $clang -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin -mno-sse -mno-mmx -mno-sse2 -O2 -Wall -Wextra -c (Join-Path $srcDir 'paging.c') -I (Join-Path $scriptDir 'include') -o $pagingObj
if ($LASTEXITCODE -ne 0) { throw 'clang paging compilation failed.' }

Write-Step "Compiling dynamic heap allocator: $heapObj"
& $clang -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin -mno-sse -mno-mmx -mno-sse2 -O2 -Wall -Wextra -c (Join-Path $srcDir 'heap.c') -I (Join-Path $scriptDir 'include') -o $heapObj
if ($LASTEXITCODE -ne 0) { throw 'clang heap compilation failed.' }

Write-Step "Compiling 8254 PIT timer driver: $timerObj"
& $clang -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin -mno-sse -mno-mmx -mno-sse2 -O2 -Wall -Wextra -c (Join-Path $srcDir 'timer.c') -I (Join-Path $scriptDir 'include') -o $timerObj
if ($LASTEXITCODE -ne 0) { throw 'clang timer compilation failed.' }

Write-Step "Compiling PS/2 keyboard driver: $keyboardObj"
& $clang -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin -mno-sse -mno-mmx -mno-sse2 -O2 -Wall -Wextra -c (Join-Path $srcDir 'keyboard.c') -I (Join-Path $scriptDir 'include') -o $keyboardObj
if ($LASTEXITCODE -ne 0) { throw 'clang keyboard compilation failed.' }

Write-Step "Compiling virtual file system (VFS): $vfsObj"
& $clang -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin -mno-sse -mno-mmx -mno-sse2 -O2 -Wall -Wextra -c (Join-Path $srcDir 'vfs.c') -I (Join-Path $scriptDir 'include') -o $vfsObj
if ($LASTEXITCODE -ne 0) { throw 'clang vfs compilation failed.' }

Write-Step "Compiling interactive shell: $shellObj"
& $clang -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin -mno-sse -mno-mmx -mno-sse2 -O2 -Wall -Wextra -c (Join-Path $srcDir 'shell.c') -I (Join-Path $scriptDir 'include') -o $shellObj
if ($LASTEXITCODE -ne 0) { throw 'clang shell compilation failed.' }

Write-Step "Compiling kernel core: $kernelObj"
& $clang -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin -mno-sse -mno-mmx -mno-sse2 -O2 -Wall -Wextra -c (Join-Path $srcDir 'kernel.c') -I (Join-Path $scriptDir 'include') -o $kernelObj
if ($LASTEXITCODE -ne 0) { throw 'clang kernel compilation failed.' }

Write-Step "Linking kernel ELF image: $elfPath"
$linkArgs = @(
    '-target', 'i386-unknown-none-elf',
    '-nostdlib',
    '-Wl,-T,' + (Join-Path $scriptDir 'linker.ld'),
    '-o', $elfPath,
    $bootObj, $isrObj, $serialObj, $pagingObj, $heapObj, $timerObj, $keyboardObj, $vfsObj, $shellObj, $kernelObj
)
& $clang @linkArgs
if ($LASTEXITCODE -ne 0) { throw 'Kernel linking failed.' }

Copy-Item -Force $elfPath $binPath

Write-Host ''
Write-Host '[+] Custom kernel build complete.' -ForegroundColor Green
Write-Host "    ELF: $elfPath" -ForegroundColor Green
Write-Host "    Bin: $binPath" -ForegroundColor Green
Write-Host ''

if ($args -contains '--run') {
    try {
        $qemu = Get-RequiredTool -Name 'qemu-system-i386.exe' -InstallHint 'winget install SoftwareFreedomConservancy.QEMU' -SearchPaths @(
            'C:\Program Files\qemu',
            'C:\Program Files\QEMU'
        )
    } catch {
        $qemu = Get-RequiredTool -Name 'qemu-system-x86_64.exe' -InstallHint 'winget install SoftwareFreedomConservancy.QEMU' -SearchPaths @(
            'C:\Program Files\qemu',
            'C:\Program Files\QEMU'
        )
    }

    Write-Step 'Launching kernel in QEMU...'
    & $qemu -kernel $elfPath
}
