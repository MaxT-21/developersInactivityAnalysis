import sys, os, shutil
import pandas
import git
import classifier

def add(dataframe, row, contributions_destination):
    """Adds a row to the tail of a dataframe"""
    dataframe.loc[-1] = row  # adding a row
    dataframe.index = dataframe.index + 1  # shifting index
    dataframe.sort_index(inplace=True)
    dataframe.iloc[::-1]
    dataframe.to_csv(contributions_destination,
                            sep=';', na_rep='N/A', index=False, quoting=None, line_terminator='\n')

### MAIN FUNCTION
def main(gitRepoURL):
    # TODO: move this to the Settings.py file
    reposDirectory = '../Local_Repositories'
    os.makedirs(reposDirectory, exist_ok=True)

    # Clone Repo Locally
    try:
        git.Git(reposDirectory).clone(gitRepoURL)
        print('Clone Complete: ', gitRepoURL)
    except:
        print('Clone Failed! Probably repo already exists.')
        pass

    repoName = gitRepoURL.split('/')[-1].split('.')[0]
    if(repoName=='Babylon'):
        repoName='Babylon.js'
    repoDir = os.path.join(reposDirectory, repoName)

    # Init
    # TODO: ./A80_Results/ should be a parameter
    outputDirectory = '../A80_Results/' + repoName
    os.makedirs(outputDirectory, exist_ok=True)

    contributions_destination = os.path.join(outputDirectory, 'commits.csv')
    aggregated_contributions_destination = os.path.join(outputDirectory, 'Cstats.csv')
    contributions = pandas.DataFrame(columns = ['name', 'email', 'date', 'sha'])
    repo = git.Repo(repoDir)

    basic_classifier = classifier.BasicFileTypeClassifier()

    '''try:
        contributions = pandas.read_csv(contributions_destination, sep=';')
        print('Contributions file ALREADY EXISTS, SKIP calculation!')
    except:'''
    exist = os.path.isfile(contributions_destination)
    if exist:
        contributions = pandas.read_csv(contributions_destination, sep=';')
    print('Contributions file not found, STARTING calculation!')
    # Get Commit List
    commits_list = list(repo.iter_commits())
    commits_count = len(commits_list)
    print('Commits: ', commits_count)

    # Select NON-DOC Commits
    Tstatus=5
    for i in range(0, commits_count - 1):
        author_name = commits_list[i].author.name
        author_email = commits_list[i].author.email
        commit_date = commits_list[i].committed_datetime
        commit_sha = commits_list[i].hexsha

        
        if not commit_sha in contributions['sha'].values:
            for file in commits_list[i].diff(commits_list[i + 1]):
                file_path = file.a_path
                # Check Type
                label = basic_classifier.labelFile(file_path)
                if label!=basic_classifier.DOC: # There is at least 1 non-DOC file changed
                    add(contributions, [author_name.lower(), author_email.lower(), commit_date, commit_sha], contributions_destination)
                    break
        else:
            print('Commit already in the list: ', commit_sha)


        ### LOGGING
        perc = int(i/commits_count*100)
        if perc == Tstatus:
            print('Commit filtered {}%'.format(perc))
            Tstatus += 5

    '''contributions['email'] = contributions['email'].str.lower()
    contributions['name'] = contributions['name'].str.lower()
    contributions.to_csv(contributions_destination,
                            sep=';', na_rep='N/A', index=False, quoting=None, line_terminator='\n')
    print('Contributions Written: ', contributions_destination)'''
    pass
    #qua finisce exept
    grouped_contributions = contributions.groupby(['name', 'email']).count()
    grouped_contributions = grouped_contributions.drop(columns=['date'])
    grouped_contributions = grouped_contributions.rename(columns={'sha': 'commits'})
    grouped_contributions.to_csv(aggregated_contributions_destination,
                                 sep=';', na_rep='N/A', index=True, quoting=None, line_terminator='\n')
    print('Grouped Contributions Written: ', aggregated_contributions_destination)

    #shutil.rmtree(repoDir)
    #print('Local Repository REMOVED')

if __name__ == "__main__":
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    os.chdir(THIS_FOLDER)

    ### ARGUMENTS MANAGEMENT
    # python script.py gitCloneURL
    print('Arguments: {} --> {}'.format(len(sys.argv), str(sys.argv)))
    gitRepoURL = sys.argv[1]

    main(gitRepoURL)
