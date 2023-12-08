import subprocess
from tqdm import tqdm
import time

def run_script(script_name):
    """ Function to run a python script using subprocess """
    result = subprocess.run(['python', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result

def main():
    scripts = ['insert_data.py', 'insert_seasonality.py', 'insert_brand_popularity.py']
    total = len(scripts)

    with tqdm(total=total, desc="Running Scripts", unit="script") as pbar:
        for script in scripts:
            result = run_script(script)
            if result.returncode != 0:
                print(f"Error in {script}: {result.stderr.decode('utf-8')}")
            else:
                print(f"{script} executed successfully.")
            pbar.update(1)
            time.sleep(1)

if __name__ == "__main__":
    main()
