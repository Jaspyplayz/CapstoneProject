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
            return PausedState(game)
        
        elif state_name == "options":
            from game_states.option_state import OptionsState
            return OptionsState(game)
        
     
        


           

