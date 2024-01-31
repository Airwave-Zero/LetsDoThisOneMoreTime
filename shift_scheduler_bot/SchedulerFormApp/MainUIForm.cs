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

        private void button4_Click(object sender, EventArgs e)
        {

        }

        private void button6_Click(object sender, EventArgs e)
        {
            WorkerForm wForm = new WorkerForm(appWorkersFileName);
            wForm.Show();
        }

        private void button5_Click(object sender, EventArgs e)
        {
            ShiftForm sForm = new ShiftForm(appWorkersFileName);
            sForm.Show();
        }

        private void exportScheduleToolStripMenuItem_Click(object sender, EventArgs e)
        {

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
            if(appWorkersFileName == "")
            {
                MessageBox.Show("User did not select file to import, cancelling import.",
                    "Import Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            appWorkersRawString = File.ReadAllText(appWorkersFileName);
            MessageBox.Show("Filename that was imported: " + appWorkersFileName);
        }

        private void exportWorkersToolStripMenuItem1_Click(object sender, EventArgs e)
        {
            // TODO: add checking/guardrail if user imports wrong file
            if(appWorkersFileName == "")
            {
                MessageBox.Show("Cannot export workers due to no file being loaded in.", 
                    "Export Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }    
            string exportedFileName = Utils.exportJSONFile(appWorkersRawString);
            MessageBox.Show("Wrote to file located at: " + exportedFileName);
        }
    }

}
