import subprocess

subprocess.run("python insert_data.py", shell=True)
subprocess.run("python insert_seasonality_data.py", shell=True)
subprocess.run("python insert_brand_popularity.py", shell=True)