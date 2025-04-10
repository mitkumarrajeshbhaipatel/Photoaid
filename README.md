python3.11 -m venv myenv 

source myenv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload  
