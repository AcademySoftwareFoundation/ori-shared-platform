

class ViewportUserInputTx:

    def __init__(self, rpc):
        self.__rpc = rpc

    def mouse_press(self, x, y):
        return self.__rpc.rpc.viewport_user_input_rx.mouse_press(x, y)

    def mouse_drag(self, x, y):
        return self.__rpc.rpc.viewport_user_input_rx.mouse_drag(x, y)

    def mouse_release(self, x, y):
        return self.__rpc.rpc.viewport_user_input_rx.mouse_release(x, y)

    def mouse_move(self, x, y):
        return self.__rpc.rpc.viewport_user_input_rx.mouse_move(x, y)
