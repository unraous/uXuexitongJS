# pylint_score_calculator.ps1
# Calculate the pylint weighted average score for all Python files in the src directory
# Weight = single file line count / total line count

param(
    [string]$SrcPath = "src"
)

# Check if src directory exists
if (-not (Test-Path $SrcPath)) {
    Write-Error "Directory '$SrcPath' does not exist"
    exit 1
}

# Get all Python files
$pythonFiles = Get-ChildItem -Path $SrcPath -Recurse -Include "*.py" -File

if ($pythonFiles.Count -eq 0) {
    Write-Warning "No Python files found in '$SrcPath' directory"
    exit 0
}

Write-Host "Found $($pythonFiles.Count) Python files"

# Initialize variables
$totalLines = 0
$weightedScoreSum = 0.0
$results = @()

foreach ($file in $pythonFiles) {
    $filePath = $file.FullName
    $relativePath = $filePath.Replace((Get-Location).Path + "\", "")
    
    try {
        # Calculate file line count
        $lineCount = (Get-Content $filePath -ErrorAction Stop | Measure-Object -Line).Lines
        
        # Run pylint and capture output
        $pylintOutput = & pylint $filePath 2>&1
        
        # Parse pylint score (format: "Your code has been rated at X.XX/10")
        $scoreMatch = $pylintOutput | Select-String -Pattern "rated at (\d+\.\d+)/10"
        
        if ($scoreMatch) {
            $score = [double]$scoreMatch.Matches[0].Groups[1].Value
        } else {
            Write-Warning "Unable to parse pylint score for file '$relativePath'"
            $score = 0.0
        }
        
        # Accumulate total lines
        $totalLines += $lineCount
        
        # Accumulate weighted score
        $weightedScoreSum += $score * $lineCount
        
        # Record result
        $results += [PSCustomObject]@{
            File = $relativePath
            Lines = $lineCount
            Score = $score
        }
        
        Write-Host "Processed: $relativePath (Lines: $lineCount, Score: $score/10)"
        
    } catch {
        Write-Warning "Error processing file '$relativePath': $($_.Exception.Message)"
    }
}

# Calculate weighted average
if ($totalLines -gt 0) {
    $weightedAverage = $weightedScoreSum / $totalLines
    Write-Host "`n=== Summary ==="
    Write-Host "Total files: $($results.Count)"
    Write-Host "Total lines: $totalLines"
    Write-Host "Weighted average score: $([math]::Round($weightedAverage, 2))/10"
    
    Write-Host "`n=== Detailed Results ==="
    $results | Format-Table -AutoSize
    
} else {
    Write-Warning "No valid file line count data"
}

Write-Host "`nScript execution completed"