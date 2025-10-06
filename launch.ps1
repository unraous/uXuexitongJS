$inVenv = python -c "import sys; print(sys.prefix != sys.base_prefix)"
$entryPath = ".\\src\\main.py"
if ($inVenv -eq "True") {
    python $entryPath
} else {
    .\.venv\Scripts\Activate.ps1
    python $entryPath
}