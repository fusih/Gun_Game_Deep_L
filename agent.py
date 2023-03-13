from game import GunGameAI

obj = GunGameAI()

while(True):
    x = input("in: ")
    if x ==  "1":
        reward, done, score = obj.play_step([1,0,0])
    elif x == "2":
        reward, done, score = obj.play_step([0,1,0])
    elif x == "3":
        reward, done, score = obj.play_step([0,0,1])
     
    print("Reward: "+ str(reward) + "Score: " + str(score))
    if(done):
        break
