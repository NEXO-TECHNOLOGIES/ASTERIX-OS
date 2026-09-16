# ==============================================================================
# ASTERIX OS Master CLI Fast-Path Alias ('s') (PowerShell Entrypoint)
# High-velocity unified launcher forwarding all arguments directly to 'ax.ps1'
# ==============================================================================
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AxPs1 = Join-Path $ScriptDir "ax.ps1"
& $AxPs1 @args
