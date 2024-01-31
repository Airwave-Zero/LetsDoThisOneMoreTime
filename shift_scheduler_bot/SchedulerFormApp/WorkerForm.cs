using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
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
            MessageBox.Show("Attempted to load in: " + fileName);
            if (fileName == "")
            {
                MessageBox.Show("No file detected, loading in default");
                workerFileName = "C:/Users/bboyf/OneDrive/Desktop/CODE/LetsDoThisOneMoreTime/shift_scheduler_bot/SchedulerFormApp/JSON_files/Workers.json";
            }
            workerFileRaw = File.ReadAllText(workerFileName);
            InitializeComponent();
        }

        private void dataGridView1_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void WorkerForm_Load(object sender, EventArgs e)
        {
            if(workerFileName != "")
            {
                string jsonString = File.ReadAllText(workerFileName);
                dataGridView1.DataSource = JsonConvert.DeserializeObject<DataTable>(jsonString);
                dataGridView1.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.AllCells;
                dataGridView1.DefaultCellStyle.WrapMode = DataGridViewTriState.True;
            }
        }
        
        private void SaveButton_Click(object sender, EventArgs e)
        {
            // Save the current data in the table back into the file
            string output = JsonConvert.SerializeObject(dataGridView1.DataSource);
            Stream myStream;
            SaveFileDialog saveFileDialog1 = new SaveFileDialog();

            saveFileDialog1.Filter = "JSON files (*.JSON)|*.JSON|All files (*.*)|*.*";
            saveFileDialog1.FilterIndex = 2;
            saveFileDialog1.RestoreDirectory = true;

            if (saveFileDialog1.ShowDialog() == DialogResult.OK)
            {
                if ((myStream = saveFileDialog1.OpenFile()) != null)
                {
                    //filename is saveFileDialog1.FileName
                    System.IO.File.WriteAllText(saveFileDialog1.FileName, output);
                    myStream.Close();
                }
            }
            
        }
        
        private void CancelButton_Click(object sender, EventArgs e)
        {
            // Close the window, do not update the file
        }

        
    }
}
