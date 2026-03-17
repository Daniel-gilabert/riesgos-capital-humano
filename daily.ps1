param(
    [ValidateSet("status", "review", "commit", "all")]
    [string]$Step = "status",
    [string]$Message = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-Status {
    git status
}

function Run-Review {
    Write-Host "Running syntax review (compileall)..." -ForegroundColor Cyan
    python -m compileall app.py config.py models services ui
}

function Run-Commit {
    param(
        [switch]$SkipIfNoChanges
    )

    if ([string]::IsNullOrWhiteSpace($Message)) {
        throw "Commit message required. Example: .\daily.ps1 commit -Message chore: update daily changes"
    }

    git add -A

    # Avoid accidentally committing the embedded repo folder.
    git reset -q HEAD -- "agent-teams-lite" 2>$null

    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        if ($SkipIfNoChanges) {
            Write-Host "No staged changes to commit. Skipping commit step." -ForegroundColor Yellow
            return
        }
        throw "No staged changes to commit."
    }

    git commit -m "$Message"
}

switch ($Step) {
    "status" { Show-Status }
    "review" { Run-Review }
    "commit" { Run-Commit }
    "all" {
        Show-Status
        Run-Review
        Run-Commit -SkipIfNoChanges
    }
}
