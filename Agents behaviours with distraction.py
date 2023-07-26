from spade.behaviour import FSMBehaviour, State
from spade.agent import Agent
from spade import behaviour
from spade.message import Message
import asyncio
import json
import random
import datetime,time

DEBUG = False

#https://spade-mas.readthedocs.io/en/latest/agents.html
#different behaviours
class Behaviours(FSMBehaviour):
    async def on_end(self):
        print(f"Behaviour finished with exit code {self.exit_code}")
        await self.agent.stop()

#https://spade-mas.readthedocs.io/en/latest/agents.html
class Player(Agent):
    name = None
    otherPlayerName = None
    #Chance of getting distraction
    distractionChance : int = 50 

    async def setup(self):
        self.name = self.get('name')
        self.otherPlayerName = self.get('otherPlayerName')
        self.message_wait_timeout = 60
        self.count = 0
        
        print(f"Player{self.name} started.")
        
        #Add start and transition
        fsm = Behaviours()
        fsm.add_state(name="COUNTING", state=Counting(), initial=True)
        fsm.add_state(name="DISTRACTED", state=Distracted())
        fsm.add_transition(source="COUNTING", dest="DISTRACTED")

        self.add_behaviour(fsm)

class Counting(State):
    async def run(self):
        isDistracted = False        
        while not isDistracted:
            isDistracted = await playerAction(self, False)
        
        self.set_next_state("DISTRACTED")

class Distracted(State):
    async def run(self):
        print(f"Player{self.agent.name}'s STATE CHANGED TO DISTRACTED")
        while True:
            isDistracted = await playerAction(self, True)
            if isDistracted:
                print(f"Player{self.agent.name} is ALREADY in DISTRACTED STATE")
                

async def playerAction(self : State, isDistracted: bool):
    # PlayerA starts waiting and then sends reply
    waitForMessage = True
    # PlayerB sends message and then starts waiting
    if (self.agent.name == "1"):
        waitForMessage = False;

    while True:
        if (waitForMessage):
            isDistracted = await wait_for_message(self, isDistracted)
            
            if (self.agent.name == "2"):
                waitForMessage = False
            else: 
                #playerA
                return isDistracted

        else: 
            #sendReply
            await send_reply(self)
            
            if (self.agent.name == "1"):
                waitForMessage = True
            else: 
                #playerB
                return isDistracted

async def wait_for_message(self:State, isDistracted:bool):
    if DEBUG : print(f"Player{self.agent.name} is waiting for message from Player{self.agent.otherPlayerName}...")
    
    while True:
        msg = await self.receive(timeout=self.agent.message_wait_timeout)
        
        if msg:
            if DEBUG : print(f"Player{self.agent.name} received message: {msg.body}")
            body = json.loads(msg.body)
            receivedCount = int(body["count"])
            
            if str(msg.sender) == "abba@shad0w.io/3":
                # message received from PlayerCAgent, check if player got distracted
                if random.randrange(1, 101) < self.agent.distractionChance:
                    
                    # got distracted
                    print(f"Player{self.agent.name} got distracted!")
                    self.agent.count = receivedCount + 1
                    isDistracted = True
                    
                    # wait for actual message from other player and discard it
                    msg = await self.receive(timeout=self.agent.message_wait_timeout)
                    if msg:
                        if DEBUG : print(f"[{self.agent.count}] Player{self.agent.name} received message: {msg.body} and discarding it!")
                        return isDistracted
                    
            

            else: 
                # message received from other player (not from the spy)
                self.agent.count = receivedCount + 1
                return isDistracted
        else:
            print(f"Player{self.agent.name} Did not receive any message after: {self.agent.message_wait_timeout} seconds")
            self.kill(exit_code=1)


async def send_reply(self : State):
    #Waiting time before reply
    await asyncio.sleep(1)
    msg = Message(to="abba@shad0w.io/" + self.agent.otherPlayerName)
    msg.set_metadata("performative", "inform")
    msg.body = json.dumps({"count" : self.agent.count})
    await self.send(msg)

    print(f"Player{self.agent.name} Count={self.agent.count}")


#https://spade-mas.readthedocs.io/en/latest/agents.html
class PlayerC(Agent):
    class PlayerCBehaviour(behaviour.PeriodicBehaviour):
        async def run(self):
            target = random.randrange(1, 3)
            randomCount = random.randrange(1, 1001)
            
            recipient = f"abba@shad0w.io/{target}"
            msg = Message(to=recipient)
            msg.set_metadata("performative", "inform")

            msg.body = json.dumps({"count" : randomCount})
            await self.send(msg)

            print(f"PlayerC sent message 'Count={randomCount}' to Player{target}")

        async def on_end(self):
            print(f"PlayerCBehaviour ended with exit code {self.exit_code}.")
            await self.agent.stop()

    async def setup(self):
        print(f"PlayerC started!")
        
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=20)
        self.add_behaviour(self.PlayerCBehaviour(period = 10, start_at=start_at))


if __name__ == "__main__":
    player1 = Player("abba@shad0w.io/1", "123456")
    player1.set("name", "1")
    player1.set("otherPlayerName", "2")

    future = player1.start()
    future.result()

    player2 = Player("abba@shad0w.io/2", "123456")
    player2.set("name", "2")
    player2.set("otherPlayerName", "1")
    player2.start()

    playerC = PlayerC("abba@shad0w.io/3", "123456")
    playerC.start()

    while player1.is_alive() or player2.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            player1.stop()
            player2.stop()
            playerC.stop()
            break
    
    playerC.stop()    
    print("Agents finished")