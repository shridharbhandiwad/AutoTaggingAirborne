"""
Main GUI Window for Radar Target Analyzer

Provides graphical interface for file selection, parameter configuration,
data visualization, and analysis control.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QTabWidget,
    QGroupBox, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QProgressBar, QTableWidget, QTableWidgetItem,
    QSplitter, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
import yaml

logger = logging.getLogger(__name__)


class ProcessingThread(QThread):
    """Background thread for data processing."""
    
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.operation(*self.args, **self.kwargs, 
                                   progress_callback=self.progress.emit,
                                   status_callback=self.status.emit)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            self.error.emit(str(e))


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for embedding plots."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)


class RadarAnalyzerGUI(QMainWindow):
    """
    Main GUI window for Radar Target Analyzer.
    """
    
    def __init__(self):
        super().__init__()
        
        self.data_loader = None
        self.feature_extractor = None
        self.tagging_engine = None
        self.synthetic_generator = None
        
        self.current_data = None
        self.current_features = None
        self.current_tags = None
        
        self.config = self.load_default_config()
        
        self.init_ui()
        self.init_modules()
        
    def load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        config_path = Path(__file__).parent.parent.parent.parent / 'config' / 'default_config.yaml'
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            return {}
    
    def init_modules(self):
        """Initialize processing modules."""
        from radar_analyzer import (
            RadarDataLoader, FeatureExtractor, 
            TaggingEngine, SyntheticDataGenerator
        )
        
        self.data_loader = RadarDataLoader(self.config.get('data_processing', {}))
        self.feature_extractor = FeatureExtractor(self.config.get('features', {}))
        self.tagging_engine = TaggingEngine(self.config.get('features', {}))
        self.synthetic_generator = SyntheticDataGenerator(self.config.get('synthetic_data', {}))
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Airborne Radar Target Behavior Analyzer v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Airborne Radar Target Behavior Analysis System")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Add tabs
        tabs.addTab(self.create_data_tab(), "Data Loading")
        tabs.addTab(self.create_analysis_tab(), "Analysis && Tagging")
        tabs.addTab(self.create_synthetic_tab(), "Synthetic Data")
        tabs.addTab(self.create_config_tab(), "Configuration")
        tabs.addTab(self.create_results_tab(), "Results")
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.progress_bar.setVisible(False)
    
    def create_data_tab(self) -> QWidget:
        """Create data loading tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        file_btn_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_btn = QPushButton("Select Radar Data File")
        self.file_btn.clicked.connect(self.select_file)
        file_btn_layout.addWidget(self.file_label)
        file_btn_layout.addWidget(self.file_btn)
        file_layout.addLayout(file_btn_layout)
        
        self.load_btn = QPushButton("Load Data")
        self.load_btn.clicked.connect(self.load_data)
        self.load_btn.setEnabled(False)
        file_layout.addWidget(self.load_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Data info group
        info_group = QGroupBox("Data Information")
        info_layout = QFormLayout()
        
        self.info_samples = QLabel("-")
        self.info_duration = QLabel("-")
        self.info_prf = QLabel("-")
        self.info_freq = QLabel("-")
        
        info_layout.addRow("Number of Samples:", self.info_samples)
        info_layout.addRow("Duration:", self.info_duration)
        info_layout.addRow("PRF:", self.info_prf)
        info_layout.addRow("Center Frequency:", self.info_freq)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Visualization
        vis_group = QGroupBox("Data Visualization")
        vis_layout = QVBoxLayout()
        
        self.data_canvas = MatplotlibCanvas(self, width=8, height=5)
        vis_layout.addWidget(self.data_canvas)
        
        vis_group.setLayout(vis_layout)
        layout.addWidget(vis_group)
        
        layout.addStretch()
        
        return widget
    
    def create_analysis_tab(self) -> QWidget:
        """Create analysis and tagging tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.extract_btn = QPushButton("Extract Features")
        self.extract_btn.clicked.connect(self.extract_features)
        self.extract_btn.setEnabled(False)
        btn_layout.addWidget(self.extract_btn)
        
        self.tag_btn = QPushButton("Tag Behavior")
        self.tag_btn.clicked.connect(self.tag_behavior)
        self.tag_btn.setEnabled(False)
        btn_layout.addWidget(self.tag_btn)
        
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        btn_layout.addWidget(self.export_btn)
        
        layout.addLayout(btn_layout)
        
        # Splitter for features and tags
        splitter = QSplitter(Qt.Horizontal)
        
        # Features table
        features_group = QGroupBox("Extracted Features")
        features_layout = QVBoxLayout()
        self.features_table = QTableWidget()
        self.features_table.setColumnCount(2)
        self.features_table.setHorizontalHeaderLabels(["Feature", "Value"])
        features_layout.addWidget(self.features_table)
        features_group.setLayout(features_layout)
        splitter.addWidget(features_group)
        
        # Tags display
        tags_group = QGroupBox("Behavior Tags")
        tags_layout = QVBoxLayout()
        self.tags_text = QTextEdit()
        self.tags_text.setReadOnly(True)
        tags_layout.addWidget(self.tags_text)
        tags_group.setLayout(tags_layout)
        splitter.addWidget(tags_group)
        
        layout.addWidget(splitter)
        
        # Trajectory plot
        traj_group = QGroupBox("Trajectory Visualization")
        traj_layout = QVBoxLayout()
        self.traj_canvas = MatplotlibCanvas(self, width=8, height=4)
        traj_layout.addWidget(self.traj_canvas)
        traj_group.setLayout(traj_layout)
        layout.addWidget(traj_group)
        
        return widget
    
    def create_synthetic_tab(self) -> QWidget:
        """Create synthetic data generation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Parameters group
        params_group = QGroupBox("Synthetic Data Parameters")
        params_layout = QFormLayout()
        
        self.synth_num_targets = QSpinBox()
        self.synth_num_targets.setRange(1, 1000)
        self.synth_num_targets.setValue(10)
        params_layout.addRow("Number of Targets:", self.synth_num_targets)
        
        self.synth_duration = QDoubleSpinBox()
        self.synth_duration.setRange(1.0, 600.0)
        self.synth_duration.setValue(60.0)
        self.synth_duration.setSuffix(" seconds")
        params_layout.addRow("Duration:", self.synth_duration)
        
        self.synth_noise = QDoubleSpinBox()
        self.synth_noise.setRange(0.0, 1.0)
        self.synth_noise.setSingleStep(0.01)
        self.synth_noise.setValue(0.05)
        params_layout.addRow("Noise Level:", self.synth_noise)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Generation buttons
        btn_layout = QHBoxLayout()
        
        self.gen_dataset_btn = QPushButton("Generate Dataset")
        self.gen_dataset_btn.clicked.connect(self.generate_synthetic_dataset)
        btn_layout.addWidget(self.gen_dataset_btn)
        
        self.gen_test_btn = QPushButton("Generate Test Scenarios")
        self.gen_test_btn.clicked.connect(self.generate_test_scenarios)
        btn_layout.addWidget(self.gen_test_btn)
        
        layout.addLayout(btn_layout)
        
        # Output log
        log_group = QGroupBox("Generation Log")
        log_layout = QVBoxLayout()
        self.synth_log = QTextEdit()
        self.synth_log.setReadOnly(True)
        log_layout.addWidget(self.synth_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        return widget
    
    def create_config_tab(self) -> QWidget:
        """Create configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Config editor
        config_group = QGroupBox("Configuration (YAML)")
        config_layout = QVBoxLayout()
        
        self.config_edit = QTextEdit()
        self.config_edit.setPlainText(yaml.dump(self.config, default_flow_style=False))
        config_layout.addWidget(self.config_edit)
        
        btn_layout = QHBoxLayout()
        
        load_config_btn = QPushButton("Load Config File")
        load_config_btn.clicked.connect(self.load_config_file)
        btn_layout.addWidget(load_config_btn)
        
        save_config_btn = QPushButton("Save Config")
        save_config_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(save_config_btn)
        
        apply_config_btn = QPushButton("Apply Config")
        apply_config_btn.clicked.connect(self.apply_config)
        btn_layout.addWidget(apply_config_btn)
        
        config_layout.addLayout(btn_layout)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        return widget
    
    def create_results_tab(self) -> QWidget:
        """Create results display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Results text
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.results_text)
        
        return widget
    
    def select_file(self):
        """Open file dialog to select radar data file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Radar Data File",
            "",
            "All Supported (*.bin *.dat *.h5 *.hdf5);;Binary Files (*.bin *.dat);;HDF5 Files (*.h5 *.hdf5);;All Files (*)"
        )
        
        if filename:
            self.file_label.setText(Path(filename).name)
            self.current_file = filename
            self.load_btn.setEnabled(True)
            self.statusBar().showMessage(f"Selected: {filename}")
    
    def load_data(self):
        """Load radar data from selected file."""
        if not hasattr(self, 'current_file'):
            return
        
        try:
            self.statusBar().showMessage("Loading data...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Load data
            self.current_data = self.data_loader.load_file(self.current_file)
            
            # Update info
            metadata = self.current_data.get('metadata', {})
            self.info_samples.setText(str(len(self.current_data.get('timestamps', []))))
            
            duration = self.current_data.get('timestamps', [0])[-1] if len(self.current_data.get('timestamps', [])) > 0 else 0
            self.info_duration.setText(f"{duration:.2f} s")
            self.info_prf.setText(f"{metadata.get('prf', 0):.1f} Hz")
            self.info_freq.setText(f"{metadata.get('center_frequency', 0)/1e9:.2f} GHz")
            
            # Visualize
            self.visualize_data()
            
            # Enable buttons
            self.extract_btn.setEnabled(True)
            
            self.statusBar().showMessage("Data loaded successfully")
            self.progress_bar.setVisible(False)
            
            QMessageBox.information(self, "Success", "Data loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{str(e)}")
            self.statusBar().showMessage("Error loading data")
            self.progress_bar.setVisible(False)
    
    def visualize_data(self):
        """Visualize loaded radar data."""
        if self.current_data is None:
            return
        
        self.data_canvas.axes.clear()
        
        # Plot Doppler spectrum
        if 'doppler' in self.current_data:
            doppler = self.current_data['doppler']
            self.data_canvas.axes.plot(np.abs(doppler[:min(1000, len(doppler))]))
            self.data_canvas.axes.set_title('Doppler Spectrum')
            self.data_canvas.axes.set_xlabel('Frequency Bin')
            self.data_canvas.axes.set_ylabel('Magnitude')
            self.data_canvas.axes.grid(True)
        
        self.data_canvas.draw()
    
    def extract_features(self):
        """Extract features from loaded data."""
        if self.current_data is None:
            return
        
        try:
            self.statusBar().showMessage("Extracting features...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(50)
            
            self.current_features = self.feature_extractor.extract_all_features(self.current_data)
            
            # Display features
            self.display_features()
            
            # Enable tagging
            self.tag_btn.setEnabled(True)
            
            self.statusBar().showMessage("Features extracted successfully")
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to extract features:\n{str(e)}")
            self.statusBar().showMessage("Error extracting features")
            self.progress_bar.setVisible(False)
    
    def display_features(self):
        """Display extracted features in table."""
        if self.current_features is None:
            return
        
        self.features_table.setRowCount(0)
        
        for i, (key, value) in enumerate(sorted(self.current_features.items())):
            if isinstance(value, (int, float, np.number)):
                self.features_table.insertRow(i)
                self.features_table.setItem(i, 0, QTableWidgetItem(key))
                self.features_table.setItem(i, 1, QTableWidgetItem(f"{float(value):.4f}"))
        
        self.features_table.resizeColumnsToContents()
    
    def tag_behavior(self):
        """Tag target behavior."""
        if self.current_features is None:
            return
        
        try:
            self.statusBar().showMessage("Tagging behavior...")
            
            self.current_tags = self.tagging_engine.tag_target(self.current_features)
            
            # Display tags
            self.display_tags()
            
            # Generate report
            report = self.tagging_engine.generate_report(self.current_features, self.current_tags)
            self.results_text.setPlainText(report)
            
            # Visualize trajectory
            self.visualize_trajectory()
            
            # Enable export
            self.export_btn.setEnabled(True)
            
            self.statusBar().showMessage("Tagging complete")
            
        except Exception as e:
            logger.error(f"Error tagging behavior: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to tag behavior:\n{str(e)}")
            self.statusBar().showMessage("Error tagging behavior")
    
    def display_tags(self):
        """Display behavior tags."""
        if self.current_tags is None:
            return
        
        text = "DETECTED BEHAVIOR TAGS:\n\n"
        for tag in self.current_tags:
            text += f"  ✓ {tag.replace('_', ' ').title()}\n"
        
        self.tags_text.setPlainText(text)
    
    def visualize_trajectory(self):
        """Visualize target trajectory."""
        if self.current_data is None or 'position' not in self.current_data:
            return
        
        position = self.current_data['position']
        
        self.traj_canvas.axes.clear()
        self.traj_canvas.axes.plot(position[:, 0], position[:, 1], 'b-', linewidth=2)
        self.traj_canvas.axes.plot(position[0, 0], position[0, 1], 'go', markersize=10, label='Start')
        self.traj_canvas.axes.plot(position[-1, 0], position[-1, 1], 'ro', markersize=10, label='End')
        self.traj_canvas.axes.set_title('Target Trajectory (Top View)')
        self.traj_canvas.axes.set_xlabel('X Position (m)')
        self.traj_canvas.axes.set_ylabel('Y Position (m)')
        self.traj_canvas.axes.legend()
        self.traj_canvas.axes.grid(True)
        self.traj_canvas.axes.axis('equal')
        
        self.traj_canvas.draw()
    
    def export_results(self):
        """Export analysis results."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                self.tagging_engine.export_tags(
                    [self.current_features],
                    [self.current_tags],
                    filename
                )
                QMessageBox.information(self, "Success", f"Results exported to:\n{filename}")
                self.statusBar().showMessage(f"Results exported to {filename}")
            except Exception as e:
                logger.error(f"Error exporting results: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to export results:\n{str(e)}")
    
    def generate_synthetic_dataset(self):
        """Generate synthetic dataset."""
        try:
            self.synth_log.append("Generating synthetic dataset...")
            
            num_targets = self.synth_num_targets.value()
            duration = self.synth_duration.value()
            noise = self.synth_noise.value()
            
            # Update config
            config = {
                'num_targets': num_targets,
                'duration': duration,
                'noise_level': noise
            }
            self.synthetic_generator = SyntheticDataGenerator(config)
            
            # Generate dataset
            dataset = self.synthetic_generator.generate_dataset()
            
            # Save dataset
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if output_dir:
                self.synthetic_generator.save_synthetic_dataset(dataset, output_dir)
                self.synth_log.append(f"✓ Generated {num_targets} synthetic targets")
                self.synth_log.append(f"✓ Saved to: {output_dir}")
                QMessageBox.information(self, "Success", f"Generated {num_targets} synthetic targets!")
            
        except Exception as e:
            logger.error(f"Error generating synthetic data: {e}", exc_info=True)
            self.synth_log.append(f"✗ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate data:\n{str(e)}")
    
    def generate_test_scenarios(self):
        """Generate test scenarios."""
        try:
            self.synth_log.append("Generating test scenarios...")
            
            scenarios = self.synthetic_generator.generate_test_scenarios()
            
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if output_dir:
                self.synthetic_generator.save_synthetic_dataset(scenarios, output_dir)
                self.synth_log.append(f"✓ Generated {len(scenarios)} test scenarios")
                self.synth_log.append(f"✓ Saved to: {output_dir}")
                QMessageBox.information(self, "Success", f"Generated {len(scenarios)} test scenarios!")
            
        except Exception as e:
            logger.error(f"Error generating test scenarios: {e}", exc_info=True)
            self.synth_log.append(f"✗ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate scenarios:\n{str(e)}")
    
    def load_config_file(self):
        """Load configuration from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.config_edit.setPlainText(yaml.dump(self.config, default_flow_style=False))
                QMessageBox.information(self, "Success", "Configuration loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load configuration:\n{str(e)}")
    
    def save_config(self):
        """Save configuration to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "",
            "YAML Files (*.yaml);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.config_edit.toPlainText())
                QMessageBox.information(self, "Success", "Configuration saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{str(e)}")
    
    def apply_config(self):
        """Apply configuration changes."""
        try:
            self.config = yaml.safe_load(self.config_edit.toPlainText())
            self.init_modules()  # Reinitialize modules with new config
            QMessageBox.information(self, "Success", "Configuration applied successfully!")
            self.statusBar().showMessage("Configuration applied")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply configuration:\n{str(e)}")


def launch_gui():
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = RadarAnalyzerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch_gui()
