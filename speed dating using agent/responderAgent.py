from osbrain import Agent
from random import randint
from kInterest import listOfKInterests


class ResponderAgent(Agent):

    noOfInterests = 0
    interests = []

    def SelectInterests(self):
        while (len(self.interests) < self.noOfInterests):
            interestIndex = randint(0,len(listOfKInterests) - 1)
            if (listOfKInterests[interestIndex] not in self.interests):
                self.interests.append(listOfKInterests[interestIndex])
        
        self.log_info(self.interests)

    
    def replyToQuestion(self, message):
        askedInterest = message.split(' ')[-2]
        
        #Check if its among the interest he/she likes
        if(askedInterest in self.interests):
            self.log_info('YES')
            self.send('reply', f'{self.name} YES')
        else:
            self.log_info('NO')
            self.send('reply',f'{self.name} NO')