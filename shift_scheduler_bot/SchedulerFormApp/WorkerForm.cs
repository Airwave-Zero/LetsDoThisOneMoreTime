using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
using System.Runtime.Remoting.Contexts;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;


namespace scheduler_test1
{
    public partial class WorkerForm : Form
    {
        public string workerFileName;
        public string workerFileRaw;
        public WorkerForm(string fileName = "")
        {
            workerFileName = fileName;
            InitializeComponent();
        }

        private void dataGridView1_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void WorkerForm_Load(object sender, EventArgs e)
        {
            MessageBox.Show("Attempted to load in: " + workerFileName);
            if (workerFileName == "")
            {
                //MessageBox.Show("No file detected, loading in default");
                workerFileName = "C:/Users/bboyf/OneDrive/Desktop/CODE/LetsDoThisOneMoreTime/shift_scheduler_bot/SchedulerFormApp/JSON_files/Workers.json";
            }
            workerFileRaw = File.ReadAllText(workerFileName);
            string jsonString = File.ReadAllText(workerFileName);
            dataGridView1.DataSource = JsonConvert.DeserializeObject<DataTable>(jsonString);
            dataGridView1.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.AllCells;
            dataGridView1.DefaultCellStyle.WrapMode = DataGridViewTriState.True;
            string shortenedFN = Path.GetFileName(workerFileName);
            WorkerFFN_Label.Text += " " + shortenedFN;
        }
        
        private void SaveButton_Click(object sender, EventArgs e)
        {
            // Save the current data in the table back into the file
            string output = JsonConvert.SerializeObject(dataGridView1.DataSource);
            SaveFileDialog saveFileDialog1 = new SaveFileDialog();

            saveFileDialog1.Filter = "JSON files (*.JSON)|*.JSON|All files (*.*)|*.*";
            saveFileDialog1.FilterIndex = 1;
            saveFileDialog1.RestoreDirectory = true;

            if (saveFileDialog1.ShowDialog() == DialogResult.OK)
            {
                if (saveFileDialog1.FileName != "")
                {
                    File.WriteAllText(saveFileDialog1.FileName, output);
                    this.Close();
                }
            }
            else
            {
                MessageBox.Show("User cancelled save.");
            }
            
        }
        
        private void CancelButton_Click(object sender, EventArgs e)
        {
            // Simply close the window, do not update the file
            this.Close();
        }

        private void WorkerForm_EscapeKeyDown(object sender, KeyEventArgs e)
        {
            // Shortcut for closing the changes window
            if (e.KeyCode == Keys.Escape)
            {
                this.Close();
            }
        }
    }
}
