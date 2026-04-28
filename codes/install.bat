@echo off
echo Installing Supplier Intelligence Agent dependencies...
echo.

pip install langchain==0.2.16 langchain-openai==0.1.25 langchain-community==0.2.16 langchain-core==0.2.40
pip install openai==1.54.4 tavily-python streamlit apscheduler tiktoken pydantic requests
pip install SQLAlchemy dataclasses-json langchain-text-splitters

echo.
echo Installation complete!
echo.
echo Now run the app with:
echo     streamlit run app.py
echo.
pause