from bin.texttest import TextTest
from bin.truetypetest import TrueTypeTest
from bin.listtest import ListTest
from bin.underlinetest import UnderlineTest
from bin.landscapetest import LandscapeTest
from bin.linetest import LinesTest
from bin.tabletest import TableTest
from bin.pngtest import PNGTest
from bin.jpgtest import JPGTest
from bin.pagenumbertest import PageNumberTest
from bin.pngsizetest import ImageSizeTest
from bin.ellipsetest import EllipseTest
from bin.circletest import CircleTest
from bin.transformtest import TransformTest
from bin.htmltest import HtmlTest
from bin.htmltest2 import HtmlTest2
from bin.justifytest import JustifyTest
from bin.pdfmargintest import MarginTest
from bin.arctest import ArcTest
from bin.linegraphtest import LineGraphTest
from bin.xyscatterplot import XYScatterPlotTest
from bin.piecharttest import PieChartTest
from bin.barcharttest import BarChartTest
from bin.multibartest import MultiBarChartTest
from bin.graphbackgrounds import GraphBackgroundTest


def main():
    print "Running TextTest"
    TextTest()
    print "Running TrueTypeTest"
    TrueTypeTest()
    print "Running List Test"
    ListTest()
    print "Running Margin Test"
    MarginTest()
    print "Running Underline Test"
    UnderlineTest()
    print "Running LandscapeTest"
    LandscapeTest()
    print "Running LinesTest"
    LinesTest()
    print "Running TableTest"
    TableTest()
    print "Running PNGTest"
    PNGTest()
    print "Running JPGTest"
    JPGTest()
    print "Running PageNumberTest"
    PageNumberTest()
    print "Running PNGSizeTest"
    ImageSizeTest()
    print "Running EllipseTest"
    EllipseTest()
    print "Running CircleTest"
    CircleTest()
    print "Running Arctest"
    ArcTest()
    print "Running TransformTest"
    TransformTest()
    print "Running HTMLTest"
    HtmlTest()
    print "Running HTMLTest2"
    HtmlTest2()
    print "Running Justify Test"
    JustifyTest()
    print "Running LineGraph Test"
    LineGraphTest()
    print "Running XYScatter Test"
    XYScatterPlotTest()
    print "Running PieChart Test"
    PieChartTest()
    print "Running BarChart Test"
    BarChartTest()
    print "Running MultiBarChart Test"
    MultiBarChartTest()
    print "Running GraphBackgrounds Test"
    GraphBackgroundTest()


if __name__ == '__main__':
    main()
