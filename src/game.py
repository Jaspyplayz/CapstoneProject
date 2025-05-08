import pygame 
from src.player import Player 
from game_states import MenuState, PlayState

class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800,600))
        pygame.display.set_caption("My Python Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(400,300)

        self.state = MenuState(self)


    def handle_events(self):

        events = pygame.event.get()
        for event in events:
            
            #Quit
            if event.type == pygame.QUIT:
                self.running = False

            #Change game state
            if self.running:
                self.state.handle_events(event)
            

    def update(self):
        self.player.update()

    def render(self):
        self.screen.fill((0,0,0))
        self.player.draw(self.screen)
        pygame.display.flip()

    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()

    