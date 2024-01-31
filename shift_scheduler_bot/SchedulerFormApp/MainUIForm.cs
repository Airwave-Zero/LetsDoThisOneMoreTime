using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO; 

namespace scheduler_test1
{
    public partial class MainUIForm : Form
    {
        public MainUIForm()
        {
            InitializeComponent();
        }
        public string appWorkersFileName = "";
        public string appWorkersRawString = "";
        public string appScheduleFileName = "";
        public string appScheduleRawString = "";
        public string appRulesFileName = "";
        public string appRulesRawString;
        public string appHolidaysFileName = "";
        public string appHolidaysRawString;
        public string appDaysOffFileName = "";
        public string appDaysOffRawString = "";

        private void GenerateSchedule_Click(object sender, EventArgs e)
        {

        }

        private void WorkerForm_Click(object sender, EventArgs e)
        {
            WorkerForm wForm = new WorkerForm(appWorkersFileName);
            wForm.Show();
        }
        private void Add_Shift_Click(object sender, EventArgs e)
        {
            ShiftForm sForm = new ShiftForm(appWorkersFileName);
            sForm.Show();
        }
        private void EditShift_Click(object sender, EventArgs e)
        {
            ShiftForm sForm = new ShiftForm(appWorkersFileName);
            sForm.Show();
        }
        private void importScheduleToolStripMenuItem_Click(object sender, EventArgs e)
        {
            appScheduleFileName = Utils.importJSONFile();
            bool successImport = sharedImport(appScheduleFileName);
            if (successImport)
            {
                appScheduleRawString = File.ReadAllText(appScheduleFileName);
            }
        }
        private void exportScheduleToolStripMenuItem_Click(object sender, EventArgs e)
        {
            bool successExport = sharedExport(appScheduleFileName);
            if (successExport)
            {
                string exportedFileName = Utils.exportJSONFile(appScheduleRawString);
                MessageBox.Show("Wrote to file located at: " + exportedFileName);
            }
        }


        private void Previous_Click(object sender, EventArgs e)
        {

        }


        private void MainUIForm_Load(object sender, EventArgs e)
        {

        }

        private void importWorkersToolStripMenuItem1_Click(object sender, EventArgs e)
        {
            // TODO: add checking/guardrail if user imports wrong file
            appWorkersFileName = Utils.importJSONFile();
            bool successImport = sharedImport(appWorkersFileName);
            if(successImport)
            {
                appWorkersRawString = File.ReadAllText(appWorkersFileName);
            }
        }

        private void exportWorkersToolStripMenuItem1_Click(object sender, EventArgs e)
        {
            // TODO: add checking/guardrail if user imports wrong file
            bool successExport = sharedExport(appWorkersFileName);
            if(successExport)
            {
                string exportedFileName = Utils.exportJSONFile(appWorkersRawString);
                MessageBox.Show("Wrote to file located at: " + exportedFileName);
            }
        }

        private bool sharedImport(string fileName)
        {
            if(fileName == "") 
            {
                MessageBox.Show("Cannot import " + fileName + " due to no file being loaded in.",
                    "Import Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
            else {
                MessageBox.Show("File that was imported: " + fileName);
            }
            return fileName == "";
        }

        private bool sharedExport(string fileName)
        {
            if (fileName == "")
            {
                MessageBox.Show("Cannot export " + fileName + " due to no file being loaded in.",
                    "Export Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
            else
            {
                MessageBox.Show("File that was exported: " + fileName);
            }
            return fileName == "";
        }
    }

}
