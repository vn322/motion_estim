@echo off
pyinstaller --clean ^
  --onefile --windowed ^
  --additional-hooks-dir=. ^
  --hidden-import scipy.stats._stats_py ^
  --hidden-import mediapipe.python.solutions.pose ^
  --hidden-import mediapipe.python.solutions.drawing_utils ^
  --hidden-import mediapipe.python.solutions.pose_landmark ^
  --icon=icon.ico ^
  main.py

pause