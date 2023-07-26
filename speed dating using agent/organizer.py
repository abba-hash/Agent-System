from time import sleep
from osbrain import run_agent
from osbrain import Agent
from initiatorAgent import InitiatorAgent
from responderAgent import ResponderAgent


class OrganizerAgent(Agent):
    
    #executed on initialization
    def on_init(self):
        self.responderAgents = []
        self.initiatorAgents = []
        self.noOfCouples = 0
        self.matched = False
        self.noOfInterests = 0
        self.CT = 1  
    
    #initialize other agents based on the number of couple and assign the interest to them
    def initializeAgents(self):

        for i in range(self.noOfCouples):
            initiatorAgent = run_agent('InitiatorAgent' + str(i), base=InitiatorAgent)
            responderAgent = run_agent('ResponderAgent' + str(i), base=ResponderAgent)
            
            initiatorAgent.noOfInterests = self.noOfInterests
            initiatorAgent.SelectInterests()
            
            responderAgent.noOfInterests = self.noOfInterests
            responderAgent.SelectInterests()

            matchNotifyAddress = initiatorAgent.bind('PUSH', alias="matchNotifyChannel")
            self.connect(matchNotifyAddress, handler='VerifyMatch')

            self.responderAgents.append(responderAgent)
            self.initiatorAgents.append(initiatorAgent) 

    
    def startDating(self):
        if (self.matched == True):
            self.stop()
            return
        
        # when single person and interest is pass
        if(self.CT > self.noOfCouples):
            self.log_info(f'ooh, none of the couples are matched!')            
            self.stop()
            return
            
        self.log_info(f'Turn# {self.CT}')
       
       #same number of initiator agent and responder agent based on the number of couples
        for i in range(self.noOfCouples):
            initiatorAgent = self.initiatorAgents[(i + self.CT - 1) % self.noOfCouples]
            initiatorAgentAddress = initiatorAgent.bind('PUSH', alias='ask')
            
            responderAgent = self.responderAgents[i]
            responderAgentAddress = responderAgent.bind('PUSH', alias='reply')

            responderAgent.connect(initiatorAgentAddress, handler='replyToQuestion')
            initiatorAgent.connect(responderAgentAddress, handler='receiveReply')
            
            initiatorAgent.send_Like_Message()
            #sleep for 1 second after sending
            sleep(1)
            
            responderAgent.close('reply')
            initiatorAgent.close('ask')

        self.CT += 1 
    
    #verify if they have same interest
    def VerifyMatch(self, message):
        if(self.matched == False):
            self.matched = True
            self.log_info(f"{message.split(' ')[0]} and {message.split(' ')[1]} are the first couple to be matched!")
        