@echo off

echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed.

echo Running crawler...
python BayerPropertyCrawler.py