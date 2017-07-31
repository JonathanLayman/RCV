from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import csv
import time
import pickle


# Create a Class Object to keep track of Candidate Data
class Candidate:
    def __init__(self, name, election):
        self.election = election
        self.name = name
        self.votes = 0
        self.status = election.candidate_statuses[0]

    # Candidate Class Method used to calculate how many votes a candidate received in a round
    # looks at the voter preference calculated in the Voter class and adds to self.votes
    # if the preference is equal to the name of the candidate
    def calculateRound(self):
        for vote in self.election.voter_list:
            if vote.preference == self.name:
                self.votes += vote.vote_weight

    # Candidate Class Method used to reset each candidates vote counts between rounds
    def reset(self):
        self.votes = 0


# Create a Class object to keep track of every vote and their preferences.
class Voter:
    def __init__(self, vote, election):
        self.election = election
        self.voter_number = vote[0]
        self.shared_status = vote[1]
        if self.shared_status == 'Shared':
            self.vote_weight = 0.5
        elif self.shared_status == 'Not Shared':
            self.vote_weight = 1
        self.votes = vote[2:]
        self.preference = None
        self.status = 'Active'

    # Voter class method to determine which choice will be used in the next round of voting
    def highestChoice(self):
        for vote in self.votes:
            for candidate in self.election.candidates:
                if vote == candidate.name and candidate.status != self.election.candidate_statuses[1]:
                    self.preference = candidate.name
                    break
            else:
                continue
            break


# Class object that keeps track of all data for an election. This object creates and manages the Voter and
# Candidate classes
class RCVElection:
    def __init__(self, result_file):
        self.candidate_statuses = ['In the Running', 'Eliminated', 'Winner', 'Tied Winner']
        self.candidates = []
        self.voter_list = []
        self.data = result_file
        self.round = 0
        self.winner = False
        self.tie = False
        self.total_votes = 0
        self.ballots_counted = 0
        self.dual_ballots = 0
        self.single_ballots = 0
        self.save = ['Summary', [], 'Time', 'Name']
        self.buildElection()

    # RCV class method to establish initial election information after __init__ method has been run.
    # Calculates generic information about the election, like candidate names, voter turn out, etc.
    def buildElection(self):
        candidate_names = []
        number_of_choices = max(len(votes) for votes in self.data)
        for choice in range(2, number_of_choices):
            for vote in self.data:
                if vote[choice] != 'OVER' and vote[choice] != 'UNDER':
                    if not vote[choice] in candidate_names:
                        candidate_names.append(vote[choice])
        candidate_names.sort()
        for name in candidate_names:
            self.candidates.append(Candidate(name, self))
        for vote in self.data:
            self.voter_list.append(Voter(vote, self))
        for vote in self.voter_list:
            self.total_votes += vote.vote_weight
            self.ballots_counted += 1
            if vote.shared_status == 'Shared':
                self.dual_ballots += 1
            elif vote.shared_status == 'Not Shared':
                self.single_ballots += 1

    # RCV class method to generate the Summary of votes for reconciliation purposes. Calls Voter
    # and Candidate class methods and variables.
    def summaryOfVotes(self):
        choice_number = 0
        temp_list = [{'Vote Count': self.total_votes, 'Single Owner Ballots': self.single_ballots,
                      'Dual Owner Ballots': self.dual_ballots}]
        for vote in self.voter_list[0].votes:
            temp_dict = {}
            under_votes = 0
            over_votes = 0
            for voter in self.voter_list:
                voter.preference = voter.votes[choice_number]
                if voter.votes[choice_number] == 'UNDER':
                    under_votes += voter.vote_weight
                elif voter.votes[choice_number] == 'OVER':
                    over_votes += voter.vote_weight
            for candidate in self.candidates:
                candidate.calculateRound()
            choice_number += 1
            temp_dict['Choice'] = choice_number
            for candidate in self.candidates:
                temp_dict[candidate.name] = candidate.votes
                candidate.reset()
            temp_dict['Over Votes'] = over_votes
            temp_dict['Under Votes'] = under_votes
            temp_list.append(temp_dict)
        self.save[0] = temp_list

    # RCV class method to calculate the results of each round of voting.
    def roundTabulation(self):
        self.round += 1
        for voter in self.voter_list:
            voter.highestChoice()
        for candidate in self.candidates:
            candidate.reset()
            candidate.calculateRound()
        self.declareWinner()
        self.eliminateLowest()
        self.saveData()

    # RCV class method to calculate if a winner has been determined.
    def declareWinner(self):
        self.checkForTie()
        if not self.tie:
            for candidate in self.candidates:
                if candidate.votes > self.total_votes / 2:
                    candidate.status = self.candidate_statuses[2]
                    self.winner = True

    # RCV class method to determine if there is a winning tie.
    def checkForTie(self):
        votes_list = []
        for candidate in self.candidates:
            if candidate.status != self.candidate_statuses[0]:
                votes_list.append(candidate.votes)
        if all(votes_list) and len(votes_list) > 0:
            self.tie = True
            self.winner = True
            for candidate in self.candidates:
                if candidate.status != self.candidate_statuses[1]:
                    candidate.status = self.candidate_statuses[3]
        else:
            self.tie = False

    # RCV class method to determine the lowest vote getter and eliminate them.
    def eliminateLowest(self):
        if not self.winner:
            votes_list = []
            for candidate in self.candidates:
                if candidate.status != self.candidate_statuses[1]:
                    votes_list.append(candidate.votes)
            lowest = min(votes_list)
            for candidate in self.candidates:
                if candidate.votes == lowest:
                    candidate.status = self.candidate_statuses[1]

    # RCV class method to create a list that can be saved and read by the GUI.
    def saveData(self):
        temp_dict = {'Round': self.round}
        for candidate in self.candidates:
            temp_dict[candidate.name] = [candidate.votes, candidate.status]
        self.save[1].append(temp_dict)
        self.save[2] = time.strftime('%m/%d%Y %H:%M')

    # RCV class method the run the election until a winner is declared
    def runElection(self):
        while not self.winner:
            self.roundTabulation()

    # RCV class method for developer to pull all candidate data
    def debugCandidateData(self):
        for candidate in self.candidates:
            print('Name: ', candidate.name, 'Votes: ', candidate.votes,
                  'Status', candidate.status)

    # RCV class method for developer to pull all voter data, or a single voter's data.
    def debugVoterData(self, voter_id='All'):
        if voter_id == 'All':
            for voter in self.voter_list:
                print('Number: ', voter.voter_number, 'Shared Status',
                      voter.shared_status, 'Votes: ', voter.votes,
                      'Preference: ', voter.preference, 'Status: ', voter.status)
        else:
            print('Number: ', self.voter_list[voter_id].voter_number, 'Shared Status',
                  self.voter_list[voter_id].shared_status, 'Votes: ', self.voter_list[voter_id].votes,
                  'Preference: ', self.voter_list[voter_id].preference,
                  'Status: ', self.voter_list[voter_id].status)


