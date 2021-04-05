# -*- coding: utf-8 -*-

import re

from PyQt5.QtGui import QValidator

class PersonalValidtor(QValidator):
    def fixup(self, a0: str) -> str:
        return super().fixup(a0)