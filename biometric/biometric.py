from scipy.spatial.distance import cityblock
from sklearn import svm
import statistics

# calculate keystroke dynamics vector based on user timings
def classify_user(dynamics):
    
    key_times = []
    key_hold = []
    key_idle = []

    # split the array from the client
    for t in dynamics.split(";"):
        key_times.append(t)

    # calculate arrays of key press times and idle times
    for i in range(0,len(key_times) - 1):
        if i % 2 == 0 or i == 0:
            key_hold.append(int(float(key_times[i+1])) - int(float(key_times[i])))
        else:
            key_idle.append(int(float(key_times[i+1])) - int(float(key_times[i])))

    key_hold_mean = statistics.mean(key_hold)
    key_hold_median = statistics.median(key_hold)
    key_idle_mean = statistics.mean(key_idle)
    key_idle_median = statistics.median(key_idle)
    
    return key_hold_mean, key_hold_median, key_idle_mean, key_idle_median


# evaluate keystroke biometrics using manhattan distance calculation, return distance (score) between vectors
def check_user_manhattan(test_vector, user_vector):

    score = cityblock(test_vector, user_vector)
    
    print("User checked with score: ", score)

    return score

# evaluate keystroke biometrics using svm method, return predicted sample
def check_user_svm(users, samples, vector):

    # svc with linear kernel
    clf = svm.SVC(C=0.1,kernel='linear',probability=True, decision_function_shape='ovr')
    clf.fit(samples, users)
    result = clf.predict([vector])

    return result
