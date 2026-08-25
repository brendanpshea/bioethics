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
    $fragment = [System.Text.RegularExpressions.Regex]::Replace(
        $fragment,
        '(?s)^\s*<h1[^>]*>.*?</h1>\s*',
        ""
    )
    $fragment = $fragment -replace '<th>', '<th scope="col">'
    $captions = @(
        "Course sections and meeting formats",
        "Grade breakdown",
        "Semester dates and holidays",
        "Weekly course schedule",
        "Graded sessions and coverage"
    )
    foreach ($caption in $captions) {
        $captionParagraph = "<p>Table: $caption</p>"
        $fragment = $fragment.Replace($captionParagraph, "")
    }
    $tableSearchStart = 0
    foreach ($caption in $captions) {
        $tableStart = $fragment.IndexOf('<table>', $tableSearchStart)
        if ($tableStart -lt 0) {
            throw "Expected another table while adding captions."
        }
        $fragment = $fragment.Remove($tableStart, 7).Insert(
            $tableStart,
            "<table>`r`n<caption>$caption</caption>"
        )
        $tableSearchStart = $tableStart + 7 + 2 + 9 + $caption.Length + 10
    }
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