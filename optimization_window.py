import sys
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from portfolio_class import Portfolio
import pmaso_tools as pmt
import numpy as np
import custom_graph as cgr
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar 

class External(qtc.QThread):
    """
    Runs a counter thread. That runs and updates progress bars
    displayed during the optimization process
    
    """
    
    #counter signal
    countChanged = qtc.pyqtSignal(int)
    #processed finished signal
    finished = qtc.pyqtSignal(str)
    #transmitted weight set signal
    weights = qtc.pyqtSignal(list)
    
    
    def __init__(self, tickers, num_portfolios, bounds, parent=None):
        
        """initializes the class, this thread requires that a tickers,
        num__portfolios and boudary conditions argument respectively be
        passed.
        """
        
        super().__init__()

        #The required arguments
        self.tickers = tickers
        self.data = None
        self.num_portfolios = num_portfolios
        self.bounds = bounds
        
        
    def run(self):
        """Runs the weight set generations routine while simultaneously
        updating a displayed progress bar in the window. I need to fix this function;
        too messy/cluttered and barely functional
        """
        #generates a permutation set based on the passed args
        perms = pmt.get_perms(len(self.tickers),self.bounds)
        
        
        count = 0
        #progress bar while loop; ends when count = 100 for 100% progress
        while count < 100:
            counter = self.num_portfolios
            #step size is determined by 100 divided by the number of portfolios to be generated
            step = 100 / counter
            total = []
            
            
            p_list = list(perms)
            pnum = len(p_list)

                     
            for i in range(pnum):
                if np.sum(np.array(list(p_list[i]))/100) == 1:
                    total.append(list(np.array(p_list[i])/100))
                    counter = counter - 1
                    count = count + step
                    self.countChanged.emit(count)
                if i == pnum - 1:
                    count = 100
        
        perms = None
        p_list = None
        
        self.weight = total
        self.weights.emit(self.weight)
        self.finished.emit('Finished')
        
        
    def stop(self):
       """Ends Thread?
       """
       self.wait()
       
       
      
