class StateFactory:

    @staticmethod
    def create_state(state_name, game, **kwargs):

        if state_name == "menu":
            from game_states.menu_state import MenuState
            return MenuState(game)
        
        elif state_name == "play":
            from game_states.play_state import PlayState
            return PlayState(game)
        
        elif state_name == "pause":
            from game_states.paused_state import PausedState
            previous_state = kwargs.get("previous_state", game.state)
            return PausedState(game, previous_state)
        
     
        


           

