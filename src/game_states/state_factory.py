from src.constants import STATE_CHAMPION_SELECT, STATE_GAME_OVER, STATE_MENU, STATE_OPTIONS, STATE_PAUSE, STATE_PLAY

class StateFactory:

    @staticmethod
    def create_state(state_name, game, **kwargs):

        if state_name == STATE_MENU:
            from src.game_states.menu_state import MenuState
            return MenuState(game)
        
        elif state_name == STATE_PLAY:
            from src.game_states.play_state import PlayState
            return PlayState(game)
        
        elif state_name == STATE_PAUSE:
            from src.game_states.paused_state import PausedState
            return PausedState(game)
        
        elif state_name == STATE_OPTIONS:
            from src.game_states.option_state import OptionsState
            return OptionsState(game)
        
        elif state_name == STATE_GAME_OVER:
            from src.game_states.game_over import GameOverState
            return GameOverState(game, game.score)
        
        elif state_name == STATE_CHAMPION_SELECT:
            from src.game_states.champion_select_state import ChampionSelectState
            return ChampionSelectState(game)

        
     
        


           

