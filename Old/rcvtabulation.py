import csv
import time

# open the results file and save the contents as a list. 
# position 0 = vote number (for audit purposes), position 1 = Shared/Not shared, Position 2 - 6 = preferences
with open('rcvresults.csv', 'r') as f:
    fhandle = csv.reader(f)
    list_of_votes = list(fhandle)

# create a new txt file named Election Results with the current time
filename = 'Election_Results_' + time.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
resultsfile = open(filename, 'w')
# Label variables. The string in position 1 on the candidates is the candidate's name
candidate1 = [0, 'A']
candidate2 = [0, 'B']
candidate3 = [0, 'C']
candidate4 = [0, 'D']
candidate5 = [0, 'E']
candidates = [candidate1, candidate2, candidate3, candidate4, candidate5]
votecount = 0
round = 0
winner = False
winnerfound = False
# number of candidates = noc
noc = len(candidates)
ballotscounted = 0
single = 0
dual = 0


# function used to calculate the lowest vote amount of a round
def resultlow(candidates):
    lowest = None
    for result in candidates:
        if result[0] is None:
            continue
        elif lowest is None:
            lowest = result[0]
        elif result[0] < lowest:
            lowest = result[0]
    return lowest


# function used to calculate the highest vote amount of a round
def resulthigh(candidates):
    highest = None
    for result in candidates:
        if result[0] is None:
            continue
        if highest is None:
            highest = result[0]
        elif result[0] > highest:
            highest = result[0]
    return highest


# function that takes the amount of votes cast in a round and determines
# if any candidate reached higher than 50%	
def resultwinner(count, high):
    majority = count / 2
    if high is None:
        return True
    elif high > majority:
        return True
    else:
        return False


# function that takes the lowest vote getter(s) and changes their type to None to declare them Eliminated
def resultelim(lowest, cvotes):
    if cvotes == lowest:
        return None
    else:
        return cvotes


# function that looks at a vote and determines which preference will be used.
# a preference is determined by the preference order chosen by the voter and then by if a candidate has been 
# eliminated or if the voter Under or Over voted.
def preference(noc, candidates, vote):
    perf = 0
    for num in range(noc):
        perf = num + 2
        for candidate in candidates:
            if vote[num + 2] == candidate[1] and candidate[0] is not None:
                return perf


# function that looks at each vote and depending on their preference assigns that vote to a candidate.
# if the vote is for a shared property, only 1/2 vote is given to the candidate.				
def tabulation(votecount, candidates, list_of_votes, noc):
    for vote in list_of_votes:
        perf = preference(noc, candidates, vote)
        for candidate in candidates:
            if perf is None:
                continue
            elif candidate[1] == vote[perf]:
                if vote[1] == 'Not Shared':
                    candidate[0] = candidate[0] + 1
                    votecount = votecount + 1
                if vote[1] == 'Shared':
                    candidate[0] = candidate[0] + .5
                    votecount = votecount + .5
    return candidates, votecount


# function for calculating the vote summary. This will add up all of the votes per preference column and return
# the total vote count of that column, how many times each candidate was voted for, how many ballots were counted,
# how many over and under votes there were. 
# this function only looks at one choice at a time (1st, 2nd, etc.) so it is looped to get the full picture
def votesummarycalc(list_of_votes, candidates, preference):
    votecount = 0
    overvotes = 0
    undervotes = 0
    ballotscounted = 0
    single = 0
    dual = 0
    for vote in list_of_votes:
        if vote[preference] == 'OVER':
            if vote[1] == 'Not Shared':
                overvotes = overvotes + 1
                votecount = votecount + 1
                single = single + 1
                ballotscounted = ballotscounted + 1
            if vote[1] == 'Shared':
                overvotes = overvotes + .5
                votecount = votecount + .5
                dual = dual + 1
                ballotscounted = ballotscounted + 1
        elif vote[preference] == 'UNDER':
            if vote[1] == 'Not Shared':
                undervotes = undervotes + 1
                votecount = votecount + 1
                single = single + 1
                ballotscounted = ballotscounted + 1
            if vote[1] == 'Shared':
                undervotes = undervotes + .5
                votecount = votecount + .5
                dual = dual + 1
                ballotscounted = ballotscounted + 1
        for candidate in candidates:
            if candidate[1] == vote[preference]:
                if vote[1] == 'Not Shared':
                    candidate[0] = candidate[0] + 1
                    votecount = votecount + 1
                    single = single + 1
                    ballotscounted = ballotscounted + 1
                if vote[1] == 'Shared':
                    candidate[0] = candidate[0] + .5
                    votecount = votecount + .5
                    dual = dual + 1
                    ballotscounted = ballotscounted + 1
    return candidates, votecount, overvotes, undervotes, ballotscounted, single, dual


