from pathlib import Path
import subprocess,shutil,sys,json,hashlib
BASE=Path(__file__).parent
if __name__=='__main__':
    manifest=json.loads((BASE/'data/source-manifest.json').read_text())
    assert hashlib.sha256((BASE/'data/source.csv').read_bytes()).hexdigest()==manifest['included_csv_sha256'], 'Source snapshot changed'
    if not shutil.which('Rscript'):raise SystemExit('Rscript is required. Install R, then reopen your terminal or run analysis.R in RStudio.')

    subprocess.run(['Rscript','--vanilla','analysis.R'],cwd=BASE,check=True)
    subprocess.run(['Rscript','--vanilla','tests/test_analysis.R'],cwd=BASE,check=True)
    subprocess.run([sys.executable,'build_report.py'],cwd=BASE,check=True)
