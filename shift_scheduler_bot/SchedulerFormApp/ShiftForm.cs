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
    public partial class ShiftForm : Form
    {
        public string shiftFileName;
        public string shiftFileRaw;
        public ShiftForm(string fileName = "")
        {
            shiftFileName = fileName;
            MessageBox.Show("Attempted to load in: " + fileName);
            if (fileName == "")
            {
                MessageBox.Show("No file detected, loading in default");
                //shiftFileName = "C:/Users/bboyf/OneDrive/Desktop/CODE/LetsDoThisOneMoreTime/shift_scheduler_bot/SchedulerFormApp/JSON_files/Workers.json";
            }
            shiftFileRaw = File.ReadAllText(shiftFileName);
            InitializeComponent();
        }

        private void panel1_Paint(object sender, PaintEventArgs e)
        {

        }

        private void ShiftForm_Load(object sender, EventArgs e)
        {

        }

        private void SaveShift_Button_Click(object sender, EventArgs e)
        {

        }

        private void CancelShift_Button_Click(object sender, EventArgs e)
        {
            // Simply closes the shift UI window without making any changes
            this.Close();
        }
        private void ShiftForm_EscapeKeyDown(object sender, KeyEventArgs e)
        {
            // Shortcut for closing the changes window
            if (e.KeyCode == Keys.Escape)
            {
                this.Close();
            }
        }
    }
}
