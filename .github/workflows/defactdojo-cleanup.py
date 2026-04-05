name: DefectDojo Cleanup

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install Python dependency
        run: pip install requests

      - name: Run cleanup
        env:
          DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
          DEFECTDOJO_TOKEN: ${{ secrets.DEFECTDOJO_TOKEN }}
          RETENTION_DAYS: 7
        run: python3 defactdojo-cleanup.py
