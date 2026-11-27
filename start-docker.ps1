<#
.SYNOPSIS
Scarica le immagini, costruisce i servizi e avvia BetterMusic su Docker.
.EXAMPLE
powershell -ExecutionPolicy Bypass -File .\start-docker.ps1
#>
[CmdletBinding()]
param([switch]$Help)

if ($Help) {
    Write-Output 'Uso: .\start-docker.ps1'
    Write-Output 'Richiede Docker Desktop avviato in modalita Linux containers e Compose con --wait.'
    Write-Output 'Usa POSTGRES_PASSWORD se presente, altrimenti la richiede.'
    return
}

$ErrorActionPreference = 'Stop'
$previousPassword = $env:POSTGRES_PASSWORD
$locationPushed = $false
$startupAttempted = $false

function Invoke-Compose {
    param([Parameter(Mandatory = $true)][string[]]$ComposeArguments)
    & $dockerExecutable compose --file $composeFile @ComposeArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose ha restituito il codice $LASTEXITCODE."
    }
}

function Read-Password {
    param([string]$Prompt)
    $securePassword = Read-Host -Prompt $Prompt -AsSecureString
    $passwordPointer = [IntPtr]::Zero
    try {
        $passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
    }
    finally {
        if ($passwordPointer -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
        }
        $securePassword.Dispose()
    }
}

try {
    $dockerCommand = Get-Command docker -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (-not $dockerCommand) {
        throw 'Docker non trovato. Installare e avviare Docker Desktop; vedere README.md.'
    }
    $dockerExecutable = $dockerCommand.Source
    $composeFile = Join-Path $PSScriptRoot 'docker-compose.yml'
    Push-Location -LiteralPath $PSScriptRoot
    $locationPushed = $true

    Invoke-Compose -ComposeArguments @('version')
    $composeHelp = Invoke-Compose -ComposeArguments @('up', '--help')
    if (($composeHelp | Out-String) -notmatch '--wait-timeout') {
        throw 'Aggiornare Docker Compose: manca il supporto --wait-timeout.'
    }
    Write-Host 'Verifica del daemon Docker; Docker Desktop deve essere avviato...'
    $dockerOs = & $dockerExecutable info --format '{{.OSType}}'
    if ($LASTEXITCODE -ne 0) {
        throw 'Daemon Docker non accessibile. Avviare Docker Desktop e verificare docker info.'
    }
    if ($dockerOs -ne 'linux') {
        throw 'Sono richiesti container Linux; selezionare Linux containers in Docker Desktop.'
    }

    if ([string]::IsNullOrEmpty($env:POSTGRES_PASSWORD)) {
        Write-Host 'Con un volume PostgreSQL esistente, inserire la password scelta al primo avvio.'
        $env:POSTGRES_PASSWORD = Read-Password -Prompt 'Password PostgreSQL'
        if ([string]::IsNullOrEmpty($env:POSTGRES_PASSWORD)) {
            throw 'La password non puo essere vuota.'
        }
        $passwordConfirmation = Read-Password -Prompt 'Ripetere la password'
        if ($env:POSTGRES_PASSWORD -cne $passwordConfirmation) {
            throw 'Le password non coincidono.'
        }
        $passwordConfirmation = $null
    }

    Write-Host 'Validazione della configurazione...'
    Invoke-Compose -ComposeArguments @('config', '--quiet')
    Write-Host 'Download delle immagini Consul e PostgreSQL...'
    Invoke-Compose -ComposeArguments @('pull', 'consul', 'postgres')
    Write-Host 'Build e avvio dei sette container; attesa degli healthcheck...'
    $startupAttempted = $true
    Invoke-Compose -ComposeArguments @('up', '-d', '--build', '--wait', '--wait-timeout', '300')
    $startupAttempted = $false
    Invoke-Compose -ComposeArguments @('ps')
    Write-Host 'BetterMusic disponibile su http://127.0.0.1:8080'
    Write-Host 'I dati dimostrativi non vengono caricati automaticamente.'
    Write-Host 'Per i comandi Compose manuali, impostare POSTGRES_PASSWORD nel proprio terminale.'
}
catch {
    Write-Error -Message $_.Exception.Message -ErrorAction Continue
    if ($startupAttempted) {
        Write-Host 'Avvio non completato. Stato e ultimi log:'
        try { Invoke-Compose -ComposeArguments @('ps') } catch { Write-Warning $_.Exception.Message }
        try { Invoke-Compose -ComposeArguments @('logs', '--tail=80') } catch { Write-Warning $_.Exception.Message }
    }
    exit 1
}
finally {
    $env:POSTGRES_PASSWORD = $previousPassword
    $passwordConfirmation = $null
    if ($locationPushed) {
        Pop-Location
    }
}
