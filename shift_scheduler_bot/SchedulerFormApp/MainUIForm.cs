﻿using Newtonsoft.Json;
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
using Newtonsoft.Json.Linq;

namespace scheduler_test1
{
    public partial class MainUIForm : Form
    {
        public string appWorkersFileName;
        public string appWorkersRawString;
        public string appScheduleFileName;
        public string appScheduleRawString;
        public string appRulesFileName;
        public string appRulesRawString;
        public string appHolidaysFileName;
        public string appHolidaysRawString;
        public string appDaysOffFileName;
        public string appDaysOffRawString;
        public enum Calendar { January = 1, February, March, April, May, June,
                                July, August, September, October, November, December};
        public MainUIForm()
        {
            appWorkersFileName = "";
            appWorkersRawString = "";
            appScheduleFileName = "";
            appScheduleRawString = "";
            appRulesFileName = "";
            appRulesRawString = "";
            appHolidaysFileName = "";
            appHolidaysRawString = "";
            appDaysOffFileName = "";
            appDaysOffRawString = "";
            InitializeComponent();
        }
        
        private void MainUIForm_Load(object sender, EventArgs e)
        {
            //TODO: look for last loaded file(s) and load those in
        }

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
            ShiftForm sForm = new ShiftForm(appScheduleFileName);
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
            JObject schedule = JObject.Parse(appScheduleRawString);
            string schedMonth = schedule["Schedule"]["Month"].ToString();
            // do this in a for loop
            TextBox[] test = { MondayTextBox, TuesdayTextBox, WednesdayTextBox, ThursdayTextBox, 
                FridayTextBox, SaturdayTextBox, SundayTextBox};

            MondayTextBox.Text = "Monday " + Enum.Parse(typeof(int), schedMonth).ToString() + ;
            //TODO : update the UI with all the shifts
        }
        private void exportScheduleJSONToolStripMenuItem_Click(object sender, EventArgs e)
        {
            bool successExport = sharedExport(appScheduleFileName);
            if (successExport)
            {
                string exportedFileName = Utils.exportJSONFile(appScheduleRawString);
                MessageBox.Show("Wrote to file located at: " + exportedFileName);
            }
        }
        
        private void exportSchedulePNGToolStripMenuItem_Click(object sender, EventArgs e)
        {
            int windowWidth = 1247;
            int windowHeight = 825;
            using (var bmp = new Bitmap(windowWidth, windowHeight))
            {
                DrawToBitmap(bmp, new Rectangle(0, 0, bmp.Width, bmp.Height));
                bmp.Save(@"C:\Users\bboyf\OneDrive\Desktop\CODE\LetsDoThisOneMoreTime\shift_scheduler_bot\SchedulerFormApp\JSON_files\screenshot.png");
            }
        }

        private void Previous_Click(object sender, EventArgs e)
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
