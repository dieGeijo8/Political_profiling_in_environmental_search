import pandas as pd
import numpy as np
import json


# some general statistics on the training session data:
# users with missing values - number of unique queries(ratio) - number of unique links(ratio)
def session_results(results, session_id):

    missing = 0
    links = []

    for users in results.keys():

        if str(session_id) not in list(results[users].keys()):
            missing += 1

        else:

            for query in results[users][session_id].keys():
                links.extend(results[users][session_id][query])

    l = np.array(links)
    return(missing / 10, len(l) / 80)


def explore_sessions():
    
    sessions = []
    wing = []
    missing_values = []
    unique_links = []

    for session in range(1, 4):

        lw = open('results_lw_env_' + str(session) + '.json')
        results_lw = json.load(lw)
        res_lw = session_results(results_lw, str(session))
        rw = open('results_rw_env_' + str(session) + '.json')
        results_rw = json.load(rw)
        res_rw = session_results(results_rw, str(session))
        sessions.extend([session, session])
        wing.extend(['left', 'right'])
        missing_values.extend([res_lw[0], res_rw[0]])
        unique_links.extend([res_lw[1], res_rw[1]])

    df = pd.DataFrame(list(zip(sessions, wing, missing_values, unique_links)),
                      columns=['Session', 'Wing', 'Missing val.', 'Uniq.links'])
    df.to_csv('exploring_env_results.csv')

explore_sessions()
