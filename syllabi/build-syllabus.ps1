$ErrorActionPreference = "Stop"

$syllabusDirectory = $PSScriptRoot
$sourcePath = Join-Path $syllabusDirectory "syllabus_fa26.md"
$templatePath = Join-Path $syllabusDirectory "syllabus_fa26.html"
$fragmentPath = [System.IO.Path]::GetTempFileName()

try {
    & pandoc $sourcePath --from=gfm --to=html5 --output=$fragmentPath
    if ($LASTEXITCODE -ne 0) {
        throw "Pandoc failed with exit code $LASTEXITCODE."
    }

    $template = Get-Content -Path $templatePath -Raw -Encoding UTF8
    $fragment = Get-Content -Path $fragmentPath -Raw -Encoding UTF8
    $mainPattern = '(?s)(<main id="main-content"[^>]*>).*?(</main>)'
    if ($template -notmatch $mainPattern) {
        throw "Could not find the main content region in $templatePath."
    }

    $html = [System.Text.RegularExpressions.Regex]::Replace(
        $template,
        $mainPattern,
        { param($match) $match.Groups[1].Value + "`r`n" + $fragment.Trim() + "`r`n" + $match.Groups[2].Value },
        [System.Text.RegularExpressions.RegexOptions]::Singleline
    )
    [System.IO.File]::WriteAllText($templatePath, $html, [System.Text.UTF8Encoding]::new($false))
}
finally {
    if (Test-Path $fragmentPath) {
        Remove-Item $fragmentPath -Force
    }
}