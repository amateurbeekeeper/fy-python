## Scope

SKU Format:
   - 1-3 uppercase letters, a hyphen, and 1-3 digits (e.g., AB-6, CD-3).      
   - Invalid SKUs: ABC-1234, A-BCD.

Amount Format:
   - Non-negative integers with 1-3 digits (e.g., 5, 100, 123).
   - Invalid amounts: -5, 1000, 0.5.

Error printed when:
   - Adding or ordering without setting. 
   - Insufficient stock error
   - Invalid commands, SKUs, or amounts.

<!-- Input File Validation: -->
   <!-- - Ensure that the input file exists before attempting to process it. -->
   <!-- - Handle cases where the file is missing or inaccessible. -->

Updating Existing SKUs in set-stock:
   - When setting stock levels using set-stock, if the SKU already exists in the stock, its value will be overwritten. This behavior might be intentional, but it's worth clarifying during your interview.

Error Handling:
   Your program doesn't stop when it encounters an error. In the process_stock_file function, you have wrapped the stock_manager.process_command(line) inside a try-except block:

   This means that if a StockError is raised while processing a command, it will be caught by the except block. The error message will be printed, but the program will then continue processing the next command in the file.

   So, if you have multiple commands in your input file and one of them is incorrect, your program will just print the error for that command and move on to process the next one.

Other:
   - possible not catching non stockerror errors

## Running

First Activate Env
source venv/bin/activate

Tests
python -m unittest -v stock_program.py

Execution
python run.py stock.txt

Dependencies
pip freeze > requirements.txt
pip install -r requirements.txt

When Done
deactivate