# Class object that creates and manages the GUI.
class RCVGUI:
    def __init__(self, master):
        self.election = None
        self.summary = None
        self.results = None
        self.save_name = None
        self.election_loaded = False
        self.open_filename = None
        self.file_load = None
        self.data = None
        self.summary_export = BooleanVar()
        self.results_export = BooleanVar()
        self.master = master
        self.master.title('Arapahoe County RCV Software')
        self.master.geometry('480x500+50+100')
        self.master.option_add('*tearOff', False)
        self.menubar = Menu(master)
        self.master.config(menu=self.menubar)
        self.file = Menu(self.menubar)
        self.help_ = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.file, label='File')
        self.menubar.add_cascade(menu=self.help_, label='Help')
        self.file.add_command(label='New', command=lambda: self.newElection())
        self.file.add_command(label='Open...', command=lambda: self.openFile())
        self.file.add_command(label='Save', command=lambda: self.saveFile(), state='disabled')
        self.file.add_command(label='Export', command=lambda: self.exportView(), state='disabled')
        self.help_.add_command(label='Arapahoe County RCV Procedures', command=lambda: self.procedureWindow())
        self.help_.add_command(label='How to use this software', command=lambda: self.howToUse())
        self.help_.add_separator()
        self.help_.add_command(label='About', command=lambda: self.aboutWindow())
        self.logo = PhotoImage(file='Data/ArapahoeLogo.png').subsample(20, 20)
        self.frame_header = ttk.Frame(master)
        self.arapahoe_logo = ttk.Label(self.frame_header, image=self.logo)
        self.title_text = ttk.Label(self.frame_header, font=('Arial', 18, 'bold'), wraplength=250,
                                    text='Arapahoe County RCV Software')
        self.frame_content = ttk.Frame(master)
        self.welcome_label = ttk.Label(self.frame_content,
                                       text='Thank you for using the RCV Tabulation Software.'
                                            ' To load a new election, click the "New" button. To'
                                            ' load a previous election, click the "Open" button',
                                       wraplength=350)
        self.notebook = ttk.Notebook(self.frame_content)
        self.notebook_frame1 = ttk.Frame(self.notebook)
        self.notebook_frame2 = ttk.Frame(self.notebook)
        self.notebook_textbox_frame1 = ScrolledText(self.notebook_frame1, height=18, width=50,
                                                    wrap='word')
        self.notebook_textbox_frame2 = ScrolledText(self.notebook_frame2, height=18, width=50,
                                                    wrap='word')
        self.file_error = messagebox
        self.save_message = ttk.Label(self.frame_content, text='Please enter a Name for this election.')
        self.save_textbox = ttk.Entry(self.frame_content, width=36)
        self.save_button = ttk.Button(self.frame_content, text='Save', command=lambda: self.picklesave())
        self.open_message = ttk.Label(self.frame_content, text='Select a rcv load file to load')
        self.open_textbox = ttk.Entry(self.frame_content, width=40)
        self.select_button = ttk.Button(self.frame_content, text='Select File', command=lambda: self.selectSave())
        self.load_button = ttk.Button(self.frame_content, text='Load Election', command=lambda: self.pickleLoad())
        self.cancel_button = ttk.Button(self.frame_content, text='Cancel', command=lambda: self.body())
        self.export_button = ttk.Button(self.frame_content, text='Export', command=lambda: self.saveExport())
        self.summary_checkbox = ttk.Checkbutton(self.frame_content, text='Summary of Votes',
                                                variable=self.summary_export, onvalue=True, offvalue=False)
        self.results_checkbox = ttk.Checkbutton(self.frame_content, text='Election Results',
                                                variable=self.results_export, onvalue=True, offvalue=False)
        self.export_text = ttk.Label(self.frame_content,
                                     text='Please select the options you would like to export'
                                          'and provide a name for this export', wraplength=350)
        self.export_name = ttk.Label(self.frame_content, text='Name: ')
        self.frame_content_list = [self.welcome_label, self.notebook, self.save_message, self.save_textbox,
                                   self.save_button, self.open_message, self.open_textbox, self.select_button,
                                   self.load_button, self.cancel_button, self.summary_checkbox,
                                   self.results_checkbox, self.export_text, self.export_button,
                                   self.export_name]
        self.header()
        self.body()

    # GUI class method to display the header on the screen.
    def header(self):
        self.frame_header.pack(fill=BOTH)
        self.arapahoe_logo.grid(row=0, column=0)
        self.title_text.grid(row=0, column=1, padx=25)

    # GUI class method to display the main body on the screen.
    def body(self):
        self.clearPage()
        self.frame_content.pack(fill=BOTH, padx=25, pady=25)
        self.welcome_label.grid(row=0, column=0)
        self.file.entryconfig('Save', state='disabled')
        self.file.entryconfig('Export', state='disabled')

    # GUI class method to view a loaded election.
    def electionView(self):
        self.clearPage()
        self.election_loaded = True
        self.notebookView()
        self.displaySummary()
        self.displayResults()
        if self.election_loaded:
            self.file.entryconfig('Save', state='normal')
            self.file.entryconfig('Export', state='normal')

    # GUI class method to manage exporting results from a loaded election.
    def exportView(self):
        self.clearPage()
        self.export_text.grid(row=0, column=0, columnspan=2, pady=15)
        self.summary_checkbox.grid(row=1, column=0, sticky='w')
        self.results_checkbox.grid(row=2, column=0, sticky='w')
        self.export_name.grid(row=3, column=0)
        self.open_textbox.grid(row=3, column=1)
        self.open_textbox.delete(0, END)
        self.export_button.grid(row=4, column=0, pady=15)
        self.cancel_button.grid(row=4, column=1, pady=15)

    # GUI class method that responds to a button press to export a loaded election.
    def saveExport(self):
        filename = 'Exports/' + self.open_textbox.get() + '.txt'
        with open(filename, 'w') as export_file:
            if self.summary_export.get() is True:
                export_file.write(self.notebook_textbox_frame1.get(1.0, END))
            if self.results_export.get() is True:
                export_file.write(self.notebook_textbox_frame2.get(1.0, END))
        self.file_error.showinfo('Save Successful', 'Your file has been saved to the export folder')
        self.open_textbox.delete(0, END)
        self.body()

    # GUI class method to load a new election.
    def newElection(self):
        filename = filedialog.askopenfile(initialdir='/')
        try:
            with open(filename.name, 'r') as csv_file:
                reader = csv.reader(csv_file)
                list_of_votes = list(reader)
            self.election = RCVElection(list_of_votes)
            self.election.summaryOfVotes()
            self.election.runElection()
            self.data = self.election.save
            self.electionView()
        except:
            self.file_error.showerror('Error', 'Please select a election result file in the proper format')
            self.body()

    # GUI class method to view a notebook of the Summary of Votes and Election Results.
    def notebookView(self):
        self.clearPage()
        self.notebook.grid(row=0, column=0)
        self.notebook.add(self.notebook_frame1, text='Summary of Votes')
        self.notebook.add(self.notebook_frame2, text='RCV Election Results')

    # GUI class method to display the Summary of Votes to the Notebook.
    def displaySummary(self):
        self.summary = self.data[0]
        self.notebook_textbox_frame1.pack()
        self.notebook_textbox_frame1.insert(1.0, '----- Summary of Votes -----\n\n----- Basic Info -----\n')
        for line in self.summary:
            for key, value in line.items():
                if key == 'Choice':
                    self.notebook_textbox_frame1.insert(END, '----- ' + key)
                    self.notebook_textbox_frame1.insert(END, ' ' + str(value) + ' -----\n')
                else:
                    self.notebook_textbox_frame1.insert(END, str(value).rjust(4) + ' -- ')
                    self.notebook_textbox_frame1.insert(END, key + '\n')
            self.notebook_textbox_frame1.insert(END, '\n')
        self.notebook_textbox_frame1.config(state='disabled')

    # GUI class method to display the Election Results to the Notebook.
    def displayResults(self):
        self.results = self.data[1]
        self.notebook_textbox_frame2.pack()
        self.notebook_textbox_frame2.insert(1.0, '----- RCV Election Results -----\n\n')
        for line in self.results:
            for key, value in line.items():
                if key == 'Round':
                    self.notebook_textbox_frame2.insert(END, '----- ' + key)
                    self.notebook_textbox_frame2.insert(END, ' ' + str(value) + ' -----\n')
                else:
                    self.notebook_textbox_frame2.insert(END, str(value[1]).rjust(14) + ' -- ' +
                                                        str(value[0]).rjust(4) + ' -- ' + key + '\n')
            self.notebook_textbox_frame2.insert(END, '\n')
        self.notebook_textbox_frame2.config(state='disabled')

    # GUI Class method to remove all widgets from the content frame
    def clearPage(self):
        for widget in self.frame_content_list:
            widget.grid_remove()

    # GUI class method to save a loaded election as a .rcv file.
    def saveFile(self):
        self.clearPage()
        self.save_message.grid(row=0, column=0)
        self.save_textbox.grid(row=0, column=1)
        self.save_button.grid(row=1, column=1, sticky='w')
        self.cancel_button.grid(row=1, column=1, sticky='e')

    # GUI class method to save the bianary data as .rcv using the pickle module.
    def picklesave(self):
        self.clearPage()
        self.save_name = self.save_textbox.get()
        self.save_name = 'Saves/' + self.save_name + '.rcv'
        pickle.dump(self.data, open(self.save_name, 'wb'))
        self.save_textbox.delete(0, END)
        self.body()

    # GUI class method to open a saved election as a .rcv file.
    def openFile(self):
        self.clearPage()
        self.open_message.grid(row=0, column=0)
        self.open_textbox.grid(row=0, column=1)
        self.open_textbox.delete(0, END)
        self.select_button.grid(row=1, column=1, sticky='w')
        self.load_button.grid(row=1, column=1)
        self.cancel_button.grid(row=1, column=1, sticky='e')

    # GUI class method to select a file to load from.
    def selectSave(self):
        self.open_filename = filedialog.askopenfile(initialdir='Saves')
        self.open_textbox.delete(0, END)
        try:
            self.open_textbox.insert(0, self.open_filename.name)
        except:
            self.openFile()

    # GUI class method to load the .rcv file and interpret it.
    def pickleLoad(self):
        self.clearPage()
        self.data = pickle.load(open(self.open_filename.name, 'rb'))
        self.electionView()

    # GUI class method to pop up a window with the arapahoe county RCV Procedures.
    def procedureWindow(self):
        with open('Data/Procedures.txt', 'r') as txt_file:
            help_doc = txt_file.read()
        help_window = Toplevel(self.master)
        help_window.geometry('800x600+75+40')
        help_window.title('RCV Procedures')
        help_text = ScrolledText(help_window, width=135, height=50, wrap='word')
        help_text.insert(1.0, help_doc)
        help_text.pack()
        help_text.config(state='disabled')

    # GUI class method that displays the about information
    def aboutWindow(self):
        self.file_error.showinfo('About', 'Arapahoe County RCV Voting Tabulation Software.\nDeveloped by Jonathan'
                                          ' Layman.')

    # GUI class method that displays the how to use documentation
    def howToUse(self):
        with open('Data/How_to_use.txt', 'r') as txt_file:
            use_doc = txt_file.read()
        use_window = Toplevel(self.master)
        use_window.geometry('800x600+75+40')
        use_window.title('How to Use')
        use_text = ScrolledText(use_window, width=135, height=50, wrap='word')
        use_text.insert(1.0, use_doc)
        use_text.pack()
        use_text.config(state='disabled')


# Main program loop
def main():
    root = Tk()
    rcv_gui = RCVGUI(root)
    root.mainloop()


if __name__ == "__main__": main()
