# Rank Choice Voting Python Tabulation Software
This software is used to tabulate a rank choice election. 
It takes a CSV with the raw tally of the election and calculates a Summary of Votes and the Instant Run Off election results.

## Installation
1. Install python 3.x
2. Clone this respository
3. Run RCVsoftware.py
4. You can load the included results.csv to see how the software works, or load your own csv in the same format as results.csv

## License

This project is licensed under the MIT License - see the [LICENSE.MD](LICENSE.MD) file for details

## How to Use:
This software is used to determine the winner of a rank choice voting election. 


To open a new election:
1. Click File > New
2. Navigate to the CSV file containing the election results (format this file
according to the guidelines in the Arapahoe County RCV Procedures)


To Load a previously saved election:
1. Click File > Open... 
2. Click Select File
3. Click the .rcv file with the name of the election you want to load
4. Click Load Election


To Save a loaded election:
1. With an election loaded, click File > Save
2. Enter the name that you want to use for the election.
- These files will be located in the /Saves/ Folder in the root directory
and will be saved in a bianary .rcv format


To Export a loaded election:
1. With an election loaded, click File > Export
2. Check which parts you want to export
3. Enter a name for the election export
4. Click Export to save the file as a .txt file in the /Exports/ folder


------------------------------------------------------------------------------------

What is the Summary of Votes?
- The summary of votes summarizes what happens in each preference column of the
results csv file. This section does not represent the results of the instant 
run off RCV method. It is used for reconciliation purposes.

What is the RCV Election Results?
- This section summarizes what happens in each round. It shows how many votes each
candidate recieved during that round and their current status. The final round will
have a winner declared.

