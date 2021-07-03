# -*- coding: utf-8 -*-
from Terminal import *

if __name__ == "__main__":
    MainApp = QApplication(sys.argv)
    MainTerminal = MainWin()
    MainTerminal.show()
    sys.exit(MainApp.exec_())