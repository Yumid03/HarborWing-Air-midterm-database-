# HarborWing Air Database Project

## 1. Setup Instructions
Follow these step-by-step instructions to create, seed, and query the HarborWing Air database.

### Prerequisites
* MySQL Server (v8.0 or higher) and MySQL Workbench installed[cite: 4].
* Python 3.x installed.

### Step 1: Create the Database and Schema
1. Open **MySQL Workbench** and connect to your local MySQL instance.
2. Open a new SQL tab, paste the schema script provided in your project files (which creates the 11 tables with proper InnoDB engines, foreign keys, constraints, and indexes), and execute it[cite: 4].
3. Ensure the database name is `harborwing_air`[cite: 7].

### Step 2: Set Up and Run the Data-Generation Script
1. Install the required Python libraries using your terminal or command prompt:
   ```bash
   pip install faker mysql-connector-python