# function that takes the results from the votesummarycalc function and prints them to the results txt
# file. 	
def votesummaryprint(candidates, votecount, overvotes, undervotes, ballotscounted, single, dual, choice):
    votesummarystr = []
    choice = str(choice - 1)
    choicestr = '          *****Summary of choice %s*****\n' % choice
    votesummarystr.append(choicestr)
    for candidate in candidates:
        canstr = '%22s %s\n' % (candidate[1], candidate[0])
        votesummarystr.append(canstr)
    overstr = '%22s %s\n' % ('Overvotes', overvotes)
    understr = '%22s %s\n' % ('Undervotes', undervotes)
    votecountstr = '%22s %s\n' % ('Votecount', votecount)
    singlestr = '%22s %s\n' % ('Single Owner Ballots', single)
    dualstr = '%22s %s\n' % ('Dual Owner Ballots', dual)
    ballotsstr = '%22s %s\n\n' % ('Total ballots counted', ballotscounted)
    votesummarystr.append(overstr)
    votesummarystr.append(understr)
    votesummarystr.append(votecountstr)
    votesummarystr.append(singlestr)
    votesummarystr.append(dualstr)
    votesummarystr.append(ballotsstr)
    for line in votesummarystr:
        resultsfile.write(line)


# function that sets all of the votecount values to 0. Used when calculating the vote summary and
# preparing for the official Rank Choice tally.
def rezero(candidates, votecount, ballotscounted):
    votecount = 0
    ballotscounted = 0
    for candidate in candidates:
        candidate[0] = 0
    return candidates, votecount, ballotscounted


# function that prints two lines of stars into the results txt file.
def stars():
    resultsfile.write('******************************************************\n')
    resultsfile.write('******************************************************\n')


# This part of the code calculates the Summary of Votes. It loops through the relevant functions
# and then writes the results to the results file.
stars()
resultsfile.write('Summary of votes\n')
for num in range(noc):
    num = num + 2
    candidates, votecount, overvotes, undervotes, ballotscounted, single, dual = votesummarycalc(list_of_votes,
                                                                                                 candidates, num)
    votesummaryprint(candidates, votecount, overvotes, undervotes, ballotscounted, single, dual, num)
    candidates, votecount, ballotscounted = rezero(candidates, votecount, ballotscounted)

# This part of the code determines the winner of the Rank Choice election. It loops until a
# winner is found using the winnerfound variable. It starts by determining the round and then
# looking at the first valid preference of each voter. If there is a candidate who has reached 
# greater than 50% that candidate is determined to be a winner. If there is no winner, it takes
# the lowest vote getter(s) and eliminates them. The loop repeats and everyone whose preference 
# was chosen for the now eliminated candidate is redistributed to the voter's next valid preference.
#
# If a ballot is removed from the count because there are no valid choices, the total vote count will
# be lower than the votecount.
#
# If there are any Shared Properties that voted, the votecount will be lower than the amount of ballots
# counted. 
while winnerfound is False:
    candidates, votecount = tabulation(votecount, candidates, list_of_votes, noc)
    round = round + 1
    low = resultlow(candidates)
    high = resulthigh(candidates)
    winner = resultwinner(votecount, high)
    roundtext = '               Round ' + str(round) + ' results: \n'
    if winner:
        for candidate in candidates:
            if candidate[0] is None:
                continue
            elif candidate[0] >= high:
                candidate[0] = str(candidate[0]) + '----- Winner!'
    stars()
    if round == 1:
        resultsfile.write('Election Results\n')
    resultsfile.write(roundtext)
    for candidate in candidates:
        if candidate[0] is None:
            resultstr1 = 'Eliminated'
        else:
            resultstr1 = str(candidate[0])
        resultstr2 = '%22s' % (candidate[1])
        resultstrfinal = resultstr2 + '-----' + resultstr1
        resultsfile.write(resultstrfinal)
        resultsfile.write('\n')
    winnerfound = resultwinner(votecount, high)
    votecount = 0
    for candidate in candidates:
        candidate[0] = resultelim(low, candidate[0])
        if candidate[0] is not None:
            candidate[0] = 0

# Close the Results File
resultsfile.close()

# Rank Choice Voting Tabulation Software. 
# Written by Jonathan Layman for Arapahoe County
# For Use in Rank Choice HoA Election
