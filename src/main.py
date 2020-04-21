import database as db
import ui
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
	app = QApplication([])
	exe_ = ui.App()
	app.exec_()