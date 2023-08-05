"""
<name>Earth</name>
<description>Multivariate Adaptive Regression Splines (MARS)</description>
<category>Regression</category>
<icon>icons/EarthMars.svg</icon>
<priority>100</priority>
<tags>MARS, Multivariate, Adaptive, Regression, Splines</tags>
"""

import Orange

from OWWidget import *
import OWGUI

from orngWrap import PreprocessedLearner

from orangecontrib import earth

NAME = "Earth"
DESCRIPTION = "Multivariate Adaptive Regression Splines (MARS)"
ICON = "icons/EarthMars.svg"
CATEGORY = "Regression"
PRIORITY = 100

KEYWORDS = ["MARS", "Multivariate", "Adaptive", "Regression", "Splines"]

INPUTS = (
    {"name": "Data",
     "type": Orange.data.Table,
     "handler": "set_data",
     "doc": "Set input training data set."},

    {"name": "Preprocessor",
     "type": PreprocessedLearner,
     "handler": "set_preprocessor",
     "doc": "Data Preprocessor"}
)

OUTPUTS = (
    ("Learner", earth.EarthLearner),
    ("Predictor", earth.EarthClassifier),
    ("Basis Matrix", Orange.data.Table)
)

REPLACES = ["Orange.OrangeWidgets.Regression.OWEarth.OWEarth"]


class OWEarth(OWWidget):
    settingsList = ["name", "degree", "terms", "penalty"]

    def __init__(self, parent=None, signalManager=None,
                 title="Earth"):
        OWWidget.__init__(self, parent, signalManager, title,
                          wantMainArea=False, resizingEnabled=False)

        self.name = "Earth Learner"
        self.degree = 1
        self.terms = 21
        self.penalty = 2

        self.loadSettings()

        #####
        # GUI
        #####

        OWGUI.lineEdit(self.controlArea, self, "name",
                       box="Learner/Classifier Name",
                       tooltip="Name for the learner/predictor")

        box = OWGUI.widgetBox(self.controlArea, "Forward Pass", addSpace=True)

        form = QFormLayout(
            labelAlignment=Qt.AlignLeft, formAlignment=Qt.AlignLeft,
            fieldGrowthPolicy=QFormLayout.AllNonFixedFieldsGrow)
        box.layout().addLayout(form)

        b1 = OWGUI.widgetBox(box, "")
        OWGUI.spin(b1, self, "degree", 1, 3, step=1,
                   tooltip="Maximum degree of the terms derived "
                           "(number of hinge functions).")

        b2 = OWGUI.widgetBox(box, "")
        s = OWGUI.spin(b2, self, "terms", 1, 200, step=1,
                       tooltip="Maximum number of terms derived in the "
                               "forward pass.")
        s.control.setSpecialValueText("Automatic")

        form.addRow("Max. term degree", b1)
        form.addRow("Max. terms", b2)

        box = OWGUI.widgetBox(self.controlArea, "Pruning Pass", addSpace=True)
        OWGUI.doubleSpin(box, self, "penalty", min=0.0, max=10.0, step=0.25,
                   label="Knot penalty")

        OWGUI.button(self.controlArea, self, "&Apply",
                     callback=self.apply)

        self.data = None
        self.preprocessor = None
        self.resize(300, 200)

        self.apply()

    def set_data(self, data=None):
        """
        Set the input data set.
        """
        self.data = data

    def set_preprocessor(self, pproc=None):
        self.preprocessor = pproc

    def handleNewSignals(self):
        self.apply()

    def apply(self):
        learner = earth.EarthLearner(
            degree=self.degree,
            terms=self.terms if self.terms >= 2 else None,
            penalty=self.penalty,
            name=self.name
        )

        predictor = None
        basis_matrix = None
        if self.preprocessor:
            learner = self.preprocessor.wrapLearner(learner)

        self.error(0)
        if self.data is not None:
            try:
                predictor = learner(self.data)
                predictor.name = self.name
            except Exception, ex:
                self.error(0, "An error during learning: %r" % ex)

            if predictor is not None:
                base_features = predictor.base_features()
                basis_domain = Orange.data.Domain(
                    base_features,
                    self.data.domain.class_var,
                    self.data.domain.class_vars)
                basis_domain.add_metas(self.data.domain.get_metas())
                basis_matrix = Orange.data.Table(basis_domain, self.data)

        self.send("Learner", learner)
        self.send("Predictor", predictor)
        self.send("Basis Matrix", basis_matrix)

    def sendReport(self):
        self.reportSettings(
            "Learning parameters",
            [("Degree", self.degree),
             ("Terms", self.terms if self.terms >= 2 else "Automatic"),
             ("Knot penalty", "%.2f" % self.penalty)
             ])

        self.reportData(self.data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWEarth()
    w.set_data(Orange.data.Table("auto-mpg"))
    w.show()
    app.exec_()
    w.saveSettings()
