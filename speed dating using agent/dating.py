import sys
from osbrain import run_agent
from osbrain import run_nameserver
from organizer import OrganizerAgent 


if __name__ == '__main__':

    noOfarg = len(sys.argv)

    if ( noOfarg != 3):
        print("You must enter only the number of couples and number of interests! (e.g.: python dating.py 10 10")
        exit()

    ns_sock = run_nameserver()
     
    #Run Organiser Agent
    organizerAgent = run_agent('OrganizerAgent', base=OrganizerAgent)
    #number of couples pass as arguement
    organizerAgent.noOfCouples = int(sys.argv[1])
    #number of interest pass as arguement
    organizerAgent.noOfInterests = int(sys.argv[2])
    #initializer other agents
    organizerAgent.initializeAgents()
    
    #Exception Handling
    while organizerAgent.is_running():
        try: 
            organizerAgent.startDating()
        except KeyboardInterrupt:
            ns_sock.shutdown_agents()
            ns_sock.shutdown()
        
    ns_sock.shutdown_agents()
    ns_sock.shutdown()