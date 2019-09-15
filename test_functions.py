from keras.models import Sequential, load_model
from keras.layers import Dense
import numpy as np
import json
import random
from sklearn.preprocessing import StandardScaler #allows to reuse scale on new data
from time import sleep
incorrect_add_train = [[1, 1]]
incorrect_add_test = [3]
correct_add_train = [[1, 3]]
correct_add_test = [4]

incorrect_subtract_train = [[4, 2]]
incorrect_subtract_test = [3]
correct_subtract_train = [[3, 1]]
correct_subtract_test = [2]

incorrect_multiply_train = [[1, 1]]
incorrect_multiply_test = [3]
correct_multiply_train = [[1, 3]]
correct_multiply_test = [3]

incorrect_divide_train = [[2, 1]]
incorrect_divide_test = [3]
correct_divide_train = [[12, 0.333]]
correct_divide_test = [4]

lists = [[correct_add_train, correct_add_test, incorrect_add_train, incorrect_add_test], 
         [correct_subtract_train, correct_subtract_test, incorrect_subtract_train, incorrect_subtract_test], 
         [correct_multiply_train, correct_multiply_test, incorrect_multiply_train, incorrect_multiply_test], 
         [correct_divide_train, correct_divide_test, incorrect_divide_train, incorrect_divide_test]]


def make_model():
    model = Sequential()
    model.add(Dense(6, input_dim=2, activation='relu'))
    model.add(Dense(6, activation='relu'))   
    model.add(Dense(1, activation='linear')) 
    model.compile(loss='mse', optimizer='adam')
    return model
    
models = [make_model(), make_model(), make_model(), make_model()]


def wrong(t):
    global lists
    generate_wrong(100, t)
    combined = list(zip(lists[t][0], lists[t][1]))
    random.shuffle(combined)
    if len(lists[t][0]) > 50:
        if len(lists[t][0]) < 1000:
            lists[t][0][:], lists[t][1][:] = zip(*combined)
            lists[t][0] = lists[t][0][50:]
            lists[t][1] = lists[t][1][50:]
        else:
            lists[t][0][:], lists[t][1][:] = zip(*combined)
            lists[t][0] = lists[t][0][100:]
            lists[t][1] = lists[t][1][100:]
    

def right(t):
    global lists
    generate_right(100, t)
    combined = list(zip(lists[t][2], lists[t][3]))
    random.shuffle(combined)

    if len(lists[t][2]) > 50:
        if len(lists[t][2]) < 1000:
            lists[t][2][:], lists[t][3][:] = zip(*combined)
            lists[t][2] = lists[t][2][50:]
            lists[t][3] = lists[t][3][50:]
        else:
            lists[t][2][:], lists[t][3][:] = zip(*combined)
            lists[t][2] = lists[t][2][100:]
            lists[t][3] = lists[t][3][100:]

def generate_wrong(n, t):
    global lists
    for i in range(n):
        n1 = random.random()*100
        if t > 1:
            n2 = random.random()*10
        else:
            n2 = random.random()*100
            
        if t == 0:
            lists[t][2].append([n1, n2])
            lists[t][3].append(random.random()*200)
        elif t == 1:
            lists[t][2].append([max(n1, n2), min(n1, n2)])
            lists[t][3].append(random.random()*100)
        elif t == 2:
            lists[t][2].append([n1, n2])
            lists[t][3].append(random.random()*1000)
        elif t == 3:
            lists[t][2].append([max(n1, n2), min(n1, n2)])
            lists[t][3].append(random.random()*100)
  
def generate_right(n, t):
    global lists
    for i in range(n):
        n1 = random.random()*100
        if t > 1:
            n2 = random.random()*10
        else:
            n2 = random.random()*100
            
        if t == 0:
            lists[t][0].append([n1, n2])
            lists[t][1].append(n1+n2)
        elif t == 1:
            lists[t][0].append([max(n1, n2), min(n1, n2)])
            lists[t][1].append(abs(n1-n2))
        elif t == 2:
            lists[t][0].append([n1, n2])
            lists[t][1].append(n1*n2)
        elif t == 3:
            lists[t][0].append([max(n1, n2), 1/min(n1, n2)])
            lists[t][1].append(max(n1, n2) / min(n1, n2))
    
c=0
while True:
    c+=1
    if c > 1000:
        break
    tt = random.randint(0, 3)
    n1 = int(random.random()*100)
    if tt > 1:
            n2 = int(random.random()*10)
    else:
        n2 = int(random.random()*100)
    scaler = StandardScaler().fit(lists[tt][0] + lists[tt][2])
    op = ""
    if tt == 0:
        correct = n1 + n2
        op = "+"
    elif tt == 1:
        correct = abs(n1-n2)
        op = "-"
    elif tt == 2:
        correct = n1 * n2
        op = "*"
    elif tt == 3:
        if n1 == 0:
            n1 = 1
        if n2 == 0:
            n2 = 1
        while max(n1, n2) % min(n1, n2) != 0:
            n1 = int(random.random()*99+1)
            n2 = int(random.random()*9+1)
        correct = max(n1, n2) / min(n1, n2)
        op = "/"
    n11 = n1
    n1 = max(n1, n2)
    n2 = min(n11, n2)
    guess = round(models[tt].predict(scaler.transform(np.array([[n1, n2 if tt != 3 else 1/n2]])))[0][0], 2)
    print("Yo, what's " + str(max(n1, n2)) + str(op)+str(min(n1, n2))+"?")
    user_input = int(input ("Yo, what's " + str(max(n1, n2)) + str(op)+str(min(n1, n2))+"?")) #n1 + n2 if tt == 0 else abs(n1-n2) if tt==1 else n1*n2 if tt==2 else max(n1,n2)/min(n1,n2) 
    print("Difference: "+ str(abs(guess-user_input)))
    if user_input == -69:
        break
    if user_input == correct:
        print("Correct")
        right(tt)
    else:
        print("Wrong! Correct answer: " + str(correct))
        wrong(tt)
    print("Brain guessed: " + str(guess))
    scaler = StandardScaler().fit(lists[tt][0] + lists[tt][2])
    X = scaler.transform(lists[tt][0] + lists[tt][2])  
    models[tt].fit(np.array(X), lists[tt][1] + lists[tt][3], epochs=10, shuffle=True, batch_size=32, verbose=0)
    