class Optimization_Window(qtw.QMainWindow):
    """Optimization Window class object
    
    Window that allows the user to generate a space of portfolios based
    on passed tickers and weight set argument, allows for analysis (in the future)
    and facilitates analysis reports"""
    
    def __init__(self,portfolio_dic,dir_path=None):
        super().__init__()
        
        
        self.setWindowTitle('Results')
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.dir_path = dir_path
        self.portfolio_dic = portfolio_dic
        self.tabs = qtw.QTabWidget()
        self.tab_dic = {}
        self.portfolio_dic = portfolio_dic
        self.data = {}
        
        self.fig_els = {key: {} for key in [key for key in self.portfolio_dic.keys()]}
        self.weights = None
        self.setGeometry(self.left,self.top,self.width,self.height)
        
        
        
        self.tabUI()
      
    
        
        
        
        menu = self.menuBar()
        menu.addMenu('File')
        
        self.show()
    
    
    
    
    def combo_selected(self,text):
        print(text)
        
    
    def combo_boxUI(self,box_type='Freq'):
        combo_box = qtg.QComboBox(self)
        
        
        if box_type == 'Freq':
            box_choices = ['Daily','Weekly','Monthly']
        
        elif box_type == 'MaxW':
            #Choices are 50 - 100 in increments of 5
            box_choices = [str(50 + (5*i)) for i in range(11)]
        
        elif box_type == 'MinW':
            #Choices are 0 - 20 in increments of five
            box_choices = [str(5*i) for i in range(5)]
        else:
            box_choices = ['100','500','1000','5000','10000','50000']
            
        for choice in box_choices:
            combo_box.addItem(choice)
        
        combo_box.activated[str].connect(self.combo_selected)
        
        return combo_box
        
    
    def tabUI(self,state='init'):
        self.tabdemo = qtw.QTabWidget()
        
        
        if state == 'init':
            self.tab_dic = {}
            for key,value in self.portfolio_dic.items():
                dic = {}
                tab1 = qtw.QWidget()
                tab1.setObjectName(key)
                freq_combo_box = self.combo_boxUI()
                
                tick_box = qtw.QLineEdit()
                tick_box.setText(value)
                
                tick_dir_box = qtw.QLineEdit()
                tick_dir_box.setObjectName('TickBox')
                
                set_dir_button = qtw.QPushButton('Set Directory')
                set_dir_button.setObjectName(key)
                set_dir_button.clicked.connect(lambda:self.set_directory(tick_dir_box))
                
                num_port_combo_box = self.combo_boxUI('Num_Ports')
                
                min_weight_box = self.combo_boxUI('MinW')
                max_weight_box = self.combo_boxUI('MaxW')
                
                
                if self.dir_path:
                    tick_dir_box.setText(self.dir_path)
                
                layout = qtw.QFormLayout()
                layout.addRow('Tickers', tick_box)
                layout.addRow('',qtw.QLabel(''))
                layout.addRow('Ticker Directory',tick_dir_box)
                layout.addRow('',set_dir_button)
                layout.addRow('',qtw.QLabel(''))
                layout.addRow('Select Frequency', freq_combo_box)
                layout.addRow('',qtw.QLabel(''))
                layout.addRow('Number of Portfolios',num_port_combo_box)
                layout.addRow('',qtw.QLabel(''))
                layout.addRow('Minimum Asset Proportion (%)',min_weight_box)
                layout.addRow('Maximum Asset Proportion (%)',max_weight_box)
                button = qtw.QPushButton('Optimize')
                button.setObjectName(key)
                button.clicked.connect(self.on_btn_clic)
                
                layout.addRow('',button)
                tab1.setLayout(layout)
                
                self.tabdemo.addTab(tab1,str(key))
                
                
                dic['Tab'] = tab1
                dic['Tickers'] = value
                dic['Layout'] = layout
                dic['Freq'] = freq_combo_box
                dic['Tick_box'] = tick_box
                dic['Dir_box'] = tick_dir_box
                dic['Dir_box_text'] = str(tick_dir_box.text())
                dic['Num_port'] = num_port_combo_box
                dic['Opt_button'] = button
                dic['MinWeight'] = min_weight_box = self.combo_boxUI('MinW')
                dic['MaxWeight'] = max_weight_box
                
                self.tab_dic[key] = dic
            
        elif state == 'update_directory':
            dic = {}
            for key,val in self.tab_dic.items():
                dic[key] = {}
                tab1 = qtw.QWidget()
                tab1.setObjectName(key)
                layout = val['Layout']
                
                for i in range(layout.count()):
                    tick_box = layout.itemAt(i).widget()
                    name = tick_box.objectName()
                    if name == 'TickBox':
                        print(name)
                        tick_box.setText(val['Dir_box_text'])
                
                
                
                tab1.setLayout(layout)
                self.tabdemo.addTab(tab1,str(key))
                
                self.tab_dic[key]['Tab'] = tab1
                self.tab_dic[key]['Layout'] = layout
                self.tab_dic[key]['Dir_box_text'] = val['Dir_box_text']
            
            
            
            
            
            
            
        else:
            self.left = 100
            self.top = 100
            self.width = 700
            self.height = 850
            self.setGeometry(self.left,self.top,self.width,self.height)

            
            dic = {}
            for key,val in self.tab_dic.items():
                
                dic[key] = {}
                tab1 = qtw.QWidget()
                tab1.setObjectName(key)
                layout = val['Layout']
                tab1.setLayout(layout)
                self.tabdemo.addTab(tab1,str(key))
            
                self.tab_dic[key]['Tab'] = tab1
                self.tab_dic[key]['Layout'] = layout
                
            
         
        
        self.layout = qtw.QVBoxLayout()
        
        self.tabdemo.setLayout(self.layout)
        
        
        self.table_widget = self.tabdemo
        self.setCentralWidget(self.table_widget)
            

    def set_directory(self,box):
        sending_button = self.sender()
        self.name = sending_button.objectName()
        dname = qtw.QFileDialog.getExistingDirectory(self,'Select a directory')
        
        self.tab_dic[self.name]['Dir_box_text'] = dname
        
        self.tabUI(state='update_directory')
        
        self.tabdemo.setCurrentWidget(self.tabdemo.findChild(qtw.QWidget,self.name))
        
        
    def clear_tab_layout(self):
        
        for i in reversed(range(self.rem_layout.count())):
            widgetToRemove = self.rem_layout.itemAt(i)
            
            if widgetToRemove.widget():
                wid = widgetToRemove.widget()
                self.rem_layout.removeWidget(wid)
                wid.setParent(None)
        
    def onCountChanged(self, value):
        self.progress.setValue(value)
        
        
    def on_btn_clic(self):
        
        """Handles portfolio optimization and refreshes the relevant
        tab to reflect the results of the optimization process"""
        
        #Gets the tab in which an optimization button was pressed
        sending_button = self.sender()
        self.name = sending_button.objectName()
        
        
    
        #Clears the current tab layout
        self.rem_layout = self.tab_dic[self.name]['Layout']
        self.clear_tab_layout()
        
        #adds a progress Bar in the middle of the tab widget
        for i in range(7):
            self.rem_layout.addRow('',qtw.QLabel(""))
        self.progress = qtw.QProgressBar(self)
        self.rem_layout.addRow('          ',self.progress)
        
        
        #Optimization work, tickers are passed to the optimization worker
        #thread which handles optimization math and progress bar 
        current_ticks = str(self.tab_dic[self.name]['Tick_box'].text())
        self.ticker_list = pmt.ticker_parse(current_ticks)
   
        
        num_portfolios = int(self.tab_dic[self.name]['Num_port'].currentText())
        
        min_b = int(self.tab_dic[self.name]['MinWeight'].currentText())
        max_b = int(self.tab_dic[self.name]['MaxWeight'].currentText())
        bounds = (min_b,max_b)
        
        self.calc = External(self.ticker_list,num_portfolios,bounds)
        self.calc.countChanged.connect(self.onCountChanged)
        self.calc.start()
        self.calc.weights.connect(self.receive_data)
        self.calc.finished.connect(self.onFinished)
    
    def receive_data(self,weights):
        self.weights = None
        if weights:
            self.weights = weights
    
    
    def graph_box_checked(self,b):
        if b.isChecked():
            self.fig_els[self.name][b.text()] = True
        else:
            self.fig_els[self.name][b.text()] = False
            
        
    
    
    def param_gen(self):
        
        
        weights = self.weights
        dir_path = self.tab_dic[self.name]['Dir_box_text']
        freq = str(self.tab_dic[self.name]['Freq'].currentText())
        
        portfolio = Portfolio(self.ticker_list,dir_path,freq)
        sec_params = portfolio.gen_sec_parameters()
        opt_params = portfolio.get_opt_portfolios(sec_params,weights,tolerance=0.2)
        
        self.data[self.name] = {'Params':sec_params,
                                'Optimization_Params':opt_params}
        
        
        
        return sec_params, opt_params
        
    def onFinished(self,fin):
        """This function is called when the optimization work is completed,
        the progress bar is cleared and data visualization widgets are 
        rendered on the tab widget"""
        
        
        if fin == 'Finished':
        
            self.calc.stop()
            self.progress.hide()
            self.clear_tab_layout()
            
            tab1 = self.tab_dic[self.name]['Tab']
            
            
            
            
            sec_params, opt_params= self.param_gen()
            self.data[self.name] ={'Securities':sec_params,
                                   'Optimization':opt_params}
            
            n = len(opt_params['Portfolio_Space_Returns'])
            m = len(opt_params['Frontier_Returns'])
            # Set white background and black foreground
            
            
            
            pos2 = [{'pos': opt_params['Frontier Vals'][:, i]} for i in range(m)]
            
            
            # plot data: x, y values
            self.graphWidget = cgr.CustomCanvas(self.data[self.name]['Optimization'])
            
            
            
            
            # Convert data array into a list of dictionaries with the x,y-coordinates
            
          
            
            
            
            
            
            layout = self.resultsUI()
            self.tab_dic[self.name]['Layout'] = layout
            
            
            self.tabUI(state='change')
            self.tabdemo.setCurrentWidget(self.tabdemo.findChild(qtw.QWidget,self.name))
    
    def apply_plot_settings(self):
        
        sending_button = self.sender()
        self.name = sending_button.objectName()
        
        f_e = self.fig_els[self.name]
        
        self.graph_items = [key for key,val in f_e.items() if val == True]
        data = self.data[self.name]['Optimization']
        
        
        
        if 'All Portfolios' in self.graph_items:
            print('cool')
            
        if 'Best Portfolios' in self.graph_items:
            print('gotta fix this')

        layout = self.resultsUI()
        self.tab_dic[self.name]['Layout'] = layout
        
        
        for key in self.fig_els[self.name].keys():
            self.fig_els[self.name][key] = False
        
        self.tabUI(state='change')
        self.tabdemo.setCurrentWidget(self.tabdemo.findChild(qtw.QWidget,self.name))
        
    def gen_report(self):
        
        fname, _ = qtw.QFileDialog.getSaveFileName(self,
                                                   'Save File',
                                                   'c:/',
                                                   'Excel Files (*.xlsx)')
        
        
        
        
        current_ticks = str(self.tab_dic[self.name]['Tick_box'].text())
        tickers = pmt.ticker_parse(current_ticks) 
        pmt.gen_report(tickers,self.data[self.name]['Optimization'],fname)
        
        
            
    def resultsUI(self):
        
        layout1a = qtw.QHBoxLayout()
        layout1 = qtw.QVBoxLayout()
        layout2 = qtw.QGridLayout()
        label = qtw.QLabel('Plot Items')
        label2 = qtw.QLabel('')
        chk1 = qtw.QCheckBox('Best Portfolios')
        chk2 = qtw.QCheckBox('All Portfolios')
        chk1.toggled.connect(lambda:self.graph_box_checked(chk1))
        chk2.toggled.connect(lambda:self.graph_box_checked(chk2))
        apply_button = qtw.QPushButton('Apply')
        report_button = qtw.QPushButton('Generate Report')
        report_button.clicked.connect(self.gen_report)
        apply_button.setObjectName(self.name)
        apply_button.clicked.connect(self.apply_plot_settings)
        graph_tools = NavigationToolbar(self.graphWidget,self)
        
        wid1 = qtw.QWidget()
        layout1.addWidget(self.graphWidget)
        layout1.addWidget(qtw.QLabel(''))
        layout1.addWidget(graph_tools)
        wid1.setLayout(layout1)
        
        wid1a = qtw.QWidget()
        layout1a.addWidget(wid1)
        wid1a.setLayout(layout1a)
        
        wid2 = qtw.QWidget()
        layout2.addWidget(label,0,0,1,1)
        layout2.addWidget(label2,1,0,1,1)
        layout2.addWidget(chk1,2,0,1,1)
        layout2.addWidget(chk2,3,0,1,1)
        layout2.addWidget(report_button,3,2,1,1)
        layout2.addWidget(apply_button,2,2,1,1)
        wid2.setLayout(layout2)
        
        layout = qtw.QVBoxLayout()
        layout.addWidget(wid1a)
        layout.addWidget(wid2)
        
        return layout
          
    
    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key_Q:
            print("Killing")
            self.deleteLater()
        elif event.key() == qtc.Qt.Key_Return:
            lsso = self.graphWidget.CustomPlot.lsso
            print(lsso.xys[lsso.ind])
        event.accept()
        
        
        
if __name__ == '__main__':
    """this allows you to intialize the window, the keys are the names of the portfolios
    and the tickers will populate ticker lineedit widgets make sure to download the 
    historical data files from the main repository and place them in the same folder 
    to run the optimization process"""
    pd = {'Hello':'AIG,BA,CVX','22':'CVX,IBM'}
    app = qtw.QApplication(sys.argv)
    mw = Results_Window(pd,'E:/')
    sys.exit(app.exec())