from osbrain import Agent
from random import randint
from kInterest import listOfKInterests


class InitiatorAgent(Agent):

    noOfInterests = 0
    interests = []
    
    #Selecting the desired interest by generating random number
    def SelectInterests(self):
        while (len(self.interests) < self.noOfInterests):
            interestIndex = randint(0,len(listOfKInterests) - 1)
            if (listOfKInterests[interestIndex] not in self.interests):
                self.interests.append(listOfKInterests[interestIndex])
                
        self.log_info(self.interests)
    
    #Sending like message
    def send_Like_Message(self):
        interest = self.interests[randint(0, len(self.interests) - 1)]
        self.log_info(f'Hey! Do you like {interest} ?')
        self.send('ask', f'Hey! Do you like {interest} ?')
    
    #receiving reply to the like query
    def receiveReply(self, message):
        sender = message.split(' ')[0]
        reply = message.split(' ')[1]
        self.log_info(f'{sender} replied {reply}')
        
        if (reply == 'YES'):
            self.send('matchNotifyChannel', f'{self.name} {sender}')